"""Phase 1 core pipeline: detect → risk → policy → action → tool gate → trace."""

from __future__ import annotations

from typing import Any, Mapping

from src.adapti_guard.core.episode import (
    ContextBuilder,
    EpisodeInput,
    EpisodeTrace,
)
from src.adapti_guard.core.models import DefenseAction
from src.adapti_guard.defense.action_layer import DefenseActionLayer
from src.adapti_guard.defense.tool_loop import MockToolRegistry, ToolCall
from src.adapti_guard.defense.tool_permission import ToolPermissionGate
from src.adapti_guard.detector.prompt_injection_detector_phase1 import (
    PromptInjectionDetectorPhase1,
)
from src.adapti_guard.policy.core_policy import CorePolicyEngine
from src.adapti_guard.risk.risk_engine_core import RiskEngineCore


class CoreDefensePipeline:
    def __init__(
        self,
        *,
        detector=None,
        risk_engine=None,
        policy_engine=None,
        action_layer=None,
        permission_gate=None,
        context_builder=None,
        defense_level: int = 0,
    ) -> None:
        self.detector = detector or PromptInjectionDetectorPhase1()
        self.risk_engine = risk_engine or RiskEngineCore()
        self.policy_engine = policy_engine or CorePolicyEngine()
        self.action_layer = action_layer or DefenseActionLayer()
        self.permission_gate = permission_gate or ToolPermissionGate()
        self.context_builder = context_builder or ContextBuilder()
        self.defense_level = defense_level

    def run(
        self,
        inp: EpisodeInput | Mapping[str, Any],
        *,
        registry: MockToolRegistry | None = None,
        requested: ToolCall | None = None,
        defense_level: int | None = None,
    ) -> EpisodeTrace:
        ctx = self.context_builder.build(inp)
        level = self.defense_level if defense_level is None else defense_level
        detection = self.detector.detect_episode(
            ctx.prompt,
            ctx.context,
            tool_name=ctx.tool_name,
            tool_output=ctx.tool_output,
        )
        risk = self.risk_engine.assess(
            detection,
            privileged_tool=ctx.privileged_tool,
            tool_name=ctx.tool_name,
            tool_declared=bool(ctx.tool_name),
        )
        decision = self.policy_engine.decide(
            risk,
            privileged_tool=ctx.privileged_tool,
            tool_declared=bool(ctx.tool_name),
            defense_level=level,
        )
        defense = self.action_layer.execute(decision.action, ctx.prompt)
        action_value = (
            decision.action.value
            if isinstance(decision.action, DefenseAction)
            else str(decision.action)
        )
        blocked = not defense.allowed
        tool = requested
        if tool is None and ctx.tool_name:
            tool = ToolCall(name=ctx.tool_name, arguments=dict(ctx.tool_arguments or {}))
        tools = registry if registry is not None else MockToolRegistry()
        turn = self.permission_gate.apply(
            requested=tool,
            action=decision.action,
            registry=tools,
        )
        return EpisodeTrace(
            prompt=ctx.prompt,
            context_present=bool(ctx.context),
            tool_name=ctx.tool_name,
            privileged_tool=ctx.privileged_tool,
            detector_probability=float(detection.injection_probability),
            detector_indicators=list(detection.indicators or []),
            detector_hit=bool(getattr(detection, "is_injection", False)),
            risk_score=float(risk.score),
            risk_level=str(risk.level.value if hasattr(risk.level, "value") else risk.level),
            risk_reasons=list(risk.reasons or []),
            risk_features=dict(risk.features or {}),
            policy_action=action_value,
            policy_reason=decision.reason,
            defense_level=level,
            blocked=blocked,
            allowed=bool(defense.allowed),
            content=defense.content,
            tool_access=bool(defense.tool_access),
            tool_requested=turn.requested.name if turn.requested else None,
            tool_permission_allowed=turn.permission_allowed if turn.requested else None,
            tool_executed=bool(turn.executed),
            tool_observation=turn.observation,
            tool_reason=(turn.log or {}).get("reason"),
        )
