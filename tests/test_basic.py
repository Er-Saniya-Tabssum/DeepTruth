from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health/")
    assert r.status_code == 200
    assert r.json()["success"] is True

def test_register_and_login():
    payload = {"name": "Test", "email": "test@example.com", "password": "Secret123!"}
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 200
    assert r.json()["success"] is True

    r2 = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert r2.status_code == 200
    token = r2.json()["data"]["access_token"]
    assert token

    r3 = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200
    assert r3.json()["data"]["user"]["email"] == payload["email"]
