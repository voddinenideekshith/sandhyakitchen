import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable

from core.request_id import request_id_var


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a UUID4 request id to each request and expose it via contextvar.

    - preserves incoming `X-Request-ID` header when present
    - sets `request.state.request_id`
    - adds `X-Request-ID` header to responses
    - ensures contextvar is reset after request
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        incoming = request.headers.get("X-Request-ID")
        rid = incoming if incoming else str(uuid.uuid4())
        # set on request.state for application code
        request.state.request_id = rid
        # set context var for logging filter
        token = request_id_var.set(rid)
        try:
            response = await call_next(request)
            # ensure header is present in response
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            # restore prior context
            request_id_var.reset(token)
