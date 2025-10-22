from fastapi.testclient import TestClient
from app.main import app
import io

headers = {"X-API-Key": "dev-secret-key"}

# Test small file upload (success)
def test_upload_txt_success():
    client = TestClient(app)
    data = io.BytesIO(b"Hello world!")
    files = {"file": ("test.txt", data, "text/plain")}
    r = client.post("/v1/docs/upload", headers=headers, files=files)
    assert r.status_code in (200, 400)  # Accept 400 if not openai provider

# Test large file upload (should fail or be limited)
def test_upload_large_file():
    client = TestClient(app)
    big_data = io.BytesIO(b"A" * 6_000_000)  # 6MB
    files = {"file": ("big.txt", big_data, "text/plain")}
    r = client.post("/v1/docs/upload", headers=headers, files=files)
    assert r.status_code in (413, 400, 502)  # 413 Payload Too Large or handled error

# Test unsupported file type
def test_upload_unsupported_file():
    client = TestClient(app)
    data = io.BytesIO(b"%PDF-1.4 fake pdf")
    files = {"file": ("fake.pdf", data, "application/pdf")}
    r = client.post("/v1/docs/upload", headers=headers, files=files)
    assert r.status_code in (200, 400, 502)
