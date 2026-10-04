"""E6 run manifest and freeze-readiness checklist (offline; computes hashes only from files that exist; never fabricates).

Every field that needs a real input is reported as NOT_SET until that input is supplied. Nothing here freezes, tags,
registers or approves anything: the approval record is a file only the owner can create (`e6/APPROVAL_RECORD.json`).
Hash definitions (protocol section 6a): scenario_set_sha256 = SHA-256 of the canonical rendered file; scoring_schema_sha256 = SHA-256
of `e6/authoring_schema_v1.json`; analysis_sha = SHA-256 of the sorted lines `path:sha256` of the three analysis scripts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_render  # noqa: E402
import e6_run_plan  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NOT_SET = "NOT_SET"
PROTOCOL = ROOT / "docs/paper/negative_result/PROTOCOL_CONFIRMATORY_E6_DRAFT.md"
SCHEMA = ROOT / "e6/authoring_schema_v1.json"
ANALYSIS_SCRIPTS = ("scripts/e6_analysis.py", "scripts/e6_run_plan.py", "scripts/e6_protocol_simulation.py")
RENDERER = ROOT / "scripts/e6_render.py"
REPLAY = ROOT / "scripts/e6_replay.py"
CONSTANTS = ROOT / "e6/harness_constants.json"
APPROVAL = ROOT / "e6/APPROVAL_RECORD.json"
STATUS = ROOT / "e6/INPUTS_STATUS.json"
DESIGN = {"model": "deepseek-v3.2", "arms": list(e6_run_plan.ARMS) + ["NOINJ"], "families": 30, "instances_per_family": 10,
          "control_episodes": 100, "total_episodes": 1300,
          "retry_policy": "HTTP retry of the pinned runner commit, unchanged from E3; no episode-level re-run; provider errors scored mechanically",
          "provider_error_policy": "kept in all-assigned estimand; >5% provider errors in an arm triggers the drop-block sensitivity"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else NOT_SET


def analysis_sha() -> str:
    parts = [f"{p}:{sha(ROOT / p)}" for p in sorted(ANALYSIS_SCRIPTS)]
    return NOT_SET if any(NOT_SET in x for x in parts) else hashlib.sha256("\n".join(parts).encode()).hexdigest()


def build_manifest(authoring_path: Path | None = None, rendered_path: Path | None = None, harness_commit: str | None = None,
                   harness_public_ref: str | None = None, replay_path: Path | None = None, selfcheck_path: Path | None = None) -> dict:
    status = json.loads(STATUS.read_text()) if STATUS.is_file() else {}
    h4 = status.get("H4_NEUTRAL_TWIN", NOT_SET)
    h4 = h4 if h4 in e6_render.H4_POLICIES else None
    consts = json.loads(CONSTANTS.read_text()) if CONSTANTS.is_file() else {}
    m: dict = {"design": DESIGN, "protocol_sha256": sha(PROTOCOL), "scoring_schema_sha256": sha(SCHEMA), "analysis_sha": analysis_sha(),
               "renderer_script_sha256": sha(RENDERER), "replay_script_sha256": sha(REPLAY), "harness_commit": harness_commit or NOT_SET,
               "harness_public_ref": harness_public_ref or NOT_SET, "replay_sha256": sha(replay_path) if replay_path else NOT_SET,
               "runner_support_verified": False, "harness_tree_sha256": NOT_SET, "launcher_script_sha256": sha(ROOT / "scripts/e6_launcher.py"),
               "stage_script_sha256": sha(ROOT / "scripts/e6_stage_harness.py"), "system_prompt_sha256": consts.get("system_prompt_sha256", NOT_SET),
               "tools_sha256": consts.get("tools_sha256", NOT_SET), "authoring_sha256": NOT_SET, "authoring_report": None,
               "scenario_set_sha256": NOT_SET, "rendered_file_sha256": sha(rendered_path) if rendered_path else NOT_SET, "rendering_reproduced": False,
               "h4_policy": h4 or "OWNER_DECISION_REQUIRED", "run_plan_sha256": NOT_SET, "seed": NOT_SET, "approval_record": sha(APPROVAL),
               "INDEPENDENT_AUTHOR": status.get("INDEPENDENT_AUTHOR", NOT_SET)}
    if selfcheck_path and Path(selfcheck_path).is_file():
        sc = json.loads(Path(selfcheck_path).read_text())
        m["runner_support_verified"] = bool(sc.get("passed")) and bool((sc.get("harness_constants") or {}).get("matches"))
        m["harness_tree_sha256"] = sc.get("harness_tree_sha256", NOT_SET)
    if authoring_path and Path(authoring_path).is_file():
        pack = json.loads(Path(authoring_path).read_text())
        rep = e6_render.validate_authoring(pack, h4_policy=h4)
        m["authoring_sha256"] = rep["authoring_sha256"]
        m["authoring_report"] = {k: rep[k] for k in ("structure_ok", "provenance_complete", "author_excluded", "synthetic", "freeze_eligible", "channel_counts", "errors")}
        if rep["structure_ok"]:
            rendered = e6_render.render(pack, h4)
            m["rendering_errors"] = e6_render.validate_rendered(rendered)
            m["scenario_set_sha256"] = e6_render.rendered_sha256(rendered)
            m["rendering_reproduced"] = rendered_path is not None and m["rendered_file_sha256"] == m["scenario_set_sha256"]
            if not m["rendering_errors"] and NOT_SET not in (m["scoring_schema_sha256"], m["analysis_sha"]):
                ids = [f["family_id"] for f in pack["families"]]
                m["seed"] = e6_run_plan.seed_from_hashes(m["scenario_set_sha256"], m["scoring_schema_sha256"], m["analysis_sha"])
                plan = e6_run_plan.make_plan(ids, DESIGN["instances_per_family"], m["seed"])
                m["run_plan_sha256"] = e6_run_plan.plan_sha256(plan)
                m["plan_accounting"] = {"episodes": len(plan), "A0R": sum(e["arm"] == "A0R" for e in plan), "NOINJ": sum(e["arm"] == "NOINJ" for e in plan)}
    return m


def checklist(m: dict) -> list[tuple[str, bool, str]]:
    rep = m.get("authoring_report") or {}
    appr = json.loads(APPROVAL.read_text()) if APPROVAL.is_file() else {}
    hex40 = lambda v: isinstance(v, str) and re.fullmatch(r"[0-9a-f]{40}", v) is not None
    approved = appr.get("status") == "APPROVED" and bool(appr.get("approver")) and appr.get("protocol_sha256") == m["protocol_sha256"]
    acc = m.get("plan_accounting") or {}
    return [
        ("independent author recorded (not NOT_AVAILABLE, not an excluded party)", m["INDEPENDENT_AUTHOR"] not in (NOT_SET, "NOT_AVAILABLE") and bool(rep.get("provenance_complete")) and not rep.get("author_excluded"), f"INDEPENDENT_AUTHOR = {m['INDEPENDENT_AUTHOR']}"),
        ("authoring pack present, valid and freeze-eligible (non-synthetic)", bool(rep.get("freeze_eligible")), f"authoring_sha256 = {m['authoring_sha256']}"),
        ("H4 neutral-twin policy decided by the owner (absent | inert) and controls rendered", m["h4_policy"] in e6_render.H4_POLICIES, f"h4_policy = {m['h4_policy']}"),
        ("rendered scenario file reproduces bit-for-bit from the authoring pack and validates", bool(m["rendering_reproduced"]) and not m.get("rendering_errors"), f"scenario_set_sha256 = {m['scenario_set_sha256']}"),
        ("scenario-set, scoring-schema and analysis hashes and seed derivable", NOT_SET not in (m["scenario_set_sha256"], m["scoring_schema_sha256"], m["analysis_sha"], m["seed"]), f"schema {m['scoring_schema_sha256'][:12]}"),
        ("harness public ref (full commit SHA reachable from a public ref or tag)", hex40(m["harness_commit"]) and m["harness_public_ref"] != NOT_SET, f"{m['harness_commit']} / {m['harness_public_ref']}"),
        ("protocol hash", m["protocol_sha256"] != NOT_SET, m["protocol_sha256"][:12]),
        ("replay hash computed on the rendered scenarios with the real defenses", m["replay_sha256"] != NOT_SET, m["replay_sha256"][:12]),
        ("launcher self-check passed on the sanitized harness (system prompt and tools hashes, /r1 id patch and restore); evidence file carries the harness tree hash", bool(m["runner_support_verified"]) and m["harness_tree_sha256"] != NOT_SET, f"harness_tree_sha256 = {m['harness_tree_sha256']}"),
        ("run plan has 300 A0R and 100 NOINJ of 1,300 episodes", acc.get("NOINJ") == 100 and acc.get("A0R") == 300 and acc.get("episodes") == 1300, str(acc)),
        ("run-plan hash", m["run_plan_sha256"] != NOT_SET, m["run_plan_sha256"][:12]),
        ("statistical specification hashed (analysis_sha over the three analysis scripts)", m["analysis_sha"] != NOT_SET, m["analysis_sha"][:12]),
        ("owner approval record bound to the protocol hash", approved, "e6/APPROVAL_RECORD.json " + ("valid" if approved else "absent or not bound")),
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--authoring", type=Path)
    ap.add_argument("--rendered", type=Path)
    ap.add_argument("--harness-commit")
    ap.add_argument("--harness-public-ref")
    ap.add_argument("--replay", type=Path)
    ap.add_argument("--selfcheck", type=Path, help="evidence file written by `e6_launcher.py selfcheck --out`")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    m = build_manifest(a.authoring, a.rendered, a.harness_commit, a.harness_public_ref, a.replay, a.selfcheck)
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
