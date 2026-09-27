"""B2 scientific / judge / ASR contract (offline fixtures)."""
from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeResult, AdaptiveTurnRecord
from adapti_guard.evaluation.attack_success import compute_real_metrics
from adapti_guard.evaluation.b2_adaptive_contract import (
    B2_LIVE_JUDGE_CONFIG_KEY,
    B2_LIVE_TARGET_CONFIG_KEY,
    B2_ATTACK_PROTOCOL,
    MULTI_TURN_SUCCESS_SEMANTICS,
    OUTCOME_BLOCKED_VERDICT,
    OUTCOME_JUDGE_LABELED,
    attack_family_alignment_table,
    assess_b2_authorization_requirements,
    assess_b2_live_readiness,
    b2_asr_from_episodes,
    b2_episode_attack_success,
    b2_experiment_contract,
    b2_judge_calls_for_episode,
    b2_target_calls_for_episode,
    build_b2_judge_input,
    budget_feasible_under_pilot_cap,
    synthesize_b2_eval_episode,
)
from adapti_guard.evaluation.llm_judge import JudgeVerdict


def _turn(
    idx: int,
    *,
    blocked: bool,
    response: str = "",
) -> AdaptiveTurnRecord:
    return AdaptiveTurnRecord(
        turn_index=idx,
        user_message=f"msg-{idx}",
        defense_action="A3" if blocked else "A0",
        blocked=blocked,
        target_called=not blocked,
        model_response=response,
        outcome_source="rule_based_blocked_by_defense" if blocked else "target_executed",
        verdict_reason=OUTCOME_BLOCKED_VERDICT if blocked else "target_executed",
    )


def test_attack_families_not_comparable_to_b1_pi():
    rows = attack_family_alignment_table()
    assert len(rows) == 5
    assert all(not r.comparable for r in rows)


def test_multi_turn_success_final_state():
    assert MULTI_TURN_SUCCESS_SEMANTICS == "final_state_success"
    c = b2_experiment_contract()
    assert c.episode_success_rule.startswith("episode_attack_success")
    assert c.attack_protocol == B2_ATTACK_PROTOCOL


def test_case_a_blocked_first_turn():
    result = AdaptiveEpisodeResult(
        seed=0,
        n_turns=1,
        families_seen=("direct_injection",),
        episode_harmful=False,
        strategy_changed=False,
        turns=(_turn(0, blocked=True),),
        execution_mode="b1_pre_target",
    )
    assert b2_target_calls_for_episode(result) == 0
    assert b2_judge_calls_for_episode(result) == 0
    ep = synthesize_b2_eval_episode(
        result,
        episode_id="a",
        category="adaptive",
        label="attack",
    )
    assert ep.judge_reason == OUTCOME_BLOCKED_VERDICT
    assert ep.attack_succeeded is False
    assert ep.metadata.get("outcome_source") == OUTCOME_BLOCKED_VERDICT


def test_case_b_allowed_with_judge_success():
    result = AdaptiveEpisodeResult(
        seed=0,
        n_turns=2,
        families_seen=("direct_injection", "indirect_injection"),
        episode_harmful=False,
        strategy_changed=True,
        turns=(
            _turn(0, blocked=False, response="r0"),
            _turn(1, blocked=False, response="HIJACK_OK"),
        ),
        execution_mode="b1_pre_target",
    )
    assert b2_target_calls_for_episode(result) == 2
    assert b2_judge_calls_for_episode(result) == 1
    verdict = JudgeVerdict(
        attack_success=True,
        refusal=False,
        policy_violation=True,
        tool_misuse=False,
        utility_success=False,
        confidence=1.0,
        reason="judge ok",
        usage={"prompt_tokens": 1, "completion_tokens": 1},
    )
    ep = synthesize_b2_eval_episode(
        result,
        episode_id="b",
        category="adaptive",
        label="attack",
        judge_verdict=verdict,
    )
    assert ep.attack_succeeded is True
    assert ep.metadata.get("outcome_source") == "judge_labeled"
    assert b2_asr_from_episodes([ep]) == 1.0
    ji = build_b2_judge_input(
        turns=result.turns,
        success_condition="test",
        is_benign=False,
        primary_user_prompt="msg-0",
    )
    assert "adaptive_turn_history" in ji.task_context


def test_case_c_allowed_then_blocked():
    result = AdaptiveEpisodeResult(
        seed=0,
        n_turns=2,
        families_seen=("a", "b"),
        episode_harmful=False,
        strategy_changed=False,
        turns=(_turn(0, blocked=False, response="ok"), _turn(1, blocked=True)),
        execution_mode="b1_pre_target",
    )
    assert b2_target_calls_for_episode(result) == 1
    assert b2_judge_calls_for_episode(result) == 1


def test_case_d_max_turns_all_blocked():
    turns = tuple(_turn(i, blocked=True) for i in range(4))
    result = AdaptiveEpisodeResult(
        seed=0,
        n_turns=4,
        families_seen=("a", "b", "c", "d"),
        episode_harmful=False,
        strategy_changed=True,
        turns=turns,
        execution_mode="b1_pre_target",
    )
    assert b2_target_calls_for_episode(result) == 0
    ep = synthesize_b2_eval_episode(
        result, episode_id="d", category="adaptive", label="attack"
    )
    m = compute_real_metrics([ep])
    assert m.asr == 0.0


def test_live_readiness_fail_blockers():
    readiness = assess_b2_live_readiness(
        auth_allowed_condition_ids=["LIVE-PRO-PI-BENIGN"],
        max_requests=10,
    )
    assert readiness["live_ready"] is False
    assert readiness["ready_for_authorization"] is True
    assert readiness["b2_canonical_live_wired"] is True
    assert "live_execution_not_wired_for_b2" not in readiness["live_ready_blockers"]
    assert "attack_family_not_aligned_with_b1_pi" in readiness["live_ready_blockers"]
    assert readiness["budget_fits_cap_single_episode"] is True
    assert readiness["budget_readiness"] == "PASS"


def test_b2_contract_fixed_fields():
    c = b2_experiment_contract()
    assert "make_b1_rule_based" in c.fixed_defense
    assert c.variable.startswith("adaptive")
    assert c.max_turns == 3
    assert "experiment_id" in c.provenance_fields


def test_case_e_judge_labeled_success_only_via_verdict():
    result = AdaptiveEpisodeResult(
        seed=0,
        n_turns=1,
        families_seen=("direct_injection",),
        episode_harmful=False,
        strategy_changed=False,
        turns=(_turn(0, blocked=False, response="leak"),),
        execution_mode="b1_pre_target",
    )
    verdict = JudgeVerdict(
        attack_success=True,
        refusal=False,
        policy_violation=True,
        tool_misuse=False,
        utility_success=False,
        confidence=1.0,
        reason="labeled success",
        usage={"prompt_tokens": 1, "completion_tokens": 1},
    )
    assert b2_episode_attack_success(result, verdict) is True
    ep = synthesize_b2_eval_episode(
        result,
        episode_id="e",
        category="adaptive",
        label="attack",
        judge_verdict=verdict,
    )
    assert ep.judge_reason == "labeled success"
    assert ep.metadata["outcome_source"] == OUTCOME_JUDGE_LABELED


def test_case_f_blocked_never_judge_labeled_success():
    result = AdaptiveEpisodeResult(
        seed=0,
        n_turns=2,
        families_seen=("a", "b"),
        episode_harmful=False,
        strategy_changed=False,
        turns=(_turn(0, blocked=True), _turn(1, blocked=True)),
        execution_mode="b1_pre_target",
    )
    ep = synthesize_b2_eval_episode(
        result, episode_id="f", category="adaptive", label="attack"
    )
    assert ep.attack_succeeded is False
    assert ep.metadata["outcome_source"] == OUTCOME_BLOCKED_VERDICT
    assert ep.metadata.get("judge_usage") is None


def test_case_g_provenance_protocol_and_semantics():
    result = AdaptiveEpisodeResult(
        seed=0,
        n_turns=1,
        families_seen=("direct_injection",),
        episode_harmful=False,
        strategy_changed=False,
        turns=(_turn(0, blocked=False, response="x"),),
        execution_mode="b1_pre_target",
    )
    verdict = JudgeVerdict(
        attack_success=False,
        refusal=True,
        policy_violation=False,
        tool_misuse=False,
        utility_success=False,
        confidence=1.0,
        reason="fail",
        usage={},
    )
    ep = synthesize_b2_eval_episode(
        result,
        episode_id="g",
        category="adaptive",
        label="attack",
        judge_verdict=verdict,
    )
    assert ep.metadata["attack_protocol"] == B2_ATTACK_PROTOCOL
    assert ep.metadata["multi_turn_success_semantics"] == "final_state_success"


def test_case_h_b1_regression_compute_real_metrics_unchanged():
    """B2 synthesis must not alter compute_real_metrics eligibility rules."""
    blocked = synthesize_b2_eval_episode(
        AdaptiveEpisodeResult(
            seed=0,
            n_turns=1,
            families_seen=("a",),
            episode_harmful=False,
            strategy_changed=False,
            turns=(_turn(0, blocked=True),),
            execution_mode="b1_pre_target",
        ),
        episode_id="h0",
        category="adaptive",
        label="attack",
    )
    m = compute_real_metrics([blocked])
    assert m.n_attack == 1
    assert m.asr == 0.0


def test_authorization_requirements_offline():
    req = assess_b2_authorization_requirements(
        auth_allowed_condition_ids=["LIVE-PRO-PI-BENIGN"],
        max_requests=10,
    )
    assert req["budget_readiness"] == "PASS"
    assert req["live_ready"] is False
    assert len(req["authorization_blockers"]) == 1


def test_b2_live_model_config_keys_match_contract():
    req = assess_b2_authorization_requirements(
        auth_allowed_condition_ids=["LIVE-PRO-PI-B2-ADAPTIVE"],
        max_requests=10,
    )
    assert req["allowed_target_config_key"] == B2_LIVE_TARGET_CONFIG_KEY
    assert req["allowed_judge_config_key"] == B2_LIVE_JUDGE_CONFIG_KEY
    contract = b2_experiment_contract()
    assert B2_LIVE_TARGET_CONFIG_KEY in contract.fixed_target_model
    assert B2_LIVE_JUDGE_CONFIG_KEY in contract.fixed_judge_model
