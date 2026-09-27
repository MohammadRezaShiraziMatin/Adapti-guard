"""Canonical B2 batch runner (offline by default; shared BudgetLedger per invocation)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal

from adapti_guard.evaluation.b2_adaptive_contract import (
    B2_ATTACK_PROTOCOL,
    B2_LIVE_JUDGE_CONFIG_KEY,
    B2_LIVE_TARGET_CONFIG_KEY,
    MULTI_TURN_SUCCESS_SEMANTICS,
    PROPOSED_LIVE_CONDITION_ID,
    b2_experiment_contract,
)
from adapti_guard.evaluation.b2_campaign_protocol import (
    B2_BATCH_AUTHORIZATION_SCOPE,
    B2BatchAuthorization,
    B2CampaignBatchPlan,
    B2CampaignEpisodePlan,
    build_b2_batch_authorization,
    build_b2_campaign_batch_plan,
    campaign_episode_artifact_dir,
    episode_accounting_invariant_ok,
    evaluate_batch_execution_gates,
    preflight_batch_worst_case_ok,
)
from adapti_guard.evaluation.live_extension_wiring import (
    DEFAULT_LIVE_RUN_ROOT,
    ExecutionMode,
    LiveExtensionBlockedError,
    budget_ledger_from_authorization,
    load_authorization_yaml,
    run_live_condition,
)

BatchRunStatus = Literal["ok", "blocked", "stopped", "preflight_failed"]


@dataclass
class B2BatchEpisodeResult:
    episode_index: int
    seed: int
    run_id: str
    run_dir: str
    status: str
    target_calls: int = 0
    judge_calls: int = 0
    requests_used: int = 0
    spent_usd_delta: float = 0.0
    attack_succeeded: bool = False
    blocked: bool = False
    turn_count: int = 0
    provenance: dict[str, Any] = field(default_factory=dict)
    stop_reason: str | None = None


@dataclass
class B2BatchRunResult:
    campaign_id: str
    batch_id: str
    expected_episode_count: int
    completed_episode_count: int
    failed_episode_count: int
    episode_results: list[B2BatchEpisodeResult]
    target_calls: int
    judge_calls: int
    requests_used: int
    spent_usd: float
    budget_status: str
    authorization_status: dict[str, Any]
    batch_complete: bool
    status: BatchRunStatus
    stop_reason: str | None = None
    authorization_scope: str = B2_BATCH_AUTHORIZATION_SCOPE
    budget_scope: str = B2_BATCH_AUTHORIZATION_SCOPE
    protocol: str = B2_ATTACK_PROTOCOL
    success_semantics: str = MULTI_TURN_SUCCESS_SEMANTICS
    condition_id: str = PROPOSED_LIVE_CONDITION_ID

    def to_aggregate_batch_dict(self) -> dict[str, Any]:
        """Shape expected by aggregate_b2_campaign (read-only)."""
        episodes = []
        for ep in self.episode_results:
            if ep.status != "ok":
                continue
            episodes.append(
                {
                    "episode_index": ep.episode_index,
                    "seed": ep.seed,
                    "run_id": ep.run_id,
                    "attack_succeeded": ep.attack_succeeded,
                    "target_calls": ep.target_calls,
                    "judge_calls": ep.judge_calls,
                    "requests_used": ep.requests_used,
                    "spent_usd": ep.spent_usd_delta,
                    "blocked": ep.blocked,
                    "metadata": ep.provenance,
                }
            )
        return {
            "batch_id": self.batch_id,
            "episode_indices": tuple(e.episode_index for e in self.episode_results if e.status == "ok"),
            "expected_episode_count": self.expected_episode_count,
            "episodes": episodes,
            "invocation_requests_used": self.requests_used,
            "invocation_spent_usd": self.spent_usd,
        }


def _episode_plans_for_batch(
    plan: B2CampaignBatchPlan, batch_id: str
) -> tuple[B2CampaignEpisodePlan, ...]:
    return tuple(e for e in plan.episodes if e.batch_id == batch_id)


def _load_b2_episode_metrics(run_dir: Path) -> dict[str, Any]:
    raw_path = run_dir / "raw" / "episode_raw.json"
    payload = json.loads(raw_path.read_text())
    b2 = payload.get("b2_evaluation") or {}
    eval_ep = b2.get("eval_episode") or {}
    result = payload.get("result") or {}
    turns = result.get("turns") or []
    return {
        "target_calls": int(b2.get("target_calls", 0)),
        "judge_calls": int(b2.get("judge_calls", 0)),
        "attack_succeeded": bool(eval_ep.get("attack_succeeded", False)),
        "blocked": bool(eval_ep.get("blocked", False)),
        "turn_count": len(turns),
        "provenance": dict(b2.get("provenance") or {}),
        "seed": int(payload.get("seed", 0)),
    }


def _audit_episode_after_run(
    *,
    ledger: Any,
    ledger_requests_before: int,
    ledger_spent_before: float,
    metrics: dict[str, Any],
    run_dir: Path,
    expected_seed: int,
    expected_index: int,
    max_requests: int,
    max_usd: float,
) -> tuple[bool, str]:
    if metrics["seed"] != expected_seed:
        return False, f"seed_integrity_failure: expected {expected_seed} got {metrics['seed']}"
    tgt = metrics["target_calls"]
    jdg = metrics["judge_calls"]
    delta_req = ledger.requests_used - ledger_requests_before
    delta_usd = ledger.spent_usd - ledger_spent_before
    ep_requests = tgt + jdg
    if delta_req != ep_requests:
        return False, (
            f"ledger_mismatch: ledger_delta={delta_req} "
            f"!= target_calls+judge_calls={ep_requests}"
        )
    if not episode_accounting_invariant_ok(
        target_calls=tgt, judge_calls=jdg, requests_used=ep_requests
    ):
        return False, "episode_accounting_invariant_failed"
    if ledger.requests_used > max_requests:
        return False, "budget_failure: requests_used exceeds max_requests"
    if ledger.spent_usd > max_usd:
        return False, "budget_failure: spent_usd exceeds max_usd"
    if not run_dir.is_dir():
        return False, "artifact_failure: run_dir missing"
    return True, "ok"


def run_live_b2_batch(
    *,
    campaign_slug: str,
    batch_id: str,
    output_root: Path | str = DEFAULT_LIVE_RUN_ROOT,
    total_episodes: int = 5,
    execution_mode: ExecutionMode = "OFFLINE_MOCK",
    batch_authorization: B2BatchAuthorization | None = None,
    injected_batch_grant: bool = False,
    injected_campaign_grant: bool | None = None,
    auth_yaml: dict[str, Any] | None = None,
    injected_target: Any | None = None,
    injected_judge: Callable[[Any], Any] | None = None,
    injected_b1_defense: Any | None = None,
    episode_runner: Callable[..., Any] | None = None,
    plan: B2CampaignBatchPlan | None = None,
    attack_mode: str | None = None,
    defense_mode: str | None = None,
) -> B2BatchRunResult:
    """
    Sequential batch execution with one shared BudgetLedger per invocation.
    Default production path blocks unless LIVE_BATCH_AUTHORIZATION_GRANTED is enabled elsewhere.
    """
    auth = auth_yaml if auth_yaml is not None else load_authorization_yaml()
    campaign_plan = plan or build_b2_campaign_batch_plan(
        campaign_slug, total_episodes=total_episodes, auth_yaml=auth
    )
    batch_auth = batch_authorization or build_b2_batch_authorization(
        campaign_plan, batch_id, auth_yaml=auth
    )
    episode_plans = _episode_plans_for_batch(campaign_plan, batch_id)
    if len(episode_plans) != batch_auth.expected_episode_count:
        return _blocked_result(
            batch_auth,
            episode_plans,
            f"episode_plan_mismatch: expected {batch_auth.expected_episode_count} "
            f"plans got {len(episode_plans)}",
        )

    gates_ok, gate_reason, gate_status = evaluate_batch_execution_gates(
        batch_auth,
        auth_yaml=auth,
        injected_batch_grant=injected_batch_grant,
        injected_campaign_grant=injected_campaign_grant,
    )
    if not gates_ok:
        return _blocked_result(batch_auth, episode_plans, gate_reason, authorization_status=gate_status)

    pf_ok, pf_reason, _worst = preflight_batch_worst_case_ok(batch_auth)
    if not pf_ok:
        return B2BatchRunResult(
            campaign_id=batch_auth.campaign_id,
            batch_id=batch_auth.batch_id,
            expected_episode_count=batch_auth.expected_episode_count,
            completed_episode_count=0,
            failed_episode_count=0,
            episode_results=[],
            target_calls=0,
            judge_calls=0,
            requests_used=0,
            spent_usd=0.0,
            budget_status="preflight_failed",
            authorization_status=gate_status,
            batch_complete=False,
            status="preflight_failed",
            stop_reason=pf_reason,
        )

    ledger = budget_ledger_from_authorization(auth)
    root = Path(output_root)
    episode_results: list[B2BatchEpisodeResult] = []
    total_target = 0
    total_judge = 0
    runner = episode_runner or run_live_condition

    for ep_plan in episode_plans:
        if ep_plan.seed not in batch_auth.seeds:
            return _stop_after(
                batch_auth,
                episode_results,
                ledger,
                f"seed_authorization_failure: seed {ep_plan.seed} not in batch auth",
            )
        if ep_plan.episode_index not in batch_auth.episode_indices:
            return _stop_after(
                batch_auth,
                episode_results,
                ledger,
                f"episode_index_failure: {ep_plan.episode_index} not authorized",
            )
        if batch_auth.allowed_condition_ids:
            if ep_plan.condition_id not in batch_auth.allowed_condition_ids:
                return _stop_after(
                    batch_auth,
                    episode_results,
                    ledger,
                    "condition_id_not_in_batch_allowed_set",
                )
        elif ep_plan.condition_id != batch_auth.condition_id:
            return _stop_after(
                batch_auth,
                episode_results,
                ledger,
                "condition_id_mismatch",
            )

        run_dir = Path(
            campaign_episode_artifact_dir(
                output_root=str(root),
                campaign_slug=campaign_plan.campaign_slug,
                batch_id=batch_id,
                run_id=ep_plan.run_id,
            )
        )
        for prior in episode_results:
            if prior.run_dir == str(run_dir):
                return _stop_after(
                    batch_auth,
                    episode_results,
                    ledger,
                    "artifact_collision: duplicate run_dir",
                )
        if run_dir.exists() and any(run_dir.iterdir()):
            return _stop_after(
                batch_auth,
                episode_results,
                ledger,
                "artifact_collision: run_dir not empty",
            )

        ledger_req_before = ledger.requests_used
        ledger_usd_before = ledger.spent_usd
        from adapti_guard.evaluation.b2_attack_mode_contract import attack_mode_for_condition_id
        from adapti_guard.evaluation.b2_matrix_contract import defense_mode_for_condition_id

        ep_attack_mode = attack_mode or attack_mode_for_condition_id(ep_plan.condition_id)
        ep_defense_mode = defense_mode or defense_mode_for_condition_id(ep_plan.condition_id)
        try:
            runner(
                ep_plan.condition_id,
                run_id=ep_plan.run_id,
                run_dir=run_dir,
                seed=ep_plan.seed,
                execution_mode=execution_mode,
                target_config_key=B2_LIVE_TARGET_CONFIG_KEY,
                judge_config_key=B2_LIVE_JUDGE_CONFIG_KEY,
                injected_target=injected_target,
                injected_judge=injected_judge,
                injected_b1_defense=injected_b1_defense,
                injected_ledger=ledger,
                attack_mode=ep_attack_mode,
                defense_mode=ep_defense_mode,
            )
        except LiveExtensionBlockedError as exc:
            episode_results.append(
                B2BatchEpisodeResult(
                    episode_index=ep_plan.episode_index,
                    seed=ep_plan.seed,
                    run_id=ep_plan.run_id,
                    run_dir=str(run_dir),
                    status="failed",
                    stop_reason=str(exc),
                )
            )
            return _finalize_batch(
                batch_auth,
                episode_results,
                ledger,
                gate_status,
                status="stopped",
                stop_reason=str(exc),
            )
        except Exception as exc:  # noqa: BLE001 — batch hard-stop surface
            episode_results.append(
                B2BatchEpisodeResult(
                    episode_index=ep_plan.episode_index,
                    seed=ep_plan.seed,
                    run_id=ep_plan.run_id,
                    run_dir=str(run_dir),
                    status="failed",
                    stop_reason=str(exc),
                )
            )
            return _finalize_batch(
                batch_auth,
                episode_results,
                ledger,
                gate_status,
                status="stopped",
                stop_reason=str(exc),
            )

        metrics = _load_b2_episode_metrics(run_dir)
        audit_ok, audit_reason = _audit_episode_after_run(
            ledger=ledger,
            ledger_requests_before=ledger_req_before,
            ledger_spent_before=ledger_usd_before,
            metrics=metrics,
            run_dir=run_dir,
            expected_seed=ep_plan.seed,
            expected_index=ep_plan.episode_index,
            max_requests=batch_auth.max_requests,
            max_usd=batch_auth.max_usd,
        )
        ep_requests = metrics["target_calls"] + metrics["judge_calls"]
        ep_usd_delta = ledger.spent_usd - ledger_usd_before
        provenance = {
            **metrics["provenance"],
            "campaign_id": batch_auth.campaign_id,
            "batch_id": batch_auth.batch_id,
            "episode_index": ep_plan.episode_index,
            "seed": ep_plan.seed,
            "run_id": ep_plan.run_id,
            "condition_id": ep_plan.condition_id,
            "attack_mode": ep_attack_mode,
            "defense_mode": ep_defense_mode,
            "protocol": B2_ATTACK_PROTOCOL,
            "success_semantics": MULTI_TURN_SUCCESS_SEMANTICS,
            "authorization_scope": batch_auth.authorization_scope,
            "budget_scope": B2_BATCH_AUTHORIZATION_SCOPE,
        }
        ep_result = B2BatchEpisodeResult(
            episode_index=ep_plan.episode_index,
            seed=ep_plan.seed,
            run_id=ep_plan.run_id,
            run_dir=str(run_dir),
            status="ok" if audit_ok else "failed",
            target_calls=metrics["target_calls"],
            judge_calls=metrics["judge_calls"],
            requests_used=ep_requests,
            spent_usd_delta=ep_usd_delta,
            attack_succeeded=metrics["attack_succeeded"],
            blocked=metrics["blocked"],
            turn_count=metrics["turn_count"],
            provenance=provenance,
            stop_reason=audit_reason if not audit_ok else None,
        )
        episode_results.append(ep_result)
        total_target += metrics["target_calls"]
        total_judge += metrics["judge_calls"]

        if not audit_ok:
            return _finalize_batch(
                batch_auth,
                episode_results,
                ledger,
                gate_status,
                status="stopped",
                stop_reason=audit_reason,
            )

    return _finalize_batch(
        batch_auth,
        episode_results,
        ledger,
        gate_status,
        status="ok",
        stop_reason=None,
    )


def _blocked_result(
    batch_auth: B2BatchAuthorization,
    episode_plans: tuple[B2CampaignEpisodePlan, ...],
    reason: str,
    *,
    authorization_status: dict[str, Any] | None = None,
) -> B2BatchRunResult:
    return B2BatchRunResult(
        campaign_id=batch_auth.campaign_id,
        batch_id=batch_auth.batch_id,
        expected_episode_count=batch_auth.expected_episode_count,
        completed_episode_count=0,
        failed_episode_count=0,
        episode_results=[],
        target_calls=0,
        judge_calls=0,
        requests_used=0,
        spent_usd=0.0,
        budget_status="blocked",
        authorization_status=authorization_status or {},
        batch_complete=False,
        status="blocked",
        stop_reason=reason,
    )


def _stop_after(
    batch_auth: B2BatchAuthorization,
    episode_results: list[B2BatchEpisodeResult],
    ledger: Any,
    reason: str,
) -> B2BatchRunResult:
    return _finalize_batch(
        batch_auth,
        episode_results,
        ledger,
        {},
        status="stopped",
        stop_reason=reason,
    )


def _finalize_batch(
    batch_auth: B2BatchAuthorization,
    episode_results: list[B2BatchEpisodeResult],
    ledger: Any,
    gate_status: dict[str, Any],
    *,
    status: BatchRunStatus,
    stop_reason: str | None,
) -> B2BatchRunResult:
    completed = sum(1 for e in episode_results if e.status == "ok")
    failed = sum(1 for e in episode_results if e.status != "ok")
    total_target = sum(e.target_calls for e in episode_results)
    total_judge = sum(e.judge_calls for e in episode_results)
    ep_sum_requests = sum(e.requests_used for e in episode_results)
    budget_status = "ok"
    if ledger.requests_used != ep_sum_requests:
        budget_status = "ledger_episode_sum_mismatch"
        status = "stopped"
        stop_reason = stop_reason or budget_status
    if ledger.requests_used > batch_auth.max_requests:
        budget_status = "max_requests_exceeded"
        status = "stopped"
        stop_reason = stop_reason or budget_status
    if ledger.spent_usd > batch_auth.max_usd:
        budget_status = "max_usd_exceeded"
        status = "stopped"
        stop_reason = stop_reason or budget_status

    batch_complete = (
        completed == batch_auth.expected_episode_count
        and failed == 0
        and status == "ok"
    )
    contract = b2_experiment_contract()
    return B2BatchRunResult(
        campaign_id=batch_auth.campaign_id,
        batch_id=batch_auth.batch_id,
        expected_episode_count=batch_auth.expected_episode_count,
        completed_episode_count=completed,
        failed_episode_count=failed,
        episode_results=episode_results,
        target_calls=total_target,
        judge_calls=total_judge,
        requests_used=ledger.requests_used,
        spent_usd=ledger.spent_usd,
        budget_status=budget_status,
        authorization_status=gate_status,
        batch_complete=batch_complete,
        status=status,
        stop_reason=stop_reason,
        protocol=contract.attack_protocol,
        success_semantics=contract.multi_turn_success_semantics,
    )
