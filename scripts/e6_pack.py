"""E6 fresh-pack loader and validator (offline). Validates structure and provenance; it cannot establish independence.

Independence is an attestation by a real author. A pack whose author is NOT_AVAILABLE, a known non-independent party, or
that is marked synthetic validates structurally at most and is never `freeze_eligible`.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

SCHEMA_VERSION = "e6-pack-1"
FAMILIES, INSTANCES, CONTROL_FAMILIES = 30, 10, 10
NON_INDEPENDENT = ("claude", "anthropic", "cursor", "assistant", "mohammad", "shirazi", "project owner", "owner", "not_available")


def canonical_bytes(pack: dict) -> bytes:
    return json.dumps(pack, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def pack_sha256(pack: dict) -> str:
    return hashlib.sha256(canonical_bytes(pack)).hexdigest()


def schema_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(pack: dict, families: int = FAMILIES, instances: int = INSTANCES, control_families: int = CONTROL_FAMILIES) -> dict:
    errors: list[str] = []
    if pack.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version")
    for k in ("pack_id", "created_utc", "frozen_utc"):
        if not pack.get(k):
            errors.append(f"missing {k}")
    fams = pack.get("families") or []
    if len(fams) != families:
        errors.append(f"families {len(fams)} != {families}")
    ids = [f.get("family_id") for f in fams]
    if len(set(ids)) != len(ids) or not all(ids):
        errors.append("family_id missing or duplicated")
    ctrl = 0
    for f in fams:
        spec = f.get("exec_spec") or {}
        if not (spec.get("tool_name") and spec.get("required_args") is not None and spec.get("body_marker")):
            errors.append(f"{f.get('family_id')}: exec_spec incomplete")
        ins = f.get("instances") or []
        if sorted(i.get("instance_index") for i in ins) != list(range(instances)):
            errors.append(f"{f.get('family_id')}: instances must be indices 0..{instances - 1}")
        for i in ins:
            msgs = i.get("messages") or []
            if sum(bool(m.get("carrier")) for m in msgs) != 1 or not all(m.get("role") in ("user", "tool") and isinstance(m.get("text"), str) for m in msgs):
                errors.append(f"{f.get('family_id')}/i{i.get('instance_index')}: need user/tool text messages with exactly one carrier")
            elif spec.get("body_marker") and not any(spec["body_marker"] in m["text"] for m in msgs if m.get("carrier")):
                errors.append(f"{f.get('family_id')}/i{i.get('instance_index')}: marker absent from the carrier")
        if ins and all(i.get("control_messages") for i in ins):
            ctrl += 1
    if ctrl < control_families:
        errors.append(f"control families {ctrl} < {control_families}")
    a = pack.get("author") or {}
    author = str(a.get("author_id", "")).strip()
    provenance_ok = bool(author and a.get("role") and a.get("independence_attestation") and a.get("attestation_utc"))
    lowered = author.lower()
    non_independent = (not author) or any(t in lowered for t in NON_INDEPENDENT)
    synthetic = bool(pack.get("synthetic"))
    return {"structure_ok": not errors, "errors": errors, "pack_sha256": pack_sha256(pack), "author_id": author or None,
            "provenance_complete": provenance_ok, "author_excluded": non_independent, "synthetic": synthetic,
            "freeze_eligible": not errors and provenance_ok and not non_independent and not synthetic}


def load(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def units_by_instance(pack: dict, control: bool = False) -> dict:
    """{(family_id, instance): [(role, text, carrier)]} for the replay (control=True uses the injection-free twins)."""
    out = {}
    for f in pack["families"]:
        for i in f["instances"]:
            msgs = i.get("control_messages") if control else i["messages"]
            if msgs:
                out[(f["family_id"], i["instance_index"])] = [(m["role"], m["text"], bool(m.get("carrier"))) for m in msgs]
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: e6_pack.py PACK.json")
        return 2
    r = validate(load(Path(argv[1])))
    print(json.dumps(r, indent=1))
    return 0 if r["freeze_eligible"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
