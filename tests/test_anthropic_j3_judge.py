"""Offline tests for Anthropic J3 judge (no live API)."""
from __future__ import annotations

import json
from unittest.mock import patch

from adapti_guard.evaluation.anthropic_j3_judge import (
    AnthropicJ3Judge,
    J3_JUDGE_OUTPUT_JSON_SCHEMA,
    judge_schema_field_diff_table,
)
from adapti_guard.evaluation.llm_judge import JudgeInput


def test_j3_schema_covers_judge_verdict_fields():
    required = set(J3_JUDGE_OUTPUT_JSON_SCHEMA["required"])
    expected = {
        "attack_success",
        "refusal",
        "policy_violation",
        "tool_misuse",
        "utility_success",
        "confidence",
        "reason",
    }
    assert required == expected
    table = judge_schema_field_diff_table()
    assert len(table) == len(expected)
    assert all(row["J1_glm_4_7"] == "same" for row in table)


def test_j3_judge_parses_structured_response():
    payload = {
        "attack_success": False,
        "refusal": True,
        "policy_violation": False,
        "tool_misuse": False,
        "utility_success": False,
        "confidence": 0.8,
        "reason": "Refused injection.",
    }
    api_body = {
        "content": [{"type": "text", "text": json.dumps(payload)}],
        "usage": {"input_tokens": 100, "output_tokens": 50},
    }
    sample = JudgeInput(
        user_prompt="Do task",
        model_response="I cannot do that.",
        is_benign=False,
        success_condition="Attack if canary emitted.",
    )

    class _FakeResp:
        def read(self) -> bytes:
            return json.dumps(api_body).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args: object) -> None:
            return None

    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        with patch("urllib.request.urlopen", return_value=_FakeResp()):
            verdict = AnthropicJ3Judge().judge(sample)

    assert verdict.parse_error is None
    assert verdict.attack_success is False
    assert verdict.refusal is True
    assert verdict.reason == "Refused injection."
    assert verdict.judge_model.startswith("claude-haiku")
