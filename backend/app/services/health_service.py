import logging
import os
from typing import Dict, Any

from sqlalchemy import text

from ..config import settings
from ..db import engine
logger = logging.getLogger("deeptruth.health")


def _safe_connect_database() -> Dict[str, Any]:
    try:
        # lightweight check
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"available": True}
    except Exception as e:
        logger.warning("Database health check failed: %s", str(e))
        return {"available": False, "reason": "DATABASE_UNAVAILABLE"}


def _check_storage_local(path: str) -> Dict[str, Any]:
    try:
        os.makedirs(path, exist_ok=True)
        if not os.path.exists(path):
            return {"available": False, "reason": "UPLOAD_DIR_MISSING"}
        # check writable
        if not os.access(path, os.W_OK | os.R_OK):
            return {"available": False, "reason": "UPLOAD_DIR_NOT_WRITABLE"}
        return {"available": True}
    except Exception as e:
        logger.warning("Storage health check failed: %s", str(e))
        return {"available": False, "reason": "STORAGE_CHECK_FAILED"}


def _check_pdf_lib() -> Dict[str, Any]:
    try:
        import reportlab  # type: ignore
        return {"available": True}
    except Exception:
        return {"available": False, "reason": "REPORTLIB_NOT_INSTALLED"}


def _check_inference_model() -> Dict[str, Any]:
    mode = settings.inference_mode.upper() if settings.inference_mode else "REAL"
    out: Dict[str, Any] = {
        "mode": mode,
        "model_id": settings.model_id,
        "available": False,
    }
    if mode == "DEMO":
        out.update({"available": True, "device": "CPU"})
        return out
    try:
        import torch
        out["device"] = "CUDA" if torch.cuda.is_available() else "CPU"
        out["available"] = True
        out["model_loaded"] = False
    except Exception:
        out.update({"available": False, "reason": "TORCH_NOT_INSTALLED"})
    return out


def _check_tracking_provider() -> Dict[str, Any]:
    try:
        from ..tracking.providers import get_provider
        provider = get_provider()
        if not provider:
            return {"available": False, "reason": "TRACKING_PROVIDER_NOT_CONFIGURED"}
        return {"available": True, "provider": provider.name}
    except Exception as e:
        logger.warning("Tracking provider health check failed: %s", str(e))
        return {"available": False, "reason": "TRACKING_CHECK_FAILED"}


def get_capabilities() -> Dict[str, Any]:
    caps: Dict[str, Any] = {}
    # database
    caps["database"] = _safe_connect_database()
    # storage
    if settings.storage_provider == "local":
        caps["storage"] = _check_storage_local(settings.upload_dir)
    else:
        # unknown/other storage providers: mark as available but with mode
        caps["storage"] = {"available": True, "provider": settings.storage_provider}
    # inference
    caps["inference"] = _check_inference_model()
    # pdf
    caps["pdf_report"] = _check_pdf_lib()
    # tracking
    caps["image_tracking"] = _check_tracking_provider()

    # deeptruth mode
    caps["mode"] = {"value": getattr(settings, "deeptruth_mode", None) or "real"}

    return caps


def overall_status(capabilities: Dict[str, Any]) -> str:
    # Required services: database
    db_ok = capabilities.get("database", {}).get("available", False)
    if not db_ok:
        return "UNAVAILABLE"

    # If inference is configured in REAL mode and unavailable -> DEGRADED or UNAVAILABLE?
    inference = capabilities.get("inference", {})
    inference_mode = inference.get("mode", "DEMO")
    inference_ok = inference.get("available", False)
    if inference_mode == "REAL" and not inference_ok:
        # If real inference is required but not present, app is degraded (cannot run analysis)
        return "DEGRADED"

    # Optional services: storage/pdf/tracking; if any unavailable -> DEGRADED
    optional = ["storage", "pdf_report", "image_tracking"]
    for key in optional:
        if not capabilities.get(key, {}).get("available", False):
            return "DEGRADED"

    return "HEALTHY"


def check_startup():
    caps = get_capabilities()
    status = overall_status(caps)
    logger.info("Startup health status: %s", status)
    for k, v in caps.items():
        logger.info("Service %s -> %s", k, v)
    # Do not abort startup for optional failures
    return caps, status
