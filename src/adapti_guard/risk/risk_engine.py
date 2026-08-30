from typing import Any, Optional

from src.adapti_guard.core.models import (
    RiskAssessment,
    RiskLevel,
)


class RiskEngine:

    ATTACK_WEIGHTS = {
        "PROMPT_INJECTION": 0.8,
        "SYSTEM_PROMPT_EXTRACTION": 1.0,
        "JAILBREAK": 1.0,
        "ROLE_ATTACK": 0.9,
        "CONTEXT_ATTACK": 0.9,
        "RAG_ATTACK": 0.9,
        "MULTI_ATTACK": 1.0,
    }

    def assess(
        self,
        detection,
        metadata: Optional[dict[str, Any]] = None,
        *,
        contextual_risk: float = 0.0,
        tool_sensitive: bool = False,
        historical_attack: float = 0.0,
    ) -> RiskAssessment:

        metadata = dict(metadata or {})

        # Backward-compatible metadata extraction.
        attack_type = metadata.get("attack_type", "PROMPT_INJECTION")
        if not detection.indicators and attack_type == "PROMPT_INJECTION":
            attack_type = "NONE"

        # Detection signal.
        detection_score = float(
            getattr(
                detection,
                "injection_probability",
                getattr(detection, "score", 0.0),
            )
        )

        contextual_risk = max(0.0, min(1.0, float(contextual_risk)))
        historical_attack = max(0.0, min(1.0, float(historical_attack)))

        # Weighted security score.
        weight = self.ATTACK_WEIGHTS.get(
            attack_type,
            0.8,
        )

        if attack_type == "NONE" and detection_score < 0.25:
            base_score = detection_score
        else:
            base_score = detection_score * weight

        # Context and history increase risk.
        score = (
            0.70 * base_score
            + 0.20 * contextual_risk
            + 0.25 * historical_attack
        )

        # Sensitive tools increase risk.
        if tool_sensitive:
            score += 0.15

        score = max(0.0, min(1.0, score))

        # Explicit attack indicators should not remain LOW.
        if detection_score >= 0.25 and score < 0.25:
            score = 0.25

        if attack_type in {
            "SYSTEM_PROMPT_EXTRACTION",
            "JAILBREAK",
            "MULTI_ATTACK",
        }:
            score = max(score, 0.75)

        if score >= 0.60:
            level = RiskLevel.HIGH
        elif score >= 0.25:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        features = {
            "detection_score": round(detection_score, 3),
            "contextual_risk": round(contextual_risk, 3),
            "historical_attack": round(historical_attack, 3),
            "tool_sensitive": float(tool_sensitive),
        }

        reasons = list(getattr(detection, "indicators", []))

        if contextual_risk > 0:
            reasons.append("contextual_risk")

        if historical_attack > 0:
            reasons.append("historical_attack")

        if tool_sensitive:
            reasons.append("tool_sensitive")

        return RiskAssessment(
            score=round(score, 3),
            level=level,
            features=features,
            reasons=reasons,
        )


RiskAssessmentEngine = RiskEngine
