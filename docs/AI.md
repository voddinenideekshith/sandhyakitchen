# AI Integration — Architecture and Usage

This document describes the AI integration layer created for the Foodz Multi-Brand API.

## Architecture

- A modular AI service is implemented at `backend/services/ai/`.
- Routes must not call provider SDKs directly; they call `ai_service.generate_response()`.
- Components:
  - `adapter.py` — provider adapter, currently implements OpenAI HTTP calls via `httpx` and normalizes responses.
  - `service.py` — orchestration layer: builds prompts, handles retries, timeouts, and normalization.
  - `schemas.py` — Pydantic models `AIRequest` and `AIResponse`.
  - `prompts.py` — centralized prompt construction.
  - `__init__.py` — exports the `generate_response` entrypoint and schemas.

## Environment variables

- `AI_PROVIDER` — currently `openai` (future: `gemini`, `claude`, ...)
- `OPENAI_API_KEY` — required when `AI_PROVIDER=openai` (must be provided via environment, not hardcoded)
- `AI_MODEL` — model name to request (e.g. `gpt-4o-mini`)
- Optional: `OPENAI_API_BASE` to override the OpenAI base URL

The application validates provider configuration at startup and will raise a clear error if required secrets are missing.

## Endpoint

- POST `/ai/test`
  - Request: `AIRequest` (JSON):
    - `message`: string
    - `context`: optional object
  - Response: `AIResponse` (JSON):
    - `reply`: string
    - `tokens_used`: optional int

Example curl:

```bash
curl -X POST "http://localhost:8000/ai/test" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello AI","context":{"brand":"VegBites"}}'
```

Example response:

```json
{
  "reply": "Hello! How can I help with your order?",
  "tokens_used": 12
}
```

## Testing

- Unit tests are available at `backend/tests/test_ai_service.py`. They mock the adapter to verify service behavior.

## Notes

- The adapter uses `httpx` with an async client — this keeps code async-compatible and testable.
- Add additional providers by extending `adapter.py` or adding provider-specific adapters and updating the factory logic.

## Request tracing and observability

- Each incoming HTTP request is assigned a `request_id` (UUID4) by `RequestIDMiddleware`.
  - If a client provides `X-Request-ID`, it is preserved.
  - The `request_id` is available on `request.state.request_id` for request handlers.
  - `X-Request-ID` is returned in every HTTP response.
- The logging system injects the current `request_id` into every log record automatically using a contextvar and a logging filter.
- Logs are JSON structured and include `request_id` so you can correlate logs for a single request across services.

Example log:

```json
{
  "timestamp": "2026-02-19T12:34:56.789Z",
  "level": "INFO",
  "module": "services.ai.service",
  "request_id": "8b1a9953-...",
  "message": "ai_response_success"
}
```

## Continuous Integration

- A GitHub Actions workflow is included at `.github/workflows/ci.yml`.
- The CI pipeline runs on push and pull_request for all branches and performs:
  - Python 3.11 setup
  - Install dependencies from `backend/requirements.txt`
  - Install dev tools: `pytest`, `black`, `isort`, `flake8`
  - Run formatting checks: `black --check .`
  - Run import sorting checks: `isort --check-only .`
  - Run linter: `flake8 .`
  - Run tests: `pytest`

This ensures formatting, import order, linting and tests must pass before merges.

