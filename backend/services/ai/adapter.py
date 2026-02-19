from core.config import settings
import logging
from typing import Dict, Any, Optional
import httpx
import time
from urllib.parse import urljoin, urlparse
from core.request_context import get_request_id


logger = logging.getLogger(__name__)


class AIAdapter:
    """Provider adapter — encapsulates provider initialization and a single send_prompt API.

    Current implementation supports 'openai' via direct HTTP calls using `httpx`.
    The adapter reads configuration from environment variables so it is safe
    for production (no hardcoded keys).
    """

    def __init__(self) -> None:
        self.provider = (settings.AI_PROVIDER or "openai").lower()
        self.model = settings.AI_MODEL

        if self.provider == "openai":
            key = settings.OPENAI_API_KEY
            if not key:
                raise RuntimeError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
            self.api_key = key
            self.base_url = str(settings.OPENAI_API_BASE) if settings.OPENAI_API_BASE else "https://api.openai.com"
            # create client with event hooks to propagate request_id and measure latency
            event_hooks = {
                "request": [self._on_request],
                "response": [self._on_response],
            }
            # reuse a single AsyncClient instance for the adapter lifetime
            self.client = httpx.AsyncClient(base_url=self.base_url, event_hooks=event_hooks)
        else:
            raise NotImplementedError(f"AI provider '{self.provider}' is not implemented")

    async def send_prompt(self, prompt: str, timeout: Optional[float] = 15.0) -> Dict[str, Any]:
        """Send the prompt to the configured provider and normalize the response.

        Returns a dict with keys: 'reply' and optional 'tokens_used'.
        """
        if self.provider == "openai":
            # Use Chat Completions for broader model compatibility; payload is safe and simple
            url = "/v1/chat/completions"
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 1024,
            }
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            logger.info("sending prompt to ai provider", extra={"provider": self.provider, "model": self.model})
            # prepare full url for safe logging
            full_url = urljoin(self.base_url, url)
            start = time.time()
            try:
                resp = await self.client.post(url, json=payload, headers=headers, timeout=timeout)
                resp.raise_for_status()
                data = resp.json()
                # compute latency: prefer response.request.extensions if set by hook
                try:
                    req_start = resp.request.extensions.get("start_time")
                    latency_ms = int((time.time() - req_start) * 1000) if req_start else int((time.time() - start) * 1000)
                except Exception:
                    latency_ms = int((time.time() - start) * 1000)
                safe_url = _safe_url(full_url)
                logger.info("ai_http_request_success", extra={
                    "method": "POST",
                    "url": safe_url,
                    "latency_ms": latency_ms,
                    "status_code": resp.status_code,
                })
            except Exception as e:
                # attempt to extract latency if possible
                try:
                    latency_ms = int((time.time() - start) * 1000)
                except Exception:
                    latency_ms = None
                safe_url = _safe_url(full_url)
                logger.error("ai_http_request_error", extra={
                    "method": "POST",
                    "url": safe_url,
                    "latency_ms": latency_ms,
                    "error": str(e),
                })
                raise

            # Normalize: support both chat completions and response-like shapes
            try:
                choice = data["choices"][0]
                # Chat completion shape
                text = choice.get("message", {}).get("content") or choice.get("text")
            except Exception:
                text = None

            if text is None:
                # Try Responses API shape
                text = data.get("output", "")

            tokens = None
            if isinstance(data.get("usage"), dict):
                tokens = data["usage"].get("total_tokens") or data["usage"].get("prompt_tokens")

            return {"reply": text or "", "tokens_used": tokens}

        raise NotImplementedError("Provider not implemented")

    async def close(self) -> None:
        try:
            await self.client.aclose()
            logger.info("ai adapter httpx client closed", extra={"provider": self.provider})
        except Exception:
            logger.exception("error closing httpx client")

    async def _on_request(self, request: httpx.Request) -> None:
        """Event hook: runs before each outgoing request.

        Propagates X-Request-ID header from contextvar and stores start_time in request.extensions.
        """
        try:
            rid = get_request_id()
            if rid:
                # do not override if already present
                if "X-Request-ID" not in request.headers:
                    request.headers["X-Request-ID"] = rid
        except Exception:
            rid = None
        # record start time for latency measurement
        request.extensions["start_time"] = time.time()
        safe_url = _safe_url(str(request.url))
        logger.info("ai_http_request_start", extra={"method": request.method, "url": safe_url})

    async def _on_response(self, response: httpx.Response) -> None:
        """Event hook: runs after each response is received (before returning to caller)."""
        req = response.request
        start = req.extensions.get("start_time")
        latency_ms = int((time.time() - start) * 1000) if start else None
        safe_url = _safe_url(str(req.url))
        logger.info("ai_http_request_success", extra={
            "method": req.method,
            "url": safe_url,
            "latency_ms": latency_ms,
            "status_code": response.status_code,
        })


def _safe_url(full_url: str) -> str:
    """Return a URL without querystring or userinfo to avoid leaking secrets."""
    try:
        p = urlparse(full_url)
        return f"{p.scheme}://{p.netloc}{p.path}"
    except Exception:
        return full_url
