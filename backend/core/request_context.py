from typing import Optional
from core.request_id import get_request_id as _get_request_id


def get_request_id() -> Optional[str]:
    """Return current request_id from context, or None if not set."""
    try:
        return _get_request_id()
    except Exception:
        return None
