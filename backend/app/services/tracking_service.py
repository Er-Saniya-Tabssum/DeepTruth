from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from ..tracking.providers import get_provider
from .. import models
import requests
import io
import time
from typing import Optional

PROVIDER = get_provider()


def _save_match(db: Session, tracked_image_id: str, match: dict):
    # match may contain fields: match_url, source_domain, page_title, thumbnail_url, match_score, first_seen, last_seen
    tm = models.TrackingMatch(tracked_image_id=tracked_image_id, match_url=match.get('match_url') or match.get('url') or '', confidence=match.get('match_score'))
    db.add(tm)
    db.commit()
    db.refresh(tm)
    return tm


def perform_search(db: Session, tracked_image_id: str):
    """Background worker that performs search using configured provider and persists results.
    This function should be resilient to provider failures and timeouts.
    """
    if not PROVIDER:
        # nothing to do if provider not configured
        return
    timg = db.query(models.TrackedImage).filter(models.TrackedImage.id == tracked_image_id).first()
    if not timg:
        return
    # Mark as processing if model had status fields; we will not modify schema; we simply persist matches
    # Determine source: prefer source_url, else try to use linked analysis.storage_path
    image_url = timg.source_url
    image_bytes = None

    if not image_url and timg.analysis_id:
        analysis = db.query(models.Analysis).filter(models.Analysis.id == timg.analysis_id).first()
        if analysis and analysis.storage_path and os.path.exists(analysis.storage_path):
            try:
                with open(analysis.storage_path, 'rb') as f:
                    image_bytes = f.read()
            except Exception:
                image_bytes = None

    try:
        results = PROVIDER.search(image_bytes=image_bytes, image_url=image_url)
    except Exception:
        results = None

    if results is None:
        # provider error: do nothing; we could mark a failure column if present
        return

    # Persist results
    for r in results:
        try:
            _save_match(db, tracked_image_id, r)
        except Exception:
            # ignore individual save errors
            pass

    # Optionally update tracked image completed_at/status if model had such fields
    return


def queue_tracking(db: Session, tracked_image_id: str, background_tasks: BackgroundTasks):
    # Add background task to perform search
    background_tasks.add_task(perform_search, db, tracked_image_id)
