from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import io
from sqlalchemy.orm import Session
import json
import os
import uuid

from ..schemas import ApiResponse, ApiError
from ..db import get_db
from .. import models
from ..auth import get_current_user
from ..config import settings

router = APIRouter()

ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv"}


def secure_filename(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return f"{uuid.uuid4().hex}{ext.lower()}"




def _validate_media(path: str, media_type: str) -> bool:
    try:
        if media_type == "IMAGE":
            from PIL import Image
            with Image.open(path) as image:
                image.verify()
            return True
        if media_type == "VIDEO":
            import cv2
            cap = cv2.VideoCapture(path)
            ok = cap.isOpened() and bool(cap.read()[0])
            cap.release()
            return ok
    except Exception:
        return False
    return False


def _owned_analysis(db: Session, analysis_id: str, user: models.User):
    analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return analysis


@router.post("/upload", response_model=ApiResponse)
def upload(file: UploadFile = File(...), model_provider: str = Form('PRODUCTION'), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    filename = (file.filename or "").strip()
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext in ALLOWED_IMAGE_EXT:
        media_type = "IMAGE"
    elif ext in ALLOWED_VIDEO_EXT:
        media_type = "VIDEO"
    else:
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_FILE", message="Unsupported file type. Use JPG, PNG, WEBP, MP4, MOV, AVI or MKV."))

    model_provider = (model_provider or "PRODUCTION").strip().upper()
    if model_provider not in {"PRODUCTION", "MY_MODEL"}:
        return ApiResponse(
            success=False,
            data=None,
            error=ApiError(
                code="INVALID_MODEL_PROVIDER",
                message="model_provider must be PRODUCTION or MY_MODEL."
            )
        )

    contents = file.file.read()
    size = len(contents)
    if size == 0:
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_FILE", message="The uploaded file is empty."))
    if size > settings.max_upload_size_mb * 1024 * 1024:
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_FILE", message=f"File exceeds {settings.max_upload_size_mb} MB limit."))

    analysis_id = str(uuid.uuid4())
    dest_dir = os.path.join(settings.upload_dir, current_user.id, analysis_id)
    os.makedirs(dest_dir, exist_ok=True)
    local_path = os.path.join(dest_dir, secure_filename(filename))

    with open(local_path, "wb") as output_file:
        output_file.write(contents)

    if not _validate_media(local_path, media_type):
        try:
            os.remove(local_path)
        except OSError:
            pass
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_MEDIA", message="The uploaded file could not be decoded as a valid image/video."))

    analysis = models.Analysis(
        id=analysis_id,
        owner_id=current_user.id,
        filename=filename,
        media_type=media_type,
        file_size=size,
        storage_path=local_path,
        status="QUEUED",
        inference_mode=settings.inference_mode.upper(),
        model_provider=model_provider,
        training_consent=None,
        training_status="NOT_REQUESTED",
        progress=0,
        current_stage="QUEUED",
    )
    try:
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
    except Exception:
        db.rollback()
        try:
            if os.path.isfile(local_path):
                os.remove(local_path)
            if os.path.isdir(dest_dir):
                os.rmdir(dest_dir)
        except OSError:
            pass
        raise HTTPException(status_code=500, detail="Unable to persist the analysis job.")

    return ApiResponse(success=True, data={
        "analysis_id": analysis.id,
        "filename": analysis.filename,
        "media_type": analysis.media_type,
        "file_size": analysis.file_size,
        "status": analysis.status,
        "inference_mode": analysis.inference_mode,
        "model_provider": analysis.model_provider,
        "created_at": analysis.created_at.isoformat(),
    })


@router.get("/stats", response_model=ApiResponse)
def stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    analyses = db.query(models.Analysis).filter(models.Analysis.owner_id == current_user.id).all()
    by_status = {k: 0 for k in ("QUEUED", "PROCESSING", "COMPLETED", "FAILED")}
    by_verdict = {}
    storage = 0
    for a in analyses:
        by_status[a.status] = by_status.get(a.status, 0) + 1
        storage += a.file_size or 0
        if a.result:
            try:
                verdict = json.loads(a.result).get("verdict")
                if verdict:
                    by_verdict[verdict] = by_verdict.get(verdict, 0) + 1
            except Exception:
                pass
    return ApiResponse(success=True, data={
        "total_analyses": len(analyses),
        "by_status": by_status,
        "by_verdict": by_verdict,
        "storage_used_bytes": storage,
        "recent_analyses": [
            {
                "analysis_id": a.id, "filename": a.filename, "media_type": a.media_type,
                "status": a.status,
                "verdict": (json.loads(a.result).get("verdict") if a.result else None),
                "created_at": a.created_at.isoformat(),
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            } for a in sorted(analyses, key=lambda x: x.created_at, reverse=True)[:5]
        ],
    })


@router.get("/history", response_model=ApiResponse)
def history(page: int = 1, limit: int = 20, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    query = db.query(models.Analysis).filter(models.Analysis.owner_id == current_user.id).order_by(models.Analysis.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    summaries = []
    for a in items:
        verdict = None
        if a.result:
            try: verdict = json.loads(a.result).get("verdict")
            except Exception: pass
        summaries.append({
            "analysis_id": a.id, "filename": a.filename, "media_type": a.media_type,
            "status": a.status, "verdict": verdict, "created_at": a.created_at.isoformat(),
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
        })
    return ApiResponse(success=True, data={"page": page, "limit": limit, "total": total, "items": summaries})


@router.get("/{analysis_id}/report")
def get_report(analysis_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    analysis = _owned_analysis(db, analysis_id, current_user)
    from ..services.report import generate_report_pdf_bytes
    evidences = db.query(models.Evidence).filter(models.Evidence.analysis_id == analysis.id).all()
    faces = db.query(models.DetectedFace).filter(models.DetectedFace.analysis_id == analysis.id).all()
    pdf = generate_report_pdf_bytes(analysis, evidences, faces)
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in analysis.filename)
    filename = f"deeptruth-report-{os.path.splitext(safe_name)[0]}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{analysis_id}/run", response_model=ApiResponse)
def run_analysis(analysis_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    analysis = _owned_analysis(db, analysis_id, current_user)
    if analysis.status in ("PROCESSING", "QUEUED"):
        return ApiResponse(success=True, data={"analysis_id": analysis.id, "status": analysis.status})
    analysis.status = "QUEUED"
    analysis.progress = 0
    analysis.current_stage = "QUEUED"
    analysis.error_code = None
    analysis.error_message = None
    analysis.result = None
    analysis.completed_at = None
    db.query(models.DetectedFace).filter(models.DetectedFace.analysis_id == analysis.id).delete(synchronize_session=False)
    db.query(models.Evidence).filter(models.Evidence.analysis_id == analysis.id).delete(synchronize_session=False)
    db.commit()
    return ApiResponse(success=True, data={"analysis_id": analysis.id, "status": analysis.status})


@router.get("/{analysis_id}", response_model=ApiResponse)
def get_analysis(analysis_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    analysis = _owned_analysis(db, analysis_id, current_user)
    result = None
    if analysis.result:
        try: result = json.loads(analysis.result)
        except Exception: result = None
    return ApiResponse(success=True, data={
        "analysis_id": analysis.id, "filename": analysis.filename, "media_type": analysis.media_type,
        "status": analysis.status, "progress": analysis.progress, "current_stage": analysis.current_stage,
        "inference_mode": analysis.inference_mode, "model_provider": analysis.model_provider,
        "training_consent": analysis.training_consent,
        "training_status": analysis.training_status,
        "result": result,
        "created_at": analysis.created_at.isoformat(),
        "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
        "error_code": analysis.error_code, "error_message": analysis.error_message,
    })


@router.delete("/{analysis_id}", response_model=ApiResponse)
def delete_analysis(analysis_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    analysis = _owned_analysis(db, analysis_id, current_user)
    storage_path = analysis.storage_path
    # Remove dependent rows explicitly so deletion works consistently on SQLite and PostgreSQL.
    tracked_ids = [row.id for row in db.query(models.TrackedImage).filter(models.TrackedImage.analysis_id == analysis.id).all()]
    if tracked_ids:
        db.query(models.TrackingMatch).filter(models.TrackingMatch.tracked_image_id.in_(tracked_ids)).delete(synchronize_session=False)
    db.query(models.TrackedImage).filter(models.TrackedImage.analysis_id == analysis.id).delete(synchronize_session=False)
    db.query(models.RemovalRequest).filter(models.RemovalRequest.analysis_id == analysis.id).delete(synchronize_session=False)
    db.query(models.DetectedFace).filter(models.DetectedFace.analysis_id == analysis.id).delete(synchronize_session=False)
    db.query(models.Evidence).filter(models.Evidence.analysis_id == analysis.id).delete(synchronize_session=False)
    db.delete(analysis)
    db.commit()
    try:
        if storage_path and os.path.exists(storage_path):
            os.remove(storage_path)
            parent = os.path.dirname(storage_path)
            if os.path.isdir(parent) and not os.listdir(parent):
                os.rmdir(parent)
    except OSError:
        pass
    return ApiResponse(success=True, data={"analysis_id": analysis_id, "deleted": True})






