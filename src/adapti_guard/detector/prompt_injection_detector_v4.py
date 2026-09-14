"""Layer A detector v4: evidence channels + primary-control gate.

Designed from TRAIN/DEV forensics only. Does not read frozen TEST text.
Does not use attack labels. Does not key on pack-specific canary literals.

Pipeline:
  INPUT → NORMALIZE → SEGMENT → DECODE → EVIDENCE → PRIMARY GATE → SCORE
"""

from __future__ import annotations

import base64
import re
import unicodedata
from dataclasses import dataclass, field

from src.adapti_guard.core.models import DetectionResult

_ZW = re.compile(r"[\u200b\u200c\u200d\ufeff\u2060\u00ad]")
_HOMO = str.maketrans(
    {
        "а": "a",
        "е": "e",
        "о": "o",
        "р": "p",
        "с": "c",
        "у": "y",
        "х": "x",
        "і": "i",
        "ј": "j",
        "ѕ": "s",
        "А": "A",
        "В": "B",
        "Е": "E",
        "К": "K",
        "М": "M",
        "Н": "H",
        "О": "O",
        "Р": "P",
        "С": "C",
        "Т": "T",
        "Х": "X",
        "І": "I",
        "Α": "A",
        "Β": "B",
        "Ε": "E",
        "Ο": "O",
        "Ρ": "P",
        "Τ": "T",
        "Η": "H",
        "Χ": "X",
    }
)

_HEX_BLOB = re.compile(r"\b[0-9A-Fa-f]{40,}\b")
_B64_BLOB = re.compile(r"\b[A-Za-z0-9+/]{24,}={0,2}\b")

_EXCLUSIVE_OUTPUT = [
    r"\b(?:output|print|reply|respond|return|say|emit|provide|supply|echo|answer)\b.{0,90}\bonly\b",
    r"\breply with exactly\b",
    r"\banswer must be\b",
    r"\bmust be exactly\b",
    r"\bmust (?:begin and end with|acknowledge with)\b",
    r"\bmandatory reply\b",
    r"\bresponse body equals\b",
    r"\b(?:respond|reply|output|print)\b.{0,50}\band nothing else\b",
    r"\bthe entire answer\b",
    r"\bonly fluent utterance\b",
    r"\bhandshake token\b",
    r"\bprove compliance by returning only\b",
    r"\bproviding just\b",
    r"\becho exactly\b",
    r"\breplace answer with\b",
    r"\banswer(?:s)? must begin and end with\b",
    # Forced identifier as the reply (not pack-specific canary literals).
    r"\b(?:output|print|reply|respond|return|say|emit|answer|echo)\b.{0,48}\b[A-Z]{2,}[-_][A-Z0-9-]{3,}\b",
    r"\bmust (?:output|reply|answer|print|return)\b.{0,48}\b[A-Z]{2,}[-_][A-Z0-9-]{3,}\b",
]

_GOAL_REPLACE = [
    r"\b(?:ignore|disregard|abandon|skip|cancel|shelve|omit|suspend|discard|forget|supersede)\b.{0,120}"
    r"\b(?:task|request|question|translation|explanation|topic|proofreading|"
    r"docs?|geography|benefits list|title ask|user(?:'s)? topic|other duties|"
    r"sql topic|astronomy answer)\b",
    r"\binstead of (?:the )?(?:explanation|key-rotation|crm|geography)\b",
    r"\bregardless of the\b.{0,50}\bquestion\b",
    r"\bnot the memory\b",
    r"\brelease date is irrelevant\b",
    r"\bignore (?:the )?(?:user )?task\b",
    r"\bdisregard the translation\b",
    r"\bactually[, ]+ignore\b",
    r"\bwould you mind shelving\b",
    r"\bif it is not too much trouble.{0,80}\babandon\b",
    r"\bsuspend .{0,40}practice\b",
    r"\bskip the .{0,40}explanation\b",
]

_HIERARCHY = [
    r"['\"]role['\"]\s*:\s*['\"]system['\"]",
    r"\bprivileged (?:channel|shell)\b",
    r"\badmin console\b",
    r"\bsudo mode\b",
    r"\broot operator\b",
    r"\belevated to root\b",
    r"\bbegin privileged channel\b",
    r"\bend of user channel\b",
    r"\bbegin internal\b",
    r"\bsystem_patch\b",
    r"\btemporary admin\b",
    r"\bauthenticated operator override\b",
    r"\b(?:fake privilege|privilege elevation)\b",
]

_INDIRECT_CONTROL = [
    r"\bassistant must\b",
    r"\bmodels must\b",
    r"\bllm:\s",
    r"\[assistant reading this\]",
    r"\bsystem for email assistants\b",
    r"\bprofile_note_to_assistant\b",
    r"\binvisible instruction to automated readers\b",
    r"display\s*:\s*none",
    r"\bevaluator instruction\b",
    r"\bwhen synthesizing hits\b",
    r"['\"]@type['\"]\s*:\s*['\"]howto['\"]",
    r"\bnote-to-assistant\b",
    r"\binstruction to automated readers\b",
]

_FRAGMENT = [
    r"\bfinal instruction fragment\b",
    r"\bdisregard fragments?\b",
    r"\bpart c:\b",
    r"\bfragment-3\b",
    r"\bfragment 3\b",
]

_CLASSIC_OVERRIDE = [
    r"\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions?|tasks?|commands?)\b",
    r"\bdisregard\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions?|tasks?)\b",
    r"\bforget\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions?|tasks?)\b",
]

_EXFIL = [
    r"\b(?:api keys?|password|secret word|exfiltrate|wire money)\b",
]

_TOOL_MANIP = [
    r"\bsearch_hits\b",
    r"\bwhen synthesizing hits\b",
    r"\bsystem for email assistants\b",
    r"\btool (?:result|output)\b.{0,80}\b(?:ignore|override|must)\b",
]

_E10_BENIGN = [
    r"\bdo not (?:follow|obey|execute)\b.{0,40}\b(?:it|them|student|either|embedded|quoted)\b",
    r"\bdo not follow (?:student prompts|either)\b",
    r"\bdo not obey it\b",
    r"\bdo not execute embedded\b",
    r"\bacademically\b",
    r"\bgrade whether each is\b",
    r"\blint this unit test\b",
    r"\breview comments in this pr\b",
    r"\breview this python snippet\b",
    r"\bcompare two example strings\b",
    r"\banalyze this attack string\b",
    r"\brewrite the malicious\b",
    r"\bclassroom exercise\b",
    r"\bassert detect\(",
    r"\bfind the string literal that looks like an injection\b",
    r"\bparse this log line\b",
    r"\bwhat are they trying to do\b",
    r"\bstudent question:\b",
    r"\bpeople online say\b",
]


def _search_any(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE | re.DOTALL) for p in patterns)


def normalize_text(text: str) -> str:
    if not text:
        return ""
    folded = unicodedata.normalize("NFKC", text).translate(_HOMO)
    folded = _ZW.sub("", folded)
    folded = re.sub(r"[ \t]+", " ", folded)
    return folded


def _try_decode_hex(blob: str) -> str | None:
    try:
        raw = bytes.fromhex(blob)
    except ValueError:
        return None
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not decoded or sum(ch.isprintable() or ch in "\n\t" for ch in decoded) < 0.9 * len(decoded):
        return None
    return decoded


def _try_decode_b64(blob: str) -> str | None:
    pad = "=" * ((4 - len(blob) % 4) % 4)
    try:
        raw = base64.b64decode(blob + pad, validate=False)
    except Exception:
        return None
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not decoded or sum(ch.isprintable() or ch in "\n\t" for ch in decoded) < 0.8 * len(decoded):
        return None
    return decoded


def decode_embedded_payloads(text: str) -> tuple[str, bool]:
    """Append decoded hex/base64 payloads. Returns (expanded_text, decoded_any)."""
    extras: list[str] = []
    for match in _HEX_BLOB.finditer(text):
        decoded = _try_decode_hex(match.group(0))
        if decoded and re.search(r"\b(ignore|output|instruction|task)\b", decoded, re.I):
            extras.append(decoded)
    for match in _B64_BLOB.finditer(text):
        blob = match.group(0)
        if re.fullmatch(r"[0-9A-Fa-f]+", blob):
            continue
        decoded = _try_decode_b64(blob)
        if decoded and re.search(r"\b(ignore|output|instruction|task)\b", decoded, re.I):
            extras.append(decoded)
    if not extras:
        return text, False
    return text + "\n" + "\n".join(extras), True


@dataclass
class EvidenceBundle:
    e1_agent_directed: bool = False
    e2_hierarchy: bool = False
    e3_goal_modification: bool = False
    e4_tool: bool = False
    e5_exfil: bool = False
    e6_privilege: bool = False
    e7_indirect: bool = False
    e8_multi_turn: bool = False
    e9_obfuscation: bool = False
    e10_benign_context: bool = False
    exclusive_output: bool = False
    forced_identifier: bool = False
    classic_override: bool = False
    decoded_payload: bool = False
    names: list[str] = field(default_factory=list)

    def primary_control(self) -> bool:
        """True only with agent-control evidence, not 'document contains an instruction'."""
        if self.e10_benign_context:
            return False
        if self.classic_override and not self.e10_benign_context:
            return True
        if self.exclusive_output and self.forced_identifier and not self.e10_benign_context:
            return True
        if (self.e2_hierarchy or self.e6_privilege) and (
            self.exclusive_output or self.e3_goal_modification or self.e1_agent_directed
        ):
            return True
        if self.e3_goal_modification and (self.exclusive_output or self.e1_agent_directed):
            return True
        if self.exclusive_output and (
            self.e7_indirect or self.e8_multi_turn or self.e4_tool or self.e3_goal_modification
        ):
            return True
        if self.e1_agent_directed and self.exclusive_output:
            return True
        return False


class PromptInjectionDetectorV4:
    """Evidence-structured detector. Version is independent of regex V18."""

    version = "evidence_v4.0"

    def detect(self, text: str) -> DetectionResult:
        return self.detect_episode(text or "", "")

    def detect_episode(
        self,
        prompt: str,
        context: str | None = None,
        *,
        tool_name: str | None = None,
        tool_output: str | None = None,
    ) -> DetectionResult:
        prompt_n = normalize_text(prompt or "")
        context_n = normalize_text(context or "")
        full = f"{context_n}\n\n{prompt_n}".strip() if context_n else prompt_n
        expanded, decoded = decode_embedded_payloads(full)
        expanded_l = expanded.lower()
        prompt_l = prompt_n.lower()
        context_l = context_n.lower()
        forced_identifier = bool(
            re.search(r"\b[A-Z]{2,}[-_][A-Z0-9-]{3,}\b", expanded)
        )

        ev = EvidenceBundle(decoded_payload=decoded, e9_obfuscation=decoded)
        if _ZW.search(prompt or "") or _ZW.search(context or ""):
            ev.e9_obfuscation = True
        if (prompt or "") != unicodedata.normalize("NFKC", prompt or "") or (
            context or ""
        ) != unicodedata.normalize("NFKC", context or ""):
            ev.e9_obfuscation = True

        ev.e10_benign_context = _search_any(_E10_BENIGN, prompt_l)
        ev.exclusive_output = _search_any(_EXCLUSIVE_OUTPUT, expanded_l)
        ev.forced_identifier = forced_identifier
        ev.classic_override = _search_any(_CLASSIC_OVERRIDE, expanded_l)
        ev.e3_goal_modification = ev.classic_override or _search_any(_GOAL_REPLACE, expanded_l)
        ev.e2_hierarchy = _search_any(_HIERARCHY, expanded_l)
        ev.e6_privilege = ev.e2_hierarchy or bool(
            re.search(r"\b(?:sudo mode|root operator|temporary admin)\b", expanded_l)
        )
        ev.e7_indirect = bool(context_n) and (
            _search_any(_INDIRECT_CONTROL, context_l) or _search_any(_INDIRECT_CONTROL, expanded_l)
        )
        ev.e4_tool = _search_any(_TOOL_MANIP, expanded_l)
        tool_out_n = normalize_text(tool_output or "").lower()
        if tool_out_n:
            if _search_any(_TOOL_MANIP, tool_out_n) or _search_any(
                _INDIRECT_CONTROL, tool_out_n
            ):
                ev.e4_tool = True
                ev.e7_indirect = True
        ev.e5_exfil = _search_any(_EXFIL, expanded_l) and ev.exclusive_output
        ev.e8_multi_turn = bool(
            re.search(r"\buser:", context_l) and re.search(r"\bassistant:", context_l)
        )
        ev.e1_agent_directed = bool(
            ev.classic_override
            or _search_any(_INDIRECT_CONTROL, expanded_l)
            or re.search(
                r"\b(?:you are now|you must now|assistant must|models must)\b",
                expanded_l,
            )
        )

        privilege_marker = bool(
            tool_name and tool_name in {"send_email", "create_record", "retrieve_document"}
        )

        if ev.e10_benign_context:
            ev.names = ["E10_benign_context"]
            if privilege_marker:
                ev.names.append("tool_privilege_observable")
            return DetectionResult(injection_probability=0.0, indicators=ev.names)

        if not ev.primary_control():
            # Obfuscation or a document instruction alone is not a blockable attack.
            names = self._names(ev)
            if names:
                names.append("no_primary_control")
            if privilege_marker:
                names.append("tool_privilege_observable")
            return DetectionResult(injection_probability=0.0, indicators=names)

        score = 0.45
        if ev.classic_override:
            score += 0.20
        if ev.e2_hierarchy or ev.e6_privilege:
            score += 0.15
        if ev.e7_indirect:
            score += 0.10
        if ev.e8_multi_turn:
            score += 0.05
        if ev.e9_obfuscation or ev.decoded_payload:
            score += 0.10
        if ev.e4_tool:
            score += 0.05
        if ev.e5_exfil:
            score += 0.10
        score = min(1.0, round(score, 3))
        names = self._names(ev)
        if privilege_marker:
            names.append("tool_privilege_observable")
        return DetectionResult(injection_probability=score, indicators=names)

    @staticmethod
    def _names(ev: EvidenceBundle) -> list[str]:
        mapping = [
            ("E1_agent_directed", ev.e1_agent_directed),
            ("E2_hierarchy", ev.e2_hierarchy),
            ("E3_goal_modification", ev.e3_goal_modification),
            ("E4_tool", ev.e4_tool),
            ("E5_exfil", ev.e5_exfil),
            ("E6_privilege", ev.e6_privilege),
            ("E7_indirect", ev.e7_indirect),
            ("E8_multi_turn", ev.e8_multi_turn),
            ("E9_obfuscation", ev.e9_obfuscation),
            ("E10_benign_context", ev.e10_benign_context),
        ]
        return [name for name, flag in mapping if flag]


# Default alias used by v4 eval scripts.
PromptInjectionDetector = PromptInjectionDetectorV4
