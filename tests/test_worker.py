from io import BytesIO
from PIL import Image
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db import Base, engine
from backend.app.worker import AnalysisWorker

client = TestClient(app)


class FakeProvider:
    def process(self, path, media_type="IMAGE"):
        return {
            "verdict": "AUTHENTIC",
            "authenticity_score": 0.91,
            "ai_probability": 0.09,
            "face_swap_probability": None,
            "confidence": "HIGH",
            "faces_detected": 0,
            "detected_faces": [],
            "evidence": [],
            "suspicious_regions": [],
            "frame_results": None,
            "model_metadata": {"model_name": "test-provider", "inference_mode": "TEST"},
        }


def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _image_bytes():
    image = Image.new("RGB", (64, 64), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_upload_and_worker_process():
    r = client.post("/auth/register", json={"name": "WorkerUser", "email": "worker@example.com", "password": "Password123"})
    token = r.json()["data"]["access_token"]

    files = {"file": ("test.png", _image_bytes(), "image/png")}
    r2 = client.post("/analysis/upload", files=files, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    analysis_id = r2.json()["data"]["analysis_id"]

    test_worker = AnalysisWorker()
    test_worker.provider = FakeProvider()
    processed = test_worker.process_once()
    assert processed is not None
    assert processed.id == analysis_id
    assert processed.status == "COMPLETED"

    r3 = client.get(f"/analysis/{analysis_id}", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200
    assert r3.json()["data"]["status"] == "COMPLETED"
