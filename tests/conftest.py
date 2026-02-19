import asyncio
import httpx
import logging
import os
from typing import Callable

import pytest


@pytest.fixture(autouse=True)
def prevent_real_http_calls(monkeypatch):
    """Fail tests if any real outbound HTTP call is attempted via httpx.AsyncClient.

    This patches `httpx.AsyncClient.send` to allow calls only when the client's
    transport is an `httpx.MockTransport`. Any other attempt will raise.
    """
    orig_send = httpx.AsyncClient.send

    async def _guarded_send(self, request, *args, **kwargs):
        transport = getattr(self, "_transport", None)
        if isinstance(transport, httpx.MockTransport):
            return await orig_send(self, request, *args, **kwargs)
        raise RuntimeError(f"Outbound HTTP disabled during tests (attempted {request.method} {request.url})")

    monkeypatch.setattr(httpx.AsyncClient, "send", _guarded_send)
    yield
    monkeypatch.setattr(httpx.AsyncClient, "send", orig_send)


@pytest.fixture
def mock_ai_env(monkeypatch):
    """Set AI-related environment variables for tests to avoid startup failures."""
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_MODEL", "gpt-4o-mini")
    yield


@pytest.fixture
def mock_transport() -> Callable[[Callable[[httpx.Request], httpx.Response]], httpx.MockTransport]:
    """Return a factory that creates a MockTransport from a handler callable."""

    def _factory(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.MockTransport:
        return httpx.MockTransport(handler)

    return _factory


@pytest.fixture
def test_client(monkeypatch, mock_ai_env, mock_transport):
    """Create a TestClient for the FastAPI app with AIAdapter patched to use a MockTransport.

    Usage: pass `mock_transport` as needed to create a transport and then use this fixture.
    """
    from main import app
    import services.ai.adapter as adapter_mod

    def _with_transport(transport: httpx.MockTransport):
        # Patch AIAdapter.__init__ to use the provided MockTransport
        def _fake_init(self) -> None:
            self.provider = os.environ.get("AI_PROVIDER", "openai")
            self.model = os.environ.get("AI_MODEL", "gpt-4o-mini")
            self.api_key = os.environ.get("OPENAI_API_KEY", "")
            self.base_url = os.environ.get("OPENAI_API_BASE", "https://api.openai.com")
            event_hooks = {"request": [self._on_request], "response": [self._on_response]}
            self.client = httpx.AsyncClient(base_url=self.base_url, transport=transport, event_hooks=event_hooks)

        monkeypatch.setattr(adapter_mod.AIAdapter, "__init__", _fake_init)
        return TestClient(app)

    yield _with_transport
