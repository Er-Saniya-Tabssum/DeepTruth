import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .db import SessionLocal
from . import models
from .inference import create_inference_provider


class AnalysisWorker:
    def __init__(self):
        # Providers are selected per analysis.
        # This prevents MY_MODEL jobs from accidentally using PRODUCTION.
        self.provider = None

    def process_once(self):
        db: Session = SessionLocal()

        try:
            analysis = (
                db.query(models.Analysis)
                .filter(models.Analysis.status == "QUEUED")
                .order_by(models.Analysis.created_at.asc())
                .first()
            )

            if not analysis:
                return None

            analysis.status = "PROCESSING"
            analysis.progress = 10
            analysis.current_stage = "PREPROCESSING"
            db.commit()
            db.refresh(analysis)

            try:
                analysis.current_stage = "AI_DETECTION"
                analysis.progress = 30
                db.commit()

                # Select the correct inference provider for this job.
                model_provider = (
                    getattr(analysis, "model_provider", None)
                    or "PRODUCTION"
                )

                provider = create_inference_provider(model_provider)

                result = provider.process(
                    analysis.storage_path or "",
                    analysis.media_type,
                )

                analysis.current_stage = "AUTHENTICITY_ANALYSIS"
                analysis.progress = 75
                db.commit()

                analysis.current_stage = "FINAL_ASSESSMENT"
                analysis.progress = 95
                analysis.result = json.dumps(result)
                analysis.status = "COMPLETED"
                analysis.progress = 100
                analysis.completed_at = (
                    datetime.now(timezone.utc).replace(tzinfo=None)
                )
                analysis.error_code = None
                analysis.error_message = None
                db.commit()

                # Persist relational forensic evidence.
                db.query(models.Evidence).filter(
                    models.Evidence.analysis_id == analysis.id
                ).delete(synchronize_session=False)

                for item in result.get("evidence") or []:
                    db.add(
                        models.Evidence(
                            analysis_id=analysis.id,
                            type=item.get("type", "MODEL_SIGNAL"),
                            url=item.get("explanation", ""),
                            size=None,
                            media_type="EVIDENCE",
                        )
                    )

                # Persist face detections.
                db.query(models.DetectedFace).filter(
                    models.DetectedFace.analysis_id == analysis.id
                ).delete(synchronize_session=False)

                for face in result.get("detected_faces") or []:
                    bbox = face.get("bbox") or {}

                    db.add(
                        models.DetectedFace(
                            analysis_id=analysis.id,
                            bbox_x=bbox.get("x"),
                            bbox_y=bbox.get("y"),
                            bbox_w=bbox.get("width"),
                            bbox_h=bbox.get("height"),
                            identity_name=face.get("identity_name"),
                            identity_confidence=face.get(
                                "identity_confidence"
                            ),
                        )
                    )

                db.commit()
                return analysis

            except Exception as exc:
                analysis_id = analysis.id
                db.rollback()

                failed = (
                    db.query(models.Analysis)
                    .filter(models.Analysis.id == analysis_id)
                    .first()
                )

                if failed:
                    failed.status = "FAILED"
                    failed.progress = 100
                    failed.current_stage = "FAILED"
                    failed.error_code = "INFERENCE_ERROR"
                    failed.error_message = str(exc)[:1000]
                    failed.completed_at = (
                        datetime.now(timezone.utc).replace(tzinfo=None)
                    )
                    db.commit()

                return failed

        finally:
            db.close()


worker = AnalysisWorker()