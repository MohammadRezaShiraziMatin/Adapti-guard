"""Offline Phase 4 runner — implements Phase 3 contract without live API."""
from __future__ import annotations

import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeRunner
from adapti_guard.evaluation.agent_environment import AgentEnvironment
from adapti_guard.evaluation.component_resolver import (
    AttackKind,
    ComponentResolutionError,
    ResolvedAttack,
    ResolvedDefense,
    TargetExecutionFailure,
    resolve_attack,
    resolve_defense,
    resolve_offline_target,
    run_target_generate,
    stateful_target_fn,
)
from adapti_guard.evaluation.condition_resolver import (
    RunContext,
    resolve_condition,
    verify_frozen_dataset,
)
from adapti_guard.evaluation.experiment_logging import (
    ExperimentRunContext,
    git_commit,
    write_json,
)
from adapti_guard.evaluation.q1_protocol_runner import (
    build_blind_judge_input,
    mcnemar_pair_complete,
    q1_episode_judge_failed,
)
from adapti_guard.evaluation.stateful_episode import StatefulEpisodeRunner

Q1_B2_CONDITION_PREFIX = "B2-ADAPTIVE-"

LIVE_STATUSES = frozenset({"LIVE", "SUPPORTED"})


class OfflineRunnerError(Exception):
    """Machine-readable failure category in message prefix."""


def _assign_run_id(ctx: RunContext, experiment_id: str, run_id: str) -> RunContext:
    d = asdict(ctx)
    d["run_id"] = run_id
    return RunContext(**d)


def run_offline(
    condition_id: str,
    *,
    seed: int = 0,
    trial: int = 0,
    runs_root: Path | None = None,
    matrix_path: Path | None = None,
    allow_error_target: bool = False,
) -> Path:
    try:
        row, ctx = resolve_condition(condition_id, matrix_path=matrix_path, seed=seed, trial=trial)
    except Exception as exc:
        raise OfflineRunnerError(str(exc)) from exc

    status = ctx.evidence_status.upper()
    if status in LIVE_STATUSES and row.get("execution_gate") == "historical_locked":
        raise OfflineRunnerError("configuration_failure: historical live condition — use AUDIT, not offline runner")
    if status not in ("OFFLINE", "DESIGN", "PLANNED") and "OFFLINE" not in status:
        if status == "BLOCKED":
            raise OfflineRunnerError(f"resolution_failure: condition blocked {condition_id}")
        raise OfflineRunnerError(f"configuration_failure: condition not offline-runnable status={status}")

    try:
        attack = resolve_attack(ctx.attack_id)
        defense = resolve_defense(ctx.defense_id, adaptivity=ctx.adaptivity)
        target = resolve_offline_target(ctx.target_model_id, allow_error_target=allow_error_target)
    except ComponentResolutionError as exc:
        raise OfflineRunnerError(str(exc)) from exc

    exp_id = str(row.get("experiment_id", condition_id))
    with ExperimentRunContext.create(
        exp_id,
        config={
            "condition_id": condition_id,
            "phase4_mode": "offline",
            "config_hash": ctx.config_hash,
            **{k: getattr(ctx, k) for k in (
                "rq_id", "attack_id", "defense_id", "target_model_id", "judge_id",
                "interaction_mode", "adaptivity", "agent_state", "tool_state",
                "dataset_id", "seed", "trial",
            )},
        },
        runs_root=runs_root,
    ) as run:
        ctx = _assign_run_id(ctx, exp_id, run.run_id)
        dataset_hash: str | None = None
        if ctx.dataset_id.startswith("p1") or ctx.dataset_id == "p1_mechanism_v1.0.0":
            dataset_hash = verify_frozen_dataset(ctx.dataset_id).get("dataset_hash")

        raw = _execute_resolved(
            attack,
            defense,
            target,
            row=row,
            ctx=ctx,
            seed=seed,
        )
        raw_path = run.run_dir / "raw_evidence.json"
        write_json(raw_path, raw)

        derived = {
            "derived_from": str(raw_path.name),
            "metrics": raw.get("metrics", {}),
            "evidence_type": "offline_fixture",
        }
        write_json(run.run_dir / "derived_metrics.json", derived)

        judge_status = _judge_status(ctx.judge_id, row)
        evidence_record = _build_evidence_record(
            row=row,
            ctx=ctx,
            run_dir=run.run_dir,
            raw_path=raw_path,
            dataset_hash=dataset_hash,
            judge_status=judge_status,
            target_provider=target.provider,
            target_model_version=target.model_version,
        )
        write_json(run.run_dir / "evidence_record.json", evidence_record)
        from adapti_guard.evaluation.human_review_packet import packet_from_evidence_record

        write_json(run.run_dir / "human_review_packet.json", packet_from_evidence_record(evidence_record))
        run.write_metrics(derived["metrics"])
        return run.run_dir


def _judge_status(judge_id: str | None, row: dict[str, Any]) -> str:
    if not judge_id or judge_id in ("n/a", "mock_judge"):
        return "not_executed"
    if row.get("target_ne_judge") and judge_id == row.get("target_model_id"):
        return "blocked_target_eq_judge"
    return "not_executed_offline"


def _build_evidence_record(
    *,
    row: dict[str, Any],
    ctx: RunContext,
    run_dir: Path,
    raw_path: Path,
    dataset_hash: str | None,
    judge_status: str,
    target_provider: str,
    target_model_version: str,
) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "experiment_id": row.get("experiment_id"),
        "condition_id": ctx.condition_id,
        "rq_id": ctx.rq_id,
        "attack_id": ctx.attack_id,
        "defense_id": ctx.defense_id,
        "target_model_id": ctx.target_model_id,
        "judge_id": ctx.judge_id,
        "target_ne_judge": bool(row.get("target_ne_judge")),
        "interaction_mode": ctx.interaction_mode,
        "adaptivity": ctx.adaptivity,
        "agent_state": ctx.agent_state,
        "tool_state": ctx.tool_state,
        "dataset_id": ctx.dataset_id,
        "seed": ctx.seed,
        "trial": ctx.trial,
        "run_id": ctx.run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.environ.get("ADAPTIGUARD_ENV", "offline"),
        "provider": target_provider,
        "model_version": target_model_version,
        "config_hash": ctx.config_hash,
        "repository_revision": git_commit(),
        "evidence_path": str(run_dir),
        "evidence_type": "offline_fixture",
        "evidence_status": "OFFLINE",
        "raw_evidence_path": str(raw_path),
        "judge_status": judge_status,
        "mode": "offline",
    }
    if dataset_hash:
        rec["dataset_hash"] = dataset_hash
    cid = str(ctx.condition_id or "")
    if cid.startswith(Q1_B2_CONDITION_PREFIX):
        rec["q1_runner_semantics"] = {
            "complete_pair_rule": mcnemar_pair_complete.__name__,
            "judge_failed_fn": q1_episode_judge_failed.__name__,
            "judge_blind_builder": build_blind_judge_input.__name__,
            "timeout_as_judge_failure": True,
            "network_only_retry": True,
        }
    return rec


def _execute_resolved(
    attack: ResolvedAttack,
    defense: ResolvedDefense,
    target: Any,
    *,
    row: dict[str, Any],
    ctx: RunContext,
    seed: int,
) -> dict[str, Any]:
    assert defense.stateful_fn is not None

    if attack.kind == AttackKind.STATEFUL_TURNS:
        specs = list(attack.turn_specs or ())
        target_rec: dict[str, Any] | None = None
        try:
            target_fn = stateful_target_fn(target, seed=seed)
            episode = StatefulEpisodeRunner(str(row.get("experiment_id", "stateful_offline"))).run(
                specs,
                target=target_fn,
                defense=defense.stateful_fn,
                seed=seed,
            )
        except TargetExecutionFailure as exc:
            target_rec = exc.record
            return {
                "pipeline": "stateful",
                "attack": {"attack_id": attack.attack_id, "implementation": attack.implementation},
                "defense": {"defense_id": defense.defense_id, "implementation": defense.implementation},
                "target_execution": target_rec,
                "outcome": "target_failure",
                "metrics": {},
            }
        return {
            "pipeline": "stateful",
            "fixture": "stateful",
            "attack": {"attack_id": attack.attack_id, "implementation": attack.implementation},
            "defense": {"defense_id": defense.defense_id, "implementation": defense.implementation},
            "target_execution": run_target_generate(target, prompt=specs[0].user_message, seed=seed),
            "episode": {"n_turns": episode.n_turns, "config_hash": episode.config_hash},
            "metrics": {"n_turns": episode.n_turns, "config_hash": episode.config_hash},
        }

    if attack.kind == AttackKind.ADAPTIVE:
        attacker = AdaptiveAttacker()

        def _target_from_model(_history: list[dict[str, str]], user_message: str) -> str:
            rec = run_target_generate(target, prompt=user_message, seed=seed)
            if rec["execution_status"] != "ok":
                raise TargetExecutionFailure(rec)
            return (
                f'MODEL: {rec["text"]} TOOL_REQUEST: {{"name":"send_email","arguments":'
                f'{{"to":"x","body":"y"}}}}'
            )

        ar = AdaptiveEpisodeRunner(3).run(
            attacker=attacker,
            defense=defense.stateful_fn,
            seed=seed,
            target=_target_from_model,
        )
        return {
            "pipeline": "adaptive",
            "fixture": "adaptive",
            "attack": {"attack_id": attack.attack_id, "implementation": attack.implementation},
            "defense": {"defense_id": defense.defense_id, "implementation": defense.implementation},
            "target_execution": {"execution_status": "ok", "provider": target.provider},
            "episode": {
                "strategy_changed": ar.strategy_changed,
                "families": list(ar.families_seen),
            },
            "metrics": {"strategy_changed": ar.strategy_changed, "families": list(ar.families_seen)},
        }

    if attack.kind == AttackKind.TOOL_REQUEST:
        env = AgentEnvironment(seed=seed)
        tool_req = attack.tool_request
        defense_action, _meta = defense.stateful_fn(prompt="agent", context="")
        step = env.step(tool_req, defense_action)
        verifier = {
            "privileged_executed": step.privileged_executed,
            "tool_executed": step.tool_executed,
            "state_hash": step.state_hash,
        }
        return {
            "pipeline": "agent",
            "fixture": "agent",
            "attack": {"attack_id": attack.attack_id, "implementation": attack.implementation},
            "defense": {"defense_id": defense.defense_id, "implementation": defense.implementation},
            "target_execution": run_target_generate(target, prompt="tool_step", seed=seed),
            "raw_evaluation": {"verifier": verifier},
            "metrics": {
                "privileged_executed": step.privileged_executed,
                "state_hash": step.state_hash,
            },
        }

    raise OfflineRunnerError(f"resolution_failure: unhandled attack kind {attack.kind}")
