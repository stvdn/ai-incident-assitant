import pytest
from fastapi.testclient import TestClient
from app.main import app


pytestmark = pytest.mark.unit

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}