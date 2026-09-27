"""Offline: pilot preflight USD cap lock (pilot 3 hard cap 0.80)."""
from __future__ import annotations

import pytest

from adapti_guard.evaluation.harness_v2.pilot_preflight import preflight_pilot_plan


def test_preflight_accepts_usd_cap_080() -> None:
    out = preflight_pilot_plan(http_cap=640, usd_cap=0.80, planned_http_cap=640)
    assert out["usd_cap"] == 0.80
    assert out["http_cap"] == 640


def test_preflight_refuses_usd_cap_above_080() -> None:
    with pytest.raises(RuntimeError, match="usd_cap 0.81 > locked 0.80"):
        preflight_pilot_plan(http_cap=640, usd_cap=0.81, planned_http_cap=640)
