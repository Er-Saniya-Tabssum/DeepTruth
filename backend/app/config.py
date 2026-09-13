import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

UNSAFE_SECRET_VALUES = {
    "", "change-me", "changeme", "default", "secret", "secret-key",
    "your-secret-key", "replace-me", "placeholder",
}

def _normalize_environment(raw_value: str) -> str:
    return (raw_value or "development").strip().lower()

def _normalize_inference_mode(raw_value: str) -> str:
    return (raw_value or "REAL").strip().upper()

def resolve_model_path(raw_model_path: str) -> str:
    raw = (raw_model_path or "").strip()
    if not raw:
        return ""

    path = Path(raw)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path

    return str(path.resolve())

class Settings(BaseSettings):
    environment: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    create_tables_on_startup: bool = True
    database_url: str = "sqlite:///./dev.db"
    upload_dir: str = "./uploads"
    storage_provider: str = "local"
    inference_mode: str = "REAL"
    model_id: str = "capcheck/ai-image-detection"
    model_path: str = ""
    max_upload_size_mb: int = 20
    video_sample_interval: float = 2.0
    max_analyzed_frames: int = 12
    worker_poll_interval_seconds: float = 1.0
    cors_origins: str = "http://localhost:3000"
    tracking_provider: str = ""
    tracking_api_key: str = ""
    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    deeptruth_mode: str = "real"
    model_cache_dir: str = "./.model-cache"
    ocr_model_name: str = "PP-OCRv5_mobile_det"
    ocr_device: str = "cpu"
    removal_model: str = "LaMa"
    removal_device: str = "cpu"
    removal_max_dimension: int = 2048
    model_revision: str = ""
    model_device: str = "auto"
    model_low_cpu_mem_usage: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

def get_runtime_settings() -> dict:
    environment = _normalize_environment(settings.environment)
    inference_mode = _normalize_inference_mode(settings.inference_mode)
    return {
        "environment": environment,
        "secret_key": (settings.secret_key or "").strip(),
        "inference_mode": inference_mode,
        "model_id": settings.model_id,
        "model_path": settings.model_path,
        "database_url": (settings.database_url or "").strip(),
        "cors_origins": (settings.cors_origins or "").strip(),
        "deeptruth_mode": (settings.deeptruth_mode or "real").strip().lower(),
    }

def validate_runtime_settings(runtime_settings: dict) -> None:
    if runtime_settings["inference_mode"] not in {"DEMO", "REAL"}:
        raise RuntimeError("INFERENCE_MODE must be either DEMO or REAL.")
    if runtime_settings["environment"] != "production":
        return
    secret = runtime_settings["secret_key"]
    if not secret or secret.lower() in UNSAFE_SECRET_VALUES:
        raise RuntimeError("Unsafe production SECRET_KEY detected. Set SECRET_KEY to a strong value.")
    if len(secret) < 32:
        raise RuntimeError("SECRET_KEY must be at least 32 characters in production.")
    if runtime_settings["cors_origins"] == "*":
        raise RuntimeError("CORS_ORIGINS cannot be '*' in production.")

