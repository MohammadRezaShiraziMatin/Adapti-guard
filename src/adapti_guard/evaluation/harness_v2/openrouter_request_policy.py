"""Harness v2 OpenRouter request defaults (Amendment 4): reasoning off where supported."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Fixed project default: disable reasoning output/generation on capable endpoints.
# Applied only when the DeepInfra endpoint lists the parameter (require_parameters: true).
_REASONING_OFF_BODY: dict[str, Any] = {
    "include_reasoning": False,
    "reasoning": {"effort": "none"},
}

_DEEPINFRA_PROVIDER_PIN: dict[str, Any] = {
    "order": ["DeepInfra"],
    "allow_fallbacks": False,
    "require_parameters": True,
}

_METADATA_PATH = (
    Path(__file__).resolve().parents[4]
    / "experiments/harness_v2/AMENDMENT4_REASONING_METADATA.json"
)


def _load_metadata() -> dict[str, Any]:
    if not _METADATA_PATH.is_file():
        return {"targets": {}}
    return json.loads(_METADATA_PATH.read_text(encoding="utf-8"))


def deepinfra_supported_parameters(model_id: str, metadata: dict[str, Any] | None = None) -> list[str]:
    meta = metadata if metadata is not None else _load_metadata()
    row = (meta.get("targets") or {}).get(model_id) or {}
    sp = row.get("deepinfra_supported_parameters")
    if isinstance(sp, list):
        return list(sp)
    return []


def reasoning_off_fields_for_model(
    model_id: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Return (fields_for_extra_body, audit) where audit documents what was applied or skipped.
    """
    sp = set(deepinfra_supported_parameters(model_id, metadata))
    applied: dict[str, Any] = {}
    skipped: dict[str, str] = {}
    if "include_reasoning" in sp:
        applied["include_reasoning"] = _REASONING_OFF_BODY["include_reasoning"]
    else:
        skipped["include_reasoning"] = "not_in_deepinfra_supported_parameters"
    if "reasoning" in sp:
        applied["reasoning"] = dict(_REASONING_OFF_BODY["reasoning"])
    else:
        skipped["reasoning"] = "not_in_deepinfra_supported_parameters"
    audit = {
        "model_id": model_id,
        "reasoning_off_applied": applied,
        "reasoning_off_skipped": skipped,
        "policy": "harness_v2_fixed_default_amendment4",
    }
    return applied, audit


def build_harness_v2_extra_body(
    model_id: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reasoning_fields, _audit = reasoning_off_fields_for_model(model_id, metadata=metadata)
    extra: dict[str, Any] = {"provider": dict(_DEEPINFRA_PROVIDER_PIN)}
    extra.update(reasoning_fields)
    return extra
