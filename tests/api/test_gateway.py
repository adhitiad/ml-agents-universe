import os
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from api.gateway import app
from shared.models.base import AgentState


# Setup env for testing
os.environ["API_ACCESS_KEYS"] = "dev_universe_key"

client = TestClient(app)

valid_headers = {"X-API-Key": "dev_universe_key"}
invalid_headers = {"X-API-Key": "wrong_key"}


def test_global_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_chat_no_auth():
    res = client.post("/v1/chat", json={"query": "hello"})
    assert res.status_code == 401


def test_chat_invalid_auth():
    res = client.post("/v1/chat", json={"query": "hello"}, headers=invalid_headers)
    assert res.status_code == 401


@patch("api.routes.chat.SupervisorAgent")
def test_chat_valid(MockSupervisor):
    # Mock SupervisorAgent and its arun method
    mock_instance = MockSupervisor.return_value
    mock_instance.arun = AsyncMock()

    # Fake final state
    fake_state = AgentState(
        messages=[
            {"role": "user", "content": "test"},
            {"role": "assistant", "content": "this is a test"},
        ],
        metadata={"final_answer": "this is a test", "selected_agents": ["nlp"]},
    )
    mock_instance.arun.return_value = fake_state

    res = client.post("/v1/chat", json={"query": "test"}, headers=valid_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "test"
    assert data["final_answer"] == "this is a test"
    assert "nlp" in data["experts_consulted"]


def test_websocket_chat_no_query():
    with client.websocket_connect("/ws/v1/chat") as websocket:
        websocket.send_json({})
        data = websocket.receive_json()
        assert "error" in data


@patch("api.routes.ws_chat.SupervisorAgent")
def test_websocket_chat_valid(MockSupervisor):
    # Mock compiled_graph.astream
    mock_instance = MockSupervisor.return_value
    mock_instance.compiled_graph = AsyncMock()

    async def fake_astream(*args, **kwargs):
        yield {"analyze": {"metadata": {"selected_agents": ["nlp"]}}}
        yield {"execute": {}}
        yield {"synthesize": {"metadata": {"final_answer": "ws test response"}}}

    mock_instance.compiled_graph.astream = fake_astream

    with client.websocket_connect("/ws/v1/chat") as websocket:
        websocket.send_json({"query": "hello"})

        # 1. queued
        data = websocket.receive_json()
        assert data["status"] == "queued"
        # 2. analyzing
        data = websocket.receive_json()
        assert data["status"] == "analyzing"
        # 3. from fake_astream analyze
        data = websocket.receive_json()
        assert data["status"] == "executing"
        assert "nlp" in data["agents"]
        # 4. execute
        data = websocket.receive_json()
        assert data["status"] == "synthesizing"
        # 5. synthesize
        data = websocket.receive_json()
        assert data["status"] == "done"
        assert data["response"] == "ws test response"


def test_rate_limiter():
    headers = {"X-Forwarded-For": "192.168.1.100"}
    for _ in range(60):
        client.get("/health", headers=headers)

    res_blocked = client.get("/health", headers=headers)
    assert res_blocked.status_code == 429
