"""OpenRouter provider metadata probe (GET /models/{id}/endpoints)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

HARNESS_V2_TARGETS: list[tuple[str, str, str]] = [
    ("qwen3", "qwen/qwen3-30b-a3b", "q1_primary_qwen3_30b_a3b"),
    ("gemma", "google/gemma-4-31b-it", "q1_primary_gemma_4_31b_it"),
    ("llama", "meta-llama/llama-3.3-70b-instruct", "q1_primary_llama_3_3_70b"),
    ("deepseek", "deepseek/deepseek-v3.2", "q1_primary_deepseek_v3_2"),
]


def fetch_model_endpoints(model_id: str, *, api_key: str | None = None) -> dict[str, Any]:
    key = (api_key or os.environ.get("OPENROUTER_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    url = f"https://openrouter.ai/api/v1/models/{model_id}/endpoints"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def analyze_deepinfra_tools(endpoints_payload: dict[str, Any]) -> dict[str, Any]:
    eps = endpoints_payload.get("data", {}).get("endpoints") or []
    deepinfra = [e for e in eps if e.get("provider_name") == "DeepInfra"]
    qualifying = []
    for e in deepinfra:
        sp = e.get("supported_parameters") or []
        if "tools" in sp and "tool_choice" in sp:
            qualifying.append(
                {
                    "name": e.get("name"),
                    "provider_name": e.get("provider_name"),
                    "supported_parameters_excerpt": [p for p in sp if p in ("tools", "tool_choice", "require_parameters")],
                    "supports_tool_choice": e.get("supports_tool_choice"),
                }
            )
    return {
        "deepinfra_endpoint_count": len(deepinfra),
        "deepinfra_tools_capable_count": len(qualifying),
        "smoke_eligible": len(qualifying) > 0,
        "qualifying_deepinfra_excerpts": qualifying,
        "first_deepinfra_excerpt": (
            {
                "name": deepinfra[0].get("name"),
                "supported_parameters": deepinfra[0].get("supported_parameters"),
            }
            if deepinfra
            else None
        ),
    }


def probe_all_targets() -> dict[str, Any]:
    out: dict[str, Any] = {"targets": {}, "planned_routing": {
        "provider": {"order": ["DeepInfra"], "allow_fallbacks": False, "require_parameters": True}
    }}
    for family, model_id, config_key in HARNESS_V2_TARGETS:
        payload = fetch_model_endpoints(model_id)
        analysis = analyze_deepinfra_tools(payload)
        out["targets"][family] = {
            "model_id": model_id,
            "config_key": config_key,
            "endpoints_url": f"https://openrouter.ai/api/v1/models/{model_id}/endpoints",
            **analysis,
        }
    return out
