"""Malformed public requests must not crash or reach the AI worker."""
import pytest
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.routes import chat


@pytest.mark.parametrize("endpoint", ["/api/chat/", "/api/chat/stream"])
@pytest.mark.parametrize("body", [
    None, [], "invalid", {}, {"messages": []}, {"messages": "invalid"},
    {"messages": [None]}, {"messages": ["invalid"]},
    {"messages": [{"role": {}, "content": "test"}]},
    {"messages": [{"role": "user", "content": 42}]},
    {"messages": [{"role": "user", "content": "  "}]},
    {"messages": [{"role": "assistant", "content": "test"}]},
    {"messages": [{"role": "user", "content": "test"}], "context": 42},
    {"messages": [{"role": "user", "content": "test"}], "topic_key": []},
    {"messages": [{"role": "user", "content": "test"}], "page_url": None},
])
def test_malformed_chat_is_a_client_error(endpoint, body, monkeypatch):
    limiter = chat.RateLimiter()
    monkeypatch.setattr(chat, "_rate_limiter", limiter)

    def no_provider(**kwargs):
        pytest.fail("Invalid input reached the AI worker")

    monkeypatch.setattr(chat.httpx, "AsyncClient", no_provider)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(endpoint, json=body)
    assert response.status_code == 400
    assert isinstance(response.json()["detail"], str)
    assert limiter.limits == {}
