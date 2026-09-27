"""HTTP preflight tests."""
from __future__ import annotations

import pytest

from adapti_guard.evaluation.harness_v2.http_preflight import (
    planned_http_requests,
    preflight_http_budget,
)


def test_planned_formula_smoke3():
    assert planned_http_requests(n_models=3, n_scenarios=1, max_rounds_per_episode=3) == 9


def test_preflight_refuses_over_cap():
    with pytest.raises(RuntimeError, match="preflight refused"):
        preflight_http_budget(n_models=3, n_scenarios=1, max_rounds_per_episode=3, http_cap=8)


def test_preflight_ok_at_cap():
    out = preflight_http_budget(n_models=3, n_scenarios=1, max_rounds_per_episode=3, http_cap=9)
    assert out["planned_http"] == 9
