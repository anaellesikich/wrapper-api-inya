from fastapi.testclient import TestClient
from app.main import app

headers = {"X-API-Key": "dev-secret-key"}

def test_generate_echo():
    client = TestClient(app)
    body = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hi"}
        ],
        "stream": False
    }
    r = client.post("/v1/generate", headers=headers, json=body)
    assert r.status_code == 200
    data = r.json()
    assert "content" in data and "hi" in data["content"].lower()
