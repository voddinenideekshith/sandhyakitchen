import json
import logging
import os
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient


def _mock_openai_handler(request: httpx.Request) -> httpx.Response:
    # Assert that X-Request-ID header was propagated by adapter
    rid = request.headers.get("X-Request-ID")
    assert rid == "test-e2e-123", "Adapter did not receive X-Request-ID"

    # Return a minimal OpenAI-like chat completion JSON
    body = {
        "choices": [{"message": {"content": "mocked reply"}}],
        "usage": {"total_tokens": 5},
    }
    return httpx.Response(200, json=body, request=request)


@pytest.mark.parametrize("endpoint", ["/ai/test"])  # project exposes /ai/test
def test_ai_generate_endpoint_e2e(test_client, mock_transport, caplog, endpoint: str):
    """Full-stack E2E test for AI endpoint with request-id propagation.

    This version uses fixtures from `tests/conftest.py` to provide a TestClient
    backed by a MockTransport and sets AI env vars automatically.
    """
    transport = mock_transport(_mock_openai_handler)
    with test_client(transport) as client:
        caplog.set_level(logging.INFO)
        headers = {"X-Request-ID": "test-e2e-123"}
        payload = {"message": "hello"}
        r = client.post(endpoint, json=payload, headers=headers)

        assert r.status_code == 200
        data: Any = r.json()
        # Adapter mocked response should be normalized to AIResponse
        assert data.get("reply") == "mocked reply"
        assert data.get("tokens_used") == 5

    # After TestClient context, shutdown should have run and adapter cleaned up
    import services.ai.service as svc

    assert getattr(svc, "_adapter", None) is None

    logs_text = caplog.text
    assert "test-e2e-123" in logs_text
    assert "ai_http_request_start" in logs_text or "ai_http_request_success" in logs_text
