from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import validators

from ..schemas import ApiResponse, ApiError
from ..db import get_db
from .. import models
from ..auth import get_current_user
from ..tracking.providers import get_provider
from ..services.tracking_service import queue_tracking

router = APIRouter()


@router.get('/available', response_model=ApiResponse)
def available():
    provider = get_provider()
    if not provider:
        return ApiResponse(success=True, data={"available": False, "reason": "TRACKING_PROVIDER_NOT_CONFIGURED"}, error=None)
    return ApiResponse(success=True, data={"available": True, "provider": provider.name}, error=None)


@router.post('/', response_model=ApiResponse)
def create_tracking(analysis_id: Optional[str] = None, source_url: Optional[str] = None, background_tasks: BackgroundTasks = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Accept either analysis_id (track an image already analyzed) OR a public source_url pointing to an image
    if not analysis_id and not source_url:
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_PAYLOAD", message="Provide analysis_id or source_url", details=None))

    # If source_url provided, validate scheme
    if source_url:
        if not validators.url(source_url):
            return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_URL", message="Invalid source_url", details=None))

    # If analysis_id provided, validate ownership
    storage_source_url = None
    if analysis_id:
        analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
        if not analysis:
            return ApiResponse(success=False, data=None, error=ApiError(code="NOT_FOUND", message="Analysis not found", details=None))
        if analysis.owner_id != current_user.id:
            return ApiResponse(success=False, data=None, error=ApiError(code="FORBIDDEN", message="Not allowed", details=None))
        # Use analysis.storage_path as source if available
        storage_source_url = analysis.storage_path

    # Create TrackedImage record
    tracked = models.TrackedImage(analysis_id=analysis_id, source_url=source_url or storage_source_url)
    db.add(tracked)
    db.commit()
    db.refresh(tracked)

    # Queue background search only if provider configured
    from ..tracking.providers import get_provider
    if get_provider():
        queue_tracking(db, tracked.id, background_tasks)
        status = "QUEUED"
    else:
        status = "NOT_CONFIGURED"

    data = {"tracked_id": tracked.id, "analysis_id": tracked.analysis_id, "status": status}
    return ApiResponse(success=True, data=data, error=None)


@router.get('/', response_model=ApiResponse)
def list_tracking(page: int = 1, limit: int = 20, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # List tracked images belonging to current_user (via analysis relationship)
    q = db.query(models.TrackedImage).join(models.Analysis, models.TrackedImage.analysis_id == models.Analysis.id).filter(models.Analysis.owner_id == current_user.id).order_by(models.TrackedImage.created_at.desc())
    total = q.count()
    items = q.offset((page-1)*limit).limit(limit).all()
    out = []
    for t in items:
        out.append({"tracked_id": t.id, "analysis_id": t.analysis_id, "source_url": t.source_url, "created_at": t.created_at.isoformat() if t.created_at else None})
    return ApiResponse(success=True, data={"page": page, "limit": limit, "total": total, "items": out}, error=None)


@router.get('/{tracked_id}', response_model=ApiResponse)
def get_tracking(tracked_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    t = db.query(models.TrackedImage).filter(models.TrackedImage.id == tracked_id).first()
    if not t:
        return ApiResponse(success=False, data=None, error=ApiError(code="NOT_FOUND", message="Tracked image not found", details=None))
    # ensure ownership via linked analysis
    if t.analysis_id:
        analysis = db.query(models.Analysis).filter(models.Analysis.id == t.analysis_id).first()
        if not analysis or analysis.owner_id != current_user.id:
            return ApiResponse(success=False, data=None, error=ApiError(code="FORBIDDEN", message="Not allowed", details=None))
    # fetch matches
    matches = db.query(models.TrackingMatch).filter(models.TrackingMatch.tracked_image_id == tracked_id).all()
    matches_out = []
    for m in matches:
        matches_out.append({"id": m.id, "match_url": m.match_url, "confidence": m.confidence, "created_at": m.created_at.isoformat() if m.created_at else None})
    data = {"tracked_id": t.id, "analysis_id": t.analysis_id, "source_url": t.source_url, "matches": matches_out}
    return ApiResponse(success=True, data=data, error=None)


@router.post('/{tracked_id}/removal', response_model=ApiResponse)
def request_removal(tracked_id: str, match_id: Optional[str] = None, reason: Optional[str] = None, contact_email: Optional[str] = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    t = db.query(models.TrackedImage).filter(models.TrackedImage.id == tracked_id).first()
    if not t:
        return ApiResponse(success=False, data=None, error=ApiError(code="NOT_FOUND", message="Tracked image not found", details=None))
    # validate ownership via linked analysis if present
    if t.analysis_id:
        a = db.query(models.Analysis).filter(models.Analysis.id == t.analysis_id).first()
        if not a or a.owner_id != current_user.id:
            return ApiResponse(success=False, data=None, error=ApiError(code="FORBIDDEN", message="Not allowed", details=None))

    target_url = None
    if match_id:
        match = db.query(models.TrackingMatch).filter(models.TrackingMatch.id == match_id).first()
        if not match:
            return ApiResponse(success=False, data=None, error=ApiError(code="NOT_FOUND", message="Match not found", details=None))
        target_url = match.match_url
    else:
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_PAYLOAD", message="match_id required", details=None))

    # Validate URL scheme
    if target_url and not (target_url.startswith('http://') or target_url.startswith('https://')):
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_URL", message="Invalid target URL", details=None))

    # Create a RemovalRequest record using existing model
    rr = models.RemovalRequest(analysis_id=t.analysis_id, target_url=target_url, platform=None, reason=reason or '', contact_email=contact_email or '', status='SUBMITTED')
    db.add(rr)
    db.commit()
    db.refresh(rr)

    return ApiResponse(success=True, data={"removal_request_id": rr.id, "status": rr.status}, error=None)
