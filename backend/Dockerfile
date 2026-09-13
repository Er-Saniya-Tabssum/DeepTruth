FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends libglib2.0-0 libsm6 libxext6 libxrender1 ffmpeg && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/backend/requirements.txt
COPY backend /app/backend
COPY alembic.ini /app/alembic.ini
COPY .env.example /app/.env.example
RUN mkdir -p /app/uploads /app/.model-cache
EXPOSE 8000
CMD ["sh","-c","alembic upgrade head && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]
