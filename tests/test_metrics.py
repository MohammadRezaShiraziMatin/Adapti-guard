"""Metric denominator and consistency checks."""

from src.adapti_guard.evaluation.metrics import (
    compute_metrics,
    family_metrics,
    temporal_windows,
)


def test_asr_defense_rate_are_complements():
    episodes = [
        {
            "episode_id": 1,
            "attack_present": True,
            "attack_success": True,
            "legitimate_success": False,
            "security_score": 0.0,
            "utility_score": 0.0,
            "defense_cost": 0.0,
            "reward": 0.0,
            "attack_family": "direct_injection",
            "detection_score": 0.9,
        },
        {
            "episode_id": 2,
            "attack_present": True,
            "attack_success": False,
            "legitimate_success": False,
            "security_score": 1.0,
            "utility_score": 0.0,
            "defense_cost": 0.5,
            "reward": 0.4,
            "attack_family": "direct_injection",
            "detection_score": 0.9,
        },
    ]
    metrics = compute_metrics(episodes)
    assert metrics["asr"] == 0.5
    assert metrics["defense_rate"] == 0.5
    assert abs(metrics["asr"] + metrics["defense_rate"] - 1.0) < 1e-9


def test_utility_denominator_is_legitimate_only():
    episodes = [
        {
            "episode_id": 1,
            "attack_present": True,
            "attack_success": False,
            "legitimate_task": False,
            "legitimate_success": False,
            "security_score": 1.0,
            "utility_score": 0.0,
            "defense_cost": 0.1,
            "reward": 0.4,
            "attack_family": "direct_injection",
            "detection_score": 0.8,
        },
        {
            "episode_id": 2,
            "attack_present": False,
            "attack_success": False,
            "legitimate_task": True,
            "legitimate_success": True,
            "security_score": 1.0,
            "utility_score": 1.0,
            "defense_cost": 0.0,
            "reward": 0.9,
            "attack_family": "legitimate",
            "detection_score": 0.0,
        },
    ]
    metrics = compute_metrics(episodes)
    assert metrics["utility"] == 1.0
    assert metrics["legitimate_episodes"] == 1.0


def test_temporal_and_family_helpers():
    episodes = []
    for i in range(1, 101):
        episodes.append(
            {
                "episode_id": i,
                "attack_present": True,
                "attack_success": i % 2 == 0,
                "legitimate_success": False,
                "security_score": 0.0 if i % 2 == 0 else 1.0,
                "utility_score": 0.0,
                "defense_cost": 0.1,
                "reward": 0.4,
                "attack_family": [
                    "direct_injection",
                    "indirect_injection",
                    "context_manipulation",
                    "tool_output_injection",
                ][(i - 1) % 4],
                "detection_score": 0.9,
            }
        )
    windows = temporal_windows(episodes)
    assert set(windows) == {"1-25", "26-50", "51-75", "76-100"}
    families = family_metrics(episodes)
    assert len(families) == 4
