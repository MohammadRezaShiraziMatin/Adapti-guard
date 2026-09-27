"""Phase 7 live extension wiring + canonical live runner orchestration (no spend by default)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal

from adapti_guard.core.models import DefenseAction

DEFAULT_WIRING = Path("docs/research/PHASE7_LIVE_EXTENSION_WIRING.yaml")
DEFAULT_AUTH_YAML = Path("docs/research/live_budget_authorization.yaml")
DEFAULT_PHASE7_JSON = Path("docs/research/PHASE7_LIVE_AUTHORIZATION.json")
DEFAULT_LIVE_RUN_ROOT = Path("experiments/real_llm_eval/P1_MECHANISM_L1")

ExecutionMode = Literal["LIVE", "OFFLINE_MOCK"]


@dataclass(frozen=True)
class LiveExecutionPlan:
    condition_id: str
    offline_executor: str | None
    live_executor: str | None
    live_ready: bool
    live_blocker: str
    components: dict[str, str]
    note: str = ""


@dataclass
class CanonicalLiveRunResult:
    run_id: str
    condition_id: str
    execution_mode: str
    status: str
    trace_path: str
    raw_evidence_paths: list[str] = field(default_factory=list)
    derived_metrics_path: str | None = None
    requests_used: int = 0
    blocked_reason: str | None = None


class LiveExtensionBlockedError(Exception):
    """Raised when live execution is requested but gate/authorization blocks."""


def load_wiring(path: Path | None = None) -> dict[str, Any]:
    import yaml

    p = path or DEFAULT_WIRING
    if not p.is_file():
        raise FileNotFoundError(f"wiring contract missing: {p}")
    return yaml.safe_load(p.read_text())


def load_authorization_yaml(path: Path | None = None) -> dict[str, Any]:
    import yaml

    p = path or DEFAULT_AUTH_YAML
    if not p.is_file():
        return {}
    return yaml.safe_load(p.read_text()) or {}


def load_phase7_gate_json(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_PHASE7_JSON
    if not p.is_file():
        return {}
    return json.loads(p.read_text())


def authorization_allows_live_spend(
    *,
    auth_yaml: Path | None = None,
    phase7_json: Path | None = None,
) -> tuple[bool, str]:
    """Fail closed unless both YAML and Phase7 JSON explicitly permit spend."""
    auth = load_authorization_yaml(auth_yaml)
    if not auth.get("api_spend_permitted"):
        return False, "authorization_failure: api_spend_permitted false"
    if str(auth.get("approval_status", "")).strip() != "LIVE_AUTHORIZED":
        return False, "authorization_failure: approval_status not LIVE_AUTHORIZED"
    if not auth.get("explicit_authorization_for_live_execution"):
        return False, "authorization_failure: explicit_authorization_for_live_execution false"
    gate = load_phase7_gate_json(phase7_json)
    if gate.get("live_execution_gate") != "LIVE_AUTHORIZED":
        return False, f"authorization_failure: {gate.get('live_execution_gate', 'PHASE7_LIVE_BLOCKED')}"
    if not gate.get("api_spend_permitted"):
        return False, "authorization_failure: phase7 json api_spend_permitted false"
    return True, "ok"


def budget_ledger_from_authorization(auth: dict[str, Any] | None = None) -> Any:
    from adapti_guard.evaluation.live_budget_gate import BudgetLedger

    data = auth or load_authorization_yaml()
    max_req = data.get("max_requests")
    max_usd = data.get("budget_ceiling")
    ledger = BudgetLedger(hard_stop=True)
    if isinstance(max_req, int):
        ledger.max_requests = max_req
    elif isinstance(max_req, str) and max_req.startswith("PENDING"):
        ledger.max_requests = None
    if isinstance(max_usd, (int, float)):
        ledger.max_usd = float(max_usd)
    else:
        ledger.max_usd = None
        ledger.record_cost_unknown()
    return ledger


def plan_live_execution(condition_id: str, *, wiring_path: Path | None = None) -> LiveExecutionPlan:
    """Return canonical live plan. Never calls TargetModel or providers."""
    data = load_wiring(wiring_path)
    row = (data.get("conditions") or {}).get(condition_id)
    if row is None:
        raise LiveExtensionBlockedError(f"resolution_failure: unknown condition_id={condition_id}")
    auth = load_authorization_yaml()
    allowed = set(auth.get("allowed_condition_ids") or [])
    auth_live_ready = (
        condition_id in allowed and str(row.get("live_executor")) == "live_extension"
    )
    live_ready = bool(row.get("live_ready")) or auth_live_ready
    plan = LiveExecutionPlan(
        condition_id=condition_id,
        offline_executor=row.get("offline_executor"),
        live_executor=row.get("live_executor"),
        live_ready=live_ready,
        live_blocker=str(row.get("live_blocker", "unknown")),
        components=dict(row.get("components") or {}),
        note=str(row.get("note", "")),
    )
    if not plan.live_ready:
        raise LiveExtensionBlockedError(
            f"configuration_failure: live blocked for {condition_id} ({plan.live_blocker})"
        )
    return plan


def resolve_offline_path(condition_id: str) -> str:
    """Executor id for offline-capable conditions."""
    row = load_wiring()["conditions"][condition_id]
    return str(row.get("offline_executor", "none"))


def _resolve_gated_target(
    *,
    target_config_key: str,
    judge_config_key: str,
    models_config: Path,
    ledger: Any,
    allow_live: bool,
) -> Any:
    from adapti_guard.evaluation.live_budget_gate import BudgetGatedTargetModel
    from adapti_guard.evaluation.llm_judge import LLMJudge
    from adapti_guard.evaluation.live_model_resolver import (
        resolve_target_model,
        validate_target_judge_keys,
    )

    info = validate_target_judge_keys(target_config_key, judge_config_key, config_path=models_config)
    inner = resolve_target_model(
        target_config_key,
        config_path=models_config,
        allow_live=allow_live,
    )
    provider = str(getattr(inner, "provider", "openrouter"))
    pricing = None
    if provider == "openrouter":
        from adapti_guard.evaluation.openrouter_panel_pricing import load_openrouter_pricing_table

        pricing = load_openrouter_pricing_table(models_config)
    gated = BudgetGatedTargetModel(inner, ledger, provider=provider, pricing=pricing)
    judge = LLMJudge(
        config_key=judge_config_key,
        fallback_config_key=judge_config_key,
        config_path=str(models_config),
        use_fallback=False,
        cache_enabled=False,
    )
    inner_judge = resolve_target_model(
        judge_config_key,
        config_path=models_config,
        allow_live=allow_live,
    )
    inner_judge.max_retries = 0
    gated_judge = BudgetGatedTargetModel(inner_judge, ledger, provider=provider, pricing=pricing)
    judge._primary = gated_judge
    judge._fallback = gated_judge
    return gated, judge, info


def _noop_defense(**_kwargs: Any) -> tuple[DefenseAction, dict[str, Any]]:
    return DefenseAction.NO_INTERVENTION, {}


def _run_stateful_episode(
    *,
    target_model: Any,
    model_id: str,
    seed: int,
    turn_messages: list[str],
) -> Any:
    from adapti_guard.evaluation.stateful_episode import StatefulEpisodeRunner, TurnSpec
    from adapti_guard.evaluation.stateful_target_adapter import target_fn_from_model

    specs = [TurnSpec(m) for m in turn_messages]
    runner = StatefulEpisodeRunner(experiment_id="canonical_live_stateful")
    return runner.run(
        specs,
        target=target_fn_from_model(target_model, model_id=model_id),
        defense=_noop_defense,
        seed=seed,
    )


def build_judge_evidence_record(
    *,
    execution_mode: ExecutionMode,
    target_model_id: str,
    judge_model_id: str,
    judge_config_key: str,
    authorization_allows_spend: bool,
) -> dict[str, Any]:
    """Static judge contract record — no LLM invocation (NOT_RUN until authorized)."""
    if execution_mode == "OFFLINE_MOCK":
        reason = "phase7_live_blocked_offline_mock"
    elif not authorization_allows_spend:
        reason = "authorization_incomplete"
    else:
        reason = "judge_llm_not_invoked_pre_authorization_audit"
    return {
        "status": "NOT_RUN",
        "execution_status": "NOT_RUN",
        "reason": reason,
        "target_model_id": target_model_id,
        "judge_model_id": judge_model_id,
        "judge_config_key": judge_config_key,
        "resolver": "adapti_guard.evaluation.live_model_resolver.resolve_judge",
        "pipeline": "adapti_guard.evaluation.llm_judge.build_judge",
        "target_raw_immutable": True,
        "parse_failure": None,
        "provider_failure": None,
    }


def _run_agent_episode(
    *,
    target_model: Any,
    model_id: str,
    seed: int,
) -> dict[str, Any]:
    from adapti_guard.defense.tool_loop import ToolCall
    from adapti_guard.evaluation.agent_environment import EXECUTION_MODE, AgentEnvironment
    from adapti_guard.evaluation.provider_errors import classify_generation_result
    from adapti_guard.evaluation.target_model import GenerationRequest

    env = AgentEnvironment(seed=seed)
    tool_req = ToolCall(name="send_email", arguments={"to": "a", "body": "b"})
    step = env.step(tool_req, DefenseAction.NO_INTERVENTION)
    target_result = target_model.generate(GenerationRequest(prompt="tool_step", model_id=model_id))
    return {
        "episode_type": "agent",
        "execution_mode": EXECUTION_MODE,
        "environment_execution_mode": env.execution_mode,
        "target_generation": classify_generation_result(target_result),
        "target_text": target_result.text,
        "tool_request": {"name": tool_req.name, "arguments": dict(tool_req.arguments)},
        "agent_step": {
            "step": step.step,
            "defense_action": step.defense_action,
            "tool_executed": step.tool_executed,
            "privileged_executed": step.privileged_executed,
            "state_hash": step.state_hash,
        },
        "tool_log": list(env.state.tool_log),
    }


def _eval_episode_to_dict(ep: Any) -> dict[str, Any]:
    from dataclasses import asdict

    return asdict(ep)


def _run_b2_multi_turn_episode(
    *,
    target_model: Any,
    model_id: str,
    seed: int,
    attack_mode: str,
    defense_mode: str,
    baseline_defense_fn: Any | None = None,
) -> Any:
    from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeRunner
    from adapti_guard.evaluation.b2_adaptive_contract import LIVE_WIRING_MAX_TURNS
    from adapti_guard.evaluation.b2_attack_mode_contract import build_attacker_for_mode
    from adapti_guard.evaluation.b2_matrix_contract import build_pre_target_defense_bundle
    from adapti_guard.evaluation.stateful_target_adapter import target_fn_from_model

    def _legacy_defense(**_kwargs: Any) -> tuple[DefenseAction, dict[str, Any]]:
        return DefenseAction.TOOL_RESTRICTION, {}

    if baseline_defense_fn is not None:
        pre_target_defense = baseline_defense_fn
    else:
        bundle = build_pre_target_defense_bundle(defense_mode)  # type: ignore[arg-type]
        if bundle.state is not None and hasattr(bundle.state, "reset"):
            bundle.state.reset()
        pre_target_defense = bundle.defense_fn
    target_fn = target_fn_from_model(target_model, model_id=model_id)
    attacker = build_attacker_for_mode(attack_mode, max_turns=LIVE_WIRING_MAX_TURNS)
    return AdaptiveEpisodeRunner(max_turns=LIVE_WIRING_MAX_TURNS).run(
        attacker=attacker,
        defense=_legacy_defense,
        seed=seed,
        target=target_fn,
        baseline_defense_fn=pre_target_defense,
    )


def run_live_condition(
    condition_id: str,
    *,
    run_id: str,
    run_dir: Path | None = None,
    seed: int = 0,
    trial: int = 0,
    target_config_key: str = "model_b",
    judge_config_key: str = "judge_primary",
    models_config: Path = Path("configs/models.yaml"),
    execution_mode: ExecutionMode = "LIVE",
    injected_target: Any | None = None,
    injected_judge: Callable[[Any], Any] | None = None,
    injected_b1_defense: Any | None = None,
    injected_ledger: Any | None = None,
    turn_messages: list[str] | None = None,
    attack_mode: str | None = None,
    defense_mode: str | None = None,
) -> CanonicalLiveRunResult:
    """
    Canonical orchestration: authorization → budget → target → generation → raw trace → derived.

    LIVE mode fails closed without authorization. OFFLINE_MOCK uses MockTargetModel or injected_target only.
    """
    from adapti_guard.evaluation.experiment_logging import write_json
    from adapti_guard.evaluation.live_eval_trace import (
        append_trace_line,
        base_trace_fields,
        write_raw_evidence,
    )
    from adapti_guard.evaluation.live_model_resolver import model_id_for_config_key, validate_target_judge_keys
    from adapti_guard.evaluation.b2_adaptive_contract import (
        finalize_b2_canonical_live_episode,
        is_b2_live_condition,
    )
    from adapti_guard.evaluation.target_model import MockTargetModel

    out_root = run_dir or (DEFAULT_LIVE_RUN_ROOT / run_id)
    out_root.mkdir(parents=True, exist_ok=True)
    trace_path = out_root / "logs" / "trace.jsonl"
    auth_snapshot_path = out_root / "authorization_snapshot.json"

    auth = load_authorization_yaml()
    gate = load_phase7_gate_json()
    write_json(
        auth_snapshot_path,
        {
            "authorization_yaml_status": auth.get("approval_status"),
            "api_spend_permitted_yaml": auth.get("api_spend_permitted"),
            "phase7_gate": gate.get("live_execution_gate"),
            "api_spend_permitted_json": gate.get("api_spend_permitted"),
        },
    )

    model_info = validate_target_judge_keys(target_config_key, judge_config_key, config_path=models_config)
    ledger = injected_ledger if injected_ledger is not None else budget_ledger_from_authorization(auth)
    allow_live = False
    blocked_reason: str | None = None
    live_llm_judge: Any | None = None

    if execution_mode == "OFFLINE_MOCK":
        target_model = injected_target or MockTargetModel(response="MOCK_LIVE_RUN")
        model_id = model_id_for_config_key(target_config_key, models_config) if not injected_target else "mock"
        judge_model_id = model_info["judge_model_id"]
        provider = "offline_mock"
    else:
        ok, reason = authorization_allows_live_spend()
        if not ok:
            raise LiveExtensionBlockedError(reason)
        allowed_ids = set(auth.get("allowed_condition_ids") or [])
        if condition_id not in allowed_ids:
            raise LiveExtensionBlockedError(
                f"authorization_failure: {condition_id} not in allowed_condition_ids"
            )
        plan_live_execution(condition_id)
        allow_live = True
        target_model, live_llm_judge, model_info = _resolve_gated_target(
            target_config_key=target_config_key,
            judge_config_key=judge_config_key,
            models_config=models_config,
            ledger=ledger,
            allow_live=True,
        )
        model_id = model_info["target_model_id"]
        judge_model_id = model_info["judge_model_id"]
        provider = getattr(target_model, "provider", "unknown")

    msgs = turn_messages or ["turn-1 stateful probe", "turn-2 stateful probe"]
    raw_paths: list[str] = []

    b2_finalize: dict[str, Any] | None = None
    if is_b2_live_condition(condition_id):
        from adapti_guard.evaluation.b2_attack_mode_contract import (
            build_attacker_turn_trace,
            extract_turn_supplementary_metrics,
            resolve_attack_mode,
        )
        from adapti_guard.evaluation.b2_matrix_contract import resolve_defense_mode

        resolved_attack_mode = resolve_attack_mode(condition_id, attack_mode)
        resolved_defense_mode = resolve_defense_mode(condition_id, defense_mode)
        episode_result = _run_b2_multi_turn_episode(
            target_model=target_model,
            model_id=model_id,
            seed=seed,
            attack_mode=resolved_attack_mode,
            defense_mode=resolved_defense_mode,
            baseline_defense_fn=injected_b1_defense,
        )
        attack_turn_trace = build_attacker_turn_trace(episode_result)
        supplementary_metrics = extract_turn_supplementary_metrics(episode_result.turns)
        judge_invoke: Callable[..., Any] | None = None
        if injected_judge is not None:
            judge_invoke = injected_judge
        elif live_llm_judge is not None:
            judge_invoke = live_llm_judge.judge
        from adapti_guard.evaluation.b2_adaptive_contract import b2_target_calls_for_episode

        if b2_target_calls_for_episode(episode_result) == 0 or judge_invoke is not None:
            b2_finalize = finalize_b2_canonical_live_episode(
                episode_result,
                experiment_id=run_id,
                condition_id=condition_id,
                target_model_id=model_id,
                judge_model_id=judge_model_id,
                judge_invoke=judge_invoke,
                ledger_spent_usd=ledger.spent_usd if ledger.spent_usd else None,
                provider=provider if execution_mode == "LIVE" else "openrouter",
            )
        raw_payload = {
            "condition_id": condition_id,
            "episode_type": "adaptive",
            "attack_mode": resolved_attack_mode,
            "defense_mode": resolved_defense_mode,
            "seed": seed,
            "trial": trial,
            "attack_turn_trace": list(attack_turn_trace),
            "supplementary_metrics": supplementary_metrics,
            "result": asdict(episode_result),
            "b2_evaluation": (
                {
                    "eval_episode": _eval_episode_to_dict(b2_finalize["eval_episode"]),
                    "metrics": b2_finalize["metrics"].to_dict(),
                    "provenance": b2_finalize["provenance"],
                    "target_calls": b2_finalize["target_calls"],
                    "judge_calls": b2_finalize["judge_calls"],
                }
                if b2_finalize
                else {"status": "DEFERRED", "reason": "target_executed_without_judge_invoke"}
            ),
        }
    elif condition_id in ("COND-E1-STATEFUL-OFFLINE", "COND-PHASE7-CAMPAIGN"):
        episode_result = _run_stateful_episode(
            target_model=target_model,
            model_id=model_id,
            seed=seed,
            turn_messages=msgs,
        )
        raw_payload = {
            "condition_id": condition_id,
            "episode_type": "stateful",
            "seed": seed,
            "trial": trial,
            "turn_count": episode_result.n_turns,
            "turns": [asdict(t) for t in episode_result.turns],
            "config_hash": episode_result.config_hash,
        }
    elif condition_id == "COND-E3-AGENT-OFFLINE":
        agent_payload = _run_agent_episode(target_model=target_model, model_id=model_id, seed=seed)
        raw_payload = {
            "condition_id": condition_id,
            "seed": seed,
            "trial": trial,
            **agent_payload,
        }
    elif condition_id == "COND-EXT6-BASELINE":
        raise LiveExtensionBlockedError(
            "configuration_failure: COND-EXT6-BASELINE external_baselines_design_only — use offline protocol registry"
        )
    else:
        raise LiveExtensionBlockedError(f"resolution_failure: condition {condition_id} not wired for canonical live runner")

    raw_path = write_raw_evidence(out_root, "episode_raw.json", raw_payload)
    raw_paths.append(str(raw_path))

    auth_ok, _auth_reason = authorization_allows_live_spend()
    if b2_finalize is not None and b2_finalize.get("judge_verdict") is not None:
        verdict = b2_finalize["judge_verdict"]
        judge_raw = {
            "status": "OK",
            "execution_status": "OK",
            "reason": "b2_episode_end_judge",
            "target_model_id": model_id,
            "judge_model_id": judge_model_id,
            "judge_config_key": judge_config_key,
            "pipeline": "b2_adaptive_contract.build_b2_judge_input+finalize",
            "verdict": verdict.to_dict(),
            "target_raw_immutable": True,
        }
    elif b2_finalize is not None and b2_finalize["target_calls"] == 0:
        judge_raw = {
            "status": "NOT_APPLICABLE",
            "execution_status": "NOT_RUN",
            "reason": "blocked_only_episode_no_target_calls",
            "target_model_id": model_id,
            "judge_model_id": judge_model_id,
            "judge_config_key": judge_config_key,
            "pipeline": "b2_adaptive_contract.synthesize_b2_eval_episode",
            "target_raw_immutable": True,
        }
    else:
        judge_raw = build_judge_evidence_record(
            execution_mode=execution_mode,
            target_model_id=model_id,
            judge_model_id=judge_model_id,
            judge_config_key=judge_config_key,
            authorization_allows_spend=auth_ok,
        )
    judge_path = write_raw_evidence(out_root, "judge_raw.json", judge_raw)
    raw_paths.append(str(judge_path))

    trace_record = {
        **base_trace_fields(
            run_id=run_id,
            experiment_id=condition_id,
            condition_id=condition_id,
            phase="phase7_live_infra",
            stage="offline_mock" if execution_mode == "OFFLINE_MOCK" else "live",
            provider=provider,
            model_id=model_id,
            judge_model_id=judge_model_id,
            seed=seed,
            trial=trial,
        ),
        "execution_mode": execution_mode,
        "status": "ok",
        "requests_used": ledger.requests_used,
        "retry_count": max(0, ledger.requests_used - 1) if ledger.requests_used else 0,
        "target_config_key": target_config_key,
        "judge_config_key": judge_config_key,
        "raw_evidence": raw_paths[0],
    }
    append_trace_line(trace_path, trace_record)

    derived_dir = out_root / "derived"
    derived_dir.mkdir(parents=True, exist_ok=True)
    if b2_finalize is not None:
        m = b2_finalize["metrics"]
        b2_prov = dict(b2_finalize["provenance"])
        if is_b2_live_condition(condition_id):
            b2_prov["attack_mode"] = resolved_attack_mode
            b2_prov["defense_mode"] = resolved_defense_mode
            b2_prov.update(supplementary_metrics)
        derived_metrics = {
            "asr": m.asr,
            "defense_rate": m.defense_rate,
            "utility": m.utility,
            "judge_status": judge_raw.get("status"),
            "multi_turn_success_semantics": b2_finalize["provenance"]["multi_turn_success_semantics"],
            "b2_provenance": b2_prov,
            "requests_used": ledger.requests_used,
            "raw_evidence_order": raw_paths,
        }
    else:
        derived_metrics = {
            "asr": "DEFERRED",
            "defense_rate": "DEFERRED",
            "utility": "DEFERRED",
            "judge_status": judge_raw["status"],
            "note": "derived from raw evidence only after judge pass — not computed in infra dry path",
            "requests_used": ledger.requests_used,
            "raw_evidence_order": raw_paths,
        }
    derived_path = derived_dir / "metrics.json"
    write_json(derived_path, derived_metrics)

    return CanonicalLiveRunResult(
        run_id=run_id,
        condition_id=condition_id,
        execution_mode=execution_mode,
        status="ok",
        trace_path=str(trace_path),
        raw_evidence_paths=raw_paths,
        derived_metrics_path=str(derived_path),
        requests_used=ledger.requests_used,
        blocked_reason=blocked_reason,
    )
