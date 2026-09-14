"""Label-blind core risk: v4 probability bands plus observable privilege features.

Does not read is_attack, label, category, or ground-truth outcomes.
Does not change the v4 HIGH/MEDIUM thresholds (0.60 / 0.25).
"""

from __future__ import annotations

from typing import Any, Mapping

from src.adapti_guard.core.models import RiskAssessment, RiskLevel

_FORBIDDEN = frozenset({"is_attack", "label", "gold_label", "category"})


class RiskEngineCore:
    version = "risk_core_phase1.0"
    high_threshold = 0.60
    medium_threshold = 0.25

    def assess(
        self,
        detection,
        metadata: Mapping[str, Any] | None = None,
        *,
        privileged_tool: bool = False,
        tool_name: str | None = None,
        **kwargs: Any,
    ) -> RiskAssessment:
        if metadata:
            leaked = _FORBIDDEN.intersection(metadata.keys())
            if leaked:
                raise ValueError(f"gold metadata forbidden in RiskEngineCore: {sorted(leaked)}")
        leaked_kw = _FORBIDDEN.intersection(kwargs.keys())
        if leaked_kw:
            raise ValueError(f"gold kwargs forbidden in RiskEngineCore: {sorted(leaked_kw)}")

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
        reasons.append("core_monotonic_probability")
        if privileged_tool:
            reasons.append("privileged_tool_observable")

        return RiskAssessment(
            score=round(p, 3),
            level=level,
            features={
                "detection_score": round(p, 3),
                "privileged_tool": float(bool(privileged_tool)),
                "tool_name": tool_name or "",
                "v4_bands": 1.0,
            },
            reasons=reasons,
        )
