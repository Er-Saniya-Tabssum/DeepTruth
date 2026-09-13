from io import BytesIO
from PIL import Image
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db import Base, engine

client = TestClient(app)


def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _image_bytes():
    image = Image.new("RGB", (64, 64), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_register_login_me_logout_and_idor():
    r = client.post("/auth/register", json={"name": "UserA", "email": "usera@example.com", "password": "Password123"})
    assert r.status_code == 200
    token_a = r.json()["data"]["access_token"]

    r2 = client.post("/auth/register", json={"name": "UserB", "email": "userb@example.com", "password": "Password456"})
    assert r2.status_code == 200
    token_b = r2.json()["data"]["access_token"]

    r4 = client.get("/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert r4.status_code == 200

    files = {"file": ("test.png", _image_bytes(), "image/png")}
    r5 = client.post("/analysis/upload", files=files, headers={"Authorization": f"Bearer {token_a}"})
    assert r5.status_code == 200
    analysis_id = r5.json()["data"]["analysis_id"]

    r6 = client.get(f"/analysis/{analysis_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert r6.status_code == 403

    r7 = client.post("/auth/logout", headers={"Authorization": f"Bearer {token_a}"})
    assert r7.status_code == 200

    r8 = client.get("/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert r8.status_code == 401
