from datetime import date
from fastapi.testclient import TestClient
from app.main import app, workflow
from app.schemas import ShipmentRecord
from app.extractor import ExtractionConfigurationError

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_process_rejects_short_document():
    response = client.post("/process", json={"document_text": "short"})
    assert response.status_code == 422

def test_missing_api_key_returns_503(monkeypatch):
    def no_key(_):
        raise ExtractionConfigurationError("missing key")
    monkeypatch.setattr(workflow, "extractor", no_key)
    response = client.post("/process", json={"document_text": "A sufficiently long synthetic document"})
    assert response.status_code == 503
