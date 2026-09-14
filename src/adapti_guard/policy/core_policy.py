"""Inspectable Phase 1 core policy table.

Independent of the detector. Does not replace historical DefensePolicyEngine
used by Layer A / VNEXT-ADAPT.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.adapti_guard.core.models import DefenseAction, RiskAssessment, RiskLevel
from src.adapti_guard.policy.policy_engine import PolicyDecision


@dataclass(frozen=True)
class CorePolicyRule:
    risk: str
    privileged_tool: bool
    action: str
    reason: str


# Documented mapping (defense_level only refines MEDIUM without a privileged tool).
CORE_POLICY_RULES: tuple[CorePolicyRule, ...] = (
    CorePolicyRule("HIGH", False, "A3", "core_high_block"),
    CorePolicyRule("HIGH", True, "A2", "core_high_privileged_tool_deny"),
    CorePolicyRule("MEDIUM", True, "A2", "core_medium_privileged_tool_deny"),
    CorePolicyRule("MEDIUM", False, "A1", "core_medium_sanitize"),
    CorePolicyRule("LOW", True, "A0", "core_low_privileged_allow"),
    CorePolicyRule("LOW", False, "A0", "core_low_allow"),
)


class CorePolicyEngine:
    """Maps risk + observable privilege + adaptive level → A0–A3."""

    rules = CORE_POLICY_RULES

    def decide(
        self,
        risk: RiskAssessment,
        *,
        privileged_tool: bool = False,
        defense_level: int = 0,
    ) -> PolicyDecision:
        if defense_level not in (0, 1, 2, 3):
            raise ValueError(f"Unsupported defense level: {defense_level}")

        if risk.level == RiskLevel.HIGH:
            if privileged_tool:
                return PolicyDecision(
                    action=DefenseAction.TOOL_RESTRICTION,
                    reason="core_high_privileged_tool_deny",
                )
            return PolicyDecision(
                action=DefenseAction.BLOCK,
                reason="core_high_block",
            )

        if risk.level == RiskLevel.MEDIUM:
            if privileged_tool:
                return PolicyDecision(
                    action=DefenseAction.TOOL_RESTRICTION,
                    reason="core_medium_privileged_tool_deny",
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
                reason="core_medium_sanitize",
            )

        # LOW: never A3. Privileged benign tools stay allowed.
        if privileged_tool:
            return PolicyDecision(
                action=DefenseAction.NO_INTERVENTION,
                reason="core_low_privileged_allow",
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
