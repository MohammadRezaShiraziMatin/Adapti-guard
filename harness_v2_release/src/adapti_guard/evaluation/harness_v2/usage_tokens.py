"""OpenRouter usage reasoning token extraction (harness v2)."""
from __future__ import annotations

from typing import Any


def reasoning_tokens_from_usage(usage: dict[str, Any] | None) -> int | None:
    if not usage:
        return None
    rt = usage.get("reasoning_tokens")
    if rt is not None:
        return int(rt)
    details = usage.get("completion_tokens_details") or {}
    inner = details.get("reasoning_tokens")
    if inner is not None:
        return int(inner)
    return None
