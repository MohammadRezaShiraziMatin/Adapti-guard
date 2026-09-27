"""B2 budget ledger accounting (offline; no API)."""
from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeRunner
from adapti_guard.evaluation.b2_adaptive_contract import (
    b2_provider_estimate_usd,
    finalize_b2_canonical_live_episode,
)
from adapti_guard.evaluation.live_budget_gate import BudgetGatedTargetModel, BudgetLedger
from adapti_guard.evaluation.openrouter_panel_pricing import ModelPrice, OpenRouterPricingTable
from adapti_guard.evaluation.llm_judge import JudgeInput, JudgeVerdict
from adapti_guard.evaluation.target_model import GenerationRequest, GenerationResult, TargetModel
from adapti_guard.experiments.defense_baselines import make_b1_rule_based


def _or_pricing() -> OpenRouterPricingTable:
    return OpenRouterPricingTable(
        {"inner": ModelPrice(prompt_usd_per_token=0.000001, completion_usd_per_token=0.000002)}
    )


class _CountingInner(TargetModel):
    model_id = "inner"

    def __init__(self) -> None:
        self.calls = 0
        self.max_retries = 0

    def generate(self, request: GenerationRequest) -> GenerationResult:
        self.calls += 1
        return GenerationResult(
            text="ok",
            model_id="inner",
            latency_ms=1.0,
            usage={"prompt_tokens": 50, "completion_tokens": 25},
            raw={"http_attempts": 1},
        )


def _legacy_defense(**_kwargs):
    return DefenseAction.TOOL_RESTRICTION, {}


def test_case_a_blocked_only_zero_ledger():
    ledger = BudgetLedger(max_requests=10, max_usd=1.0)
    episode = AdaptiveEpisodeRunner(1).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=make_b1_rule_based(),
    )
    fin = finalize_b2_canonical_live_episode(
        episode,
        experiment_id="a",
        condition_id="COND-E2-ADAPTIVE-OFFLINE",
        target_model_id="t",
        judge_model_id="j",
        judge_invoke=None,
        ledger_spent_usd=ledger.spent_usd or None,
    )
    assert fin["target_calls"] == 0
    assert fin["judge_calls"] == 0
    assert ledger.requests_used == 0


def test_case_c_target_plus_judge_two_ledger_requests():
    ledger = BudgetLedger(max_requests=10, max_usd=1.0)
    inner_t = _CountingInner()
    inner_j = _CountingInner()
    pricing = _or_pricing()
    gated_t = BudgetGatedTargetModel(inner_t, ledger, provider="openrouter", pricing=pricing)
    gated_j = BudgetGatedTargetModel(inner_j, ledger, provider="openrouter", pricing=pricing)

    def judge_fn(_inp: JudgeInput) -> JudgeVerdict:
        gated_j.generate(GenerationRequest(prompt="judge", max_tokens=64, model_id="inner"))
        return JudgeVerdict(
            attack_success=False,
            refusal=True,
            policy_violation=False,
            tool_misuse=False,
            utility_success=False,
            confidence=1.0,
            reason="mock",
            usage={"prompt_tokens": 50, "completion_tokens": 25},
        )

    episode = AdaptiveEpisodeRunner(1).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=make_b1_rule_based(threshold=0.99),
            target=lambda _h, _m: gated_t.generate(
                GenerationRequest(prompt="x", max_tokens=64, model_id="inner")
            ).text,
    )
    fin = finalize_b2_canonical_live_episode(
        episode,
        experiment_id="c",
        condition_id="LIVE-PRO-PI-B2-ADAPTIVE",
        target_model_id="t",
        judge_model_id="j",
        judge_invoke=judge_fn,
        ledger_spent_usd=ledger.spent_usd or None,
    )
    assert fin["target_calls"] == 1
    assert fin["judge_calls"] == 1
    assert ledger.requests_used == 2
    assert inner_t.calls == 1
    assert inner_j.calls == 1


def test_case_d_worst_case_four_requests():
    ledger = BudgetLedger(max_requests=10, max_usd=1.0)
    inner_t = _CountingInner()
    inner_j = _CountingInner()
    pricing = _or_pricing()
    gated_t = BudgetGatedTargetModel(inner_t, ledger, provider="openrouter", pricing=pricing)
    gated_j = BudgetGatedTargetModel(inner_j, ledger, provider="openrouter", pricing=pricing)
    def allow_all(prompt: str, _context: str | None):
        return "A0", False, prompt

    def target(_h, _m):
        gated_t.generate(GenerationRequest(prompt="t", max_tokens=32, model_id="inner"))
        return "r"

    episode = AdaptiveEpisodeRunner(3).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=allow_all,
        target=target,
    )
    assert len(episode.turns) == 3
    assert sum(1 for t in episode.turns if t.target_called) == 3

    def judge_fn(_inp: JudgeInput) -> JudgeVerdict:
        gated_j.generate(GenerationRequest(prompt="j", max_tokens=32, model_id="inner"))
        return JudgeVerdict(
            attack_success=False,
            refusal=False,
            policy_violation=False,
            tool_misuse=False,
            utility_success=False,
            confidence=1.0,
            reason="j",
            usage={},
        )

    finalize_b2_canonical_live_episode(
        episode,
        experiment_id="d",
        condition_id="LIVE-PRO-PI-B2-ADAPTIVE",
        target_model_id="t",
        judge_model_id="j",
        judge_invoke=judge_fn,
        ledger_spent_usd=ledger.spent_usd or None,
    )
    assert ledger.requests_used == 4
    assert ledger.requests_used <= 10


def test_case_e_finalize_does_not_double_count_ledger():
    ledger = BudgetLedger(max_requests=10, max_usd=1.0)
    inner = _CountingInner()
    pricing = _or_pricing()
    gated = BudgetGatedTargetModel(inner, ledger, provider="openrouter", pricing=pricing)

    def judge_fn(_inp: JudgeInput) -> JudgeVerdict:
        gated.generate(GenerationRequest(prompt="once", max_tokens=32, model_id="inner"))
        return JudgeVerdict(
            attack_success=False,
            refusal=True,
            policy_violation=False,
            tool_misuse=False,
            utility_success=False,
            confidence=1.0,
            reason="x",
            usage={"prompt_tokens": 10, "completion_tokens": 5},
        )

    episode = AdaptiveEpisodeRunner(1).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=make_b1_rule_based(threshold=0.99),
        target=lambda _h, _m: "ok",
    )
    before = ledger.requests_used
    finalize_b2_canonical_live_episode(
        episode,
        experiment_id="e",
        condition_id="LIVE-PRO-PI-B2-ADAPTIVE",
        target_model_id="t",
        judge_model_id="j",
        judge_invoke=judge_fn,
        ledger_spent_usd=ledger.spent_usd or None,
    )
    assert ledger.requests_used == before + 1
    assert inner.calls == 1


def test_case_f_provider_estimate_from_usage():
    verdict = JudgeVerdict(
        attack_success=False,
        refusal=True,
        policy_violation=False,
        tool_misuse=False,
        utility_success=False,
        confidence=1.0,
        reason="x",
        usage={"prompt_tokens": 1000, "completion_tokens": 500},
    )
    est = b2_provider_estimate_usd(ledger_spent_usd=None, judge_verdict=verdict)
    assert est is not None and est > 0


def test_case_g_provider_estimate_unavailable():
    assert b2_provider_estimate_usd(ledger_spent_usd=None, judge_verdict=None) is None
    verdict = JudgeVerdict(
        attack_success=False,
        refusal=True,
        policy_violation=False,
        tool_misuse=False,
        utility_success=False,
        confidence=1.0,
        reason="x",
        usage={},
    )
    assert b2_provider_estimate_usd(ledger_spent_usd=None, judge_verdict=verdict) is None


def test_provider_estimate_prefers_ledger_spend():
    est = b2_provider_estimate_usd(
        ledger_spent_usd=0.42,
        judge_verdict=None,
    )
    assert est == 0.42
