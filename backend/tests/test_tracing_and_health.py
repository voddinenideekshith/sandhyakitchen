import asyncio
import uuid

import httpx
import pytest

from core import request_id as rid_mod

from services.ai.adapter import AIAdapter
from services.ai import health_check, shutdown_service as shutdown


@pytest.mark.asyncio
async def test_request_id_propagation(monkeypatch):
    # ensure adapter can initialize (provide dummy API key)
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    # set a request id in contextvar as middleware would
    test_rid = str(uuid.uuid4())
    token = rid_mod.request_id_var.set(test_rid)

    adapter = AIAdapter()

    # handler to assert X-Request-ID present on incoming request
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("X-Request-ID") == test_rid
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}], "usage": {"total_tokens": 1}}, request=request)

    transport = httpx.MockTransport(handler)
    # create a client with same event hooks so adapter's hooks run
    adapter.client = httpx.AsyncClient(base_url=adapter.base_url, transport=transport, event_hooks={"request": [adapter._on_request], "response": [adapter._on_response]})

    try:
        res = await adapter.send_prompt("hello")
        assert res.get("reply") == "ok"
    finally:
        await adapter.client.aclose()
        rid_mod.request_id_var.reset(token)


@pytest.mark.asyncio
async def test_ai_health_function(monkeypatch):
    # ensure AI env is set to allow adapter init
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    res = await health_check()
    assert res.get("status") == "ok"


@pytest.mark.asyncio
async def test_graceful_shutdown_called(monkeypatch):
    called = {"closed": False}

    class Dummy:
        async def close(self):
            called["closed"] = True

    # inject dummy adapter into service module
    import services.ai.service as svc

    svc._adapter = Dummy()
    await shutdown()
    assert called["closed"] is True
