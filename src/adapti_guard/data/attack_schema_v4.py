"""Schema and validator for the attack-pack v4 dataset upgrade (Stage 1).

This module is separate from ``schema.py`` / ``validator.py`` in this package,
which are unused legacy stubs and are left untouched.

``validate_record`` checks one record and returns a list of error strings
(empty means valid). ``validate_dataset`` checks a collection and adds
dataset-level rules. Malformed input never raises: it produces errors and is
never coerced into a valid record. Every rule is described in
``docs/dataset_upgrade/SCHEMA_v4.md``; keep the two in sync.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import math
import re
from datetime import datetime
from typing import Any, Iterator, Mapping
from urllib.parse import urlsplit

LABELS = ("attack", "benign", "hard_negative")

CATEGORIES = (
    "direct_instruction_override",
    "indirect_context_injection",
    "rag_document_injection",
    "tool_output_injection",
    "email_injection",
    "web_content_injection",
    "obfuscation_encoding",
    "privilege_exfil_unauthorized_tool",
    "system_prompt_leakage",
    "jailbreak_roleplay",
    "multi_turn_persistence",
    "multi_turn_injection",
    "benign_task",
    "hard_negative_benign",
)

TURN_TYPES = ("single", "multi")

CHANNELS = ("user_turn", "tool_output", "retrieved_doc", "email", "web_content", "none")

# Benign-side categories are excluded by name, so every other category is an attack category.
BENIGN_CATEGORIES = ("benign_task", "hard_negative_benign")
ATTACK_CATEGORIES = tuple(c for c in CATEGORIES if c not in BENIGN_CATEGORIES)

# Category -> (allowed injection channels, allowed turn types) for attack records.
# Multi-turn categories are multi-turn only; every other attack category is single-turn in v4.
CATEGORY_RULES: dict[str, tuple[frozenset[str], frozenset[str]]] = {
    "direct_instruction_override": (frozenset({"user_turn"}), frozenset({"single"})),
    "jailbreak_roleplay": (frozenset({"user_turn"}), frozenset({"single"})),
    "system_prompt_leakage": (
        frozenset({"user_turn", "retrieved_doc", "web_content"}),
        frozenset({"single"}),
    ),
    "email_injection": (frozenset({"email"}), frozenset({"single"})),
    "rag_document_injection": (frozenset({"retrieved_doc"}), frozenset({"single"})),
    "tool_output_injection": (frozenset({"tool_output"}), frozenset({"single"})),
    "web_content_injection": (frozenset({"web_content"}), frozenset({"single"})),
    "indirect_context_injection": (
        frozenset({"email", "retrieved_doc", "tool_output", "web_content"}),
        frozenset({"single"}),
    ),
    "obfuscation_encoding": (
        frozenset({"user_turn", "email", "retrieved_doc", "tool_output", "web_content"}),
        frozenset({"single"}),
    ),
    "privilege_exfil_unauthorized_tool": (
        frozenset({"user_turn", "email", "retrieved_doc", "tool_output", "web_content"}),
        frozenset({"single"}),
    ),
    "multi_turn_persistence": (frozenset({"user_turn"}), frozenset({"multi"})),
    "multi_turn_injection": (
        frozenset({"email", "retrieved_doc", "tool_output", "web_content"}),
        frozenset({"multi"}),
    ),
}

# Explicit family -> category registry. Each attack family maps to exactly one category.
FAMILY_CATEGORY: dict[str, str] = {
    "DIRECT_OVERRIDE": "direct_instruction_override",
    "EMAIL_INJECTION": "email_injection",
    "RAG_DOC_INJECTION": "rag_document_injection",
    "TOOL_OUTPUT_INJECTION": "tool_output_injection",
    "WEB_CONTENT_INJECTION": "web_content_injection",
    "INDIRECT_CONTEXT": "indirect_context_injection",
    "OBFUSCATION": "obfuscation_encoding",
    "UNAUTHORIZED_TOOL": "privilege_exfil_unauthorized_tool",
    "SYSTEM_PROMPT_LEAKAGE": "system_prompt_leakage",
    "JAILBREAK_ROLEPLAY": "jailbreak_roleplay",
    "MULTI_TURN_PERSISTENCE": "multi_turn_persistence",
    "MULTI_TURN_INJECTION": "multi_turn_injection",
}
BENIGN_FAMILY = "benign"

# Every field a record must carry. Unknown fields are rejected.
REQUIRED_FIELDS = (
    "id",
    "label",
    "family",
    "category",
    "turn_type",
    "injection_channel",
    "injection_location",
    "attack_objective",
    "success_condition",
    "tools",
    "tool_call",
    "source",
    "author_id",
    "created_at",
    "version",
    "license",
    "sha256",
    # Content and evidence fields (SCHEMA_v4.md section 1).
    "turns",
    "untrusted_content",
    "injection_span",
    "pair_id",
    "canary",
    "redistributable",
)

SELF_AUTHORED = "self_authored"
EXTERNAL_SOURCES = frozenset({"garak", "InjecAgent", "TrustLLM", "AgentDojo", "LLMail-Inject"})
EXTERNAL_PROVENANCE_FIELDS = ("source_url", "source_version", "retrieved_at")

# Reserved names (RFC 2606 / RFC 6761) and documentation address ranges (RFC 5737, RFC 3849).
RESERVED_TLDS = (".invalid", ".example", ".test", ".localhost")
RESERVED_DOMAINS = ("example.com", "example.org", "example.net")
DOCUMENTATION_NETS = tuple(
    ipaddress.ip_network(n)
    for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "2001:db8::/32")
)
# Bare domains are flagged only when their final label is a public TLD, so file names such as
# ``plate.png`` or ``config.json`` are not treated as hosts. URLs with a scheme and e-mail
# addresses are always checked, whatever their TLD. Limitation: an unlisted TLD in a bare
# domain is not detected.
PUBLIC_TLDS = frozenset({
    "com", "net", "org", "edu", "gov", "mil", "int", "info", "biz", "io", "ai", "dev",
    "app", "co", "us", "uk", "de", "fr", "ru", "cn", "jp", "online", "site", "xyz", "top",
    "cloud", "tech",
})

ID_RE = re.compile(r"av4-(atk|ben|hn)-[0-9]{6}")
SHA256_RE = re.compile(r"[0-9a-f]{64}")
VERSION_RE = re.compile(r"attack_v4(?:_[a-z0-9_]+)?")
TURN_LOCATION_RE = re.compile(r"turns\[(0|[1-9][0-9]*)\]")
UNTRUSTED_LOCATION = "untrusted_content"
URL_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*://[^\s\"'<>)]+")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@([A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+)")
BARE_DOMAIN_RE = re.compile(
    r"(?<![A-Za-z0-9@/._\-])((?:[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?\.)+([A-Za-z]{2,63}))"
    r"(?![A-Za-z0-9\-])"
)
IPV4_RE = re.compile(r"(?<![0-9.])([0-9]{1,3}(?:\.[0-9]{1,3}){3})(?![0-9.])")

MIN_TEXT_LENGTH = 10
MIN_SPAN_LENGTH = 8

_METADATA_KEYS = frozenset({"sha256", "id", "pair_id", "version", "created_at", "license", "author_id",
                            "source", "source_url", "source_version", "retrieved_at"})


def compute_sha256(record: Mapping[str, Any]) -> str:
    """SHA-256 of the canonical JSON of ``record`` with its ``sha256`` key removed.

    Raises ``TypeError`` for values that are not JSON-compatible; callers validate types first.
    """
    body = {k: v for k, v in record.items() if k != "sha256"}
    canonical = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _is_str(value: Any) -> bool:
    return isinstance(value, str)


def _is_nonblank(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _json_problems(value: Any, path: str, out: list[str]) -> None:
    """Record every value that is not JSON-compatible, without raising."""
    if value is None or isinstance(value, (bool, int, str)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            out.append(f"{path}: non-finite number")
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            _json_problems(item, f"{path}[{i}]", out)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                out.append(f"{path}: non-string key {key!r}")
                continue
            _json_problems(item, f"{path}.{key}", out)
        return
    out.append(f"{path}: non-JSON type {type(value).__name__}")


def _string_leaves(value: Any, path: str) -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from _string_leaves(item, f"{path}[{i}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _string_leaves(item, f"{path}.{key}")


def _host_allowed(host: str) -> bool:
    """True only for reserved names and documentation address ranges."""
    h = host.lower().rstrip(".")
    if not h:
        return False
    try:
        ip = ipaddress.ip_address(h)
    except ValueError:
        ip = None
    if ip is not None:
        return any(ip in net for net in DOCUMENTATION_NETS)
    if h == "localhost":
        return False
    if h.endswith(RESERVED_TLDS):
        return True
    return any(h == d or h.endswith("." + d) for d in RESERVED_DOMAINS)


def _safety_errors(path: str, text: str) -> list[str]:
    errors: list[str] = []
    for match in URL_RE.finditer(text):
        url = match.group(0)
        try:
            host = urlsplit(url).hostname
        except ValueError:
            errors.append(f"{path}: malformed URL {url!r}")
            continue
        if not host or not _host_allowed(host):
            errors.append(f"{path}: contains non-reserved host {host!r} in URL")
    for match in EMAIL_RE.finditer(text):
        host = match.group(1)
        if not _host_allowed(host):
            errors.append(f"{path}: contains non-reserved host {host!r} in e-mail address")
    # Remove URLs and e-mail addresses so their hosts are not reported twice.
    remainder = URL_RE.sub(" ", EMAIL_RE.sub(" ", text))
    for match in BARE_DOMAIN_RE.finditer(remainder):
        host, tld = match.group(1), match.group(2).lower()
        if tld in PUBLIC_TLDS and not _host_allowed(host):
            errors.append(f"{path}: contains non-reserved host {host!r} as a bare domain")
    for match in IPV4_RE.finditer(remainder):
        try:
            ip = ipaddress.ip_address(match.group(1))
        except ValueError:
            continue
        if not any(ip in net for net in DOCUMENTATION_NETS):
            errors.append(f"{path}: contains non-reserved host {match.group(1)!r} as an IPv4 address")
    return errors


def _safety_scan(record: Mapping[str, Any]) -> list[str]:
    """Scan every content string, including nested tool definitions and arguments."""
    errors: list[str] = []
    for key, value in record.items():
        if key in _METADATA_KEYS:
            continue
        for path, text in _string_leaves(value, key):
            errors.extend(_safety_errors(path, text))
    return errors


def validate_record(record: Any) -> list[str]:
    """Return a list of error strings. An empty list means the record is valid."""
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    try:
        return _validate(record)
    except Exception as exc:  # last-resort guard: a malformed record must give an error, not an exception
        return [f"internal validation failure ({type(exc).__name__}): {exc}"]


def _validate(record: dict) -> list[str]:
    problems: list[str] = []
    _json_problems(record, "record", problems)
    if problems:
        return problems

    missing = [name for name in REQUIRED_FIELDS if name not in record]
    if missing:
        return [f"missing field: {name}" for name in missing]
    unknown = sorted(set(record) - set(REQUIRED_FIELDS) - set(EXTERNAL_PROVENANCE_FIELDS))
    if unknown:
        return [f"unknown field: {name}" for name in unknown]

    errors: list[str] = []

    label = record["label"]
    if not _is_str(label) or label not in LABELS:
        return [f"invalid label: {label!r}"]

    category = record["category"]
    if not _is_str(category) or category not in CATEGORIES:
        errors.append(f"invalid category: {category!r}")

    turn_type = record["turn_type"]
    if not _is_str(turn_type) or turn_type not in TURN_TYPES:
        errors.append(f"invalid turn_type: {turn_type!r}")

    channel = record["injection_channel"]
    if channel == "":
        errors.append("injection_channel is empty")
    elif not _is_str(channel) or channel not in CHANNELS:
        errors.append(f"invalid injection_channel: {channel!r}")

    family = record["family"]
    if not _is_str(family) or not family.strip():
        errors.append("family is empty")

    _check_identity(record, errors, label)
    _check_provenance(record, errors)
    turns = _check_turns(record, errors, turn_type)
    _check_tools(record, errors)

    untrusted = record["untrusted_content"]
    if not _is_str(untrusted):
        errors.append("untrusted_content must be a string")
        untrusted = ""
    elif channel == "none":
        if untrusted:
            errors.append("injection_channel 'none' requires untrusted_content to be empty")
    elif channel != "user_turn" and not untrusted.strip():
        errors.append(f"injection_channel {channel!r} requires non-empty untrusted_content")

    if not _is_str(record["success_condition"]) or len(record["success_condition"].strip()) < MIN_TEXT_LENGTH:
        errors.append("success_condition is empty or too short")

    if label == "attack":
        _check_attack(record, errors, channel, turn_type, category, family, turns, untrusted)
    elif label == "benign":
        _check_benign(record, errors, category, family)
    else:
        _check_hard_negative(record, errors, channel, category, family, turns, untrusted)

    errors.extend(_safety_scan(record))
    return errors


def _check_identity(record: dict, errors: list[str], label: str) -> None:
    rid = record["id"]
    if not _is_str(rid) or not ID_RE.fullmatch(rid):
        errors.append(f"id must match {ID_RE.pattern}: {rid!r}")
    else:
        middle = {"attack": "atk", "benign": "ben", "hard_negative": "hn"}[label]
        if rid.split("-")[1] != middle:
            errors.append(f"id segment does not match label {label!r}")

    version = record["version"]
    if not _is_str(version) or not VERSION_RE.fullmatch(version):
        errors.append(f"invalid version: {version!r}")

    if not _is_nonblank(record["author_id"]):
        errors.append("author_id is empty")
    if not _is_nonblank(record["license"]):
        errors.append("license is empty")

    created = record["created_at"]
    if not _is_str(created):
        errors.append("created_at must be an ISO-8601 string")
    else:
        try:
            datetime.fromisoformat(created)
        except ValueError:
            errors.append(f"created_at is not ISO-8601: {created!r}")

    digest = record["sha256"]
    if not _is_str(digest) or not SHA256_RE.fullmatch(digest):
        errors.append("sha256 is not a 64-character lowercase hex digest")
    else:
        try:
            expected = compute_sha256(record)
        except (TypeError, ValueError) as exc:
            errors.append(f"sha256 cannot be computed: {exc}")
        else:
            if digest != expected:
                errors.append("sha256 does not match canonical record content")


def _check_provenance(record: dict, errors: list[str]) -> None:
    source = record["source"]
    redistributable = record["redistributable"]
    if not isinstance(redistributable, bool):
        errors.append("redistributable must be a boolean")
    if source == SELF_AUTHORED:
        present = [name for name in EXTERNAL_PROVENANCE_FIELDS if name in record]
        if present:
            errors.append(f"provenance fields {present} are only allowed for external sources")
        return
    if not _is_str(source) or source not in EXTERNAL_SOURCES:
        errors.append(f"invalid source: {source!r}")
        return
    for name in EXTERNAL_PROVENANCE_FIELDS:
        if not _is_nonblank(record.get(name)):
            errors.append(f"external source {source!r} requires {name}")
    if isinstance(redistributable, bool) and not redistributable:
        text_present = bool(record["untrusted_content"]) or (
            isinstance(record["turns"], list) and any(record["turns"])
        )
        if text_present:
            errors.append("non-redistributable external record must not contain text; publish identifiers only")


def _check_turns(record: dict, errors: list[str], turn_type: Any) -> list[str] | None:
    """Validate ``turns``. Returns the list when it is well-formed, otherwise None."""
    turns = record["turns"]
    if not isinstance(turns, list) or not all(isinstance(t, str) for t in turns):
        errors.append("turns must be a list of strings")
        return None
    if any(not t.strip() for t in turns):
        errors.append("turns contains an empty or whitespace-only string")
    if turn_type == "single" and len(turns) != 1:
        errors.append(f"single-turn record must have exactly 1 turn, has {len(turns)}")
    if turn_type == "multi" and len(turns) < 2:
        errors.append(f"multi-turn record must have at least 2 turns, has {len(turns)}")
    return turns


def _check_tools(record: dict, errors: list[str]) -> None:
    tools = record["tools"]
    names: list[str] = []
    if not isinstance(tools, list) or not tools:
        errors.append("tools must be a non-empty list")
    else:
        for tool in tools:
            if not isinstance(tool, dict) or not _is_nonblank(tool.get("name")):
                errors.append("each tool needs a non-empty name")
                continue
            if set(tool) - {"name", "arguments"}:
                errors.append(f"tool {tool['name']!r} has unknown keys {sorted(set(tool) - {'name', 'arguments'})}")
            if "arguments" in tool and not (
                isinstance(tool["arguments"], list) and all(isinstance(a, str) for a in tool["arguments"])
            ):
                errors.append(f"tool {tool['name']!r} arguments must be a list of strings")
            names.append(tool["name"])
        if len(set(names)) != len(names):
            errors.append("tool names must be unique")

    call = record["tool_call"]
    if call is None:
        return
    if not isinstance(call, dict) or set(call) != {"name", "arguments"}:
        errors.append("tool_call must be null or an object with exactly name and arguments")
    elif not _is_nonblank(call["name"]):
        errors.append("tool_call.name is empty")
    elif call["name"] not in names:
        errors.append(f"tool_call.name {call['name']!r} is not in tools")
    elif not isinstance(call["arguments"], dict):
        errors.append("tool_call.arguments must be an object")


def _check_evidence(record: dict, errors: list[str], channel: Any, turns: list[str] | None,
                    untrusted: str) -> None:
    """The injection (attack) or decoy (hard negative) must be present in the stated location."""
    span = record["injection_span"]
    if not _is_str(span) or len(span.strip()) < MIN_SPAN_LENGTH:
        errors.append(f"injection_span must be a string of at least {MIN_SPAN_LENGTH} non-space characters")
        return
    location = record["injection_location"]
    if channel == "user_turn":
        match = TURN_LOCATION_RE.fullmatch(location) if _is_str(location) else None
        if match is None:
            errors.append(f"user_turn injection_location must be turns[<index>], got {location!r}")
            return
        if turns is None:
            return
        index = int(match.group(1))
        if index >= len(turns):
            errors.append(f"injection_location index {index} is out of range for {len(turns)} turn(s)")
        elif span not in turns[index]:
            errors.append(f"injection_span is not present in turns[{index}]")
    else:
        if location != UNTRUSTED_LOCATION:
            errors.append(f"{channel!r} injection_location must be 'untrusted_content', got {location!r}")
            return
        if span not in untrusted:
            errors.append("injection_span is not present in untrusted_content")


def _check_attack(record: dict, errors: list[str], channel: Any, turn_type: Any, category: Any,
                  family: Any, turns: list[str] | None, untrusted: str) -> None:
    if _is_str(category) and category in ATTACK_CATEGORIES:
        allowed_channels, allowed_turns = CATEGORY_RULES[category]
        if not _is_str(channel) or channel not in allowed_channels:
            errors.append(f"category {category!r} does not allow channel {channel!r}")
        if not _is_str(turn_type) or turn_type not in allowed_turns:
            errors.append(f"category {category!r} does not allow turn_type {turn_type!r}")
    elif category is not None and _is_str(category) and category in CATEGORIES:
        errors.append(f"attack record has non-attack category {category!r}")

    if family == BENIGN_FAMILY:
        errors.append("attack record must carry an attack family name, not 'benign'")
    elif _is_str(family) and family.strip():
        if family not in FAMILY_CATEGORY:
            errors.append(f"unknown family {family!r}")
        elif _is_str(category) and FAMILY_CATEGORY[family] != category:
            errors.append(f"family {family!r} requires category {FAMILY_CATEGORY[family]!r}, got {category!r}")

    if channel == "none":
        errors.append("attack record must have an injection channel other than 'none'")
    if not _is_str(record["injection_location"]) or record["injection_location"] == "none":
        errors.append("attack record requires an exact injection_location")
    if not _is_nonblank(record["attack_objective"]) or _normalise(record["attack_objective"]) == "none":
        errors.append("attack record requires attack_objective")

    _check_evidence(record, errors, channel, turns, untrusted)

    call = record["tool_call"]
    canary = record["canary"]
    if call is None and not _is_nonblank(canary):
        errors.append("attack needs tool_call or canary to measure its effect")
    if canary is not None and not _is_nonblank(canary):
        errors.append("canary must be null or a non-empty string")
    if isinstance(call, dict) and _is_str(call.get("name")) and _is_str(record["success_condition"]):
        if call["name"] not in record["success_condition"]:
            errors.append("success_condition must name tool_call.name")
    if _is_nonblank(canary) and _is_str(record["success_condition"]) and canary not in record["success_condition"]:
        errors.append("success_condition must contain the canary")
    if not _is_nonblank(record["pair_id"]):
        errors.append("attack record requires pair_id (its structural counterpart)")


def _normalise(text: str) -> str:
    return text.strip().lower()


def _check_benign(record: dict, errors: list[str], category: Any, family: Any) -> None:
    if category != "benign_task":
        errors.append(f"benign record must use category 'benign_task', got {category!r}")
    if family != BENIGN_FAMILY:
        errors.append("benign record must have family 'benign'")
    if record["injection_location"] != "none":
        errors.append("benign record must have injection_location 'none'")
    if record["injection_span"] is not None:
        errors.append("benign record must have injection_span null")
    if not _is_str(record["attack_objective"]) or _normalise(record["attack_objective"]) != "none":
        errors.append("benign record must have attack_objective 'none'")
    if record["canary"] is not None:
        errors.append("benign record must have canary null")
    if not _is_nonblank(record["pair_id"]):
        errors.append("benign record requires pair_id")


def _check_hard_negative(record: dict, errors: list[str], channel: Any, category: Any, family: Any,
                         turns: list[str] | None, untrusted: str) -> None:
    if category != "hard_negative_benign":
        errors.append(f"hard_negative record must use category 'hard_negative_benign', got {category!r}")
    if family != BENIGN_FAMILY:
        errors.append("hard_negative record must have family 'benign'")
    if channel == "none":
        errors.append("hard_negative record must carry untrusted content (channel other than 'none')")
    else:
        _check_evidence(record, errors, channel, turns, untrusted)
    if not _is_nonblank(record["injection_location"]) or record["injection_location"] == "none":
        errors.append("hard_negative record requires injection_location naming the decoy text")
    if not _is_str(record["attack_objective"]) or _normalise(record["attack_objective"]) != "none":
        errors.append("hard_negative record must have attack_objective 'none'")
    if record["canary"] is not None:
        errors.append("hard_negative record must have canary null")
    if not _is_nonblank(record["pair_id"]):
        errors.append("hard_negative record requires pair_id")


def _pair_mismatches(record: dict, partner: dict) -> list[str]:
    errs: list[str] = []
    for name in ("injection_channel", "turn_type"):
        if record.get(name) != partner.get(name):
            errs.append(f"pair mismatch on {name}: {record.get(name)!r} vs {partner.get(name)!r}")
    if _canonical_tools(record.get("tools")) != _canonical_tools(partner.get("tools")):
        errs.append("pair mismatch on tools")
    rt, pt = record.get("turns"), partner.get("turns")
    if not (isinstance(rt, list) and isinstance(pt, list)):
        errs.append("pair cannot be verified: turns is not a list in this record or its partner")
    elif len(rt) != len(pt):
        errs.append("pair mismatch on number of turns")
    return errs


def _canonical_tools(tools: Any) -> list[str] | None:
    if not isinstance(tools, list):
        return None
    return sorted(json.dumps(t, sort_keys=True) for t in tools)


def validate_dataset(records: Any) -> dict[str, list[str]]:
    """Validate records one by one, then check dataset-level rules.

    Returns a mapping ``{record_id_or_index: [errors]}``. Empty means valid.
    Dataset-level rules: unique ids; each labelled record's ``pair_id`` resolves to a record
    that points back to it; an attack pairs only with a benign-side record and vice versa; the
    pair matches on channel, turn type, tool definitions (order-insensitive) and turn count.
    """
    if not isinstance(records, (list, tuple)):
        return {"dataset": ["dataset must be a list of records"]}
    report: dict[str, list[str]] = {}
    by_id: dict[str, dict] = {}
    seen: dict[str, int] = {}

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            report[f"#{index}"] = ["record must be a JSON object"]
            continue
        rid = record.get("id")
        key = rid if _is_str(rid) and rid else f"#{index}"
        if key in seen:
            report.setdefault(key, []).append(f"duplicate id (first at index {seen[key]})")
        else:
            seen[key] = index
            by_id[key] = record
        errs = validate_record(record)
        if errs:
            report.setdefault(key, []).extend(errs)

    for key, record in by_id.items():
        if record.get("label") not in LABELS:
            continue
        pair_id = record.get("pair_id")
        if not _is_nonblank(pair_id):
            continue
        partner = by_id.get(pair_id)
        if partner is None:
            report.setdefault(key, []).append(f"pair_id {pair_id!r} not found")
            continue
        errs: list[str] = []
        if record["label"] == "attack" and partner.get("label") == "attack":
            errs.append("attack must be paired with a benign-side record, not another attack")
        if record["label"] != "attack" and partner.get("label") != "attack":
            errs.append("benign-side record must be paired with an attack")
        if partner.get("pair_id") != key:
            errs.append(f"pair is not reciprocal: {pair_id!r} points elsewhere")
        errs.extend(_pair_mismatches(record, partner))
        if errs:
            report.setdefault(key, []).extend(errs)

    return report
