"""Pilot preflight: scope caps (HTTP 640, USD 0.80)."""
from __future__ import annotations


def pilot_scope_constants() -> dict[str, int]:
    n_models = 4
    n_scenarios = 10
    n_instances = 2
    n_conditions = 2
    max_rounds = 4
    episodes = n_scenarios * n_instances * n_models * n_conditions
    http_cap = n_models * n_scenarios * n_instances * n_conditions * max_rounds
    return {
        "n_models": n_models,
        "n_scenarios": n_scenarios,
        "n_instances_pilot": n_instances,
        "n_conditions": n_conditions,
        "max_rounds": max_rounds,
        "episodes_total": episodes,
        "http_cap": http_cap,
    }


def preflight_pilot_plan(*, http_cap: int, usd_cap: float, planned_http_cap: int) -> dict[str, float | int]:
    scope = pilot_scope_constants()
    if scope["http_cap"] != planned_http_cap:
        raise RuntimeError(
            f"pilot preflight: scope http_cap {scope['http_cap']} != configured {planned_http_cap}"
        )
    if planned_http_cap > http_cap:
        raise RuntimeError(
            f"pilot preflight refused: planned_http_cap {planned_http_cap} > http_cap {http_cap}"
        )
    if usd_cap > 0.80 + 1e-9:
        raise RuntimeError(f"pilot preflight refused: usd_cap {usd_cap} > locked 0.80")
    return {**scope, "usd_cap": usd_cap, "configured_http_cap": http_cap}
