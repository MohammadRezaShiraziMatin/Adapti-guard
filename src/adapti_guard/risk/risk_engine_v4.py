"""v4 risk mapping: monotonic in detector probability.

Historical ``RiskEngine`` compresses PROMPT_INJECTION as
``0.70 * p * 0.8``, so p=1.0 cannot reach HIGH. That mapping remains
for Layer A v2/v3 reproducibility.

v4 maps detection probability to risk bands without label use:
HIGH if p >= 0.60, MEDIUM if p >= 0.25, else LOW.
"""

from __future__ import annotations

from typing import Any, Optional

from src.adapti_guard.core.models import RiskAssessment, RiskLevel


class RiskEngineV4:
    version = "risk_v4.0"
    high_threshold = 0.60
    medium_threshold = 0.25

    def assess(
        self,
        detection,
        metadata: Optional[dict[str, Any]] = None,
        **_kwargs,
    ) -> RiskAssessment:
        del metadata
        p = float(
            getattr(
                detection,
                "injection_probability",
                getattr(detection, "score", 0.0),
            )
        )
        p = max(0.0, min(1.0, p))
        if p >= self.high_threshold:
            level = RiskLevel.HIGH
        elif p >= self.medium_threshold:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        reasons = list(getattr(detection, "indicators", []) or [])
        reasons.append("v4_monotonic_probability")
        return RiskAssessment(
            score=round(p, 3),
            level=level,
            features={"detection_score": round(p, 3), "v4": 1.0},
            reasons=reasons,
        )
