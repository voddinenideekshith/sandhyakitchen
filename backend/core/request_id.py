import contextvars

# context var holding current request id for the active async context
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    return request_id_var.get()


def set_request_id(value: str):
    return request_id_var.set(value)
