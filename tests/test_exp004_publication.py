"""Offline tests for EXP-004 publication blockers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.adapti_guard.evaluation.attack_success import EvalEpisode
from src.adapti_guard.evaluation.multi_model_statistics import (
    EpisodeOutcome,
    compute_baseline_statistics,
)
from src.adapti_guard.evaluation.prediction_provenance import (
    PROVENANCE_SCHEMA_VERSION,
    build_prediction_row,
)
from src.adapti_guard.evaluation.target_model import build_target_model
from src.adapti_guard.experiments.multi_model_eval import (
    MultiModelConfig,
    resolve_cache_enabled,
)
from src.adapti_guard.experiments.resume_validation import (
    ResumeExpectation,
    validate_baseline_resume,
)

FROZEN_HASH = "27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24"


def _expectation(**overrides) -> ResumeExpectation:
    base = {
        "model_id": "openai/gpt-4o-mini",
        "model_config_key": "model_a",
        "baseline": "B0",
        "n_samples": 2,
        "seed": 42,
        "dataset_hash": FROZEN_HASH,
        "cache_enabled": False,
        "config_version": PROVENANCE_SCHEMA_VERSION,
        "sample_ids": ("s1", "s2"),
        "experiment_id": "EXP-004",
    }
    base.update(overrides)
    return ResumeExpectation(**base)


def _write_valid_artifacts(tmp_path: Path, *, sample_ids=("s1", "s2")) -> tuple[Path, Path]:
    metrics_path = tmp_path / "B0_metrics.json"
    predictions_path = tmp_path / "B0_predictions.jsonl"
    provenance = {
        "experiment_id": "EXP-004",
        "model_id": "openai/gpt-4o-mini",
        "model_config_key": "model_a",
        "baseline": "B0",
        "n_samples": len(sample_ids),
        "seed": 42,
        "dataset_hash": FROZEN_HASH,
        "cache_enabled": False,
        "config_version": PROVENANCE_SCHEMA_VERSION,
        "sample_ids": list(sample_ids),
        "git_commit": "abc123",
    }
    metrics_path.write_text(
        json.dumps({"baseline": "B0", "provenance": provenance, **provenance}),
        encoding="utf-8",
    )
    rows = [{"sample_id": sid, "id": sid, "baseline": "B0"} for sid in sample_ids]
    predictions_path.write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n",
        encoding="utf-8",
    )
    return metrics_path, predictions_path


def test_exp004_publication_config_disables_cache():
    config = MultiModelConfig(
        experiment_id="EXP-004",
        publication_mode=True,
        cache_enabled=False,
    )
    assert resolve_cache_enabled(config) is False


def test_build_target_model_respects_cache_disabled(monkeypatch):
    captured: dict[str, object] = {}

    class FakeOpenRouterTargetModel:
        def __init__(self, model_id: str, *, cache=None, **kwargs):
            captured["cache"] = cache
            self.cache = cache
            self.model_id = model_id

    monkeypatch.setattr(
        "src.adapti_guard.evaluation.target_model.OpenRouterTargetModel",
        FakeOpenRouterTargetModel,
    )

    model = build_target_model("model_a", cache_enabled=False)

    assert captured["cache"] is None
    assert model.cache is None


def test_build_prediction_row_contains_publication_fields():
    ep = EvalEpisode(
        id="sample-1",
        prompt="attack",
        context="",
        category="prompt_injection",
        label="attack",
        defense_action="A0",
        blocked=False,
        model_response="output text",
        attack_succeeded=False,
        utility_success=False,
        judge_reason="refused",
        latency_ms=12.5,
        target_latency_ms=5.0,
        judge_latency_ms=7.5,
        prompt_tokens=100,
        completion_tokens=20,
        metadata={
            "judge_raw": '{"attack_success": false}',
            "judge_model": "anthropic/claude-sonnet-4",
            "judge_fallback_used": True,
            "cache_hit": False,
            "target_cache_hit": False,
        },
    )
    row = build_prediction_row(
        ep,
        baseline="B0",
        model_id="openai/gpt-4o-mini",
        model_config_key="model_a",
        experiment_id="EXP-004",
        git_commit="abc123",
        seed=42,
        dataset_hash=FROZEN_HASH,
        cache_enabled=False,
    )
    required = {
        "sample_id",
        "episode_id",
        "model_id",
        "baseline",
        "category",
        "label",
        "blocked",
        "attack_succeeded",
        "utility_success",
        "target_response",
        "judge_raw",
        "judge_model",
        "judge_reason",
        "target_latency_ms",
        "judge_latency_ms",
        "episode_latency_ms",
        "cache_hit",
        "timestamp",
        "prompt_tokens",
        "completion_tokens",
        "dataset_hash",
        "git_commit",
        "seed",
        "cache_enabled",
        "config_version",
        "judge_fallback_used",
    }
    assert required.issubset(row.keys())
    assert row["judge_fallback_used"] is True
    assert row["cache_enabled"] is False


def test_attack_only_multi_model_statistics_use_none():
    outcomes = [
        EpisodeOutcome("e1", "attack", True, False, False, "B0", "model_a"),
        EpisodeOutcome("e2", "attack", False, False, False, "B0", "model_a"),
    ]
    stats = compute_baseline_statistics(outcomes)
    assert stats["n_benign"] == 0
    assert stats["fpr"] is None
    assert stats["utility"] is None
    assert stats["balanced_accuracy"] is None
    assert stats["asr"]["point"] == 0.5


def test_mixed_multi_model_statistics_remain_valid():
    outcomes = [
        EpisodeOutcome("e1", "attack", True, False, False, "B0", "model_a"),
        EpisodeOutcome("e2", "attack", False, False, False, "B0", "model_a"),
        EpisodeOutcome("e3", "benign", False, True, False, "B0", "model_a"),
        EpisodeOutcome("e4", "benign", False, False, False, "B0", "model_a"),
    ]
    stats = compute_baseline_statistics(outcomes)
    assert stats["fpr"]["point"] == 0.5
    assert stats["utility"]["point"] == 0.5
    assert stats["balanced_accuracy"]["point"] == 0.5
    assert len(stats["fpr"]["bootstrap_ci_95"]) == 2


@pytest.mark.parametrize(
    "mutator,expected_substring",
    [
        (lambda p: p.unlink(), "missing predictions artifact"),
        (lambda p: p.write_text('{"baseline":"B0"}\n', encoding="utf-8"), "prediction count mismatch"),
        (
            lambda p: p.write_text(
                "\n".join(
                    [
                        json.dumps({"sample_id": "s1", "id": "s1"}),
                        json.dumps({"sample_id": "s1", "id": "s1"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            ),
            "duplicate sample IDs",
        ),
    ],
)
def test_resume_validation_invalid_predictions(tmp_path, mutator, expected_substring):
    metrics_path, predictions_path = _write_valid_artifacts(tmp_path)
    mutator(predictions_path)
    result = validate_baseline_resume(
        metrics_path=metrics_path,
        predictions_path=predictions_path,
        expected=_expectation(),
    )
    assert not result.valid
    assert any(expected_substring in reason for reason in result.reasons)


def test_resume_validation_valid_artifact(tmp_path):
    metrics_path, predictions_path = _write_valid_artifacts(tmp_path)
    assert validate_baseline_resume(
        metrics_path=metrics_path,
        predictions_path=predictions_path,
        expected=_expectation(),
    ).valid


def test_resume_validation_mismatch_cases(tmp_path):
    metrics_path, predictions_path = _write_valid_artifacts(tmp_path)

    for field, value, needle in [
        ("baseline", "B6", "baseline mismatch"),
        ("model_config_key", "model_b", "model_config_key mismatch"),
        ("model_id", "qwen/qwen3-30b-a3b", "model_id mismatch"),
        ("seed", 99, "seed mismatch"),
        ("dataset_hash", "deadbeef", "dataset_hash mismatch"),
        ("cache_enabled", True, "cache_enabled mismatch"),
        ("config_version", "0.9", "config_version mismatch"),
    ]:
        bad_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        bad_metrics["provenance"][field] = value
        if field in bad_metrics:
            bad_metrics[field] = value
        metrics_path.write_text(json.dumps(bad_metrics), encoding="utf-8")
        result = validate_baseline_resume(
            metrics_path=metrics_path,
            predictions_path=predictions_path,
            expected=_expectation(),
        )
        assert not result.valid
        assert any(needle in r for r in result.reasons)
        metrics_path, predictions_path = _write_valid_artifacts(tmp_path)

    metrics_path, predictions_path = _write_valid_artifacts(tmp_path, sample_ids=("s1", "s3"))
    assert not validate_baseline_resume(
        metrics_path=metrics_path,
        predictions_path=predictions_path,
        expected=_expectation(),
    ).valid

    metrics_path, _ = _write_valid_artifacts(tmp_path)
    assert not validate_baseline_resume(
        metrics_path=metrics_path,
        predictions_path=tmp_path / "missing.jsonl",
        expected=_expectation(),
    ).valid
