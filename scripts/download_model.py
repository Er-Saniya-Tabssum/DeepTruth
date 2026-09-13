from transformers import pipeline
from backend.app.config import settings

print(f"Downloading/loading model: {settings.model_id}")
kwargs = {"model": settings.model_id}
if settings.model_revision:
    kwargs["revision"] = settings.model_revision
if settings.model_cache_dir:
    kwargs["model_kwargs"] = {"cache_dir": settings.model_cache_dir}
detector = pipeline("image-classification", **kwargs)
print("Model is ready.")
