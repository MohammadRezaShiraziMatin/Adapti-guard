"""Harmonized runner invariants."""

import json
from pathlib import Path

from src.adapti_guard.experiments.harmonized_runner import (
    HarmonizedRunner,
    PolicyMode,
    build_schedule_75_25,
    population_fingerprint,
    summarize_method,
)


def _load_stream():
    return json.loads(
        Path("results/common_attack_stream.json").read_text(encoding="utf-8")
    )


def test_schedule_is_75_25():
    schedule = build_schedule_75_25(100)
    assert len(schedule) == 100
    assert sum(schedule) == 25
    assert len(schedule) - sum(schedule) == 75


def test_all_methods_share_population():
    runner = HarmonizedRunner(_load_stream(), build_schedule_75_25(100))
    results = runner.run_all()
    fps = [population_fingerprint(r) for r in results.values()]
    assert all(fp == fps[0] for fp in fps)


def test_fixed_methods_have_zero_transitions():
    runner = HarmonizedRunner(_load_stream(), build_schedule_75_25(100))
    for mode in (
        PolicyMode.FIXED_L0,
        PolicyMode.FIXED_L1,
        PolicyMode.FIXED_L2,
        PolicyMode.FIXED_L3,
    ):
        summary = summarize_method(runner.run_method(mode))
        assert summary["transition_statistics"]["number_of_transitions"] == 0


def test_ablation_directionality():
    runner = HarmonizedRunner(_load_stream(), build_schedule_75_25(100))
    esc = summarize_method(runner.run_method(PolicyMode.ESCALATION_ONLY))
    deesc = summarize_method(runner.run_method(PolicyMode.DE_ESCALATION_ONLY))
    assert esc["transition_statistics"]["deescalation_count"] == 0
    assert deesc["transition_statistics"]["escalation_count"] == 0
