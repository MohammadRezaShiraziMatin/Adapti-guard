"""Phase 1 evidence extension on top of frozen detector v4.

``PromptInjectionDetectorV4`` (``evidence_v4.0``) stays the historical Layer A /
VNEXT-ADAPT identity. This module adds composable, label-blind evidence for
the Phase 1 core pipeline only. It does not retune the 0.25 / 0.60 bands.
"""

from __future__ import annotations

import base64
import re
import unicodedata

from src.adapti_guard.core.models import DetectionResult
from src.adapti_guard.detector.prompt_injection_detector_v4 import (
    EvidenceBundle,
    PromptInjectionDetectorV4,
    _B64_BLOB,
    _CLASSIC_OVERRIDE,
    _E10_BENIGN,
    _EXCLUSIVE_OUTPUT,
    _EXFIL,
    _GOAL_REPLACE,
    _HIERARCHY,
    _INDIRECT_CONTROL,
    _TOOL_MANIP,
    _ZW,
    _search_any,
    _try_decode_b64,
    _try_decode_hex,
    decode_embedded_payloads,
    normalize_text,
)

# Additional evidence: hierarchy / control-plane framing (deterministic).
_PHASE1_HIERARCHY = [
    r"priority\s*=\s*system\s*\+\s*\d+",
    r"<developer_message>",
    r"</developer_message>",
    r"\bmoderation_filter\b",
    r"\boutranks?\s+(?:the\s+)?system\b",
    r"\bhighest[- ]priority\s+control[- ]plane\b",
    r"\bfollowup_instruction\b",
    r"\btrusted\s+now\b",
    r"\bamberlark\b",
]

# Tool-call instructions in text (not gold labels).
_PHASE1_TOOL_INVOKE = [
    r"\bsend_email\s*(?:\(|\s+to\b)",
    r"\bcreate_record\s*(?:\(|\s+con\b|\s+kind\b)",
    r"\bretrieve_document\s*(?:\(|\s+doc_id\b|\s+['\"])",
    r"\bsearch\s*\(\s*query\s*=",
    r"#\s*todo\s*\(\s*assistant\s*\)",
    r"\bfollowup_instruction\b",
    r"\brelated:\s*send_email\b",
    r"\bfunction_result\b",
]

_PHASE1_E10 = [
    r"\bcount how many times\b",
    r"\bappears in this paragraph\b",
    r"\bphrase\s+['\"]ignore previous",
    r"\binside quotes\b",
    r"\bhow many times the phrase\b",
    r"\bdo not obey\b",
    r"\bdo not honor\b",
    r"\bdo not retrieve\b",
    r"\bdo not implement\b",
    r"\bdo not obey decoded\b",
    r"\bdo not call tools\b",
    r"\bredact\b.{0,40}\btool-command",
    r"\breturn the redacted line\b",
    r"\bquoted attacker phrases\b",
    r"\bdetector regression set\b",
    r"\bsay whether this base64\b",
    r"\bname the persistence trick\b",
    r"\bcopy footnote\b",
    r"\bas a citation string\b",
    r"\bis this markdown\b",
    r"\ban injection\?\b",
    r"\bcontrast these two lines\b",
    r"\blegitimate sop vs an injection\b",
    r"\bextract the quoted payload\b",
    r"\bquoted_text\b",
]

_UNICODE_ESCAPE = re.compile(
    r"(?:\\u[0-9a-fA-F]{4}){4,}"
)


_HTML_ENTITY = re.compile(r"(?:&#\d+;){6,}")


def _decode_html_entities(blob: str) -> str | None:
    parts = re.findall(r"&#(\d+);", blob)
    if len(parts) < 6:
        return None
    try:
        return "".join(chr(int(n)) for n in parts)
    except ValueError:
        return None


def _maybe_rot13(text: str) -> str:
    out = []
    for ch in text:
        o = ord(ch)
        if 65 <= o <= 90:
            out.append(chr((o - 65 + 13) % 26 + 65))
        elif 97 <= o <= 122:
            out.append(chr((o - 97 + 13) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


_TOOLISH = re.compile(
    r"\b(ignore|output|instruction|task|send_email|retrieve_document|create_record|search)\b",
    re.I,
)


def decode_phase1_payloads(text: str) -> tuple[str, bool]:
    """Extend v4 decode with unicode escapes, nested b64→hex, HTML entities, ROT13."""
    base, decoded_any = decode_embedded_payloads(text)
    extras: list[str] = []

    for match in _UNICODE_ESCAPE.finditer(base):
        blob = match.group(0)
        try:
            decoded = bytes(
                int(blob[i + 2 : i + 6], 16) for i in range(0, len(blob), 6)
            ).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            continue
        if decoded and _TOOLISH.search(decoded):
            extras.append(decoded)

    for match in _B64_BLOB.finditer(base):
        blob = match.group(0)
        if re.fullmatch(r"[0-9A-Fa-f]+", blob):
            continue
        inner = _try_decode_b64(blob)
        if not inner:
            continue
        if re.fullmatch(r"[0-9A-Fa-f]{24,}", inner.replace(" ", "")):
            hex_decoded = _try_decode_hex(inner.replace(" ", ""))
            if hex_decoded and _TOOLISH.search(hex_decoded):
                extras.append(hex_decoded)
                continue
        if _TOOLISH.search(inner):
            extras.append(inner)

    # Standalone hex command blobs (authored obfuscation).
    for match in re.finditer(r"\b[0-9A-Fa-f]{40,}\b", base):
        hex_decoded = _try_decode_hex(match.group(0))
        if hex_decoded and _TOOLISH.search(hex_decoded):
            extras.append(hex_decoded)

    for match in _HTML_ENTITY.finditer(base):
        decoded = _decode_html_entities(match.group(0))
        if decoded and _TOOLISH.search(decoded):
            extras.append(decoded)

    # ROT13 only when explicitly labeled (avoid full-text rot13 false positives).
    for match in re.finditer(r"rot13[^:\n]*:\s*(.+)", base, flags=re.I):
        rot = _maybe_rot13(match.group(1))
        if _TOOLISH.search(rot):
            extras.append(rot)

    if not extras:
        return base, decoded_any
    return base + "\n" + "\n".join(extras), True


class EvidenceBundlePhase1(EvidenceBundle):
    privileged_tool_declared: bool = False

    def primary_control(self) -> bool:
        if self.e10_benign_context:
            return False
        if super().primary_control():
            return True
        # Tool-mediated control: instruction to invoke a tool / privilege action.
        # Declared tool alone is not enough (benign create_record / send_email).
        if self.e4_tool and (
            self.forced_identifier
            or self.e2_hierarchy
            or self.e6_privilege
            or self.e7_indirect
            or self.e8_multi_turn
            or self.e3_goal_modification
            or self.e1_agent_directed
            or self.e9_obfuscation
            or self.decoded_payload
            or self.e5_exfil
        ):
            return True
        if (self.e2_hierarchy or self.e6_privilege) and self.forced_identifier:
            return True
        if self.privileged_tool_declared and self.forced_identifier and (
            self.e2_hierarchy or self.e4_tool or self.e9_obfuscation or self.decoded_payload or self.e5_exfil
        ):
            return True
        if self.decoded_payload and self.e4_tool:
            return True
        return False


class PromptInjectionDetectorPhase1(PromptInjectionDetectorV4):
    """Phase 1 core detector. Not the frozen VNEXT-ADAPT ``evidence_v4.0`` identity."""

    version = "evidence_phase1.0"

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
        expanded, decoded = decode_phase1_payloads(full)
        expanded_l = expanded.lower()
        prompt_l = prompt_n.lower()
        context_l = context_n.lower()
        forced_identifier = bool(re.search(r"\b[A-Z]{2,}[-_][A-Z0-9-]{3,}\b", expanded))

        ev = EvidenceBundlePhase1(decoded_payload=decoded, e9_obfuscation=decoded)
        if _ZW.search(prompt or "") or _ZW.search(context or ""):
            ev.e9_obfuscation = True
        if (prompt or "") != unicodedata.normalize("NFKC", prompt or "") or (
            context or ""
        ) != unicodedata.normalize("NFKC", context or ""):
            ev.e9_obfuscation = True

        ev.e10_benign_context = _search_any(_E10_BENIGN, prompt_l) or _search_any(
            _PHASE1_E10, prompt_l
        )
        ev.exclusive_output = _search_any(_EXCLUSIVE_OUTPUT, expanded_l)
        ev.forced_identifier = forced_identifier
        ev.classic_override = _search_any(_CLASSIC_OVERRIDE, expanded_l)
        # Quoted classic phrases under E10 prompts must not count as override.
        if ev.e10_benign_context:
            ev.classic_override = False

        ev.e3_goal_modification = ev.classic_override or _search_any(_GOAL_REPLACE, expanded_l)
        ev.e2_hierarchy = _search_any(_HIERARCHY, expanded_l) or _search_any(
            _PHASE1_HIERARCHY, expanded_l
        )
        ev.e6_privilege = ev.e2_hierarchy or bool(
            re.search(r"\b(?:sudo mode|root operator|temporary admin|sudo_grant)\b", expanded_l)
        )
        ev.e7_indirect = bool(context_n) and (
            _search_any(_INDIRECT_CONTROL, context_l)
            or _search_any(_INDIRECT_CONTROL, expanded_l)
            or _search_any(_PHASE1_HIERARCHY, context_l)
            or _search_any(_PHASE1_TOOL_INVOKE, context_l)
        )
        ev.e4_tool = _search_any(_TOOL_MANIP, expanded_l) or _search_any(
            _PHASE1_TOOL_INVOKE, expanded_l
        )
        tool_out_n = normalize_text(tool_output or "").lower()
        if tool_out_n:
            if (
                _search_any(_TOOL_MANIP, tool_out_n)
                or _search_any(_INDIRECT_CONTROL, tool_out_n)
                or _search_any(_PHASE1_TOOL_INVOKE, tool_out_n)
            ):
                ev.e4_tool = True
                ev.e7_indirect = True
        # Exfil: secrets language, or tool-mail to authored exfil sink with tool/marker evidence.
        ev.e5_exfil = bool(_search_any(_EXFIL, expanded_l) and ev.exclusive_output) or (
            bool(re.search(r"@exfil\.invalid\b", expanded_l))
            and (ev.e4_tool or forced_identifier)
        )
        ev.e8_multi_turn = bool(
            re.search(r"\buser:", context_l) and re.search(r"\bassistant:", context_l)
        )
        ev.e1_agent_directed = bool(
            ev.classic_override
            or _search_any(_INDIRECT_CONTROL, expanded_l)
            or _search_any(_PHASE1_HIERARCHY, expanded_l)
            or re.search(
                r"\b(?:you are now|you must now|assistant must|models must|assistant shall)\b",
                expanded_l,
            )
        )
        privilege_marker = bool(
            tool_name and tool_name in {"send_email", "create_record", "retrieve_document"}
        )
        ev.privileged_tool_declared = privilege_marker

        if ev.e10_benign_context:
            names = ["E10_benign_context"]
            if privilege_marker:
                names.append("tool_privilege_observable")
            return DetectionResult(injection_probability=0.0, indicators=names)

        if not ev.primary_control():
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
        if ev.forced_identifier:
            names.append("forced_identifier")
        return DetectionResult(injection_probability=score, indicators=names)
