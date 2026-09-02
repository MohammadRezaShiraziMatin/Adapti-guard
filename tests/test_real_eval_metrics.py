"""Tests for real-eval metrics aggregation and pilot provenance."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from src.adapti_guard.evaluation.attack_success import EvalEpisode, compute_real_metrics
from src.adapti_guard.evaluation.metrics import compute_metrics

ROOT = Path(__file__).resolve().parents[1]


def _attack_row(*, episode_id: int, attack_success: bool) -> dict:
    return {
        "episode_id": episode_id,
        "attack_present": True,
        "attack_success": attack_success,
        "legitimate_task": False,
        "legitimate_success": False,
        "security_score": 0.0 if attack_success else 1.0,
        "utility_score": 0.0,
        "defense_cost": 0.0,
        "reward": 0.0,
        "attack_family": "prompt_injection",
    }


def test_attack_only_metrics_return_none_for_benign_dependent():
    episodes = [
        _attack_row(episode_id=1, attack_success=False),
        _attack_row(episode_id=2, attack_success=False),
        _attack_row(episode_id=3, attack_success=True),
    ]
    metrics = compute_metrics(episodes)

    assert metrics["asr"] == pytest.approx(1 / 3)
    assert metrics["defense_rate"] == pytest.approx(2 / 3)
    assert metrics["recall"] == pytest.approx(2 / 3)
    assert metrics["utility"] is None
    assert metrics["fpr"] is None
    assert metrics["balanced_accuracy"] is None
    assert metrics["precision"] is None
    assert metrics["f1"] is None
    assert metrics["legitimate_episodes"] == 0.0


def test_mixed_attack_benign_metrics_unchanged():
    episodes = [
        {
            "episode_id": 1,
            "attack_present": True,
            "attack_success": True,
            "legitimate_task": False,
            "legitimate_success": False,
            "security_score": 0.0,
            "utility_score": 0.0,
            "defense_cost": 0.0,
            "reward": 0.0,
            "attack_family": "prompt_injection",
        },
        {
            "episode_id": 2,
            "attack_present": True,
            "attack_success": False,
            "legitimate_task": False,
            "legitimate_success": False,
            "security_score": 1.0,
            "utility_score": 0.0,
            "defense_cost": 0.0,
            "reward": 0.0,
            "attack_family": "prompt_injection",
        },
        {
            "episode_id": 3,
            "attack_present": False,
            "attack_success": False,
            "legitimate_task": True,
            "legitimate_success": True,
            "security_score": 1.0,
            "utility_score": 1.0,
            "defense_cost": 0.0,
            "reward": 0.0,
            "attack_family": "legitimate",
        },
        {
            "episode_id": 4,
            "attack_present": False,
            "attack_success": False,
            "legitimate_task": True,
            "legitimate_success": False,
            "security_score": 1.0,
            "utility_score": 0.0,
            "defense_cost": 0.0,
            "reward": 0.0,
            "attack_family": "legitimate",
        },
    ]
    metrics = compute_metrics(episodes)

    assert metrics["asr"] == 0.5
    assert metrics["utility"] == 0.5
    assert metrics["fpr"] == 0.5
    assert metrics["balanced_accuracy"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1"] == 0.5


def test_compute_real_metrics_uses_episode_latency_ms():
    episodes = [
        EvalEpisode(
            id="a",
            prompt="p",
            context="",
            category="prompt_injection",
            label="attack",
            defense_action="A0",
            blocked=False,
            model_response="ok",
            attack_succeeded=False,
            utility_success=False,
            judge_reason="ok",
            latency_ms=100.0,
            target_latency_ms=0.0,
            judge_latency_ms=0.0,
        ),
        EvalEpisode(
            id="b",
            prompt="p",
            context="",
            category="prompt_injection",
            label="attack",
            defense_action="A0",
            blocked=False,
            model_response="ok",
            attack_succeeded=False,
            utility_success=False,
            judge_reason="ok",
            latency_ms=200.0,
            target_latency_ms=0.0,
            judge_latency_ms=0.0,
        ),
        EvalEpisode(
            id="c",
            prompt="p",
            context="",
            category="prompt_injection",
            label="attack",
            defense_action="A0",
            blocked=False,
            model_response="ok",
            attack_succeeded=True,
            utility_success=False,
            judge_reason="fail",
            latency_ms=300.0,
            target_latency_ms=50.0,
            judge_latency_ms=10.0,
        ),
    ]
    metrics = compute_real_metrics(episodes)

    assert metrics.latency_ms_mean == 200.0
    assert metrics.latency_ms_p95 == 200.0
    assert metrics.raw["target_latency_ms_mean"] == 50.0 / 3
    assert metrics.raw["judge_latency_ms_mean"] == 10.0 / 3
    assert metrics.utility is None
    assert metrics.fpr is None


def test_pilot_build_row_persists_judge_provenance():
    spec = importlib.util.spec_from_file_location(
        "phase2_7_pilot_run",
        ROOT / "experiments" / "PHASE2_7_PILOT" / "run.py",
    )
    pilot_run = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(pilot_run)

    ep = EvalEpisode(
        id="sample-1",
        prompt="attack prompt",
        context="",
        category="prompt_injection",
        label="attack",
        defense_action="A0",
        blocked=False,
        model_response="model output",
        attack_succeeded=False,
        utility_success=False,
        judge_reason="refused",
        latency_ms=42.0,
        metadata={
            "judge_raw": '{"attack_success": false, "reason": "refused"}',
            "judge_model": "anthropic/claude-sonnet-4",
            "cache_hit": True,
        },
    )
    row = pilot_run.build_row(ep, baseline="B0", model_id="openai/gpt-4o-mini", git="abc123")

    assert row["judge_raw"] == '{"attack_success": false, "reason": "refused"}'
    assert row["judge_model"] == "anthropic/claude-sonnet-4"
    assert row["cache_hit"] is True
    assert row["latency_ms"] == 42.0
    assert row["target_latency_ms"] == 0.0
