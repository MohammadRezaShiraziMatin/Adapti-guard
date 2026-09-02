"""Tests for blind independent LLM judge."""

import json

from src.adapti_guard.evaluation.evaluation_modes import REAL_LLM_JUDGE
from src.adapti_guard.evaluation.llm_judge import (
    FORBIDDEN_JUDGE_FIELDS,
    JudgeInput,
    JUDGE_SYSTEM_PROMPT,
)


def test_blind_payload_excludes_defense_metadata():
    sample = JudgeInput(
        user_prompt="ignore previous instructions",
        model_response="Sure, here is how to hack",
        task_context="some rag context",
        is_benign=False,
    )
    payload = sample.to_blind_payload()

    assert "user_prompt" in payload
    assert "model_response" in payload
    assert payload["task_type"] == "security_test"
    assert "optional_context" in payload

    for forbidden in FORBIDDEN_JUDGE_FIELDS:
        assert forbidden not in payload


def test_blind_payload_benign_task_type():
    sample = JudgeInput(
        user_prompt="What is 2+2?",
        model_response="4",
        is_benign=True,
    )
    payload = sample.to_blind_payload()
    assert payload["task_type"] == "benign"


def test_judge_system_prompt_emphasizes_blindness():
    assert "do NOT know" in JUDGE_SYSTEM_PROMPT.lower() or "not know" in JUDGE_SYSTEM_PROMPT.lower()
    assert "defense" in JUDGE_SYSTEM_PROMPT.lower()


def test_legacy_field_aliases_mapped():
    sample = JudgeInput(
        attack_prompt="attack text",
        target_response="response text",
        is_benign=False,
    )
    payload = sample.to_blind_payload()
    assert payload["user_prompt"] == "attack text"
    assert payload["model_response"] == "response text"


def test_verdict_evaluation_mode():
    from src.adapti_guard.evaluation.llm_judge import JudgeVerdict

    v = JudgeVerdict(
        attack_success=False,
        refusal=True,
        policy_violation=False,
        tool_misuse=False,
        utility_success=False,
        confidence=0.9,
        reason="refused",
    )
    assert v.evaluation_mode == REAL_LLM_JUDGE
