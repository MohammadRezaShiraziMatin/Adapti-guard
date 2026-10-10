"""Verify a local InjecAgent checkout against the pins in the registered MANIFEST, and map the S-A sample to release records.

Read-only on the release: no network, no model call. Usage: python scripts/verify_injecagent_release.py <release_dir>
It writes docs/protocols/injecagent_S-A_release_map_20261001.json only if every pin matches and every sample case maps
to exactly one base record whose user tool and attacker tools equal those in the registered A0 episodes.

Each case carries an attacker-instruction identifier: sha256 of the attacker instruction text as published in the release.
The release has no numeric instruction id, so the text hash is the identifier.
"""
from __future__ import annotations

import hashlib
import json
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


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    release = Path(argv[1]).resolve()
    pins = json.loads(MANIFEST.read_text())["external"]
    head = __import__("subprocess").run(["git", "-C", str(release), "rev-parse", "HEAD"],
                                        capture_output=True, text=True).stdout.strip()
    print(f"release HEAD: {head} (pinned: {pins['head']}) {'MATCH' if head == pins['head'] else 'MISMATCH'}")
    pin_rows = check_pins(release, pins)
    for r in pin_rows:
        print(f"{r['pin']:6s} {r['file']:32s} pinned {r['pinned'][:16]}  computed {r['computed'][:16]}  "
              f"{'MATCH' if r['match'] else 'MISMATCH'}")

    sample_ids = sorted(json.loads(SAMPLE.read_text())["case_ids"])
    episodes = json.loads(EPISODES.read_text())["episodes"]
    rows, problems = map_cases(release, sample_ids, episodes)
    print(f"mapped to a unique base record: {len(rows)} of {len(sample_ids)}")
    for p in problems:
        print("  problem:", p)

    if head != pins["head"] or not all(r["match"] for r in pin_rows) or problems or len(rows) != len(sample_ids):
        print("NOT WRITTEN: a check failed.")
        return 1

    doc = {
        "status": "DRAFT, NOT FROZEN",
        "release": {"repo": pins["repo"], "head": head},
        "pins": pin_rows,
        "n_cases": len(rows),
        "verbatim_file_match": "the three pinned files match; every mapped record is read from a pinned file",
        "cases": rows,
    }
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} sha256={sha256_file(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
