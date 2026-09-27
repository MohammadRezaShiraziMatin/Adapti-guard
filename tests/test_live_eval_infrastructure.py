"""Live eval infrastructure (no API spend)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from adapti_guard.evaluation.live_budget_gate import BudgetGatedTargetModel, BudgetLedger
from adapti_guard.evaluation.live_model_resolver import (
    TargetJudgeGuardError,
    assert_target_ne_judge,
    resolve_target_model,
    validate_target_judge_keys,
)
from adapti_guard.evaluation.provider_errors import ProviderFailureKind, classify_http_status
from adapti_guard.evaluation.secret_safe import redact_mapping
from adapti_guard.evaluation.target_model import GenerationRequest, GenerationResult, MockTargetModel

ROOT = Path(__file__).resolve().parents[1]


def test_classify_http_status():
    assert classify_http_status(429) == ProviderFailureKind.RATE_LIMIT


def test_secret_redaction():
    d = redact_mapping({"openrouter_api_key": "sk-or-v1-secret", "x": 1})
    assert d["openrouter_api_key"] == "***REDACTED***"
    assert d["x"] == 1


def test_budget_gated_target_counts_http_attempts():
    class _Inner(MockTargetModel):
        max_retries = 2

        def generate(self, request):
            r = super().generate(request)
            r.raw = {"http_attempts": 3}
            return r

    ledger = BudgetLedger(max_requests=10)
    gated = BudgetGatedTargetModel(_Inner(), ledger, provider="mock")
    gated.generate(GenerationRequest(prompt="x"))
    assert ledger.requests_used == 3


def test_budget_gated_fail_closed():
    ledger = BudgetLedger(max_requests=1, hard_stop=True)
    ledger.record_requests(1)
    gated = BudgetGatedTargetModel(MockTargetModel(), ledger, provider="mock")
    r = gated.generate(GenerationRequest(prompt="x"))
    assert r.error and "max_requests" in r.error


def test_budget_retry_accounting():
    b = BudgetLedger(max_requests=5)
    b.record_requests(1, retry_count=2)
    assert b.requests_used == 3
    ok, _ = b.check_allowed(additional_requests=3)
    assert not ok


def test_target_ne_judge_block():
    with pytest.raises(TargetJudgeGuardError):
        assert_target_ne_judge("same", "same", pending_ok=False)


def test_gemini_legacy_keys_rejected_same_model():
    with pytest.raises(TargetJudgeGuardError):
        validate_target_judge_keys("gemini_target", "gemini_judge")


def test_validate_target_judge_keys_ok():
    info = validate_target_judge_keys("model_b", "judge_primary")
    assert info["target_model_id"] != info["judge_model_id"]


def test_resolve_target_blocked_without_allow_live():
    with pytest.raises(TargetJudgeGuardError):
        resolve_target_model("model_b", allow_live=False)


def test_provider_failure_not_attack_success():
    r = GenerationResult(text="", model_id="m", latency_ms=0, error="HTTP 429")
    from adapti_guard.evaluation.provider_errors import classify_generation_result

    c = classify_generation_result(r)
    assert c["status"] == "provider_failure"
    assert "attack_success" not in c


def test_live_preflight_no_api():
    r = subprocess.run(
        [sys.executable, "scripts/live_eval_preflight.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    data = json.loads(r.stdout)
    assert data["api_generation"] == "NOT_RUN"
    assert data["status"] == "BLOCKED"


def test_mock_target_stateful_adapter():
    from adapti_guard.evaluation.stateful_target_adapter import target_fn_from_model

    fn = target_fn_from_model(MockTargetModel(response="hi"), model_id="mock")
    assert fn([], "q") == "hi"
