import pytest

from pydantic import ValidationError

from services.ai import generate_response, AIRequest


class DummyAdapter:
    def __init__(self, result=None, exc=None):
        self._result = result
        self._exc = exc
        # minimal attributes expected by service logging
        self.provider = "test"
        self.model = "test-model"

    async def send_prompt(self, prompt, timeout=None):
        if self._exc:
            raise self._exc
        return self._result


@pytest.mark.asyncio
async def test_successful_response(monkeypatch):
    dummy = DummyAdapter(result={"reply": "Hello from AI", "tokens_used": 7})
    monkeypatch.setattr("services.ai.service._get_adapter", lambda: dummy)
    req = AIRequest(message="Hello")
    res = await generate_response(req)
    assert res.reply == "Hello from AI"
    assert res.tokens_used == 7


def test_invalid_input():
    with pytest.raises(ValidationError):
        AIRequest()  # missing required 'message'


@pytest.mark.asyncio
async def test_provider_failure_handling(monkeypatch):
    dummy = DummyAdapter(exc=Exception("provider down"))
    monkeypatch.setattr("services.ai.service._get_adapter", lambda: dummy)
    req = AIRequest(message="Will fail")
    with pytest.raises(Exception):
        await generate_response(req)
