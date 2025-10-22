from fastapi.testclient import TestClient
from app.main import app

def test_missing_api_key():
    client = TestClient(app)
    r = client.post("/v1/generate", json={"messages":[], "stream":False})
    assert r.status_code == 401
    assert "Invalid or missing API key" in r.text

def test_invalid_api_key():
    client = TestClient(app)
    r = client.post("/v1/generate", headers={"X-API-Key": "bad-key"}, json={"messages":[], "stream":False})
    assert r.status_code == 401
    assert "Invalid or missing API key" in r.text
