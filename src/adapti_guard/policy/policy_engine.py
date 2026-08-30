from dataclasses import dataclass

from src.adapti_guard.core.models import (
    DefenseAction,
    RiskAssessment,
    RiskLevel,
)


@dataclass
class PolicyDecision:
    action: DefenseAction
    reason: str


class DefensePolicyEngine:

    def decide(
        self,
        risk: RiskAssessment,
        tool_sensitive: bool = False,
        defense_level: int = 0,
    ) -> PolicyDecision:

        if defense_level not in (0, 1, 2, 3):
            raise ValueError(
                f"Unsupported defense level: {defense_level}"
            )

        # ==========================================================
        # HIGH RISK
        # ==========================================================
        #
        # High-risk requests remain strongly protected regardless
        # of adaptive level.
        #
        # ==========================================================

        if risk.level == RiskLevel.HIGH:

            if tool_sensitive:
                return PolicyDecision(
                    action=DefenseAction.TOOL_RESTRICTION,
                    reason="high_risk_sensitive_tool",
                )

            return PolicyDecision(
                action=DefenseAction.BLOCK,
                reason="high_risk_block",
            )

        # ==========================================================
        # MEDIUM RISK
        # ==========================================================
        #
        # Adaptive defense controls escalation.
        #
        # Level 0 -> Sanitize
        # Level 1 -> Sanitize
        # Level 2 -> Tool restriction
        # Level 3 -> Block
        #
        # ==========================================================

        if risk.level == RiskLevel.MEDIUM:

            if defense_level >= 3:
                return PolicyDecision(
                    action=DefenseAction.BLOCK,
                    reason="adaptive_medium_level_3",
                )

            if defense_level >= 2 or tool_sensitive:
                return PolicyDecision(
                    action=DefenseAction.TOOL_RESTRICTION,
                    reason="adaptive_medium_level_2",
                )

            return PolicyDecision(
                action=DefenseAction.SANITIZE,
                reason="medium_risk",
            )

        # ==========================================================
        # LOW RISK
        # ==========================================================
        #
        # CRITICAL UTILITY-AWARE RULE:
        #
        # Low-risk traffic must never be blocked solely because
        # the adaptive defense level is high.
        #
        # Adaptive level may increase protection, but the maximum
        # intervention for low-risk traffic is TOOL_RESTRICTION.
        #
        # This prevents the previous failure mode where legitimate
        # tasks were systematically blocked at defense level 3.
        #
        # ==========================================================

        if risk.level == RiskLevel.LOW:

            if tool_sensitive:
                return PolicyDecision(
                    action=DefenseAction.TOOL_RESTRICTION,
                    reason="low_risk_tool_sensitive",
                )

            if defense_level >= 2:
                return PolicyDecision(
                    action=DefenseAction.SANITIZE,
                    reason="adaptive_low_level_sanitize",
                )

            if defense_level == 1:
                return PolicyDecision(
                    action=DefenseAction.SANITIZE,
                    reason="adaptive_low_level_1",
                )

            return PolicyDecision(
                action=DefenseAction.NO_INTERVENTION,
                reason="low_risk",
            )

        raise ValueError(
            f"Unsupported risk level: {risk.level}"
        )
