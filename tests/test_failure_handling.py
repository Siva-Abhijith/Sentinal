from unittest.mock import patch

from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError

from app.main import app


client = TestClient(app)


def test_rate_limiter_failure_returns_503():
    with patch(
        "app.main.rate_limiter.allow",
        side_effect=ConnectionError("Valkey unavailable"),
    ):
        response = client.get("/")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Rate limiter unavailable"
    }
