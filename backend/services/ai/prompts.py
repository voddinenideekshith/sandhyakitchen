from typing import Optional, Dict, Any


def build_prompt(message: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Construct a simple, clear prompt using optional context.

    Keep prompt construction logic centralized so other callers can extend it.
    """
    if not context:
        return message

    ctx_lines = []
    for k, v in context.items():
        ctx_lines.append(f"{k}: {v}")

    return "\n".join(ctx_lines) + "\n\nUser: " + message
