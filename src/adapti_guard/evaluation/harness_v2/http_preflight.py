"""HTTP completion budget preflight (Amendment 2 formula)."""
from __future__ import annotations


def planned_http_requests(*, n_models: int, n_scenarios: int, max_rounds_per_episode: int) -> int:
    return n_models * n_scenarios * max_rounds_per_episode


def preflight_http_budget(
    *,
    n_models: int,
    n_scenarios: int,
    max_rounds_per_episode: int,
    http_cap: int,
) -> dict[str, int]:
    planned = planned_http_requests(
        n_models=n_models,
        n_scenarios=n_scenarios,
        max_rounds_per_episode=max_rounds_per_episode,
    )
    if planned > http_cap:
        raise RuntimeError(
            f"harness_v2 preflight refused: planned_http={planned} "
            f"({n_models}x{n_scenarios}x{max_rounds_per_episode}) exceeds cap={http_cap}"
        )
    return {
        "planned_http": planned,
        "http_cap": http_cap,
        "n_models": n_models,
        "n_scenarios": n_scenarios,
        "max_rounds_per_episode": max_rounds_per_episode,
    }
