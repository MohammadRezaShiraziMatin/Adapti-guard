#!/usr/bin/env python3
"""Phase 6 gate: pre-experiment validation & statistical readiness (no live runs)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

DOC = "docs/research/PHASE6_PRE_EXPERIMENT_VALIDATION.md"
COND_YAML = "docs/research/PHASE6_CONDITION_READINESS.yaml"
MARKERS = [
    "Primary outcome",
    "McNemar",
    "Target ≠ Judge",
    "phase7_live_campaign",
    "target_failure",
    "Episode",
]


def _phase_done(name: str, key: str) -> bool:
    p = ROOT / f"docs/research/{name}"
    if not p.is_file():
        return False
    return json.loads(p.read_text()).get(key) == "DONE"


def _matrix_rows():
    import yaml

    data = yaml.safe_load((ROOT / "docs/research/EXPERIMENT_MATRIX.yaml").read_text())
    return data.get("rows", [])


def main() -> int:
    errors = []
    for rel in (DOC, COND_YAML, "docs/research/EXPERIMENT_MATRIX.yaml"):
        if not (ROOT / rel).is_file():
            errors.append(f"missing {rel}")
    if (ROOT / DOC).is_file():
        text = (ROOT / DOC).read_text()
        for m in MARKERS:
            if m not in text:
                errors.append(f"{DOC}: missing '{m}'")

    for phase_file, key in (
        ("PHASE3_COMPLETION.json", "phase3_framework"),
        ("PHASE4_COMPLETION.json", "phase4_infrastructure"),
        ("PHASE5_COMPLETION.json", "phase5_trustworthy"),
    ):
        if not _phase_done(phase_file, key):
            errors.append(f"{phase_file} not DONE")

    rows = _matrix_rows()
    yaml_rows = []
    if (ROOT / COND_YAML).is_file():
        import yaml

        yaml_rows = yaml.safe_load((ROOT / COND_YAML).read_text()).get("rows", [])
    matrix_ids = {r.get("condition_id") for r in rows}
    yaml_ids = {r.get("condition_id") for r in yaml_rows}
    if matrix_ids != yaml_ids:
        errors.append("PHASE6_CONDITION_READINESS.yaml ids != EXPERIMENT_MATRIX.yaml")

    from adapti_guard.evaluation.component_resolver import (
        ComponentResolutionError,
        resolve_attack,
        resolve_defense,
    )
    from adapti_guard.evaluation.condition_resolver import resolve_condition

    for row in rows:
        cid = row.get("condition_id")
        if row.get("target_ne_judge") and row.get("judge_id") not in (None, "n/a", "mock_judge"):
            if row.get("target_model_id") == row.get("judge_id"):
                errors.append(f"target==judge: {cid}")
        try:
            resolve_condition(cid)
        except Exception as exc:
            errors.append(f"resolve_condition {cid}: {exc}")

    for cid in (
        "COND-E1-STATEFUL-OFFLINE",
        "COND-E2-ADAPTIVE-OFFLINE",
        "COND-E3-AGENT-OFFLINE",
    ):
        row, ctx = resolve_condition(cid)
        try:
            resolve_attack(ctx.attack_id)
            resolve_defense(ctx.defense_id, adaptivity=ctx.adaptivity)
        except ComponentResolutionError as exc:
            errors.append(f"component resolve {cid}: {exc}")

    for live_attack in ("vnext_confirm_v1.0", "phase1_confirm_v1"):
        try:
            resolve_attack(live_attack)
            errors.append(f"live attack {live_attack} should not resolve offline")
        except ComponentResolutionError:
            pass

    blocked = sum(1 for r in yaml_rows if r.get("phase7_prerun") == "BLOCKED")
    if blocked < 2:
        errors.append("expected BLOCKED conditions in readiness yaml")

    phase6_design = "PHASE6_READY" if not errors else "PHASE6_NOT_READY"
    phase7_live = "PHASE7_LIVE_BLOCKED"
    status = "DONE" if phase6_design == "PHASE6_READY" else "PARTIAL"
    out = {
        "phase6_pre_experiment": status,
        "phase6_design_gate": phase6_design,
        "phase7_live_gate": phase7_live,
        "errors": errors,
    }
    (ROOT / "docs/research/PHASE6_COMPLETION.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if status == "DONE" else 1


if __name__ == "__main__":
    sys.exit(main())
