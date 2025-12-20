from __future__ import annotations
from .base import EventSchema
from .login_attempt import SCHEMA as LOGIN_ATTEMPT_SCHEMA
from .checkout_attempt import SCHEMA as CHECKOUT_ATTEMPT_SCHEMA

_REGISTRY: dict[str, EventSchema] = {
    LOGIN_ATTEMPT_SCHEMA.name: LOGIN_ATTEMPT_SCHEMA,
    CHECKOUT_ATTEMPT_SCHEMA.name: CHECKOUT_ATTEMPT_SCHEMA,
}

def list_schemas() -> list[str]:
    return sorted(_REGISTRY.keys())

def get_schema(name: str) -> EventSchema:
    if name not in _REGISTRY:
        raise KeyError(f"Unknown schema: {name}. Known: {list_schemas()}")
    return _REGISTRY[name]
