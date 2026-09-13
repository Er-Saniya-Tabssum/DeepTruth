from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import models
from ..auth import get_current_user
from ..config import settings
from ..db import get_db
from ..schemas import ApiError, ApiResponse
from ..services.removal import detect_text_regions, remove_masked_object, remove_text

router = APIRouter()
ALLOWED = {".jpg", ".jpeg", ".png", ".webp"}


def _save_upload(upload: UploadFile, directory: str, filename: str) -> tuple[str, int]:
    data = upload.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(data) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File is too large")
    Path(directory).mkdir(parents=True, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, "wb") as handle:
        handle.write(data)
    return path, len(data)


def _job(db: Session, job_id: str, user: models.User) -> models.RemovalJob:
    job = db.query(models.RemovalJob).filter(models.RemovalJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Removal job not found")
    if job.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return job


@router.post("/detect-text", response_model=ApiResponse)
def detect_text(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_FILE", message="Use JPG, PNG or WEBP."))
    temp_dir = os.path.join(settings.upload_dir, current_user.id, "removal-detect")
    source, _ = _save_upload(file, temp_dir, f"{uuid.uuid4().hex}{ext}")
    try:
        regions = detect_text_regions(source)
        return ApiResponse(success=True, data={"regions": regions, "count": len(regions), "model": settings.ocr_model_name})
    finally:
        try:
            os.remove(source)
        except OSError:
            pass


@router.post("/text", response_model=ApiResponse)
def remove_detected_text(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_FILE", message="Use JPG, PNG or WEBP."))
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(settings.upload_dir, current_user.id, "removals", job_id)
    source, size = _save_upload(file, job_dir, f"original{ext}")
    output = os.path.join(job_dir, "cleaned.png")
    job = models.RemovalJob(id=job_id, owner_id=current_user.id, mode="AUTO_TEXT", source_path=source, output_path=output, status="PROCESSING", model_name=settings.removal_model, file_size=size)
    db.add(job)
    db.commit()
    try:
        meta = remove_text(source, output)
        job.status = "COMPLETED"
        job.detected_regions = json.dumps(meta["regions"])
        job.model_name = f"{settings.ocr_model_name} + {settings.removal_model}"
        db.commit()
        return ApiResponse(success=True, data={"job_id": job.id, "status": job.status, "region_count": meta["region_count"], "model": job.model_name, "cleaned_url": f"/removal/{job.id}/cleaned"})
    except Exception as exc:
        failed = db.query(models.RemovalJob).filter(models.RemovalJob.id == job_id).first()
        if failed:
            failed.status = "FAILED"
            failed.error_message = str(exc)[:1000]
            db.commit()
        return ApiResponse(success=False, data=None, error=ApiError(code="REMOVAL_ERROR", message=str(exc)[:500]))


@router.post("/object", response_model=ApiResponse)
def remove_object(file: UploadFile = File(...), mask: UploadFile = File(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_FILE", message="Use JPG, PNG or WEBP."))
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(settings.upload_dir, current_user.id, "removals", job_id)
    source, size = _save_upload(file, job_dir, f"original{ext}")
    mask_filename = (mask.filename or "mask.png").lower()
    if Path(mask_filename).suffix not in {".png", ".webp", ".jpg", ".jpeg"}:
        raise HTTPException(status_code=400, detail="Mask must be an image file.")
    mask_path, _ = _save_upload(mask, job_dir, "mask.png")
    output = os.path.join(job_dir, "cleaned.png")
    job = models.RemovalJob(id=job_id, owner_id=current_user.id, mode="MANUAL_OBJECT", source_path=source, mask_path=mask_path, output_path=output, status="PROCESSING", model_name=settings.removal_model, file_size=size)
    db.add(job)
    db.commit()
    try:
        meta = remove_masked_object(source, mask_path, output)
        job.status = "COMPLETED"
        db.commit()
        return ApiResponse(success=True, data={"job_id": job.id, "status": job.status, "model": meta["model"], "cleaned_url": f"/removal/{job.id}/cleaned"})
    except Exception as exc:
        failed = db.query(models.RemovalJob).filter(models.RemovalJob.id == job_id).first()
        if failed:
            failed.status = "FAILED"
            failed.error_message = str(exc)[:1000]
            db.commit()
        return ApiResponse(success=False, data=None, error=ApiError(code="REMOVAL_ERROR", message=str(exc)[:500]))


@router.get("/{job_id}", response_model=ApiResponse)
def get_removal(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    job = _job(db, job_id, current_user)
    regions = []
    if job.detected_regions:
        try: regions = json.loads(job.detected_regions)
        except Exception: pass
    return ApiResponse(success=True, data={"job_id": job.id, "mode": job.mode, "status": job.status, "model": job.model_name, "regions": regions, "error": job.error_message, "cleaned_url": f"/removal/{job.id}/cleaned" if job.status == "COMPLETED" else None})


@router.get("/{job_id}/cleaned")
def cleaned(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    job = _job(db, job_id, current_user)
    if job.status != "COMPLETED" or not job.output_path or not os.path.isfile(job.output_path):
        raise HTTPException(status_code=404, detail="Cleaned image is not available")
    return FileResponse(job.output_path, media_type="image/png", filename=f"deeptruth-cleaned-{job.id}.png")
