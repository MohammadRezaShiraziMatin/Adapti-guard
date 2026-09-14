"""Label-blind core risk: evidence strength + action sensitivity.

Uses detector probability bands (same 0.25 / 0.60 cutoffs as v4) plus
observable privilege / evidence indicators. Never reads gold labels.
"""

from __future__ import annotations

from typing import Any, Mapping

from src.adapti_guard.core.models import RiskAssessment, RiskLevel

_FORBIDDEN = frozenset({"is_attack", "label", "gold_label", "category"})

_STRONG_EVIDENCE = frozenset(
    {
        "E1_agent_directed",
        "E2_hierarchy",
        "E3_goal_modification",
        "E4_tool",
        "E5_exfil",
        "E6_privilege",
        "E7_indirect",
        "E9_obfuscation",
        "forced_identifier",
        "tool_privilege_observable",
    }
)

# Floors require attack-like evidence beyond "user asked for a normal tool call".
_FLOOR_EVIDENCE = frozenset(
    {
        "E1_agent_directed",
        "E2_hierarchy",
        "E3_goal_modification",
        "E5_exfil",
        "E6_privilege",
        "E7_indirect",
        "E9_obfuscation",
        "forced_identifier",
    }
)


class RiskEngineCore:
    version = "risk_core_phase1.1"
    high_threshold = 0.60
    medium_threshold = 0.25

    def assess(
        self,
        detection,
        metadata: Mapping[str, Any] | None = None,
        *,
        privileged_tool: bool = False,
        tool_name: str | None = None,
        tool_declared: bool = False,
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
        indicators = list(getattr(detection, "indicators", []) or [])
        strong = sorted(_STRONG_EVIDENCE.intersection(indicators))
        floor_hits = sorted(_FLOOR_EVIDENCE.intersection(indicators))
        evidence_strength = len(strong)

        # Action sensitivity: declared tool presence is observable, not a label.
        any_tool = bool(tool_declared or tool_name)

        score = p
        reasons = list(indicators)
        reasons.append("core_monotonic_probability")

        if p >= self.medium_threshold and privileged_tool:
            reasons.append("privileged_tool_with_detection")
        if p >= self.medium_threshold and any_tool and not privileged_tool:
            reasons.append("declared_tool_with_detection")

        # Evidence-informed floor: attack-like evidence + privileged tool.
        # Do not floor on E4_tool alone (benign create_record / send_email requests).
        if p < self.medium_threshold and privileged_tool and floor_hits:
            score = max(score, self.medium_threshold)
            reasons.append("evidence_privilege_floor_medium")
        if p < self.high_threshold and privileged_tool and (
            "E5_exfil" in indicators or ("E2_hierarchy" in indicators and "E4_tool" in indicators)
        ):
            if score >= self.medium_threshold:
                score = max(score, self.high_threshold)
                reasons.append("evidence_privilege_floor_high")

        score = max(0.0, min(1.0, score))
        if score >= self.high_threshold:
            level = RiskLevel.HIGH
        elif score >= self.medium_threshold:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        if privileged_tool:
            reasons.append("privileged_tool_observable")

        return RiskAssessment(
            score=round(score, 3),
            level=level,
            features={
                "detection_score": round(p, 3),
                "risk_score": round(score, 3),
                "privileged_tool": float(bool(privileged_tool)),
                "tool_declared": float(bool(any_tool)),
                "tool_name": tool_name or "",
                "evidence_strength": float(evidence_strength),
                "v4_bands": 1.0,
            },
            reasons=reasons,
        )
