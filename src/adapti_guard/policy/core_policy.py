"""Inspectable Phase 1 core policy table (action-sensitive).

Independent of the detector. Does not replace historical DefensePolicyEngine
used by Layer A / VNEXT-ADAPT.

Principle: minimum effective security intervention given risk + requested action.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.adapti_guard.core.models import DefenseAction, RiskAssessment, RiskLevel
from src.adapti_guard.policy.policy_engine import PolicyDecision


@dataclass(frozen=True)
class CorePolicyRule:
    risk: str
    action_class: str
    action: str
    reason: str


# action_class: none | any_tool | privileged
CORE_POLICY_RULES: tuple[CorePolicyRule, ...] = (
    CorePolicyRule("HIGH", "none", "A3", "core_high_block"),
    CorePolicyRule("HIGH", "any_tool", "A2", "core_high_tool_deny"),
    CorePolicyRule("HIGH", "privileged", "A2", "core_high_privileged_tool_deny"),
    CorePolicyRule("MEDIUM", "privileged", "A2", "core_medium_privileged_tool_deny"),
    CorePolicyRule("MEDIUM", "any_tool", "A2", "core_medium_tool_deny"),
    CorePolicyRule("MEDIUM", "none", "A1", "core_medium_sanitize_text_only"),
    CorePolicyRule("LOW", "privileged", "A0", "core_low_privileged_allow"),
    CorePolicyRule("LOW", "any_tool", "A0", "core_low_tool_allow"),
    CorePolicyRule("LOW", "none", "A0", "core_low_allow"),
)


class CorePolicyEngine:
    """Maps risk + observable action sensitivity + adaptive level → A0–A3."""

    rules = CORE_POLICY_RULES

    def decide(
        self,
        risk: RiskAssessment,
        *,
        privileged_tool: bool = False,
        tool_declared: bool = False,
        defense_level: int = 0,
    ) -> PolicyDecision:
        if defense_level not in (0, 1, 2, 3):
            raise ValueError(f"Unsupported defense level: {defense_level}")

        any_tool = bool(tool_declared or privileged_tool)

        if risk.level == RiskLevel.HIGH:
            if any_tool:
                return PolicyDecision(
                    action=DefenseAction.TOOL_RESTRICTION,
                    reason=(
                        "core_high_privileged_tool_deny"
                        if privileged_tool
                        else "core_high_tool_deny"
                    ),
                )
            return PolicyDecision(
                action=DefenseAction.BLOCK,
                reason="core_high_block",
            )

        if risk.level == RiskLevel.MEDIUM:
            # Tool-mediated risk: deny the tool (A2). Text-only: sanitize (A1).
            if any_tool:
                return PolicyDecision(
                    action=DefenseAction.TOOL_RESTRICTION,
                    reason=(
                        "core_medium_privileged_tool_deny"
                        if privileged_tool
                        else "core_medium_tool_deny"
                    ),
                )
            if defense_level >= 3:
                return PolicyDecision(
                    action=DefenseAction.BLOCK,
                    reason="core_medium_level_3",
                )
            if defense_level >= 2:
                return PolicyDecision(
                    action=DefenseAction.TOOL_RESTRICTION,
                    reason="core_medium_level_2",
                )
            return PolicyDecision(
                action=DefenseAction.SANITIZE,
                reason="core_medium_sanitize_text_only",
            )

        # LOW: never A3. Benign tool workflows stay allowed.
        if any_tool:
            return PolicyDecision(
                action=DefenseAction.NO_INTERVENTION,
                reason=(
                    "core_low_privileged_allow"
                    if privileged_tool
                    else "core_low_tool_allow"
                ),
            )
        if defense_level >= 1:
            return PolicyDecision(
                action=DefenseAction.SANITIZE,
                reason="core_low_level_sanitize",
            )
        return PolicyDecision(
            action=DefenseAction.NO_INTERVENTION,
            reason="core_low_allow",
        )
