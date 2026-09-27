"""B2 batch runner + authorization gate (offline only; no API)."""
import hashlib
import json
from pathlib import Path

import pytest

from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.b2_campaign_protocol import (
    B2_BATCH_AUTHORIZATION_SCOPE,
    LIVE_BATCH_AUTHORIZATION_GRANTED,
    aggregate_b2_campaign,
    build_b2_batch_authorization,
    build_b2_campaign_batch_plan,
    campaign_worst_case_requests,
    evaluate_batch_execution_gates,
    preflight_batch_worst_case_ok,
)
from adapti_guard.evaluation.b2_batch_runner import run_live_b2_batch
from adapti_guard.evaluation.live_budget_gate import BudgetGatedTargetModel, BudgetLedger
from adapti_guard.evaluation.live_extension_wiring import (
    authorization_allows_live_spend,
    load_authorization_yaml,
    run_live_condition,
)
from adapti_guard.evaluation.llm_judge import JudgeInput, JudgeVerdict
from adapti_guard.evaluation.target_model import GenerationRequest, MockTargetModel
from adapti_guard.experiments.defense_baselines import make_b1_rule_based

PILOT_METRICS = Path(
    "experiments/real_llm_eval/P1_MECHANISM_L1/"
    "LIVE-PRO-PI-B2-EVAL-20260924-182806-8aac6be3/derived/metrics.json"
)
# B2 pilot metrics only; B0/B1 live_pro_eval_report.json are local pilot artifacts (not git-canonical).
B2_PILOT_METRICS_SHA256 = "93a0a5e2765981e954d5846849daea476fe4802e80eeee031cb443e79f7eddc9"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _block_all_b1(prompt: str, _context: str | None):
    return "A3", True, prompt


def _fixture_judge_factory(ledger: BudgetLedger, inner_judge_model):
    def _judge(_inp: JudgeInput) -> JudgeVerdict:
        inner_judge_model.generate(GenerationRequest(prompt="judge", max_tokens=32))
        return JudgeVerdict(
            attack_success=False,
            refusal=True,
            policy_violation=False,
            tool_misuse=False,
            utility_success=False,
            confidence=1.0,
            reason="fixture",
            usage={"prompt_tokens": 10, "completion_tokens": 5},
            judge_model="fixture",
        )

    return _judge


def _gated_offline_stack(ledger: BudgetLedger):
    inner_t = MockTargetModel(response="MOCK_ALLOW")
    inner_j = MockTargetModel(response="JUDGE")
    gated_t = BudgetGatedTargetModel(inner_t, ledger, provider="offline_mock")
    gated_j = BudgetGatedTargetModel(inner_j, ledger, provider="offline_mock")
    return gated_t, _fixture_judge_factory(ledger, gated_j)


@pytest.fixture
def tmp_campaign_root(tmp_path):
    return tmp_path / "campaign_root"


@pytest.fixture
def batch_auth_b01():
    plan = build_b2_campaign_batch_plan("OFFLINE-B01", total_episodes=5)
    return build_b2_batch_authorization(plan, "B01").with_test_injected_grant()


def test_batch_auth_default_blocks_without_injection(batch_auth_b01):
    plan = build_b2_campaign_batch_plan("OFFLINE-B01", total_episodes=5)
    auth = build_b2_batch_authorization(plan, "B01")
    ok, reason, status = evaluate_batch_execution_gates(auth, injected_batch_grant=False)
    assert not ok
    assert "batch authorization" in reason
    assert status["batch_authorization"] is False


def test_batch_auth_injected_allows_mock(batch_auth_b01):
    ok, reason, status = evaluate_batch_execution_gates(
        batch_auth_b01, injected_batch_grant=True, injected_campaign_grant=True
    )
    assert ok, reason
    assert status["batch_authorization"] is True


def test_campaign_auth_false_blocks(batch_auth_b01):
    ok, reason, status = evaluate_batch_execution_gates(
        batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=False,
    )
    assert not ok
    assert status["campaign_authorization"] is False


def test_condition_auth_false_blocks():
    plan = build_b2_campaign_batch_plan("OFFLINE-B01", total_episodes=5)
    auth = build_b2_batch_authorization(plan, "B01").with_test_injected_grant()
    yaml = load_authorization_yaml()
    bad = dict(yaml)
    bad["allowed_condition_ids"] = ["LIVE-PRO-PI-BENIGN"]
    ok, reason, status = evaluate_batch_execution_gates(
        auth,
        auth_yaml=bad,
        injected_batch_grant=True,
        injected_campaign_grant=True,
    )
    assert not ok
    assert status["condition_authorization"] is False


def _batch_gated_runner(condition_id, **kwargs):
    led = kwargs["injected_ledger"]
    gated_target, judge_fn = _gated_offline_stack(led)
    kwargs["injected_target"] = gated_target
    kwargs["injected_judge"] = judge_fn
    kwargs["injected_b1_defense"] = make_b1_rule_based(threshold=0.99)
    return run_live_condition(condition_id, **kwargs)


def test_all_auth_true_runs_mock_b01(tmp_campaign_root, batch_auth_b01):
    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        episode_runner=_batch_gated_runner,
    )
    assert result.status == "ok"
    assert result.batch_complete
    assert result.completed_episode_count == 2
    assert result.episode_results[0].seed == 42
    assert result.episode_results[1].seed == 43


def test_production_path_blocked_no_injection(tmp_campaign_root):
    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
    )
    assert result.status == "blocked"
    assert result.completed_episode_count == 0


def test_budget_worst_case_preflight():
    plan = build_b2_campaign_batch_plan("W", total_episodes=5)
    b01 = build_b2_batch_authorization(plan, "B01")
    ok, _, worst = preflight_batch_worst_case_ok(b01)
    assert ok and worst == 8
    assert campaign_worst_case_requests(1) == 4
    assert campaign_worst_case_requests(2) == 8
    assert campaign_worst_case_requests(3) == 12
    bad = b01.__class__(
        **{
            **b01.__dict__,
            "expected_episode_count": 3,
            "episode_indices": (0, 1, 2),
            "seeds": (42, 43, 44),
        }
    )
    ok3, reason, worst3 = preflight_batch_worst_case_ok(bad)
    assert not ok3
    assert worst3 == 12
    assert b01.max_requests == 10
    assert b01.max_usd == 1.0


def test_same_ledger_across_episodes(tmp_campaign_root, batch_auth_b01):
    ids = []

    def tracking_runner(*args, **kwargs):
        led = kwargs.get("injected_ledger")
        ids.append(id(led))
        gated_target, judge_fn = _gated_offline_stack(led)
        kwargs["injected_target"] = gated_target
        kwargs["injected_judge"] = judge_fn
        kwargs["injected_b1_defense"] = make_b1_rule_based(threshold=0.99)
        return run_live_condition(*args, **kwargs)

    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        episode_runner=tracking_runner,
    )
    assert result.status == "ok"
    assert len(ids) == 2
    assert ids[0] == ids[1]


def test_ledger_target_judge_counted(tmp_campaign_root, batch_auth_b01):
    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        episode_runner=_batch_gated_runner,
    )
    assert result.requests_used == result.target_calls + result.judge_calls
    assert result.requests_used >= 2


def test_batch_total_equals_sum_episode_deltas(tmp_campaign_root, batch_auth_b01):
    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        episode_runner=_batch_gated_runner,
    )
    assert sum(e.requests_used for e in result.episode_results) == result.requests_used


def test_unique_run_dirs(tmp_campaign_root, batch_auth_b01):
    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        injected_b1_defense=_block_all_b1,
    )
    dirs = [e.run_dir for e in result.episode_results]
    assert len(dirs) == len(set(dirs))
    assert "batch-B01" in dirs[0]


def test_no_overwrite_collision(tmp_campaign_root, batch_auth_b01):
    plan = build_b2_campaign_batch_plan("OFFLINE-B01", total_episodes=5)
    ep0 = next(e for e in plan.episodes if e.episode_index == 0)
    from adapti_guard.evaluation.b2_campaign_protocol import campaign_episode_artifact_dir

    existing = Path(
        campaign_episode_artifact_dir(
            output_root=str(tmp_campaign_root),
            campaign_slug="OFFLINE-B01",
            batch_id="B01",
            run_id=ep0.run_id,
        )
    )
    existing.mkdir(parents=True)
    (existing / "marker.txt").write_text("keep")
    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
    )
    assert result.status == "stopped"
    assert result.completed_episode_count == 0


def test_e01_only_after_e00_pass(tmp_campaign_root, batch_auth_b01):
    ledger = BudgetLedger(max_requests=10, max_usd=1.0)

    def fail_audit_runner(condition_id, **kwargs):
        kwargs["injected_ledger"] = ledger
        kwargs["injected_b1_defense"] = make_b1_rule_based(threshold=0.99)
        gated_target, judge_fn = _gated_offline_stack(ledger)
        kwargs["injected_target"] = gated_target
        kwargs["injected_judge"] = judge_fn
        res = run_live_condition(condition_id, **kwargs)
        run_dir = kwargs["run_dir"]
        raw = json.loads((run_dir / "raw" / "episode_raw.json").read_text())
        raw["seed"] = 999
        (run_dir / "raw" / "episode_raw.json").write_text(json.dumps(raw))
        return res

    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        episode_runner=fail_audit_runner,
    )
    assert result.status == "stopped"
    assert result.completed_episode_count == 0
    assert len(result.episode_results) == 1


def test_e00_runner_failure_stops(tmp_campaign_root, batch_auth_b01):
    def boom_runner(*_a, **_k):
        raise RuntimeError("E00 fail")

    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        episode_runner=boom_runner,
    )
    assert result.status == "stopped"
    assert result.completed_episode_count == 0


def test_ledger_mismatch_stops(tmp_campaign_root, batch_auth_b01):
    def ungated_runner(condition_id, **kwargs):
        kwargs.pop("injected_target", None)
        kwargs.pop("injected_judge", None)
        kwargs["injected_b1_defense"] = make_b1_rule_based(threshold=0.99)
        return run_live_condition(
            condition_id,
            injected_target=MockTargetModel(response="x"),
            injected_judge=lambda _i: JudgeVerdict(
                attack_success=False,
                refusal=True,
                policy_violation=False,
                tool_misuse=False,
                utility_success=False,
                confidence=1.0,
                reason="j",
                usage={},
            ),
            **kwargs,
        )

    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        episode_runner=ungated_runner,
    )
    assert result.status == "stopped"
    assert "ledger_mismatch" in (result.stop_reason or "")


def test_budget_overflow_stops(tmp_campaign_root, batch_auth_b01):
    def tight_ledger_runner(condition_id, **kwargs):
        kwargs["injected_ledger"].max_requests = 1
        return _batch_gated_runner(condition_id, **kwargs)

    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        episode_runner=tight_ledger_runner,
    )
    assert result.status == "stopped"


def test_provenance_fields(tmp_campaign_root, batch_auth_b01):
    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        injected_b1_defense=_block_all_b1,
    )
    for ep in result.episode_results:
        for key in (
            "campaign_id",
            "batch_id",
            "episode_index",
            "seed",
            "run_id",
            "condition_id",
            "protocol",
            "success_semantics",
            "authorization_scope",
            "budget_scope",
        ):
            assert key in ep.provenance
    assert result.authorization_scope == B2_BATCH_AUTHORIZATION_SCOPE


def test_aggregate_compatibility(tmp_campaign_root, batch_auth_b01):
    result = run_live_b2_batch(
        campaign_slug="OFFLINE-B01",
        batch_id="B01",
        output_root=tmp_campaign_root,
        batch_authorization=batch_auth_b01,
        injected_batch_grant=True,
        injected_campaign_grant=True,
        injected_b1_defense=_block_all_b1,
    )
    batch_dict = result.to_aggregate_batch_dict()
    agg = aggregate_b2_campaign(
        campaign_id=result.campaign_id,
        expected_episodes=5,
        batch_results=[batch_dict],
    )
    assert agg["completed_episodes"] == 2
    assert agg["campaign_complete"] is False


def test_synthetic_three_batches_aggregate_n5():
    plan = build_b2_campaign_batch_plan("SYN5", total_episodes=5)
    batches = []
    for b in plan.batches:
        eps = []
        for idx in b.episode_indices:
            seed = plan.seeds[idx]
            eps.append(
                {
                    "episode_index": idx,
                    "seed": seed,
                    "run_id": plan.episodes[idx].run_id,
                    "attack_succeeded": False,
                    "target_calls": 0,
                    "judge_calls": 0,
                    "requests_used": 0,
                    "spent_usd": 0.0,
                    "blocked": True,
                }
            )
        batches.append(
            {
                "batch_id": b.batch_id,
                "episode_indices": b.episode_indices,
                "expected_episode_count": b.expected_episode_count,
                "episodes": eps,
                "invocation_requests_used": 0,
                "invocation_spent_usd": 0.0,
            }
        )
    agg = aggregate_b2_campaign(
        campaign_id=plan.campaign_id,
        expected_episodes=5,
        batch_results=batches,
    )
    assert agg["campaign_complete"] is True
    assert agg["completed_episodes"] == 5


def test_historical_hashes_unchanged():
    assert PILOT_METRICS.is_file(), "committed B2 pilot metrics artifact missing"
    assert _sha256(PILOT_METRICS) == B2_PILOT_METRICS_SHA256


def test_real_campaign_yaml_allows_condition_but_batch_gate_blocks():
    ok_campaign, _ = authorization_allows_live_spend()
    assert ok_campaign
    plan = build_b2_campaign_batch_plan("LIVE-GATE", total_episodes=5)
    auth = build_b2_batch_authorization(plan, "B01")
    ok_batch, _, st = evaluate_batch_execution_gates(auth, injected_batch_grant=False)
    assert not ok_batch
    assert st["campaign_authorization"] is True
    assert st["condition_authorization"] is True
    assert st["batch_authorization"] is False
