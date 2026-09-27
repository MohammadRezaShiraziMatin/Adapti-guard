"""B2 batch campaign contract + aggregation (offline)."""
from adapti_guard.evaluation.b2_campaign_protocol import (
    BATCH_AUTHORIZATION_SCOPE,
    LIVE_BATCH_AUTHORIZATION_GRANTED,
    aggregate_b2_campaign,
    assess_b2_batch_campaign_preflight,
    build_b2_campaign_batch_plan,
    campaign_episode_artifact_dir,
    campaign_worst_case_requests,
    canonical_campaign_id,
    expand_campaign_seeds,
    plan_batch_id,
    plan_b2_campaign_run_id,
)


def test_campaign_id_stable():
    assert canonical_campaign_id("X") == "LIVE-PRO-PI-B2-CAMPAIGN-X"


def test_seed_mapping_42_to_46():
    assert expand_campaign_seeds([42], 5) == (42, 43, 44, 45, 46)


def test_batch_plan_2_2_1_partition():
    plan = build_b2_campaign_batch_plan("AUDIT5", total_episodes=5)
    assert plan.batch_sizes == (2, 2, 1)
    assert plan.seeds == (42, 43, 44, 45, 46)
    assert [e.episode_index for e in plan.episodes] == [0, 1, 2, 3, 4]
    assert plan.episodes[0].batch_id == "B01" and plan.episodes[0].seed == 42
    assert plan.episodes[1].batch_id == "B01" and plan.episodes[1].seed == 43
    assert plan.episodes[2].batch_id == "B02" and plan.episodes[2].seed == 44
    assert plan.episodes[3].batch_id == "B02" and plan.episodes[3].seed == 45
    assert plan.episodes[4].batch_id == "B03" and plan.episodes[4].seed == 46
    assert len({e.run_id for e in plan.episodes}) == 5


def test_batch_worst_requests_8_8_4():
    plan = build_b2_campaign_batch_plan("W", total_episodes=5)
    assert [b.worst_case_requests for b in plan.batches] == [8, 8, 4]
    assert plan.campaign_worst_requests_total == 20
    assert plan.batch_plan_status == "BATCH_PLAN_FEASIBLE_PER_INVOCATION"
    assert not plan.single_invocation_feasible


def test_batch_preflight_scenario_e():
    pf = assess_b2_batch_campaign_preflight("E", total_episodes=5)
    assert pf["batch_plan_status"] == "BATCH_PLAN_FEASIBLE_PER_INVOCATION"
    assert pf["per_batch_worst_requests"] == [8, 8, 4]
    assert pf["campaign_total_worst_requests"] == 20
    assert pf["api_calls"] == 0
    assert pf["live_batch_authorization_granted"] is LIVE_BATCH_AUTHORIZATION_GRANTED


def test_artifact_path_isolation():
    p0 = campaign_episode_artifact_dir(
        output_root="experiments/real_llm_eval/P1_MECHANISM_L1",
        campaign_slug="C",
        batch_id="B01",
        run_id=plan_b2_campaign_run_id("C", 0, 42),
    )
    p1 = campaign_episode_artifact_dir(
        output_root="experiments/real_llm_eval/P1_MECHANISM_L1",
        campaign_slug="C",
        batch_id="B02",
        run_id=plan_b2_campaign_run_id("C", 2, 44),
    )
    assert p0 != p1
    assert "batch-B01" in p0 and "batch-B02" in p1


def _ep(idx: int, seed: int, ok: bool, tgt: int, jdg: int, req: int, usd: float):
    return {
        "episode_index": idx,
        "seed": seed,
        "run_id": plan_b2_campaign_run_id("AGG", idx, seed),
        "attack_succeeded": ok,
        "target_calls": tgt,
        "judge_calls": jdg,
        "requests_used": req,
        "spent_usd": usd,
        "blocked": tgt == 0,
    }


def test_aggregate_five_episodes_no_double_count():
    plan = build_b2_campaign_batch_plan("AGG", total_episodes=5)
    batches = []
    offset = 0
    for b in plan.batches:
        eps = [
            _ep(
                plan.episodes[offset + i].episode_index,
                plan.episodes[offset + i].seed,
                ok=(i == 0),
                tgt=1,
                jdg=1,
                req=2,
                usd=0.0001,
            )
            for i in range(b.expected_episode_count)
        ]
        inv_req = sum(e["requests_used"] for e in eps)
        inv_usd = sum(e["spent_usd"] for e in eps)
        batches.append(
            {
                "batch_id": b.batch_id,
                "episode_indices": b.episode_indices,
                "expected_episode_count": b.expected_episode_count,
                "episodes": eps,
                "invocation_requests_used": inv_req,
                "invocation_spent_usd": inv_usd,
            }
        )
        offset += b.expected_episode_count

    agg = aggregate_b2_campaign(
        campaign_id=plan.campaign_id,
        expected_episodes=5,
        batch_results=batches,
    )
    assert agg["completed_episodes"] == 5
    assert agg["campaign_complete"] is True
    assert agg["total_requests"] == 10  # 5 episodes × 2 each in fixture
    assert agg["missing_episodes"] == 0
    assert agg["episode_successes"] == 3  # one success per batch in fixture
    assert agg["comparable"] is False
    assert agg["success_semantics"] == "final_state_success"


def test_partial_campaign_4_of_5():
    plan = build_b2_campaign_batch_plan("PART", total_episodes=5)
    batches = [
        {
            "batch_id": "B01",
            "episode_indices": (0, 1),
            "expected_episode_count": 2,
            "episodes": [_ep(0, 42, False, 1, 1, 2, 0.0), _ep(1, 43, False, 1, 1, 2, 0.0)],
            "invocation_requests_used": 4,
            "invocation_spent_usd": 0.0002,
        },
        {
            "batch_id": "B02",
            "episode_indices": (2, 3),
            "expected_episode_count": 2,
            "episodes": [_ep(2, 44, False, 1, 1, 2, 0.0), _ep(3, 45, False, 1, 1, 2, 0.0)],
            "invocation_requests_used": 4,
            "invocation_spent_usd": 0.0002,
        },
    ]
    agg = aggregate_b2_campaign(
        campaign_id=plan.campaign_id,
        expected_episodes=5,
        batch_results=batches,
    )
    assert agg["completed_episodes"] == 4
    assert agg["missing_episodes"] == 1
    assert agg["campaign_complete"] is False


def test_batch_ids_unique():
    plan = build_b2_campaign_batch_plan("U", total_episodes=5)
    ids = [b.batch_id for b in plan.batches]
    assert ids == [plan_batch_id(1), plan_batch_id(2), plan_batch_id(3)]
    assert len(set(ids)) == 3


def test_budget_constants():
    assert campaign_worst_case_requests(1) == 4
    assert campaign_worst_case_requests(2) == 8
    assert BATCH_AUTHORIZATION_SCOPE == "per_batch_run_live_condition_invocation"
