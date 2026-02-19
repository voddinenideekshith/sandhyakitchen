"""Shim package to allow imports from app.core.config in CI and other contexts.
This module intentionally re-exports settings from the canonical `core.config`.
"""

from ..core.config import settings  # re-export for `from app.core.config import settings`

__all__ = ["settings"]
