"""Option D M1 — main pilot runner scope (3 models, K=24 attack, K_benign=5)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_pilot_module():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        ROOT / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_option_d_runner_caps_and_model_order():
    mod = _load_pilot_module()
    assert mod.MODEL_ORDER == ("qwen3", "gemma", "deepseek")
    assert "llama" not in mod.MODEL_ORDER
    assert mod.HTTP_CAP == 12636
    assert mod.USD_CAP == pytest.approx(0.80)
    assert mod.PILOT_ATTACK_K == 24
    assert mod.PILOT_BENIGN_K == 5


def test_option_d_schedule_episode_counts_and_instance_ranges():
    mod = _load_pilot_module()
    schedule = mod.pilot_episode_schedule()
    assert len(schedule) == 1098
    attack_rows = [r for r in schedule if not r["scenario_id"].startswith("benign_")]
    benign_rows = [r for r in schedule if r["scenario_id"].startswith("benign_")]
    assert len(attack_rows) == 7 * 24 * 3 * 2
    assert len(benign_rows) == 3 * 5 * 3 * 2
    assert {r["instance_index"] for r in attack_rows} == set(range(24))
    assert {r["instance_index"] for r in benign_rows} == set(range(5))
    assert {r["family"] for r in schedule} == {"qwen3", "gemma", "deepseek"}


def test_option_d_preflight_plan_matches_http_cap():
    mod = _load_pilot_module()
    plan = mod.option_d_preflight_pilot_plan(
        http_cap=mod.HTTP_CAP,
        usd_cap=mod.USD_CAP,
        planned_http_cap=mod.HTTP_CAP,
    )
    assert plan["http_cap"] == 12636
    assert plan["episodes_total"] == 1098
    assert plan["k_attack"] == 24
    assert plan["k_benign"] == 5
