# DeepTruth Verification Notes

## What was checked in the delivered source

- Python source compiles with `python -m compileall backend tests scripts`.
- FastAPI routes use one consistent public prefix: `/auth`, `/analysis`, `/removal`, `/tracking`, `/health`.
- JWT expiration uses timezone-aware UTC timestamps.
- Registration normalizes email addresses before the uniqueness check.
- Uploaded analysis media is decoded/validated before queueing.
- Analysis ownership is enforced for reads, reports and deletion.
- Analysis deletion explicitly removes dependent relational rows and stored media.
- The worker persists model results, evidence and face detections.
- Alembic migrations now include the removal-job schema and supporting indexes.
- Docker API startup runs `alembic upgrade head` before starting Uvicorn.
- Docker API and worker share the upload/model-cache volumes and PostgreSQL database.
- The frontend cleanup page no longer has the duplicate `blob` variable that prevented TypeScript compilation.
- Frontend Vitest configuration uses jsdom and React Testing Library's `renderHook`.

## Model provenance

The AI-image detector is pinned to the CapCheck `capcheck/ai-image-detection` commit:
`a6661e07d38f1a097bba07ca9415538819278f09`.

The published model configuration maps `REAL=0` and `FAKE=1`. DeepTruth maps those labels explicitly.

## Runtime verification required on the developer machine

The environment used to prepare this archive cannot download Python/Node dependencies or Hugging Face/PaddleOCR/LaMa model weights. Therefore the following must be run after installing dependencies:

```powershell
python -m compileall backend tests scripts
pytest -q
```

Then run the application and verify:

1. Register -> login -> `/auth/me`.
2. Upload a real JPG/PNG -> queued analysis.
3. Worker -> real pretrained model -> completed result.
4. Refresh result page -> result remains in the database.
5. History -> persisted analysis.
6. PDF report -> downloads successfully.
7. Clean Media -> OCR text detection -> LaMa output.
8. Manual object mask -> LaMa output.
9. `docker compose up --build` -> API, worker, frontend and PostgreSQL become healthy.
