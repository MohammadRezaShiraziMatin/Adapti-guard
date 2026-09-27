"""USD hard-cap budget gate (no live API)."""
from __future__ import annotations

import pytest

from adapti_guard.evaluation.live_budget_gate import (
    PILOT_HARD_CAP_USD,
    BudgetGatedTargetModel,
    BudgetLedger,
    estimate_request_cost_usd,
)
from adapti_guard.evaluation.openrouter_panel_pricing import ModelPrice, OpenRouterPricingTable
from adapti_guard.evaluation.target_model import GenerationRequest, GenerationResult, TargetModel


class _CountingInner(TargetModel):
    model_id = "test/inner"

    def __init__(self, *, max_retries: int = 0) -> None:
        self.max_retries = max_retries
        self.calls = 0

    def generate(self, request: GenerationRequest) -> GenerationResult:
        self.calls += 1
        return GenerationResult(
            text="ok",
            model_id=self.model_id,
            latency_ms=1.0,
            usage={"prompt_tokens": 100, "completion_tokens": 100},
            raw={"http_attempts": 1},
        )


def _pricing() -> OpenRouterPricingTable:
    return OpenRouterPricingTable(
        {"test/inner": ModelPrice(prompt_usd_per_token=0.00001, completion_usd_per_token=0.00002)}
    )


def _ledger_cap_1() -> BudgetLedger:
    return BudgetLedger(max_usd=PILOT_HARD_CAP_USD, hard_stop=True)


def test_pilot_cap_constant():
    assert PILOT_HARD_CAP_USD == 1.0


def test_under_cap_allow():
    ledger = _ledger_cap_1()
    ok, _ = ledger.check_spend_allowed(0.10)
    assert ok and ledger.spent_usd == 0.0


def test_over_cap_block():
    ledger = _ledger_cap_1()
    ok, msg = ledger.check_spend_allowed(1.01)
    assert not ok and "max_usd" in msg


def test_exact_boundary_allow():
    ledger = _ledger_cap_1()
    ok, _ = ledger.check_spend_allowed(1.00)
    assert ok


def test_cumulative_block():
    ledger = _ledger_cap_1()
    ledger.record_spend_usd(0.95)
    ok, _ = ledger.check_spend_allowed(0.10)
    assert not ok


def test_unknown_cost_blocks():
    ledger = _ledger_cap_1()
    ok, msg = ledger.check_spend_allowed(None)
    assert not ok and "UNKNOWN" in msg


def test_gate_blocks_before_provider():
    inner = _CountingInner()
    ledger = _ledger_cap_1()
    ledger.record_spend_usd(0.95)
    gated = BudgetGatedTargetModel(inner, ledger, provider="openrouter", pricing=_pricing())
    req = GenerationRequest(prompt="x" * 400, max_tokens=500_000, model_id="test/inner")
    est = estimate_request_cost_usd(
        req, provider="openrouter", pricing=_pricing(), model_id="test/inner"
    )
    assert est is not None and ledger.spent_usd + est > 1.0
    r = gated.generate(req)
    assert r.error and inner.calls == 0


def test_retry_worst_case_blocks_before_provider():
    inner = _CountingInner(max_retries=2)
    ledger = _ledger_cap_1()
    ledger.record_spend_usd(0.50)
    gated = BudgetGatedTargetModel(inner, ledger, provider="openrouter", pricing=_pricing())
    req = GenerationRequest(prompt="x" * 400, max_tokens=400_000, model_id="test/inner")
    per = estimate_request_cost_usd(
        req, provider="openrouter", pricing=_pricing(), model_id="test/inner"
    )
    assert per is not None
    worst = per * 3
    assert ledger.spent_usd + worst > 1.0
    r = gated.generate(req)
    assert r.error and inner.calls == 0


def test_success_updates_ledger():
    inner = _CountingInner()
    ledger = _ledger_cap_1()
    gated = BudgetGatedTargetModel(inner, ledger, provider="openrouter", pricing=_pricing())
    req = GenerationRequest(prompt="hello world", max_tokens=64, model_id="test/inner")
    r = gated.generate(req)
    assert not r.error and inner.calls == 1
    assert ledger.spent_usd > 0


def test_unknown_prompt_blocks_without_provider():
    inner = _CountingInner()
    ledger = _ledger_cap_1()
    gated = BudgetGatedTargetModel(inner, ledger, provider="openrouter", pricing=_pricing())
    r = gated.generate(GenerationRequest(prompt="", max_tokens=512, model_id="test/inner"))
    assert r.error and "UNKNOWN" in r.error and inner.calls == 0


def test_blocked_request_does_not_increment_requests():
    inner = _CountingInner()
    ledger = BudgetLedger(max_usd=1.0, max_requests=0, hard_stop=True)
    gated = BudgetGatedTargetModel(inner, ledger, provider="openrouter", pricing=_pricing())
    r = gated.generate(GenerationRequest(prompt="test", max_tokens=32, model_id="test/inner"))
    assert r.error and ledger.requests_used == 0
