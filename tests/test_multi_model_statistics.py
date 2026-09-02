"""Tests for multi-model statistical analysis."""

import json
from pathlib import Path

import pytest

from src.adapti_guard.evaluation.multi_model_statistics import (
    analyze_multi_model_results,
    compute_baseline_statistics,
    outcomes_from_predictions,
    paired_baseline_comparison,
)
from src.adapti_guard.evaluation.statistics import holm_correction


def _make_outcomes(n_attack: int, asr: float, baseline: str, model: str):
    from src.adapti_guard.evaluation.multi_model_statistics import EpisodeOutcome

    outcomes = []
    n_success = int(n_attack * asr)
    for i in range(n_attack):
        outcomes.append(EpisodeOutcome(
            episode_id=f"ep_{i}",
            label="attack",
            attack_succeeded=i < n_success,
            utility_success=False,
            blocked=False,
            baseline=baseline,
            model_key=model,
        ))
    return outcomes


def test_holm_correction():
    adjusted = holm_correction([0.01, 0.04, 0.03])
    assert len(adjusted) == 3
    assert all("adjusted_p" in a for a in adjusted)
    assert adjusted[0]["adjusted_p"] <= adjusted[1]["adjusted_p"] + 0.001


def test_paired_mcnemar_b0_vs_b3():
    b0 = _make_outcomes(20, 0.5, "B0", "target_1")
    b3 = _make_outcomes(20, 0.1, "B3", "target_1")
    # Align episode IDs
    for o in b3:
        o.episode_id = f"ep_{int(o.episode_id.split('_')[1])}"

    result = paired_baseline_comparison(b0, b3, reference="B0", treatment="B3")
    assert result["n_paired"] == 20
    assert result["asr_reduction"] > 0
    assert "mcnemar" in result


def test_compute_baseline_statistics():
    outcomes = _make_outcomes(10, 0.3, "B0", "target_1")
    stats = compute_baseline_statistics(outcomes)
    assert stats["n_attack"] == 10
    assert 0.2 <= stats["asr"]["point"] <= 0.4
    assert len(stats["asr"]["bootstrap_ci_95"]) == 2


def test_analyze_from_predictions(tmp_path: Path):
    model_dir = tmp_path / "target_1" / "B0"
    model_dir.mkdir(parents=True)
    rows = [
        {"id": "e1", "label": "attack", "attack_succeeded": True, "utility_success": False, "blocked": False},
        {"id": "e2", "label": "attack", "attack_succeeded": False, "utility_success": False, "blocked": False},
        {"id": "e3", "label": "benign", "attack_succeeded": False, "utility_success": True, "blocked": False},
    ]
    pred_path = model_dir / "B0_predictions.jsonl"
    with pred_path.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    report = analyze_multi_model_results(
        tmp_path,
        models=["target_1"],
        baselines=["B0"],
        seed=42,
    )
    assert report.status == "COMPLETED"
    assert "target_1" in report.per_model_baseline
