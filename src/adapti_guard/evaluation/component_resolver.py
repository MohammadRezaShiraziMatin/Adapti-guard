"""Resolve attack_id / defense_id / offline target to canonical implementations (Phase 4)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.core.models import DefenseAction
from adapti_guard.defense.tool_loop import ToolCall
from adapti_guard.evaluation.stateful_episode import TurnSpec
from adapti_guard.evaluation.target_model import GenerationRequest, GenerationResult, MockTargetModel, TargetModel
from adapti_guard.experiments.defense_baselines import get_defense_fn

DefenseFnStateful = Callable[..., tuple[DefenseAction | str, dict[str, Any]]]


class ComponentResolutionError(Exception):
    """resolution_failure or configuration_failure."""


class AttackKind(str, Enum):
    STATEFUL_TURNS = "stateful_turns"
    ADAPTIVE = "adaptive"
    TOOL_REQUEST = "tool_request"


@dataclass(frozen=True)
class ResolvedAttack:
    attack_id: str
    kind: AttackKind
    implementation: str
    turn_specs: tuple[TurnSpec, ...] | None = None
    tool_request: ToolCall | None = None


@dataclass(frozen=True)
class ResolvedDefense:
    defense_id: str
    implementation: str
    stateful_fn: DefenseFnStateful | None = None
    baseline_key: str | None = None


@dataclass(frozen=True)
class ResolvedOfflineTarget:
    target_model_id: str
    provider: str
    model_version: str
    model: TargetModel


def resolve_attack(attack_id: str) -> ResolvedAttack:
    if attack_id == "adaptive_attacker_fixture":
        return ResolvedAttack(
            attack_id=attack_id,
            kind=AttackKind.ADAPTIVE,
            implementation="adapti_guard.attacker.adaptive_attacker.AdaptiveAttacker",
        )
    if attack_id == "fixture":
        return ResolvedAttack(
            attack_id=attack_id,
            kind=AttackKind.STATEFUL_TURNS,
            implementation="adapti_guard.evaluation.stateful_episode.TurnSpec",
            turn_specs=(TurnSpec("hi"),),
        )
    if attack_id == "tool_fixture":
        return ResolvedAttack(
            attack_id=attack_id,
            kind=AttackKind.TOOL_REQUEST,
            implementation="adapti_guard.defense.tool_loop.ToolCall",
            tool_request=ToolCall(name="send_email", arguments={"to": "a", "body": "b"}),
        )
    if attack_id in ("vnext_confirm_v1.0", "phase1_confirm_v1"):
        raise ComponentResolutionError(
            f"resolution_failure: attack_id={attack_id} not available offline (live confirmatory pack)"
        )
    raise ComponentResolutionError(f"resolution_failure: unknown attack_id={attack_id}")


def resolve_defense(
    defense_id: str,
    *,
    adaptivity: str = "static",
) -> ResolvedDefense:
    if defense_id == "runtime_fixture":
        if adaptivity == "adaptive":
            action = DefenseAction.TOOL_RESTRICTION

            def _fn(**_kwargs: Any) -> tuple[DefenseAction, dict[str, Any]]:
                return action, {}

            return ResolvedDefense(
                defense_id=defense_id,
                implementation="adapti_guard.evaluation.component_resolver.runtime_fixture_adaptive",
                stateful_fn=_fn,
            )

        def _noop(**_kwargs: Any) -> tuple[DefenseAction, dict[str, Any]]:
            return DefenseAction.NO_INTERVENTION, {}

        return ResolvedDefense(
            defense_id=defense_id,
            implementation="adapti_guard.evaluation.component_resolver.runtime_fixture_static",
            stateful_fn=_noop,
        )

    try:
        _fn_baseline, _state = get_defense_fn(defense_id)
    except KeyError:
        raise ComponentResolutionError(f"resolution_failure: unknown defense_id={defense_id}") from None

    def _bridge(**kwargs: Any) -> tuple[DefenseAction | str, dict[str, Any]]:
        prompt = str(kwargs.get("prompt", ""))
        context = kwargs.get("context")
        action, blocked, content = _fn_baseline(prompt, context)
        if blocked:
            return DefenseAction.BLOCK, {"baseline_action": action, "blocked": True}
        return DefenseAction.NO_INTERVENTION, {"baseline_action": action, "content": content}

    return ResolvedDefense(
        defense_id=defense_id,
        implementation=f"adapti_guard.experiments.defense_baselines.get_defense_fn({defense_id})",
        stateful_fn=_bridge,
        baseline_key=defense_id,
    )


def resolve_offline_target(target_model_id: str, *, allow_error_target: bool = False) -> ResolvedOfflineTarget:
    if target_model_id == "mock_target":
        model: TargetModel
        if allow_error_target:
            model = _ErrorTargetModel()
        else:
            model = MockTargetModel(response="ack")
        return ResolvedOfflineTarget(
            target_model_id=target_model_id,
            provider="mock",
            model_version="offline",
            model=model,
        )
    raise ComponentResolutionError(
        f"configuration_failure: target_model_id={target_model_id} requires live provider; blocked offline"
    )


def run_target_generate(
    resolved: ResolvedOfflineTarget,
    *,
    prompt: str,
    seed: int,
) -> dict[str, Any]:
    """Execute TargetModel once; map failures to explicit status (not attack outcome)."""
    req = GenerationRequest(prompt=prompt, model_id=resolved.target_model_id, metadata={"seed": seed})
    try:
        result = resolved.model.generate(req)
    except Exception as exc:  # noqa: BLE001 — explicit target failure bucket
        return {
            "target_model_id": resolved.target_model_id,
            "provider": resolved.provider,
            "model_version": resolved.model_version,
            "execution_status": "execution_error",
            "failure_type": type(exc).__name__,
            "failure_message": str(exc),
            "text": None,
        }
    if result.error:
        return {
            "target_model_id": resolved.target_model_id,
            "provider": resolved.provider,
            "model_version": resolved.model_version,
            "execution_status": "provider_error",
            "failure_type": result.error,
            "text": result.text or None,
            "latency_ms": result.latency_ms,
        }
    if not (result.text or "").strip() and not result.raw:
        return {
            "target_model_id": resolved.target_model_id,
            "provider": resolved.provider,
            "model_version": resolved.model_version,
            "execution_status": "invalid_response",
            "failure_type": "empty_output",
            "text": result.text,
            "latency_ms": result.latency_ms,
        }
    return {
        "target_model_id": resolved.target_model_id,
        "provider": resolved.provider,
        "model_version": resolved.model_version,
        "execution_status": "ok",
        "failure_type": None,
        "text": result.text,
        "latency_ms": result.latency_ms,
        "model_id_reported": result.model_id,
    }


def stateful_target_fn(resolved: ResolvedOfflineTarget, *, seed: int) -> Callable[[list[dict[str, str]], str], str]:
    def _fn(_history: list[dict[str, str]], user_message: str) -> str:
        rec = run_target_generate(resolved, prompt=user_message, seed=seed)
        if rec["execution_status"] != "ok":
            raise TargetExecutionFailure(rec)
        return str(rec["text"])

    return _fn


class TargetExecutionFailure(Exception):
    """Target failed; carries machine-readable record (not attack_success)."""

    def __init__(self, record: dict[str, Any]) -> None:
        self.record = record
        super().__init__(record.get("failure_type") or record.get("execution_status"))


class _ErrorTargetModel(TargetModel):
    def generate(self, request: GenerationRequest) -> GenerationResult:
        return GenerationResult(
            text="",
            model_id=request.model_id or "mock",
            latency_ms=0.0,
            error="provider_error",
        )
