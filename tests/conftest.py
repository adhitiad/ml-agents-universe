"""Global Pytest Fixtures."""

import pytest
from fastapi.testclient import TestClient

from api.dependencies import request_history
from api.gateway import app


@pytest.fixture(scope="module")
def api_client():
    """Shared HTTP client for all tests."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Reset rate limiter state before each test."""
    request_history.clear()

@pytest.fixture
def auth_headers():
    return {"X-API-Key": "dev_universe_key"}
