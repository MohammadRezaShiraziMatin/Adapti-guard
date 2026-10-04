"""E6 run manifest and freeze-readiness checklist (offline; computes hashes only from files that exist; never fabricates).

Every field that needs a real input is reported as NOT_SET until that input is supplied. Nothing here freezes, tags,
registers or approves anything: the approval record is a file only the owner can create (`e6/APPROVAL_RECORD.json`).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_pack  # noqa: E402
import e6_run_plan  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NOT_SET = "NOT_SET"
PROTOCOL = ROOT / "docs/paper/negative_result/PROTOCOL_CONFIRMATORY_E6_DRAFT.md"
SCHEMA = ROOT / "e6/pack_schema_v1.json"
ANALYSIS = ROOT / "scripts/e6_analysis.py"
REPLAY = ROOT / "scripts/e6_replay.py"
APPROVAL = ROOT / "e6/APPROVAL_RECORD.json"
STATUS = ROOT / "e6/INPUTS_STATUS.json"
DESIGN = {"model": "deepseek-v3.2", "arms": list(e6_run_plan.ARMS) + ["NOINJ"], "families": 30, "instances_per_family": 10,
          "control_episodes": 100, "total_episodes": 1300,
          "retry_policy": "HTTP retry of the pinned runner commit, unchanged from E3; no episode-level re-run; provider errors scored mechanically",
          "provider_error_policy": "kept in all-assigned estimand; >5% provider errors in an arm triggers the drop-block sensitivity"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else NOT_SET


def build_manifest(pack_path: Path | None = None, harness_commit: str | None = None, harness_public_ref: str | None = None,
                   replay_path: Path | None = None, runner_support: bool = False) -> dict:
    m: dict = {"design": DESIGN, "protocol_sha256": sha(PROTOCOL), "schema_sha256": sha(SCHEMA), "analysis_script_sha256": sha(ANALYSIS),
               "replay_script_sha256": sha(REPLAY), "harness_commit": harness_commit or NOT_SET, "harness_public_ref": harness_public_ref or NOT_SET,
               "replay_sha256": sha(replay_path) if replay_path else NOT_SET, "runner_support_verified": bool(runner_support),
               "pack_sha256": NOT_SET, "pack_report": None, "run_plan_sha256": NOT_SET, "seed": NOT_SET, "approval_record": sha(APPROVAL)}
    status = json.loads(STATUS.read_text()) if STATUS.is_file() else {}
    m["INDEPENDENT_AUTHOR"] = status.get("INDEPENDENT_AUTHOR", NOT_SET)
    if pack_path and Path(pack_path).is_file():
        pack = e6_pack.load(Path(pack_path))
        rep = e6_pack.validate(pack)
        m["pack_sha256"], m["pack_report"] = rep["pack_sha256"], {k: rep[k] for k in ("structure_ok", "provenance_complete", "author_excluded", "synthetic", "freeze_eligible", "errors")}
        if rep["structure_ok"] and m["schema_sha256"] != NOT_SET and m["analysis_script_sha256"] != NOT_SET:
            ids = [f["family_id"] for f in pack["families"]]
            m["seed"] = e6_run_plan.seed_from_hashes(m["pack_sha256"], m["schema_sha256"], m["analysis_script_sha256"])
            plan = e6_run_plan.make_plan(ids, DESIGN["instances_per_family"], m["seed"])
            m["run_plan_sha256"] = e6_run_plan.plan_sha256(plan)
            m["plan_accounting"] = {"episodes": len(plan), "A0R": sum(e["arm"] == "A0R" for e in plan), "NOINJ": sum(e["arm"] == "NOINJ" for e in plan)}
    return m


def checklist(m: dict) -> list[tuple[str, bool, str]]:
    rep = m.get("pack_report") or {}
    appr = json.loads(APPROVAL.read_text()) if APPROVAL.is_file() else {}
    hex40 = lambda v: isinstance(v, str) and re.fullmatch(r"[0-9a-f]{40}", v) is not None
    approved = appr.get("status") == "APPROVED" and bool(appr.get("approver")) and appr.get("protocol_sha256") == m["protocol_sha256"]
    return [
        ("independent author recorded (not NOT_AVAILABLE, not an excluded party)", m["INDEPENDENT_AUTHOR"] not in (NOT_SET, "NOT_AVAILABLE") and bool(rep.get("provenance_complete")) and not rep.get("author_excluded"), f"INDEPENDENT_AUTHOR = {m['INDEPENDENT_AUTHOR']}"),
        ("fresh pack present, valid and freeze-eligible (non-synthetic)", bool(rep.get("freeze_eligible")), f"pack_sha256 = {m['pack_sha256']}"),
        ("pack hash, schema hash and seed derivable", NOT_SET not in (m["pack_sha256"], m["schema_sha256"], m["seed"]), f"schema {m['schema_sha256'][:12]}"),
        ("harness public ref (full commit SHA reachable from a public ref or tag)", hex40(m["harness_commit"]) and m["harness_public_ref"] != NOT_SET, f"{m['harness_commit']} / {m['harness_public_ref']}"),
        ("protocol hash", m["protocol_sha256"] != NOT_SET, m["protocol_sha256"][:12]),
        ("replay hash computed on the frozen pack with the real defenses", m["replay_sha256"] != NOT_SET, m["replay_sha256"][:12]),
        ("runner supports E6 (unique ids, A0 replicate, controls, pack loading, DeepSeek only) verified against the public harness", bool(m["runner_support_verified"]), "launcher integration not verified"),
        ("controls and A0 replicate in the run plan (100 / 300)", (m.get("plan_accounting") or {}).get("NOINJ") == 100 and (m.get("plan_accounting") or {}).get("A0R") == 300, str(m.get("plan_accounting"))),
        ("run-plan hash", m["run_plan_sha256"] != NOT_SET, m["run_plan_sha256"][:12]),
        ("statistical specification hashed (analysis script)", m["analysis_script_sha256"] != NOT_SET, m["analysis_script_sha256"][:12]),
        ("owner approval record bound to the protocol hash", approved, "e6/APPROVAL_RECORD.json " + ("valid" if approved else "absent or not bound")),
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack", type=Path)
    ap.add_argument("--harness-commit")
    ap.add_argument("--harness-public-ref")
    ap.add_argument("--replay", type=Path)
    ap.add_argument("--runner-support", action="store_true", help="assert that integration was verified against the public harness (owner statement)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    m = build_manifest(a.pack, a.harness_commit, a.harness_public_ref, a.replay, a.runner_support)
    items = checklist(m)
    if a.json:
        print(json.dumps({"manifest": m, "checklist": [{"item": i, "ok": ok, "detail": d} for i, ok, d in items]}, indent=1, default=str))
    else:
        for i, ok, d in items:
            print(f"[{'x' if ok else ' '}] {i}  ({d})")
        print("FREEZE: " + ("ALLOWED" if all(ok for _, ok, _ in items) else "BLOCKED"))
    return 0 if all(ok for _, ok, _ in items) else 1


if __name__ == "__main__":
    sys.exit(main())
