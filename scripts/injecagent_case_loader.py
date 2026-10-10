"""Case loader for the S-A campaign (protocol §9A items 10–13). Offline. Reads only the pinned InjecAgent release.

For each planned case it returns the released data the launcher needs: the user instruction, the user tool and its
parameters, the attacker tools and instruction, the tool response with the attacker instruction inserted (the
release template's single <Attacker Instruction> placeholder is replaced), and the tool specifications in the
OpenAI function format. Every record is checked against the pinned release files and the committed release map.

Not done here: the message layout of each arm (A0, A0_REP, SPOT_TOOL, NOINJ). The protocol does not define it and the
author has not decided it, so this module does not build arm messages. The campaign plan therefore stays
launcher_input_ready: false.

Usage (needs a local checkout of the release at the pinned commit):
  python scripts/injecagent_case_loader.py <release_dir> --run R1 --out <file.json>
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments/external/injecagent_registered_20261001/MANIFEST.json"
RELEASE_MAP = ROOT / "docs/protocols/injecagent_S-A_release_map_20261001.json"
CAMPAIGN_PLAN = ROOT / "docs/protocols/injecagent_S-A_campaign_plan_20261001.json"
PIN_FILES = {"dh": "data/test_cases_dh_base.json", "ds": "data/test_cases_ds_base.json", "tools": "data/tools.json"}
PLACEHOLDER = "<Attacker Instruction>"
PARAM_TYPES = {"string", "integer", "number", "boolean", "array", "object"}


class LoaderError(RuntimeError):
    """A release file, record, or tool does not match the pins or the committed map."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def check_release_files(release: Path, pins: Mapping[str, str]) -> None:
    """Refuse unless the three pinned release files hash to the pinned values."""
    for name, rel in PIN_FILES.items():
        path = release / rel
        if not path.is_file():
            raise LoaderError(f"release file missing: {rel}")
        got = sha256_bytes(path.read_bytes())
        if got != pins[name]:
            raise LoaderError(f"pin {name} ({rel}): computed {got} differs from pinned {pins[name]}")


def openai_function(name: str, tool: Mapping) -> dict:
    """One release tool as an OpenAI function spec. The release names a tool by toolkit + tool name, e.g.
    'Amazon' + 'GetProductDetails'. Refuses parameter types outside JSON Schema's basic set."""
    props, required = {}, []
    for p in tool["parameters"]:
        if p["type"] not in PARAM_TYPES:
            raise LoaderError(f"tool {name}: unsupported parameter type {p['type']!r}")
        if not isinstance(p["required"], bool):
            raise LoaderError(f"tool {name}: 'required' for {p['name']!r} must be a bool")
        props[p["name"]] = {"type": p["type"], "description": p["description"]}
        if p["required"]:
            required.append(p["name"])
    return {"type": "function", "function": {
        "name": name, "description": tool["summary"],
        "parameters": {"type": "object", "properties": props, "required": required}}}


def tool_specs(tools_json: Sequence[Mapping], names: Sequence[str]) -> dict[str, dict]:
    """Specs for the named full tool names (toolkit + name). A name with no spec, or with two different specs, is refused."""
    found: dict[str, list[dict]] = {}
    for kit in tools_json:
        for t in kit["tools"]:
            found.setdefault(kit["toolkit"] + t["name"], []).append(t)
    out = {}
    for name in sorted(set(names)):
        specs = found.get(name, [])
        if not specs:
            raise LoaderError(f"tool {name!r} is not in the release tool file")
        distinct = {json.dumps(s, sort_keys=True) for s in specs}
        if len(distinct) > 1:
            raise LoaderError(f"tool {name!r} has {len(distinct)} different specs in the release")
        out[name] = openai_function(name, specs[0])
    return out


def tool_response(template: str, attacker_instruction: str) -> str:
    """Insert the attacker instruction into the release template. The template must hold exactly one placeholder."""
    if template.count(PLACEHOLDER) != 1:
        raise LoaderError(f"tool response template has {template.count(PLACEHOLDER)} placeholders, expected 1")
    return template.replace(PLACEHOLDER, attacker_instruction)


def parse_parameters(text: str) -> dict:
    try:
        value = ast.literal_eval(text)
    except (ValueError, SyntaxError) as exc:
        raise LoaderError(f"tool parameters are not a literal: {text[:60]!r}") from exc
    if not isinstance(value, dict):
        raise LoaderError("tool parameters must be a dict literal")
    return value


def load_planned_cases(release: Path, pins: Mapping[str, str], release_map: Mapping,
                       case_ids: Sequence[str]) -> list[dict]:
    """Released data for each planned case, checked against the pinned files and the committed map row."""
    check_release_files(release, pins)
    rows = {r["case_id"]: r for r in release_map["cases"]}
    base = {k: json.loads((release / PIN_FILES[k]).read_text()) for k in ("dh", "ds")}
    tools_json = json.loads((release / PIN_FILES["tools"]).read_text())
    out = []
    for cid in case_ids:
        row = rows.get(cid)
        if row is None:
            raise LoaderError(f"{cid}: not in the committed release map")
        kind = cid.split("-")[0]
        if row["kind"] != kind or row["release_file"] != PIN_FILES[kind]:
            raise LoaderError(f"{cid}: map row names the wrong release file")
        idx = row["release_index"]
        if not 0 <= idx < len(base[kind]):
            raise LoaderError(f"{cid}: release index {idx} outside {PIN_FILES[kind]}")
        rec = base[kind][idx]
        if sha256_text(rec["Attacker Instruction"]) != row["attacker_instruction_sha256"]:
            raise LoaderError(f"{cid}: attacker instruction hash differs from the committed map")
        if sha256_text(rec["User Instruction"]) != row["user_instruction_sha256"]:
            raise LoaderError(f"{cid}: user instruction hash differs from the committed map")
        if rec["User Tool"] != row["user_tool"] or sorted(rec["Attacker Tools"]) != row["attacker_tools"]:
            raise LoaderError(f"{cid}: tools differ from the committed map")
        names = [rec["User Tool"], *sorted(rec["Attacker Tools"])]
        specs = tool_specs(tools_json, names)
        out.append({
            "case_id": cid, "kind": kind, "release_index": idx,
            "user_instruction": rec["User Instruction"],
            "user_tool": rec["User Tool"],
            "user_tool_parameters": parse_parameters(rec["Tool Parameters"]),
            "tool_response": tool_response(rec["Tool Response Template"], rec["Attacker Instruction"]),
            "attacker_tools": sorted(rec["Attacker Tools"]),
            "attacker_instruction": rec["Attacker Instruction"],
            "tools": [specs[n] for n in sorted(specs)],
        })
    return out


def planned_case_ids(campaign_plan: Mapping, run: str) -> list[str]:
    matches = [r for r in campaign_plan["runs"] if r["run"] == run]
    if len(matches) != 1:
        raise LoaderError(f"campaign plan has no unique run {run!r}")
    return [c["case_id"] for c in matches[0]["cases"]]


def load_pins() -> dict[str, str]:
    return json.loads(MANIFEST.read_text())["external"]


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("release_dir", type=Path)
    ap.add_argument("--run", required=True, choices=["R1", "R2", "R3"])
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    ids = planned_case_ids(json.loads(CAMPAIGN_PLAN.read_text()), a.run)
    cases = load_planned_cases(a.release_dir.resolve(), load_pins(), json.loads(RELEASE_MAP.read_text()), ids)
    a.out.write_text(json.dumps({"run": a.run, "cases": cases}, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"wrote {len(cases)} released cases for {a.run} to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
