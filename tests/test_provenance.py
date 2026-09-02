"""Tests for scientific provenance validation."""

import pytest

from src.adapti_guard.evaluation.provenance import (
    ExperimentValidity,
    classify_real_llm_validity,
)


def test_classify_all_judge_errors_as_invalid():
    metrics = {
        "status": "COMPLETED",
        "n_samples": 5,
        "metrics": {
            "n_attack": 5,
            "n_benign": 0,
            "n_judge_errors": 5,
            "prompt_tokens_total": 0,
            "asr": 0.0,
        },
    }
    validity, issues = classify_real_llm_validity(metrics, min_samples=1)
    assert validity == ExperimentValidity.INVALID
    assert any("judge errors" in i for i in issues)


def test_classify_simulation_mode():
    metrics = {
        "status": "COMPLETED",
        "evaluation_mode": "HARMONIZED_SIMULATION",
        "n_samples": 100,
        "metrics": {"n_attack": 75, "n_benign": 25, "n_judge_errors": 0},
    }
    validity, _ = classify_real_llm_validity(metrics)
    assert validity == ExperimentValidity.SIMULATION


def test_classify_blocked():
    metrics = {"status": "BLOCKED", "reason": "no api key"}
    validity, issues = classify_real_llm_validity(metrics)
    assert validity == ExperimentValidity.BLOCKED
    assert issues


def test_classify_valid_real_llm():
    metrics = {
        "status": "COMPLETED",
        "evaluation_mode": "real_llm_judge",
        "n_samples": 100,
        "metrics": {
            "n_attack": 75,
            "n_benign": 25,
            "n_judge_errors": 2,
            "prompt_tokens_total": 50000,
            "asr": 0.12,
        },
    }
    validity, issues = classify_real_llm_validity(metrics, min_samples=50)
    assert validity == ExperimentValidity.VALID
    assert not issues
