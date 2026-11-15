from fastapi.testclient import TestClient
from app.main import app
from app.services import posting_service as service_module
from app.schemas import PlatformResult

client = TestClient(app)


def test_rejects_message_over_200_characters():
    response = client.post("/posting", json={"message": "x" * 201 + " https://example.com"})
    assert response.status_code == 422


def test_rejects_missing_cta_link():
    response = client.post("/posting", json={"message": "Hello there"})
    assert response.status_code == 422


def test_rejects_two_links():
    response = client.post("/posting", json={"message": "Visit https://one.example and https://two.example"})
    assert response.status_code == 422


def test_endpoint_returns_platform_results(monkeypatch):
    async def fake_publish_everywhere(message: str):
        return [
            PlatformResult(platform="Example A", status="success", posted_url="https://example.com/p/1", public_access=True, date="2026-01-01", time="10:00:00"),
            PlatformResult(platform="Example B", status="failed", error="Not configured"),
        ]

    monkeypatch.setattr(service_module.posting_service, "publish_everywhere", fake_publish_everywhere)
    response = client.post("/posting", json={"message": "See our site https://example.com"})
    assert response.status_code == 200
    body = response.json()
    assert body["overall_status"] == "partial_success"
    assert len(body["results"]) == 2
