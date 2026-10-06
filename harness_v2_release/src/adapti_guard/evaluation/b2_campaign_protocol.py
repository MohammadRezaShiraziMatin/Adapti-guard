"""B2 controlled campaign protocol (offline preflight; no live execution)."""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal, Sequence

from adapti_guard.evaluation.b2_adaptive_contract import (
    LIVE_WIRING_MAX_TURNS,
    PROPOSED_LIVE_CONDITION_ID,
    b2_experiment_contract,
    is_b2_live_condition,
)

# Scientific metadata (immutable).
B2_COMPARABLE_TO_B1_PI = False
CAMPAIGN_SIZE_TBD = "authorization_required"

B2_EPISODE_REQUEST_BUDGET_WORST = LIVE_WIRING_MAX_TURNS + 1  # 3 target + 1 judge
B2_CAMPAIGN_RUN_ID_PREFIX = "LIVE-PRO-PI-B2-CAMPAIGN"

# Evidence: budget_ledger_from_authorization() is called once per run_live_condition().
BUDGET_MAX_REQUESTS_SCOPE = "per_run_live_condition_invocation"
# Evidence: n_episodes appears only in authorization schema validation, not B2 runner.
N_EPISODES_RUNTIME_ENFORCED = False


BATCH_AUTHORIZATION_SCOPE = "per_batch_run_live_condition_invocation"
# Explicit batch gate contract (distinct from per-episode / single-invocation campaign scope).
B2_BATCH_AUTHORIZATION_SCOPE = "per_batch_invocation"
DEFAULT_B2_BATCH_AUTH_YAML = Path("docs/research/live_b2_batch_authorization.yaml")
LIVE_BATCH_AUTHORIZATION_GRANTED = True  # gated by live_b2_batch_authorization.yaml + GRANTED contract


@dataclass(frozen=True)
class B2CampaignEpisodePlan:
    episode_index: int
    seed: int
    run_id: str
    run_id_template: str
    condition_id: str
    batch_id: str
    campaign_id: str


BatchAuthorizationStatus = Literal["BLOCKED", "GRANTED", "TEST_INJECTED_GRANTED"]


@dataclass(frozen=True)
class B2BatchAuthorization:
    """Explicit batch invocation authorization (separate from campaign YAML live spend)."""

    campaign_id: str
    batch_id: str
    condition_id: str
    episode_indices: tuple[int, ...]
    seeds: tuple[int, ...]
    expected_episode_count: int
    max_requests: int
    max_usd: float
    authorization_status: BatchAuthorizationStatus
    authorization_scope: str = B2_BATCH_AUTHORIZATION_SCOPE
    allowed_condition_ids: tuple[str, ...] = ()

    def with_test_injected_grant(self) -> B2BatchAuthorization:
        """Test-only grant; does not flip LIVE_BATCH_AUTHORIZATION_GRANTED."""
        return replace(self, authorization_status="TEST_INJECTED_GRANTED")


@dataclass(frozen=True)
class B2BatchContract:
    campaign_id: str
    batch_id: str
    episode_indices: tuple[int, ...]
    seeds: tuple[int, ...]
    expected_episode_count: int
    max_requests_per_invocation: int
    max_usd_per_invocation: float
    authorization_scope: str
    worst_case_requests: int


@dataclass(frozen=True)
class B2CampaignBatchPlan:
    campaign_id: str
    campaign_slug: str
    expected_episodes: int
    seeds: tuple[int, ...]
    batches: tuple[B2BatchContract, ...]
    episodes: tuple[B2CampaignEpisodePlan, ...]
    batch_sizes: tuple[int, ...]
    campaign_worst_requests_total: int
    single_invocation_feasible: bool
    batch_plan_status: str
    batch_authorization_required: bool
    live_batch_authorization_granted: bool


@dataclass(frozen=True)
class B2CampaignPreflight:
    ready: bool
    campaign_size: int | None
    campaign_size_status: str
    max_episodes_under_request_cap: int
    episode_request_budget_worst: int
    blockers: tuple[str, ...]
    seeds: tuple[int, ...]
    episode_plans: tuple[B2CampaignEpisodePlan, ...]
    comparable_to_b1_pi: bool
    budget: dict[str, Any]
    authorization: dict[str, Any]


def b2_episode_request_budget_worst() -> int:
    return B2_EPISODE_REQUEST_BUDGET_WORST


def inspect_authorization_budget_semantics(auth_yaml: dict[str, Any]) -> dict[str, Any]:
    """Documented scope from implementation (no inference beyond code paths)."""
    return {
        "max_requests": auth_yaml.get("max_requests"),
        "max_usd": auth_yaml.get("budget_ceiling"),
        "max_requests_scope": BUDGET_MAX_REQUESTS_SCOPE,
        "max_requests_scope_evidence": (
            "live_extension_wiring.run_live_condition → budget_ledger_from_authorization "
            "once per invocation"
        ),
        "n_episodes_yaml": auth_yaml.get("n_episodes"),
        "n_episodes_runtime_enforced_in_b2_runner": N_EPISODES_RUNTIME_ENFORCED,
        "n_episodes_semantics": (
            "authorization_yaml_schema_field_only; "
            "validate_phase7_live_authorization requires key present; "
            "not read by run_live_condition or b2_campaign_protocol execution"
        ),
        "batch_ledger_reset_in_repository": False,
        "batch_ledger_reset_evidence": (
            "run_live_b2_batch shares one BudgetLedger per batch invocation; "
            "run_live_condition alone still creates a fresh ledger unless injected_ledger is passed"
        ),
    }


def campaign_worst_case_requests(n_episodes: int) -> int:
    return n_episodes * b2_episode_request_budget_worst()


def plan_campaign_batches(total_episodes: int, *, max_episodes_per_batch: int) -> tuple[int, ...]:
    """Greedy batch split (planning only; no batch runner in repo)."""
    if total_episodes <= 0 or max_episodes_per_batch <= 0:
        return ()
    batches: list[int] = []
    remain = total_episodes
    while remain > 0:
        take = min(max_episodes_per_batch, remain)
        batches.append(take)
        remain -= take
    return tuple(batches)


def campaign_cost_preflight(
    *,
    n_target_calls: int,
    n_judge_calls: int,
    max_usd: float,
) -> dict[str, Any]:
    from adapti_guard.evaluation.live_b0_report import preflight_worst_case_usd

    ok, worst = preflight_worst_case_usd(
        n_target_calls=n_target_calls,
        n_judge_calls=n_judge_calls,
        max_usd=max_usd,
    )
    return {
        "cost_preflight_ok": ok,
        "worst_case_usd_estimate": worst,
        "cost_note": (
            "repository preflight_worst_case_usd (conservative per-call estimate); "
            "runtime actual from BudgetLedger.spent_usd"
        ),
    }


def campaign_scenario_fact_table(auth_yaml: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    max_req = int(auth_yaml.get("max_requests", 10))
    max_usd = float(auth_yaml.get("budget_ceiling", 1.0))
    per = b2_episode_request_budget_worst()
    max_n = max_campaign_episodes_under_request_cap(max_req)

    def _row(plan: str, episodes: int, batch_note: str) -> dict[str, Any]:
        worst = campaign_worst_case_requests(episodes)
        single_inv_ok = worst <= max_req
        cost = campaign_cost_preflight(
            n_target_calls=episodes * LIVE_WIRING_MAX_TURNS,
            n_judge_calls=episodes,
            max_usd=max_usd,
        )
        return {
            "plan": plan,
            "episodes": episodes,
            "worst_requests_single_invocation": worst,
            "current_budget_compatible_single_invocation": single_inv_ok,
            "batch_note": batch_note,
            "cost_preflight": cost,
        }

    batches_5 = plan_campaign_batches(5, max_episodes_per_batch=max_n)
    batch_inv_worsts = [campaign_worst_case_requests(b) for b in batches_5]
    batch_feasible_each = all(w <= max_req for w in batch_inv_worsts)

    return (
        _row("A", 2, "single run_live_condition invocation"),
        {
            "plan": "B",
            "episodes": 5,
            "worst_requests_single_invocation": 20,
            "current_budget_compatible_single_invocation": False,
            "batch_note": f"planned_batches={list(batches_5)} per_invocation_worsts={batch_inv_worsts}",
            "batch_each_invocation_within_max_requests": batch_feasible_each,
            "batch_semantics_in_repo": "each invocation fresh ledger; no cumulative campaign cap",
            "cost_preflight": campaign_cost_preflight(
                n_target_calls=5 * LIVE_WIRING_MAX_TURNS,
                n_judge_calls=5,
                max_usd=max_usd,
            ),
        },
        _row("C", 5, "single campaign requires 20 requests worst-case"),
    )


def authorization_consistency_state(auth_yaml: dict[str, Any]) -> str:
    """
    Evidence-based consistency (no automatic remediation).
    """
    max_req = int(auth_yaml.get("max_requests", 10))
    auth_n = auth_yaml.get("n_episodes")
    per = b2_episode_request_budget_worst()
    max_n = max_campaign_episodes_under_request_cap(max_req)

    if isinstance(auth_n, int) and auth_n * per > max_req:
        if auth_n <= max_n:
            return "AUTHORIZED_BUDGET_COMPATIBLE"
        batches = plan_campaign_batches(auth_n, max_episodes_per_batch=max_n)
        if batches and all(campaign_worst_case_requests(b) <= max_req for b in batches):
            return "AUTHORIZED_BATCH_REQUIRED"
        return "AUTHORIZATION_UPDATE_REQUIRED"
    return "AUTHORIZED_BUDGET_COMPATIBLE"


def max_campaign_episodes_under_request_cap(max_requests: int) -> int:
    per = b2_episode_request_budget_worst()
    return max_requests // per if per > 0 else 0


def expand_campaign_seeds(base_seeds: Sequence[int], campaign_size: int) -> tuple[int, ...]:
    """Deterministic seed list: use auth seeds, then consecutive integers."""
    if campaign_size <= 0:
        return ()
    if len(base_seeds) >= campaign_size:
        return tuple(int(s) for s in base_seeds[:campaign_size])
    out = [int(s) for s in base_seeds] if base_seeds else [42]
    cursor = out[-1]
    while len(out) < campaign_size:
        cursor += 1
        out.append(cursor)
    return tuple(out)


def canonical_campaign_id(campaign_slug: str) -> str:
    return f"{B2_CAMPAIGN_RUN_ID_PREFIX}-{campaign_slug}"


def plan_b2_campaign_run_id(campaign_slug: str, episode_index: int, seed: int) -> str:
    """Deterministic run_id (no timestamp); unique per episode."""
    return f"{B2_CAMPAIGN_RUN_ID_PREFIX}-{campaign_slug}-E{episode_index:02d}-S{seed}"


def plan_batch_id(batch_sequence: int) -> str:
    return f"B{batch_sequence:02d}"


def batch_authorization_yaml_path(batch_id: str) -> Path:
    """Per-batch authorization file (B01 legacy path supported)."""
    specific = Path(f"docs/research/live_b2_batch_{batch_id}_authorization.yaml")
    if specific.is_file():
        return specific
    if batch_id == "B01" and DEFAULT_B2_BATCH_AUTH_YAML.is_file():
        return DEFAULT_B2_BATCH_AUTH_YAML
    return specific


def load_b2_batch_authorization_yaml(
    path: Path | None = None,
    *,
    batch_id: str | None = None,
) -> dict[str, Any]:
    import yaml

    if path is not None:
        p = path
    elif batch_id is not None:
        p = batch_authorization_yaml_path(batch_id)
    else:
        p = DEFAULT_B2_BATCH_AUTH_YAML
    if not p.is_file():
        return {}
    return yaml.safe_load(p.read_text()) or {}


def batch_authorization_record_matches(
    batch_auth: B2BatchAuthorization,
    record: dict[str, Any],
) -> tuple[bool, str]:
    if not record.get("live_batch_authorization_granted"):
        return False, "yaml: live_batch_authorization_granted false"
    if str(record.get("authorization_status", "")).strip() != "GRANTED":
        return False, "yaml: authorization_status not GRANTED"
    if record.get("batch_id") != batch_auth.batch_id:
        return False, "yaml: batch_id mismatch"
    if record.get("campaign_id") != batch_auth.campaign_id:
        return False, "yaml: campaign_id mismatch"
    yaml_allowed = tuple(record.get("allowed_condition_ids") or ())
    if yaml_allowed:
        if tuple(batch_auth.allowed_condition_ids) != yaml_allowed:
            return False, "yaml: allowed_condition_ids mismatch"
    elif record.get("condition_id") != batch_auth.condition_id:
        return False, "yaml: condition_id mismatch"
    if tuple(record.get("episode_indices") or []) != tuple(batch_auth.episode_indices):
        return False, "yaml: episode_indices mismatch"
    if tuple(int(s) for s in (record.get("seeds") or [])) != tuple(batch_auth.seeds):
        return False, "yaml: seeds mismatch"
    if int(record.get("max_requests", -1)) != batch_auth.max_requests:
        return False, "yaml: max_requests mismatch"
    if float(record.get("max_usd", -1)) != batch_auth.max_usd:
        return False, "yaml: max_usd mismatch"
    return True, "ok"


def build_b2_batch_authorization_live_granted(
    plan: B2CampaignBatchPlan,
    batch_id: str,
    *,
    auth_yaml: dict[str, Any] | None = None,
    batch_yaml: dict[str, Any] | None = None,
) -> B2BatchAuthorization:
    record = (
        batch_yaml
        if batch_yaml is not None
        else load_b2_batch_authorization_yaml(batch_id=batch_id)
    )
    batch_auth = build_b2_batch_authorization(
        plan, batch_id, authorization_status="GRANTED", auth_yaml=auth_yaml
    )
    ok, reason = batch_authorization_record_matches(batch_auth, record)
    if not ok:
        raise ValueError(f"batch authorization record mismatch: {reason}")
    return batch_auth


def build_b2_batch_authorization(
    plan: B2CampaignBatchPlan,
    batch_id: str,
    *,
    authorization_status: BatchAuthorizationStatus = "BLOCKED",
    auth_yaml: dict[str, Any] | None = None,
) -> B2BatchAuthorization:
    from adapti_guard.evaluation.live_extension_wiring import load_authorization_yaml

    auth = auth_yaml if auth_yaml is not None else load_authorization_yaml()
    contract = next((b for b in plan.batches if b.batch_id == batch_id), None)
    if contract is None:
        raise ValueError(f"unknown batch_id={batch_id} for campaign {plan.campaign_id}")
    return B2BatchAuthorization(
        campaign_id=plan.campaign_id,
        batch_id=contract.batch_id,
        condition_id=PROPOSED_LIVE_CONDITION_ID,
        episode_indices=contract.episode_indices,
        seeds=contract.seeds,
        expected_episode_count=contract.expected_episode_count,
        max_requests=int(auth.get("max_requests", 10)),
        max_usd=float(auth.get("budget_ceiling", 1.0)),
        authorization_status=authorization_status,
    )


def preflight_batch_worst_case_ok(
    batch_auth: B2BatchAuthorization,
    *,
    episode_worst_requests: int | None = None,
) -> tuple[bool, str, int]:
    per = episode_worst_requests if episode_worst_requests is not None else b2_episode_request_budget_worst()
    worst = campaign_worst_case_requests(batch_auth.expected_episode_count)
    if worst > batch_auth.max_requests:
        return False, f"worst_case_requests={worst} > max_requests={batch_auth.max_requests}", worst
    if worst * 0.0 > batch_auth.max_usd:
        return False, "worst_case_cost exceeds max_usd", worst
    return True, "ok", worst


def evaluate_batch_execution_gates(
    batch_auth: B2BatchAuthorization,
    *,
    auth_yaml: dict[str, Any] | None = None,
    injected_batch_grant: bool = False,
    injected_campaign_grant: bool | None = None,
) -> tuple[bool, str, dict[str, Any]]:
    """
    Campaign + condition + batch gates. Production batch path requires LIVE_BATCH_AUTHORIZATION_GRANTED
    or explicit TEST_INJECTED_GRANTED on batch_auth when injected_batch_grant is True (tests only).
    """
    from adapti_guard.evaluation.live_extension_wiring import (
        authorization_allows_live_spend,
        load_authorization_yaml,
    )

    auth = auth_yaml if auth_yaml is not None else load_authorization_yaml()
    allowed = set(auth.get("allowed_condition_ids") or [])
    required_conditions = (
        batch_auth.allowed_condition_ids
        if batch_auth.allowed_condition_ids
        else (PROPOSED_LIVE_CONDITION_ID,)
    )
    condition_ok = all(cid in allowed for cid in required_conditions)
    status: dict[str, Any] = {
        "campaign_authorization": False,
        "condition_authorization": condition_ok,
        "required_condition_ids": list(required_conditions),
        "batch_authorization": False,
        "batch_authorization_scope": batch_auth.authorization_scope,
        "live_batch_authorization_granted_constant": LIVE_BATCH_AUTHORIZATION_GRANTED,
        "injected_batch_grant": injected_batch_grant,
    }

    for cid in required_conditions:
        if cid not in allowed:
            return False, f"authorization_failure: {cid} not in allowed_condition_ids", status
        if not is_b2_live_condition(cid):
            return False, f"authorization_failure: {cid} not registered as B2 live", status

    if injected_campaign_grant is not None:
        status["campaign_authorization"] = injected_campaign_grant
        if not injected_campaign_grant:
            return False, "authorization_failure: campaign authorization not granted", status
    else:
        ok, reason = authorization_allows_live_spend()
        status["campaign_authorization"] = ok
        if not ok:
            return False, reason, status

    batch_ok = False
    if batch_auth.authorization_status == "TEST_INJECTED_GRANTED" and injected_batch_grant:
        batch_ok = True
    elif batch_auth.authorization_status == "GRANTED":
        record = load_b2_batch_authorization_yaml(batch_id=batch_auth.batch_id)
        status["batch_authorization_yaml_id"] = record.get("authorization_id")
        if LIVE_BATCH_AUTHORIZATION_GRANTED:
            ok_rec, rec_reason = batch_authorization_record_matches(batch_auth, record)
            status["batch_yaml_match"] = ok_rec
            batch_ok = ok_rec
            if not ok_rec:
                status["batch_yaml_mismatch_reason"] = rec_reason
    status["batch_authorization"] = batch_ok
    if not batch_ok:
        return False, "authorization_failure: batch authorization not granted", status

    if batch_auth.campaign_id and batch_auth.batch_id:
        pass
    else:
        return False, "authorization_failure: incomplete batch authorization contract", status

    return True, "ok", status


def campaign_episode_artifact_dir(
    *,
    output_root: str,
    campaign_slug: str,
    batch_id: str,
    run_id: str,
) -> str:
    """Suggested layout (planning); run_live_condition still uses run_dir override."""
    cid = canonical_campaign_id(campaign_slug)
    return f"{output_root}/{cid}/batch-{batch_id}/{run_id}"


def build_b2_campaign_batch_plan(
    campaign_slug: str,
    *,
    total_episodes: int = 5,
    auth_yaml: dict[str, Any] | None = None,
) -> B2CampaignBatchPlan:
    from adapti_guard.evaluation.live_extension_wiring import load_authorization_yaml

    auth = auth_yaml if auth_yaml is not None else load_authorization_yaml()
    max_requests = int(auth.get("max_requests", 10))
    max_usd = float(auth.get("budget_ceiling", 1.0))
    max_per_batch = max_campaign_episodes_under_request_cap(max_requests)
    campaign_id = canonical_campaign_id(campaign_slug)
    base = [int(s) for s in (auth.get("seeds") or [])]
    seeds = expand_campaign_seeds(base, total_episodes)
    batch_sizes = plan_campaign_batches(total_episodes, max_episodes_per_batch=max_per_batch)

    batches: list[B2BatchContract] = []
    episodes: list[B2CampaignEpisodePlan] = []
    ep_cursor = 0
    for b_seq, b_count in enumerate(batch_sizes, start=1):
        batch_id = plan_batch_id(b_seq)
        indices = tuple(range(ep_cursor, ep_cursor + b_count))
        batch_seeds = tuple(seeds[i] for i in indices)
        batches.append(
            B2BatchContract(
                campaign_id=campaign_id,
                batch_id=batch_id,
                episode_indices=indices,
                seeds=batch_seeds,
                expected_episode_count=b_count,
                max_requests_per_invocation=max_requests,
                max_usd_per_invocation=max_usd,
                authorization_scope=BATCH_AUTHORIZATION_SCOPE,
                worst_case_requests=campaign_worst_case_requests(b_count),
            )
        )
        for idx in indices:
            rid = plan_b2_campaign_run_id(campaign_slug, idx, seeds[idx])
            episodes.append(
                B2CampaignEpisodePlan(
                    episode_index=idx,
                    seed=seeds[idx],
                    run_id=rid,
                    run_id_template=rid,
                    condition_id=PROPOSED_LIVE_CONDITION_ID,
                    batch_id=batch_id,
                    campaign_id=campaign_id,
                )
            )
        ep_cursor += b_count

    inv_worsts = [b.worst_case_requests for b in batches]
    all_inv_ok = all(w <= max_requests for w in inv_worsts)
    total_worst = sum(inv_worsts)
    single_ok = campaign_worst_case_requests(total_episodes) <= max_requests
    status = (
        "BATCH_PLAN_FEASIBLE_PER_INVOCATION"
        if all_inv_ok and not single_ok
        else ("SINGLE_INVOCATION_FEASIBLE" if single_ok else "BATCH_PLAN_INFEASIBLE")
    )

    return B2CampaignBatchPlan(
        campaign_id=campaign_id,
        campaign_slug=campaign_slug,
        expected_episodes=total_episodes,
        seeds=seeds,
        batches=tuple(batches),
        episodes=tuple(episodes),
        batch_sizes=batch_sizes,
        campaign_worst_requests_total=total_worst,
        single_invocation_feasible=single_ok,
        batch_plan_status=status,
        batch_authorization_required=True,
        live_batch_authorization_granted=LIVE_BATCH_AUTHORIZATION_GRANTED,
    )


def assess_b2_batch_campaign_preflight(
    campaign_slug: str,
    *,
    total_episodes: int = 5,
    auth_yaml: dict[str, Any] | None = None,
) -> dict[str, Any]:
    plan = build_b2_campaign_batch_plan(
        campaign_slug, total_episodes=total_episodes, auth_yaml=auth_yaml
    )
    return {
        "campaign_id": plan.campaign_id,
        "expected_episodes": plan.expected_episodes,
        "batch_sizes": list(plan.batch_sizes),
        "batch_plan_status": plan.batch_plan_status,
        "per_batch_worst_requests": [b.worst_case_requests for b in plan.batches],
        "campaign_total_worst_requests": plan.campaign_worst_requests_total,
        "single_invocation_feasible": plan.single_invocation_feasible,
        "batch_authorization_required": plan.batch_authorization_required,
        "live_batch_authorization_granted": plan.live_batch_authorization_granted,
        "live_execution": False,
        "api_calls": 0,
    }


def aggregate_b2_campaign(
    *,
    campaign_id: str,
    expected_episodes: int,
    batch_results: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """
    Cross-invocation read-only aggregation. Sums per-batch invocation ledgers (no re-charge).
    batch_results[] keys: batch_id, episodes[], invocation_requests_used, invocation_spent_usd
    episode keys: episode_index, seed, run_id, attack_succeeded, target_calls, judge_calls,
                  requests_used, spent_usd (episode slice optional)
    """
    from adapti_guard.evaluation.attack_success import EvalEpisode, compute_real_metrics

    contract = b2_experiment_contract()
    all_episodes: list[dict[str, Any]] = []
    batch_summaries: list[dict[str, Any]] = []
    total_requests = 0
    total_spend = 0.0

    for batch in batch_results:
        inv_req = int(batch.get("invocation_requests_used", 0))
        inv_spend = float(batch.get("invocation_spent_usd", 0.0))
        total_requests += inv_req
        total_spend += inv_spend
        eps = list(batch.get("episodes") or [])
        all_episodes.extend(eps)
        batch_summaries.append(
            {
                "campaign_id": campaign_id,
                "batch_id": batch.get("batch_id"),
                "episode_indices": batch.get("episode_indices"),
                "expected_count": batch.get("expected_episode_count"),
                "completed_count": len(eps),
                "budget_scope": BATCH_AUTHORIZATION_SCOPE,
                "requests_used": inv_req,
                "spent_usd": inv_spend,
            }
        )

    completed = len(all_episodes)
    missing = max(0, expected_episodes - completed)
    campaign_complete = completed == expected_episodes and missing == 0

    eval_rows: list[EvalEpisode] = []
    for ep in all_episodes:
        if "eval_episode" in ep and isinstance(ep["eval_episode"], EvalEpisode):
            eval_rows.append(ep["eval_episode"])
        else:
            eval_rows.append(
                EvalEpisode(
                    id=str(ep.get("run_id", ep.get("episode_index", "?"))),
                    prompt="",
                    context="",
                    category=contract.experiment_family,
                    label="attack",
                    defense_action=str(ep.get("defense_action", "A0")),
                    blocked=bool(ep.get("blocked", False)),
                    model_response=str(ep.get("model_response", "")),
                    attack_succeeded=bool(ep.get("attack_succeeded", False)),
                    utility_success=False,
                    judge_reason=str(ep.get("judge_reason", "")),
                    metadata=dict(ep.get("metadata") or {}),
                )
            )

    metrics = compute_real_metrics(eval_rows) if eval_rows else None
    successes = sum(1 for e in all_episodes if e.get("attack_succeeded"))
    failed = completed - successes

    return {
        "campaign_id": campaign_id,
        "expected_episodes": expected_episodes,
        "completed_episodes": completed,
        "missing_episodes": missing,
        "campaign_complete": campaign_complete,
        "failed_episodes": failed,
        "total_episodes": completed,
        "total_target_calls": sum(int(e.get("target_calls", 0)) for e in all_episodes),
        "total_judge_calls": sum(int(e.get("judge_calls", 0)) for e in all_episodes),
        "total_requests": total_requests,
        "total_spend_usd": total_spend,
        "episode_successes": successes,
        "campaign_asr": metrics.asr if metrics else ((successes / completed) if completed else None),
        "success_semantics": contract.multi_turn_success_semantics,
        "protocol": contract.attack_protocol,
        "comparable": B2_COMPARABLE_TO_B1_PI,
        "batches": batch_summaries,
        "seeds": [e.get("seed") for e in all_episodes],
        "aggregation_note": "campaign totals sum per-invocation ledgers; no double charge",
    }


def episode_accounting_invariant_ok(
    *,
    target_calls: int,
    judge_calls: int,
    requests_used: int,
) -> bool:
    """Canonical: requests_used == target_calls + judge_calls when all calls are ledger-gated."""
    expected_judge = 1 if target_calls > 0 else 0
    if judge_calls != expected_judge:
        return False
    return requests_used == target_calls + judge_calls


def assess_b2_campaign_preflight(
    *,
    campaign_id: str,
    campaign_size: int | None = None,
    auth_yaml: dict[str, Any] | None = None,
) -> B2CampaignPreflight:
    from adapti_guard.evaluation.live_extension_wiring import load_authorization_yaml

    auth = auth_yaml if auth_yaml is not None else load_authorization_yaml()
    allowed = set(auth.get("allowed_condition_ids") or [])
    max_requests = int(auth.get("max_requests", 10))
    max_usd = float(auth.get("budget_ceiling", 1.0))
    per_ep = b2_episode_request_budget_worst()
    max_n = max_campaign_episodes_under_request_cap(max_requests)

    blockers: list[str] = []
    if PROPOSED_LIVE_CONDITION_ID not in allowed:
        blockers.append(f"{PROPOSED_LIVE_CONDITION_ID} not in allowed_condition_ids")
    if not is_b2_live_condition(PROPOSED_LIVE_CONDITION_ID):
        blockers.append("condition not registered as B2 live")

    size_status = CAMPAIGN_SIZE_TBD
    size = campaign_size
    if size is None:
        auth_n = auth.get("n_episodes")
        if isinstance(auth_n, int) and auth_n > 1:
            size_status = f"auth_n_episodes={auth_n}_requires_explicit_campaign_authorization"
        else:
            size_status = CAMPAIGN_SIZE_TBD
        seeds: tuple[int, ...] = ()
        plans: tuple[B2CampaignEpisodePlan, ...] = ()
    else:
        size_status = f"campaign_size={size}"
        if size * per_ep > max_requests:
            blockers.append(
                f"campaign_size={size} worst_requests={size * per_ep} > max_requests={max_requests}"
            )
        if size > max_n:
            blockers.append(
                f"campaign_size={size} exceeds max_episodes_under_cap={max_n} "
                f"(batch or new authorization required)"
            )
        base = [int(s) for s in (auth.get("seeds") or [])]
        seeds = expand_campaign_seeds(base, size)
        cid = canonical_campaign_id(campaign_id)
        plans = tuple(
            B2CampaignEpisodePlan(
                episode_index=i,
                seed=seeds[i],
                run_id=plan_b2_campaign_run_id(campaign_id, i, seeds[i]),
                run_id_template=plan_b2_campaign_run_id(campaign_id, i, seeds[i]),
                condition_id=PROPOSED_LIVE_CONDITION_ID,
                batch_id="",
                campaign_id=cid,
            )
            for i in range(size)
        )
        if len({p.run_id_template for p in plans}) != len(plans):
            blockers.append("run_id collision in campaign plan")

    contract = b2_experiment_contract()
    ready = not blockers and size is not None and size > 1
    semantics = inspect_authorization_budget_semantics(auth)
    consistency = authorization_consistency_state(auth)

    return B2CampaignPreflight(
        ready=ready,
        campaign_size=size,
        campaign_size_status=size_status,
        max_episodes_under_request_cap=max_n,
        episode_request_budget_worst=per_ep,
        blockers=tuple(blockers),
        seeds=seeds,
        episode_plans=plans,
        comparable_to_b1_pi=B2_COMPARABLE_TO_B1_PI,
        budget={
            "max_requests": max_requests,
            "max_usd": max_usd,
            "episode_request_budget_worst": per_ep,
            "campaign_worst_requests": (size or 0) * per_ep if size else None,
        },
        authorization={
            "condition_id": PROPOSED_LIVE_CONDITION_ID,
            "allowed": PROPOSED_LIVE_CONDITION_ID in allowed,
            "attack_protocol": contract.attack_protocol,
            "success_semantics": contract.multi_turn_success_semantics,
            "budget_semantics": semantics,
            "consistency_state": consistency,
            "scenario_fact_table": campaign_scenario_fact_table(auth),
        },
    )


def aggregate_campaign_episode_rows(episodes: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Episode-level aggregation for campaign (no statistical inference)."""
    n = len(episodes)
    success = sum(1 for e in episodes if e.get("attack_succeeded"))
    blocked = sum(1 for e in episodes if e.get("blocked"))
    target_called = sum(1 for e in episodes if e.get("target_calls", 0) > 0)
    judge_called = sum(1 for e in episodes if e.get("judge_calls", 0) > 0)
    turns = sum(int(e.get("turn_count", 0)) for e in episodes)
    return {
        "episode_count": n,
        "success_count": success,
        "blocked_episodes": blocked,
        "target_called_episodes": target_called,
        "judge_called_episodes": judge_called,
        "turn_count_total": turns,
        "asr": (success / n) if n else None,
        "comparable_to_b1_pi": B2_COMPARABLE_TO_B1_PI,
    }
