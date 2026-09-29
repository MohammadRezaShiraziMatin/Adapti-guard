"""Extract finish_reason metadata from OpenRouter chat completion payloads."""
from __future__ import annotations

from typing import Any


def finish_metadata_from_raw_response(raw: dict[str, Any]) -> dict[str, str | None]:
    """Return finish_reason and native_finish_reason from choices[0] if present."""
    choices = raw.get("choices") or []
    if not choices:
        return {"finish_reason": None, "native_finish_reason": None}
    ch0 = choices[0] if isinstance(choices[0], dict) else {}
    fr = ch0.get("finish_reason")
    nfr = ch0.get("native_finish_reason")
    if nfr is None and isinstance(ch0.get("provider_metadata"), dict):
        nfr = ch0["provider_metadata"].get("native_finish_reason")
    return {
        "finish_reason": str(fr) if fr is not None else None,
        "native_finish_reason": str(nfr) if nfr is not None else None,
    }


def response_complete_for_attack_eval(
    *,
    finish_reason: str | None,
    provider_error: str | None,
) -> bool:
    """C2 gate: truncated or errored responses are not valid for exec_success / content_leak."""
    if provider_error:
        return False
    if finish_reason == "length":
        return False
    return True
