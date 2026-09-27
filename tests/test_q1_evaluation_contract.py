from adapti_guard.evaluation.b2_adaptive_contract import LIVE_WIRING_MAX_TURNS
from adapti_guard.evaluation.q1_evaluation_contract import (
    PRIMARY_CAUSAL_EPISODES,
    VNEXT_DATASET_SHA,
    VNEXT_MODELS_YAML_SHA,
    validate_q1_evaluation_contract,
)


def test_q1_contract_offline_validation():
    report = validate_q1_evaluation_contract(repo_root=".")
    assert report["execution_gate"] == "BLOCKED"
    assert report["p0_freeze_ready"] is True
    assert report["phase_cost_preflight"]["estimator"] == "model_aware_panel_pricing"
    assert report["dataset_sha256"] == VNEXT_DATASET_SHA
    assert report["models_yaml_sha256"] == VNEXT_MODELS_YAML_SHA
    assert report["derived_attack_episodes"] == 61 * 4 * 3
    assert report["primary_causal_episodes"] == PRIMARY_CAUSAL_EPISODES
    assert report["attack_episodes_declared"] == 732
    assert float(report["budget_cap_usd"]) == 2.0
    assert report["j2_subset_manifest_sha256"] is not None
    assert report["phase_cost_preflight"]["all_phases_within_cap"] is True
    assert not report["panel_keys_pending_verification"]
    assert LIVE_WIRING_MAX_TURNS == 3
