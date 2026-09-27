#!/usr/bin/env python3
"""Fetch OpenRouter endpoint metadata for harness v2 reasoning policy (GET only)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.provider_probe import (  # noqa: E402
    HARNESS_V2_TARGETS,
    fetch_model_endpoints,
)

OUT = ROOT / "experiments/harness_v2/AMENDMENT4_REASONING_METADATA.json"


def main() -> int:
    targets: dict[str, object] = {}
    for family, model_id, config_key in HARNESS_V2_TARGETS:
        payload = fetch_model_endpoints(model_id)
        eps = payload.get("data", {}).get("endpoints") or []
        deepinfra = [e for e in eps if e.get("provider_name") == "DeepInfra"]
        first = deepinfra[0] if deepinfra else {}
        sp = first.get("supported_parameters") or []
        reasoning_related = [p for p in sp if "reason" in p.lower()]
        targets[model_id] = {
            "family": family,
            "config_key": config_key,
            "deepinfra_endpoint_name": first.get("name"),
            "deepinfra_pricing": first.get("pricing"),
            "deepinfra_supported_parameters": sp,
            "reasoning_related_parameters": reasoning_related,
            "supports_include_reasoning": "include_reasoning" in sp,
            "supports_reasoning_object": "reasoning" in sp,
        }
    doc = {
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "endpoints": "GET https://openrouter.ai/api/v1/models/{model_id}/endpoints",
            "reasoning_docs": "https://openrouter.ai/docs/guides/best-practices/reasoning-tokens",
        },
        "harness_v2_default_reasoning_off": {
            "include_reasoning": False,
            "reasoning": {"effort": "none"},
            "note_exclude_only": "reasoning.exclude:true hides text but still bills tokens; not used as primary off switch",
        },
        "targets": targets,
    }
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(doc, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
