"""Q1 P1 schedule + panel-priced budget gate (no live API)."""
from __future__ import annotations

import pytest

from adapti_guard.evaluation.live_budget_gate import (
    BudgetGatedTargetModel,
    BudgetLedger,
    estimate_request_cost_usd,
)
from adapti_guard.evaluation.openrouter_panel_pricing import (
    ModelPrice,
    OpenRouterPricingTable,
    OpenRouterPricingError,
    charge_usd_for_result,
    load_openrouter_pricing_table,
)
from adapti_guard.evaluation.q1_cost_preflight import estimate_q1_phase_preflight
from adapti_guard.evaluation.q1_evaluation_contract import load_q1_contract
from adapti_guard.evaluation.q1_p1_episode_schedule import (
    build_round_robin_attack_target_order,
    group_a0_b3_pairs,
    pair_boundary_stop_ok,
)
from adapti_guard.evaluation.q1_p1_live_runner import build_episode_plans
from adapti_guard.evaluation.target_model import GenerationRequest, GenerationResult, TargetModel


class _Inner(TargetModel):
    model_id = "test/model-a"

    def __init__(self) -> None:
        self.max_retries = 0
        self.calls = 0

    def generate(self, request: GenerationRequest) -> GenerationResult:
        self.calls += 1
        return GenerationResult(
            text="ok",
            model_id=request.model_id or self.model_id,
            latency_ms=1.0,
            usage={"prompt_tokens": 1000, "completion_tokens": 50, "cost": 0.0025},
            raw={"http_attempts": 1, "cost": 0.0025},
        )


def _cheap_table() -> OpenRouterPricingTable:
    return OpenRouterPricingTable(
        {
            "test/model-a": ModelPrice(0.000001, 0.000002),
        }
    )


def test_panel_pricing_loads():
    table = load_openrouter_pricing_table("configs/models_q1_eval_panel.yaml")
    assert table.price_for_model("qwen/qwen3-30b-a3b") is not None


def test_missing_model_fail_closed():
    table = _cheap_table()
    with pytest.raises(OpenRouterPricingError):
        table.require_price("missing/model")


def test_prefer_openrouter_reported_cost():
    table = _cheap_table()
    req = GenerationRequest(prompt="hello", max_tokens=32, model_id="test/model-a")
    result = GenerationResult(
        text="x",
        model_id="test/model-a",
        latency_ms=1.0,
        usage={"prompt_tokens": 10, "completion_tokens": 10, "cost": 0.99},
        raw={"cost": 0.99},
    )
    assert charge_usd_for_result(result, req, model_id="test/model-a", pricing=table) == 0.99


def test_gate_uses_panel_not_generic():
    ledger = BudgetLedger(max_usd=1.0, hard_stop=True)
    gated = BudgetGatedTargetModel(
        _Inner(), ledger, provider="openrouter", pricing=_cheap_table()
    )
    req = GenerationRequest(prompt="hello world", max_tokens=64, model_id="test/model-a")
    est = estimate_request_cost_usd(req, provider="openrouter", pricing=_cheap_table(), model_id="test/model-a")
    assert est is not None
    r = gated.generate(req)
    assert not r.error
    assert ledger.spent_usd == 0.0025


def test_round_robin_interleave_targets():
    targets = ["t0", "t1", "t2", "t3"]
    attacks = ["a0", "a1"]
    order = build_round_robin_attack_target_order(targets, attacks)
    assert order[:4] == [("a0", "t0"), ("a0", "t1"), ("a0", "t2"), ("a0", "t3")]
    assert order[4:8] == [("a1", "t0"), ("a1", "t1"), ("a1", "t2"), ("a1", "t3")]


def test_plans_a0_b3_back_to_back():
    plans = build_episode_plans()
    assert len(plans) == 488
    for i in range(0, len(plans), 2):
        a, b = plans[i], plans[i + 1]
        assert a.defense_arm == "A0" and b.defense_arm == "B3"
        assert a.attack_id == b.attack_id and a.target_model_id == b.target_model_id


def test_pair_boundary_stop():
    rows = [
        {"episode_index": 0, "defense_arm": "A0", "attack_id": "x", "target_model_id": "t"},
        {"episode_index": 1, "defense_arm": "B3", "attack_id": "x", "target_model_id": "t"},
    ]
    group_a0_b3_pairs(rows)
    assert pair_boundary_stop_ok(2)
    assert not pair_boundary_stop_ok(1)


def test_p1_preflight_dry_worst_case_under_cap():
    contract = load_q1_contract()
    report = estimate_q1_phase_preflight(contract)
    p1 = next(r for r in report["phases"] if r["phase_id"] == "P1_rq1_primary_j1_j2")
    assert p1["within_cap"] and p1["cap_usd"] == 2.0
    print("P1 worst_case_usd_estimate", p1["worst_case_usd_estimate"])
