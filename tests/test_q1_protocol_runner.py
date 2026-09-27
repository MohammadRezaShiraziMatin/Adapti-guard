from adapti_guard.evaluation.attack_success import EvalEpisode
from adapti_guard.evaluation.q1_protocol_runner import (
    Q1NetworkRetryBudget,
    build_blind_judge_input,
    classify_retry_allowed,
    mcnemar_pair_complete,
    q1_episode_judge_failed,
    validate_judge_blind_payload,
)


def _ep(**kwargs):
    base = {
        "id": "atk_1",
        "prompt": "p",
        "context": "",
        "category": "direct",
        "label": "attack",
        "defense_action": "allow",
        "blocked": False,
        "model_response": "r",
        "attack_succeeded": False,
        "utility_success": False,
        "judge_reason": "ok",
    }
    base.update(kwargs)
    return EvalEpisode(**base)


def test_timeout_counts_as_judge_failure():
    ep = _ep(judge_reason="timeout")
    assert q1_episode_judge_failed(ep) is True


def test_complete_pair_rule():
    ok_a = _ep(attack_succeeded=True)
    fail_b = _ep(judge_reason="judge_api_error")
    assert mcnemar_pair_complete(ok_a, ok_a) is True
    assert mcnemar_pair_complete(ok_a, fail_b) is False


def test_network_only_retry():
    assert classify_retry_allowed("network_error") is True
    assert classify_retry_allowed("judge_parse_error") is False
    budget = Q1NetworkRetryBudget(max_retries=1)
    assert budget.attempt("timeout") is True
    budget.record_retry()
    assert budget.attempt("timeout") is False


def test_judge_blind_to_arm():
    ji = build_blind_judge_input(user_prompt="u", model_response="r", success_condition="c")
    payload = ji.to_blind_payload()
    validate_judge_blind_payload(payload)
    try:
        validate_judge_blind_payload({**payload, "condition_id": "B2-ADAPTIVE-B3"})
    except ValueError:
        pass
    else:
        raise AssertionError("condition_id must be rejected")


def test_phase_preflight_model_aware_within_two_dollars():
    from adapti_guard.evaluation.q1_cost_preflight import estimate_q1_phase_preflight
    from adapti_guard.evaluation.q1_evaluation_contract import load_q1_contract

    report = estimate_q1_phase_preflight(load_q1_contract())
    assert report["estimator"] == "model_aware_panel_pricing"
    assert report["all_phases_within_cap"] is True
    assert report["cap_usd_per_phase"] == 2.0
    p1 = next(r for r in report["phases"] if r["phase_id"] == "P1_rq1_primary_j1_j2")
    p2 = next(r for r in report["phases"] if r["phase_id"] == "P2_rq1b_exploratory_j1")
    assert p1["j2_usd"] > 0
    assert p2["j2_usd"] == 0
    assert p1["worst_case_usd_estimate"] != p2["worst_case_usd_estimate"] or p1["j2_usd"] != p2["j2_usd"]
    for row in report["phases"]:
        assert row["within_cap"] is True
        assert row["worst_case_usd_estimate"] <= 2.0
        assert row["attacker_usd"] == 0
