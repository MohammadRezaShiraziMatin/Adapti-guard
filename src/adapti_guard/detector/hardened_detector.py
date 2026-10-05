"""Hardened regex detector (Q1 H-3).

Subclass of :class:`PromptInjectionDetector` that adds input normalisation
and extra patterns for evasions the base detector misses (paraphrase,
non-English, spaced letters, base64, document-embedded notes). The base
detector is left unchanged because frozen experiments depend on it.

This is still a pattern matcher: it raises the cost of the evasions below
and nothing more. ``tests/test_hardened_detector.py`` records both what it
catches and what it still misses.
"""

from __future__ import annotations

import base64
import binascii
import re
import unicodedata

from adapti_guard.core.models import DetectionResult
from adapti_guard.detector.prompt_injection_detector import (
    PromptInjectionDetector,
)

_SPACED_LETTERS = re.compile(r"(?<!\w)(?:\w[ \t.\-_]){3,}\w(?!\w)")
_B64_TOKEN = re.compile(r"[A-Za-z0-9+/]{24,}={0,2}")

# Matched against the normalised, lower-cased text.
_EXTRA_PATTERNS: dict[str, list[str]] = {
    "ignore_previous_instructions": [
        r"\b(?:disregard|forget|set\s+aside|drop|abandon|discard)\b.{0,40}"
        r"\b(?:guidance|guidelines?|instructions?|rules?|directives?|"
        r"what\s+you\s+were\s+(?:told|given)|told\s+earlier)\b",
        r"\bforget\s+what\s+you\s+(?:were\s+told|know|learned)\b",
        r"\b(?:oubliez|oublie|ignorez|ignore)\b.{0,40}"
        r"\b(?:instructions?|consignes?|pr[eé]c[eé]d\w*|ce\s+qui\s+pr[eé]c[eè]de)\b",
        r"\b(?:ignora|ignore|olvida|olvide)\b.{0,30}\b(?:instrucciones|anteriores)\b",
        r"\b(?:ignoriere|vergiss|missachte)\b.{0,30}\b(?:anweisungen|befehle|regeln)\b",
        r"(?:忽略|无视|忘记|忽视).{0,12}(?:指令|指示|提示|规则|说明|之前|以前)",
    ],
    "secret_extraction": [
        r"\b(?:reveal|tell|say|give|repeat|spell|print|write|share|read)\b.{0,60}"
        r"\b(?:access\s+code|secret|password|passphrase|api\s+key|token|credentials?)\b",
        r"\b(?:repeat|translate|summari[sz]e|recite)\b.{0,50}"
        r"\b(?:initial|original|system|hidden)\s+(?:instructions?|prompt|message)\b",
        r"\b(?:repeat|recite|output)\b.{0,40}\bcodes?\b.{0,40}"
        r"\b(?:you\s+(?:hold|have|were\s+given)|your\s+instructions?)\b",
        r"\bcode\s+d['’ ]?acc[eè]s\b",
        r"(?:泄露|透露|告诉我|说出).{0,12}(?:密码|密钥|口令|提示词|系统提示|访问码)",
    ],
    "authority_impersonation": [
        r"\b(?:admin|administrator|system|developer|operator)\s+"
        r"(?:has\s+|have\s+)?(?:authori[sz]ed|approved|allows?|permits?)\b",
    ],
    "tool_context_attack": [
        r"\b(?:notes?|messages?|instructions?)\s+(?:to|for)\s+(?:the\s+)?"
        r"(?:ai|assistant|model|llm|agent|reader)\b",
        r"\b(?:note|message)\s+for\s+the\s+ai\b",
        r"\b(?:include|append|add|insert|output|reply\s+with)\b.{0,40}"
        r"\b(?:the\s+)?(?:exact\s+)?(?:token|string|word|phrase|marker)\s+\S+",
    ],
}
_EXTRA_COMPILED = {
    cat: [re.compile(p) for p in pats] for cat, pats in _EXTRA_PATTERNS.items()
}

EXTRA_SCORE = 0.6


def normalize(text: str) -> str:
    """NFKC-normalise, drop format characters, rejoin spaced letters."""
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    return _SPACED_LETTERS.sub(
        lambda m: re.sub(r"[ \t.\-_]", "", m.group(0)), text
    )


def _decoded_payloads(text: str) -> list[str]:
    out = []
    for token in _B64_TOKEN.findall(text):
        try:
            raw = base64.b64decode(token + "=" * (-len(token) % 4), validate=True)
            decoded = raw.decode("utf-8")
        except (binascii.Error, UnicodeDecodeError, ValueError):
            continue
        if decoded and sum(c.isprintable() for c in decoded) / len(decoded) > 0.9:
            out.append(decoded)
    return out


class HardenedPromptInjectionDetector(PromptInjectionDetector):
    def _detect_one(self, text: str) -> DetectionResult:
        norm = normalize(text)
        base = super()._detect_one(norm)
        score = base.injection_probability
        indicators = list(base.indicators)

        lowered = norm.lower()
        for category, patterns in _EXTRA_COMPILED.items():
            if any(p.search(lowered) for p in patterns):
                score = max(score, EXTRA_SCORE)
                if category not in indicators:
                    indicators.append(category)

        for decoded in _decoded_payloads(norm):
            inner = self._detect_one(decoded)
            if inner.injection_probability >= 0.25:
                score = max(score, inner.injection_probability)
                if "encoded_payload" not in indicators:
                    indicators.append("encoded_payload")

        return DetectionResult(
            injection_probability=round(min(score, 1.0), 3),
            indicators=indicators,
        )
