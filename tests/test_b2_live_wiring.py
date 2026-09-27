"""B2 canonical live path wiring (OFFLINE_MOCK only; no API)."""
import json
from pathlib import Path

from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeRunner
from adapti_guard.evaluation.b2_adaptive_contract import (
    B2_PROVENANCE_FIELDS,
    OUTCOME_BLOCKED_VERDICT,
    PROPOSED_LIVE_CONDITION_ID,
    assess_b2_live_readiness,
    finalize_b2_canonical_live_episode,
    is_b2_live_condition,
)
from adapti_guard.evaluation.attack_success import compute_real_metrics
from adapti_guard.evaluation.live_extension_wiring import run_live_condition
from adapti_guard.evaluation.llm_judge import JudgeInput, JudgeVerdict
from adapti_guard.experiments.defense_baselines import make_b1_rule_based


def _legacy_defense(**_kwargs):
    return DefenseAction.TOOL_RESTRICTION, {}


def _fixture_judge(_inp: JudgeInput) -> JudgeVerdict:
    return JudgeVerdict(
        attack_success=True,
        refusal=False,
        policy_violation=True,
        tool_misuse=False,
        utility_success=False,
        confidence=1.0,
        reason="fixture_judge",
        usage={"prompt_tokens": 0, "completion_tokens": 0},
        judge_model="fixture",
    )


def test_is_b2_live_condition_ids():
    assert is_b2_live_condition("COND-E2-ADAPTIVE-OFFLINE")
    assert is_b2_live_condition(PROPOSED_LIVE_CONDITION_ID)


def _block_all_b1(prompt: str, _context: str | None):
    return "A3", True, prompt


def test_case_a_run_live_blocked_no_judge(tmp_path: Path):
    result = run_live_condition(
        "COND-E2-ADAPTIVE-OFFLINE",
        run_id="b2-a",
        run_dir=tmp_path,
        execution_mode="OFFLINE_MOCK",
        injected_b1_defense=_block_all_b1,
    )
    raw = json.loads((tmp_path / "raw" / "episode_raw.json").read_text())
    b2 = raw["b2_evaluation"]
    assert b2["target_calls"] == 0
    assert b2["judge_calls"] == 0
    assert b2["eval_episode"]["attack_succeeded"] is False
    assert b2["eval_episode"]["metadata"]["outcome_source"] == OUTCOME_BLOCKED_VERDICT
    judge = json.loads((tmp_path / "raw" / "judge_raw.json").read_text())
    assert judge["execution_status"] == "NOT_RUN"
    derived = json.loads((tmp_path / "derived" / "metrics.json").read_text())
    assert derived["asr"] == 0.0
    assert result.status == "ok"


def test_case_b_multiturn_finalize_judge_once():
    calls = {"n": 0}

    def target(_h, _m):
        calls["n"] += 1
        return "ok"

    b1 = make_b1_rule_based(threshold=0.99)
    episode = AdaptiveEpisodeRunner(3).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=b1,
        target=target,
        seed=1,
    )
    assert len(episode.turns) == 3
    assert calls["n"] >= 1
    fin = finalize_b2_canonical_live_episode(
        episode,
        experiment_id="b2-b",
        condition_id=PROPOSED_LIVE_CONDITION_ID,
        target_model_id="mock-target",
        judge_model_id="mock-judge",
        judge_invoke=_fixture_judge,
    )
    assert fin["target_calls"] == calls["n"]
    assert fin["judge_calls"] == 1
    assert fin["eval_episode"].attack_succeeded is True


def test_case_c_mid_block_judge_on_final_executed():
    turn = {"i": 0}
    real_b1 = make_b1_rule_based()

    def selective(prompt: str, context: str | None):
        turn["i"] += 1
        if turn["i"] == 1:
            return "A0", False, prompt
        return real_b1(prompt, context)

    episode = AdaptiveEpisodeRunner(2).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=selective,
        target=lambda _h, _m: "first-only",
    )
    fin = finalize_b2_canonical_live_episode(
        episode,
        experiment_id="b2-c",
        condition_id="COND-E2-ADAPTIVE-OFFLINE",
        target_model_id="t",
        judge_model_id="j",
        judge_invoke=_fixture_judge,
    )
    assert fin["target_calls"] == 1
    assert fin["judge_calls"] == 1
    assert fin["eval_episode"].model_response == "first-only"


def test_case_d_max_three_turns_in_canonical_runner():
    episode = AdaptiveEpisodeRunner(3).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=make_b1_rule_based(threshold=0.99),
        target=lambda _h, _m: "r",
    )
    assert episode.n_turns == 3
    assert len(episode.turns) == 3


def test_case_e_f_run_live_with_injected_judge(tmp_path: Path):
    from adapti_guard.evaluation.target_model import MockTargetModel

    result = run_live_condition(
        PROPOSED_LIVE_CONDITION_ID,
        run_id="b2-ef",
        run_dir=tmp_path,
        execution_mode="OFFLINE_MOCK",
        injected_target=MockTargetModel(response="MOCK_ALLOW"),
        injected_judge=_fixture_judge,
        injected_b1_defense=make_b1_rule_based(threshold=0.99),
    )
    raw = json.loads((tmp_path / "raw" / "episode_raw.json").read_text())
    b2 = raw["b2_evaluation"]
    assert b2["judge_calls"] == 1
    assert b2["eval_episode"]["metadata"]["outcome_source"] == "judge_labeled"
    judge = json.loads((tmp_path / "raw" / "judge_raw.json").read_text())
    assert judge["status"] == "OK"
    assert result.status == "ok"


def test_case_g_provenance_fields_present():
    episode = AdaptiveEpisodeRunner(1).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=make_b1_rule_based(threshold=0.99),
        target=lambda _h, _m: "x",
    )
    fin = finalize_b2_canonical_live_episode(
        episode,
        experiment_id="b2-g",
        condition_id=PROPOSED_LIVE_CONDITION_ID,
        target_model_id="t",
        judge_model_id="j",
        judge_invoke=_fixture_judge,
    )
    for key in B2_PROVENANCE_FIELDS:
        assert key in fin["provenance"]


def test_case_metrics_compute_real_metrics_unchanged():
    episode = AdaptiveEpisodeRunner(1).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=make_b1_rule_based(),
    )
    fin = finalize_b2_canonical_live_episode(
        episode,
        experiment_id="b2-metrics",
        condition_id="COND-E2-ADAPTIVE-OFFLINE",
        target_model_id="t",
        judge_model_id="j",
        judge_invoke=None,
    )
    m2 = compute_real_metrics([fin["eval_episode"]])
    assert m2.asr == fin["metrics"].asr


def test_readiness_no_live_execution_wiring_blocker():
    r = assess_b2_live_readiness(auth_allowed_condition_ids=["LIVE-PRO-PI-BENIGN"])
    assert r["b2_canonical_live_wired"] is True
    assert "live_execution_not_wired_for_b2" not in r["live_ready_blockers"]
