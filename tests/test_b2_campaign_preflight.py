"""B2 campaign protocol (offline; no API)."""
from pathlib import Path

import pytest

from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeRunner
from adapti_guard.evaluation.b2_campaign_protocol import (
    B2_COMPARABLE_TO_B1_PI,
    BUDGET_MAX_REQUESTS_SCOPE,
    CAMPAIGN_SIZE_TBD,
    N_EPISODES_RUNTIME_ENFORCED,
    assess_b2_campaign_preflight,
    authorization_consistency_state,
    b2_episode_request_budget_worst,
    campaign_worst_case_requests,
    episode_accounting_invariant_ok,
    expand_campaign_seeds,
    inspect_authorization_budget_semantics,
    max_campaign_episodes_under_request_cap,
    plan_b2_campaign_run_id,
    plan_campaign_batches,
)
from adapti_guard.evaluation.live_extension_wiring import load_authorization_yaml
from adapti_guard.evaluation.live_extension_wiring import run_live_condition

PILOT_METRICS = Path(
    "experiments/real_llm_eval/P1_MECHANISM_L1/"
    "LIVE-PRO-PI-B2-EVAL-20260924-182806-8aac6be3/derived/metrics.json"
)
PILOT_HASH = "93a0a5e2765981e954d5846849daea476fe4802e80eeee031cb443e79f7eddc9"


def _b2_preflight_auth() -> dict:
    """Repo YAML stays BLOCKED; preflight unit tests inject B2 condition allowance."""
    auth = dict(load_authorization_yaml())
    auth["allowed_condition_ids"] = ["LIVE-PRO-PI-B2-ADAPTIVE"]
    return auth


def _legacy_defense(**_kwargs):
    return DefenseAction.TOOL_RESTRICTION, {}


def test_campaign_size_tbd_when_unspecified():
    pf = assess_b2_campaign_preflight(campaign_id="TBD", campaign_size=None)
    assert pf.campaign_size is None
    assert CAMPAIGN_SIZE_TBD in pf.campaign_size_status or "authorization" in pf.campaign_size_status
    assert not pf.ready


def test_max_episodes_under_cap_is_two():
    assert max_campaign_episodes_under_request_cap(10) == 2
    assert b2_episode_request_budget_worst() == 4


def test_hypothetical_n2_preflight_passes_budget():
    pf = assess_b2_campaign_preflight(
        campaign_id="AUDIT-N2", campaign_size=2, auth_yaml=_b2_preflight_auth()
    )
    assert pf.budget["campaign_worst_requests"] == 8
    assert pf.blockers == ()
    assert len(pf.seeds) == 2
    assert pf.seeds[0] == 42


def test_n3_blocked_by_request_cap():
    pf = assess_b2_campaign_preflight(campaign_id="AUDIT-N3", campaign_size=3)
    assert any("max_requests" in b for b in pf.blockers)
    assert not pf.ready


def test_expand_campaign_seeds_deterministic():
    assert expand_campaign_seeds([42], 3) == (42, 43, 44)
    assert expand_campaign_seeds([42], 3) == expand_campaign_seeds([42], 3)


def test_distinct_run_ids_per_episode():
    ids = [plan_b2_campaign_run_id("C1", i, s) for i, s in enumerate((42, 43))]
    assert len(set(ids)) == 2


def test_case_e_same_seed_same_offline_trajectory():
    a = AdaptiveEpisodeRunner(3).run(
        attacker=AdaptiveAttacker(), defense=_legacy_defense, seed=42
    )
    b = AdaptiveEpisodeRunner(3).run(
        attacker=AdaptiveAttacker(), defense=_legacy_defense, seed=42
    )
    assert a.families_seen == b.families_seen
    assert [t.user_message for t in a.turns] == [t.user_message for t in b.turns]


def test_case_g_artifact_isolation_offline(tmp_path: Path):
    r1 = run_live_condition(
        "COND-E2-ADAPTIVE-OFFLINE",
        run_id=plan_b2_campaign_run_id("ISO", 0, 42),
        run_dir=tmp_path / "ep0",
        execution_mode="OFFLINE_MOCK",
    )
    r2 = run_live_condition(
        "COND-E2-ADAPTIVE-OFFLINE",
        run_id=plan_b2_campaign_run_id("ISO", 1, 43),
        run_dir=tmp_path / "ep1",
        execution_mode="OFFLINE_MOCK",
    )
    assert r1.run_id != r2.run_id
    assert (tmp_path / "ep0/raw/episode_raw.json").exists()
    assert (tmp_path / "ep1/raw/episode_raw.json").exists()


def test_accounting_invariant_cases():
    assert episode_accounting_invariant_ok(target_calls=0, judge_calls=0, requests_used=0)
    assert episode_accounting_invariant_ok(target_calls=1, judge_calls=1, requests_used=2)
    assert episode_accounting_invariant_ok(target_calls=3, judge_calls=1, requests_used=4)
    assert not episode_accounting_invariant_ok(target_calls=1, judge_calls=1, requests_used=1)


def test_budget_scope_per_invocation():
    sem = inspect_authorization_budget_semantics(load_authorization_yaml())
    assert sem["max_requests_scope"] == BUDGET_MAX_REQUESTS_SCOPE
    assert sem["n_episodes_runtime_enforced_in_b2_runner"] is N_EPISODES_RUNTIME_ENFORCED


def test_yaml_n_episodes_conflicts_single_invocation_cap():
    auth = load_authorization_yaml()
    assert int(auth["n_episodes"]) == 5
    assert authorization_consistency_state(auth) == "AUTHORIZED_BATCH_REQUIRED"
    assert plan_campaign_batches(5, max_episodes_per_batch=2) == (2, 2, 1)


def test_case_a_n1_preflight():
    pf = assess_b2_campaign_preflight(
        campaign_id="N1", campaign_size=1, auth_yaml=_b2_preflight_auth()
    )
    assert campaign_worst_case_requests(1) == 4
    assert pf.blockers == ()


def test_case_b_n2_preflight():
    pf = assess_b2_campaign_preflight(
        campaign_id="N2", campaign_size=2, auth_yaml=_b2_preflight_auth()
    )
    assert campaign_worst_case_requests(2) == 8
    assert pf.blockers == ()


def test_case_c_n3_blocked():
    pf = assess_b2_campaign_preflight(campaign_id="N3", campaign_size=3)
    assert campaign_worst_case_requests(3) == 12
    assert pf.blockers


def test_case_d_n5_blocked_single_invocation():
    pf = assess_b2_campaign_preflight(campaign_id="N5", campaign_size=5)
    assert campaign_worst_case_requests(5) == 20
    assert pf.blockers


def test_batch_plan_each_batch_within_cap():
    for batch_n in plan_campaign_batches(5, max_episodes_per_batch=2):
        assert campaign_worst_case_requests(batch_n) <= 10


def test_comparable_to_b1_false():
    assert B2_COMPARABLE_TO_B1_PI is False
    pf = assess_b2_campaign_preflight(campaign_id="X", campaign_size=2)
    assert pf.comparable_to_b1_pi is False


def test_pilot_metrics_hash_unchanged():
    assert PILOT_METRICS.is_file(), "committed B2 pilot metrics artifact missing"
    import hashlib

    h = hashlib.sha256(PILOT_METRICS.read_bytes()).hexdigest()
    assert h == PILOT_HASH
