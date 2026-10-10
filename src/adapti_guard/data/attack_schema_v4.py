"""Schema and validator for the attack-pack v4 dataset upgrade (Stage 1).

This module is separate from ``schema.py`` / ``validator.py`` in this package,
which are unused legacy stubs and are left untouched.

The validator checks one record at a time (``validate_record``) and a set of
records together (``validate_dataset``). Every rule is listed in
``docs/dataset_upgrade/SCHEMA_v4.md``; keep the two in sync.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Any, Iterable, Mapping
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

ATTACK_CATEGORIES = CATEGORIES[:11]
BENIGN_CATEGORIES = ("benign_task", "hard_negative_benign")

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

# Fields that every record must carry, in the order the schema doc lists them.
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
    # Content fields required in addition to the list above (see SCHEMA_v4.md, section 3).
    "turns",
    "untrusted_content",
    "pair_id",
    "canary",
    "redistributable",
)

# External sources and the provenance fields each one must carry.
SELF_AUTHORED = "self_authored"
EXTERNAL_SOURCES = frozenset({"garak", "InjecAgent", "TrustLLM", "AgentDojo", "LLMail-Inject"})
EXTERNAL_PROVENANCE_FIELDS = ("source_url", "source_version", "retrieved_at")

# Only reserved names may appear in attack content (RFC 2606 / RFC 6761).
RESERVED_TLDS = (".invalid", ".example", ".test", ".localhost")
RESERVED_DOMAINS = ("example.com", "example.org", "example.net")

ID_PATTERN = re.compile(r"^av4-(atk|ben|hn)-\d{6}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
VERSION_PATTERN = re.compile(r"^attack_v4(_[a-z0-9_]+)?$")
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
URL_PATTERN = re.compile(r"https?://[^\s\"'<>)]+")
MIN_TEXT_LENGTH = 10


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def compute_sha256(record: Mapping[str, Any]) -> str:
    """SHA-256 of the canonical JSON of ``record`` with its ``sha256`` key removed."""
    body = {k: v for k, v in record.items() if k != "sha256"}
    canonical = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _reserved_host(host: str) -> bool:
    host = host.lower().rstrip(".")
    if host.endswith(RESERVED_TLDS):
        return True
    return any(host == d or host.endswith("." + d) for d in RESERVED_DOMAINS)


def _non_reserved_hosts(text: str) -> list[str]:
    hosts = []
    for match in EMAIL_PATTERN.finditer(text):
        hosts.append(match.group(1))
    for match in URL_PATTERN.finditer(text):
        host = urlsplit(match.group(0)).hostname or ""
        hosts.append(host)
    return [h for h in hosts if h and not _reserved_host(h)]


def validate_record(record: Mapping[str, Any]) -> list[str]:
    """Return a list of error strings. An empty list means the record is valid."""
    errors: list[str] = []

    for name in REQUIRED_FIELDS:
        if name not in record:
            errors.append(f"missing field: {name}")
    if errors:
        # Further checks assume every field exists.
        return errors

    label = record["label"]
    if label not in LABELS:
        errors.append(f"invalid label: {label!r}")
        return errors

    category = record["category"]
    if category not in CATEGORIES:
        errors.append(f"invalid category: {category!r}")

    turn_type = record["turn_type"]
    if turn_type not in TURN_TYPES:
        errors.append(f"invalid turn_type: {turn_type!r}")

    channel = record["injection_channel"]
    if not channel:
        errors.append("injection_channel is empty")
    elif channel not in CHANNELS:
        errors.append(f"invalid injection_channel: {channel!r}")

    if not _is_nonempty_str(record["id"]) or not ID_PATTERN.match(record["id"]):
        errors.append(f"id must match {ID_PATTERN.pattern}: {record['id']!r}")
    else:
        expected_middle = {"attack": "atk", "benign": "ben", "hard_negative": "hn"}[label]
        if f"-{expected_middle}-" not in record["id"]:
            errors.append(f"id segment does not match label {label!r}")

    if not _is_nonempty_str(record["version"]) or not VERSION_PATTERN.match(record["version"]):
        errors.append(f"invalid version: {record['version']!r}")

    if not _is_nonempty_str(record["author_id"]):
        errors.append("author_id is empty")
    if not _is_nonempty_str(record["license"]):
        errors.append("license is empty")

    try:
        datetime.fromisoformat(str(record["created_at"]))
    except ValueError:
        errors.append(f"created_at is not ISO-8601: {record['created_at']!r}")

    if not isinstance(record["sha256"], str) or not SHA256_PATTERN.match(record["sha256"]):
        errors.append("sha256 is not a 64-character lowercase hex digest")
    elif record["sha256"] != compute_sha256(record):
        errors.append("sha256 does not match canonical record content")

    # Source and provenance.
    source = record["source"]
    if source == SELF_AUTHORED:
        pass
    elif source in EXTERNAL_SOURCES:
        for name in EXTERNAL_PROVENANCE_FIELDS:
            if not _is_nonempty_str(record.get(name)):
                errors.append(f"external source {source!r} requires {name}")
        if not isinstance(record["redistributable"], bool):
            errors.append("redistributable must be a boolean")
        elif not record["redistributable"] and (
            record["untrusted_content"]
            or (isinstance(record["turns"], list) and any(record["turns"]))
        ):
            errors.append("non-redistributable external record must not contain text; publish identifiers only")
    else:
        errors.append(f"invalid source: {source!r}")

    if not isinstance(record["redistributable"], bool):
        errors.append("redistributable must be a boolean")

    # Turns: single = 1 user message, multi = at least 2.
    turns = record["turns"]
    if not isinstance(turns, list) or not all(isinstance(t, str) for t in turns):
        errors.append("turns must be a list of strings")
        turns = []
    if turn_type == "single" and len(turns) != 1:
        errors.append(f"single-turn record must have exactly 1 turn, has {len(turns)}")
    if turn_type == "multi" and len(turns) < 2:
        errors.append(f"multi-turn record must have at least 2 turns, has {len(turns)}")
    if any(not t.strip() for t in turns):
        errors.append("turns contains an empty string")

    # Tools (mock tool definitions) and tool_call.
    tools = record["tools"]
    tool_names: set[str] = set()
    if not isinstance(tools, list) or not tools:
        errors.append("tools must be a non-empty list")
    else:
        for tool in tools:
            if not isinstance(tool, dict) or not _is_nonempty_str(tool.get("name")):
                errors.append("each tool needs a non-empty name")
                continue
            tool_names.add(tool["name"])

    tool_call = record["tool_call"]
    if tool_call is not None:
        if not isinstance(tool_call, dict) or not _is_nonempty_str(tool_call.get("name")):
            errors.append("tool_call must be null or an object with a name")
        elif tool_call["name"] not in tool_names:
            errors.append(f"tool_call.name {tool_call['name']!r} is not in tools")
        elif not isinstance(tool_call.get("arguments"), dict):
            errors.append("tool_call.arguments must be an object")

    # Text fields that every record needs.
    for name in ("success_condition",):
        if not _is_nonempty_str(record[name]) or len(record[name].strip()) < MIN_TEXT_LENGTH:
            errors.append(f"{name} is empty or too short")

    untrusted = record["untrusted_content"]
    if not isinstance(untrusted, str):
        errors.append("untrusted_content must be a string")
        untrusted = ""

    if channel == "none":
        if untrusted:
            errors.append("injection_channel 'none' requires untrusted_content to be empty")
    elif channel != "user_turn" and not untrusted.strip():
        errors.append(f"injection_channel {channel!r} requires non-empty untrusted_content")

    # Label-specific rules.
    if label == "attack":
        _check_attack(record, errors, channel, turn_type, category, tool_call)
    elif label == "benign":
        _check_benign(record, errors, channel, category, tool_call)
    else:  # hard_negative
        _check_hard_negative(record, errors, channel, category)

    # Safety: every address or URL in attack or benign content must use a reserved name.
    for name in ("attack_objective", "success_condition", "untrusted_content"):
        value = record.get(name)
        if isinstance(value, str):
            bad = _non_reserved_hosts(value)
            if bad:
                errors.append(f"{name} contains non-reserved host(s): {sorted(set(bad))}")
    for t in turns if isinstance(turns, list) else []:
        if isinstance(t, str):
            bad = _non_reserved_hosts(t)
            if bad:
                errors.append(f"turns contains non-reserved host(s): {sorted(set(bad))}")

    return errors


def _check_attack(record, errors, channel, turn_type, category, tool_call) -> None:
    if category not in ATTACK_CATEGORIES:
        errors.append(f"attack record has non-attack category {category!r}")
    else:
        allowed_channels, allowed_turns = CATEGORY_RULES[category]
        if channel not in allowed_channels:
            errors.append(f"category {category!r} does not allow channel {channel!r}")
        if turn_type not in allowed_turns:
            errors.append(f"category {category!r} does not allow turn_type {turn_type!r}")

    if record["family"] == "benign":
        errors.append("attack record must carry an attack family name, not 'benign'")
    if not _is_nonempty_str(record["family"]):
        errors.append("family is empty")

    if channel == "none":
        errors.append("attack record must have an injection channel other than 'none'")
    if not _is_nonempty_str(record["injection_location"]) or record["injection_location"] == "none":
        errors.append("attack record requires an exact injection_location")
    if record["attack_objective"] in ("", "none"):
        errors.append("attack record requires attack_objective")

    # Measurable effect: a tool call or a canary token the success condition can check.
    if tool_call is None and not _is_nonempty_str(record["canary"]):
        errors.append("attack needs tool_call or canary to measure its effect")
    if not isinstance(record["pair_id"], str) or not record["pair_id"]:
        errors.append("attack record requires pair_id (its structural counterpart)")


def _check_benign(record, errors, channel, category, tool_call) -> None:
    if category != "benign_task":
        errors.append(f"benign record must use category 'benign_task', got {category!r}")
    if record["family"] != "benign":
        errors.append("benign record must have family 'benign'")
    if record["injection_location"] != "none":
        errors.append("benign record must have injection_location 'none'")
    if record["attack_objective"] != "none":
        errors.append("benign record must have attack_objective 'none'")
    if record["canary"] is not None:
        errors.append("benign record must have canary null")
    if not isinstance(record["pair_id"], str) or not record["pair_id"]:
        errors.append("benign record requires pair_id")


def _check_hard_negative(record, errors, channel, category) -> None:
    if category != "hard_negative_benign":
        errors.append(f"hard_negative record must use category 'hard_negative_benign', got {category!r}")
    if record["family"] != "benign":
        errors.append("hard_negative record must have family 'benign'")
    if channel == "none":
        errors.append("hard_negative record must carry untrusted content (channel other than 'none')")
    if not _is_nonempty_str(record["injection_location"]) or record["injection_location"] == "none":
        errors.append("hard_negative record requires injection_location naming the decoy text")
    if record["attack_objective"] != "none":
        errors.append("hard_negative record must have attack_objective 'none'")
    if record["canary"] is not None:
        errors.append("hard_negative record must have canary null")
    if not isinstance(record["pair_id"], str) or not record["pair_id"]:
        errors.append("hard_negative record requires pair_id")


def validate_dataset(records: Iterable[Mapping[str, Any]]) -> dict[str, list[str]]:
    """Validate records one by one, then check dataset-level rules.

    Returns a mapping ``{record_id_or_index: [errors]}``. Empty means valid.
    Dataset-level rules: unique ids; each attack's ``pair_id`` names a benign-side
    record that points back to it and matches it on channel, turn type, tools and
    turn count; each benign-side record's ``pair_id`` names an attack.
    """
    records = list(records)
    report: dict[str, list[str]] = {}
    by_id: dict[str, Mapping[str, Any]] = {}
    seen: dict[str, int] = {}

    for index, record in enumerate(records):
        key = str(record.get("id", f"#{index}"))
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
        if not isinstance(pair_id, str) or not pair_id:
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
        for name in ("injection_channel", "turn_type"):
            if record.get(name) != partner.get(name):
                errs.append(f"pair mismatch on {name}: {record.get(name)!r} vs {partner.get(name)!r}")
        if record.get("tools") != partner.get("tools"):
            errs.append("pair mismatch on tools")
        if len(record.get("turns", [])) != len(partner.get("turns", [])):
            errs.append("pair mismatch on number of turns")
        if errs:
            report.setdefault(key, []).extend(errs)

    return report
