from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from .config import settings, get_runtime_settings, validate_runtime_settings
from .db import engine, Base
from .routes import auth, analysis, health, tracking, removal

logger = logging.getLogger("deeptruth")

@asynccontextmanager
async def lifespan(app: FastAPI):
    runtime = get_runtime_settings()
    validate_runtime_settings(runtime)
    if settings.storage_provider == "local":
        os.makedirs(settings.upload_dir, exist_ok=True)
    if settings.model_cache_dir:
        os.makedirs(settings.model_cache_dir, exist_ok=True)
    if settings.create_tables_on_startup:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ready.")
    try:
        from .services.health_service import check_startup
        check_startup()
    except Exception:
        logger.exception("Startup health checks failed.")
    yield


app = FastAPI(
    title="DeepTruth API",
    version="1.0.0",
    description="AI-generated media detection and forensic analysis API.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(tracking.router, prefix="/tracking", tags=["tracking"])
app.include_router(removal.router, prefix="/removal", tags=["removal"])

