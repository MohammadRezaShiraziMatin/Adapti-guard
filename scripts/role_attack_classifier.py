"""Conservative Role Attack classifier for external benchmark imports.

Evidence hierarchy:
1. Official dataset label (TrustLLM jailbreak subclass ``scenario``)
2. Explicit persona/role-play mechanism in prompt text
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# TrustLLM jailbreak subclass for scenario / role-play based attacks.
TRUSTLLM_SCENARIO_LABEL = "scenario"

# Semantic evidence of persona/role mechanism (required alongside official label).
PERSONA_MECHANISM = re.compile(
    r"(?:"
    r"\blets play a game\b|\blet's play a game\b|"
    r"\bfrom now on\b|"
    r"\bact as (?:a |an )?(?:completely )?(?:different )?(?:kind of )?(?:AI|assistant|chatbot|model|character)|"
    r"\bpretend (?:you are|to be)\b|"
    r"\byou are (?:a |an )?(?:typical )?(?:\w+ ){0,6}(?:user|character|assistant|AI|model|persona)\b|"
    r"\bcontinue as (?:the )?(?:\w+ ){0,3}(?:language model|AI|character|persona)\b|"
    r"\b(?:named|called)\s+[\"']?(?:Kevin|DAN|STAN|PersonGPT|BetterDAN|BH|VIOLET|AIM|UCAR)|"
    r"\broleplay as\b|\brole-play as\b|"
    r"\bcompletely different kind of AI\b|"
    r"\bfree of all restrictions\b|"
    r"\bwill prefix all your answers as\b|"
    r"\bI want you to act as\b|"
    r"\banswer every question in two ways\b|"
    r"\bPlease simulate an AI\b|"
    r"\bsimulate (?:an AI|a language model)\b|"
    r"\bDeveloper Mode\b|\bBetterDAN\b|\bPersonGPT\b"
    r")",
    re.I | re.S,
)


@dataclass
class RoleAttackDecision:
    is_role_attack: bool
    reason: str
    evidence: list[str]


def classify_trustllm_jailbreak_record(record: dict[str, Any]) -> RoleAttackDecision:
    """Classify a TrustLLM jailbreak.json record as role_attack or exclude."""
    labels = record.get("label") or []
    text = str(record.get("prompt") or "").strip()
    evidence: list[str] = []

    if not text:
        return RoleAttackDecision(False, "empty_prompt", [])

    if TRUSTLLM_SCENARIO_LABEL not in labels:
        return RoleAttackDecision(
            False,
            "missing_official_scenario_label",
            [f"labels={labels}"],
        )

    evidence.append("trustllm_label:scenario")

    if not PERSONA_MECHANISM.search(text):
        return RoleAttackDecision(
            False,
            "scenario_without_persona_mechanism",
            evidence,
        )

    evidence.append("persona_mechanism:regex_match")
    return RoleAttackDecision(True, "trustllm_scenario_with_persona_mechanism", evidence)
