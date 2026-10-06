"""Redact secrets from log/evidence payloads."""
from __future__ import annotations

import re
from typing import Any

_SECRET_KEYS = frozenset(
    {
        "openrouter_api_key",
        "gemini_api_key",
        "groq_api_key",
        "cerebras_api_key",
        "google_api_key",
        "authorization",
        "api_key",
        "bearer",
    }
)
_BEARER_RE = re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.I)
_SK_RE = re.compile(r"sk-or-[A-Za-z0-9]+")


def redact_value(key: str, value: Any) -> Any:
    if key.lower() in _SECRET_KEYS:
        return "***REDACTED***" if value else None
    if isinstance(value, str):
        if _BEARER_RE.search(value) or _SK_RE.search(value):
            return "***REDACTED***"
    return value


def redact_mapping(payload: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in payload.items():
        if isinstance(v, dict):
            out[k] = redact_mapping(v)
        elif isinstance(v, list):
            out[k] = [redact_mapping(x) if isinstance(x, dict) else redact_value(k, x) for x in v]
        else:
            out[k] = redact_value(k, v)
    return out
