# DeepTruth

DeepTruth is a development-ready AI media authenticity and cleanup platform. It combines pretrained ML models with a persistent backend, background processing, forensic evidence, and an investigator-style web UI.

## What DeepTruth does

### Detect
- AI-generated image detection with `capcheck/ai-image-detection` (ViT, CIFAKE fine-tune).
- Video detection by sampling frames and aggregating model probabilities.
- OpenCV face localization as contextual evidence. Face detection is **not** represented as proof of a face swap.
- Image fingerprinting: dimensions, format, EXIF presence and SHA-256.
- Persisted model metadata, scores, limitations and structured evidence.

### Clean
- Automatic text removal: PP-OCRv5 mobile text detection -> binary mask -> LaMa inpainting.
- Manual object removal: user-painted mask -> LaMa inpainting.
- Original and cleaned media are retained in a per-user job directory.

## Architecture

```text
React + Vite
     |
     v
FastAPI REST API ---- PostgreSQL / SQLite
     |
     +---- Analysis Queue ---- Worker ---- Hugging Face ViT
     |                              |
     |                              +---- OpenCV face detection
     |
     +---- Cleanup API ---- PP-OCRv5 ---- LaMa
     |
     +---- PDF forensic reports
```

The ML models are pretrained. DeepTruth does not require local model training or a high-end GPU. The image detector defaults to CPU and automatically uses CUDA when available.

## Local development

### Backend

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item .env.example .env
python -m compileall backend
pytest -q
python -m uvicorn backend.app.main:app --reload
```

In a second terminal:

```powershell
.venv\Scripts\Activate.ps1
python -m backend.app.worker_runner
```

### Frontend

```powershell
cd frontend
npm install
npm run build
npm run dev
```

Open `http://localhost:3000`.

## Docker

```powershell
docker compose up --build
```

Services:
- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- PostgreSQL: internal Docker service
- Worker: internal Docker service

## Model behavior

The detector is a probabilistic signal, not a forensic guarantee. The configured CapCheck model publishes `REAL=0` and `FAKE=1`; DeepTruth maps those labels explicitly and normalizes their probabilities. Its model card notes that performance can vary on newer generators, compressed images and out-of-distribution content.

## API flow

1. Register/login.
2. Upload valid image/video.
3. API stores a user-owned analysis in `QUEUED` state.
4. Worker claims the job and performs inference.
5. Results, evidence, model metadata and detected faces are persisted.
6. Frontend polls the analysis and displays the forensic assessment.
7. User can download a PDF report.

## Cleanup flow

Automatic text removal:

```text
Image -> PP-OCRv5 -> text polygons -> mask dilation -> LaMa -> cleaned PNG
```

Manual object removal:

```text
Image + user brush mask -> LaMa -> cleaned PNG
```

## Important engineering choices

- No fake confidence values: results come from the pretrained classifier.
- No local model training requirement.
- User ownership is enforced on analyses and removal jobs.
- Uploaded media is validated before being queued.
- JWT expiration uses timezone-aware UTC timestamps.
- API routes consistently use `/auth`, `/analysis`, `/removal`, `/tracking` and `/health`.
- Re-running an analysis clears stale results and relational evidence.
- Model/evidence metadata is retained so historical reports remain explainable.

## Limitations

AI-generated-media detection is an evolving research problem. A result should not be treated as definitive proof of authenticity or manipulation. DeepTruth is intended for investigation, content moderation and educational/portfolio use, not for high-stakes decisions without human review.
