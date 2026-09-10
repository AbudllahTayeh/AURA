from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    # In CI, databases won't be running unless configured, so it may return 'degraded'
    assert response.json()["status"] in ["ok", "degraded"]
