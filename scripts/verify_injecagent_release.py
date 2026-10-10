"""Verify a local InjecAgent checkout against the pins in the registered MANIFEST and the committed S-A release map.

Read-only on the release: no network, no model call. Usage:
  python scripts/verify_injecagent_release.py <release_dir>            compare; exit 1 on any difference, write nothing
  python scripts/verify_injecagent_release.py <release_dir> --write    the same checks; write the map only if they all pass

Each case's attacker instruction identifier is sha256 of the attacker instruction text as published in the release. The
release has no numeric instruction id, so the text hash is the identifier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments/external/injecagent_registered_20261001/MANIFEST.json"
SAMPLE = ROOT / "datasets/external_samples/injecagent_phase2_sample.json"
EPISODES = ROOT / "experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json"
OUT = ROOT / "docs/protocols/injecagent_S-A_release_map_20261001.json"
PIN_FILES = {"dh": "data/test_cases_dh_base.json", "ds": "data/test_cases_ds_base.json", "tools": "data/tools.json"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_pins(release: Path, pins: dict) -> list[dict]:
    rows = []
    for name, rel in PIN_FILES.items():
        computed = sha256_file(release / rel)
        rows.append({"pin": name, "file": rel, "pinned": pins[name], "computed": computed,
                     "match": computed == pins[name]})
    return rows


def map_cases(release: Path, sample_ids: list[str], episodes: list[dict]) -> tuple[list[dict], list[str]]:
    base = {k: json.loads((release / PIN_FILES[k]).read_text()) for k in ("dh", "ds")}
    expected = {e["case_id"]: e for e in episodes if e["arm"] == "A0"}
    rows, problems = [], []
    for cid in sample_ids:
        kind, num = cid.split("-")
        idx = int(num)  # 0-based index into the base file; checked below against the episode metadata
        if idx >= len(base[kind]):
            problems.append(f"{cid}: index {idx} outside {PIN_FILES[kind]}")
            continue
        rec = base[kind][idx]
        ep = expected.get(cid)
        if ep is None:
            problems.append(f"{cid}: no A0 episode")
            continue
        if (rec["User Tool"], sorted(rec["Attacker Tools"])) != (ep["user_tool"], sorted(ep["attacker_tools"])):
            problems.append(f"{cid}: release record {idx} does not match the registered episode's tools")
            continue
        rows.append({
            "case_id": cid,
            "kind": kind,
            "release_file": PIN_FILES[kind],
            "release_index": idx,
            "user_tool": rec["User Tool"],
            "attacker_tools": sorted(rec["Attacker Tools"]),
            "attacker_instruction_sha256": sha256_text(rec["Attacker Instruction"]),
            "user_instruction_sha256": sha256_text(rec["User Instruction"]),
        })
    return sorted(rows, key=lambda r: r["case_id"]), problems


def build_map(release: Path, pins: dict, head: str) -> tuple[dict, list[str]]:
    """The map document a fresh run would write, and every problem found. Writes nothing."""
    pin_rows = check_pins(release, pins)
    sample_ids = sorted(json.loads(SAMPLE.read_text())["case_ids"])
    episodes = json.loads(EPISODES.read_text())["episodes"]
    rows, problems = map_cases(release, sample_ids, episodes)
    if head != pins["head"]:
        problems.append(f"release HEAD {head} differs from pinned head {pins['head']}")
    for r in pin_rows:
        if not r["match"]:
            problems.append(f"pin {r['pin']} ({r['file']}): computed {r['computed']} differs from pinned {r['pinned']}")
    if len(rows) != len(sample_ids):
        problems.append(f"mapped {len(rows)} of {len(sample_ids)} cases")
    doc = {
        "status": "DRAFT, NOT FROZEN",
        "release": {"repo": pins["repo"], "head": head},
        "pins": pin_rows,
        "n_cases": len(rows),
        "verbatim_file_match": "the three pinned files match; every mapped record is read from a pinned file",
        "cases": rows,
    }
    return doc, problems


def diff_maps(committed: dict, fresh: dict) -> list[str]:
    """Every difference between the committed map and a fresh one, as readable lines. Empty means identical."""
    if committed == fresh:
        return []
    out = []
    for key in sorted(set(committed) | set(fresh)):
        if key == "cases":
            continue
        if committed.get(key) != fresh.get(key):
            out.append(f"top-level '{key}' differs")
    c_cases = {r["case_id"]: r for r in committed.get("cases", [])}
    f_cases = {r["case_id"]: r for r in fresh.get("cases", [])}
    for cid in sorted(set(c_cases) | set(f_cases)):
        if cid not in f_cases:
            out.append(f"{cid}: in the committed map, not produced by the release")
        elif cid not in c_cases:
            out.append(f"{cid}: produced by the release, not in the committed map")
        elif c_cases[cid] != f_cases[cid]:
            fields = sorted(k for k in set(c_cases[cid]) | set(f_cases[cid]) if c_cases[cid].get(k) != f_cases[cid].get(k))
            out.append(f"{cid}: differs in {', '.join(fields)}")
    if not out:
        out.append("documents differ in a way not covered above")
    return out


def _show(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def run(release: Path, write: bool, committed_path: Path = OUT) -> int:
    pins = json.loads(MANIFEST.read_text())["external"]
    head = subprocess.run(["git", "-C", str(release), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    fresh, problems = build_map(release, pins, head)
    for r in fresh["pins"]:
        print(f"{r['pin']:6s} {r['file']:32s} pinned {r['pinned'][:16]}  computed {r['computed'][:16]}  "
              f"{'MATCH' if r['match'] else 'MISMATCH'}")
    print(f"release HEAD {head}: {'MATCH' if head == pins['head'] else 'MISMATCH'}")
    print(f"mapped to a unique base record: {fresh['n_cases']} of {len(fresh['cases'])}")
    for p in problems:
        print("  problem:", p)
    if problems:
        print("FAILED: the release does not match the pins or the mapping. Nothing written.")
        return 1
    committed = json.loads(committed_path.read_text())
    diffs = diff_maps(committed, fresh)
    for d in diffs:
        print("  difference vs committed map:", d)
    if diffs:
        print("FAILED: the fresh map differs from the committed map. Nothing written.")
        return 1
    print("OK: fresh map identical to the committed map.")
    if write:
        committed_path.write_text(json.dumps(fresh, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
        print(f"wrote {_show(committed_path)} sha256={sha256_file(committed_path)}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("release_dir", type=Path)
    ap.add_argument("--write", action="store_true", help="write the map after all checks pass")
    a = ap.parse_args(argv[1:])
    return run(a.release_dir.resolve(), a.write)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
