#!/usr/bin/env python3
"""Phase 3 gate: framework, matrix, evidence schema, protocol."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "docs/research/UNIFIED_RESEARCH_FRAMEWORK.md",
    "docs/research/EXPERIMENT_PROTOCOL.md",
    "docs/research/EXPERIMENT_MATRIX.yaml",
    "docs/research/EVIDENCE_SCHEMA.yaml",
    "docs/research/REPRODUCIBILITY.md",
]
MARKERS = {
    "docs/research/UNIFIED_RESEARCH_FRAMEWORK.md": ["Phase 4", "interaction_mode", "adaptivity"],
    "docs/research/EXPERIMENT_PROTOCOL.md": ["Target ≠ Judge", "Failure semantics", "Live execution gate"],
    "docs/research/EVIDENCE_SCHEMA.yaml": ["target_ne_judge", "evidence_type", "historical_audit"],
}

def main() -> int:
    import yaml
    errors = []
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing: {rel}")
            continue
        if rel in MARKERS:
            text = (ROOT / rel).read_text()
            for m in MARKERS[rel]:
                if m not in text:
                    errors.append(f"{rel}: missing '{m}'")
    matrix = yaml.safe_load((ROOT / "docs/research/EXPERIMENT_MATRIX.yaml").read_text())
    rows = matrix.get("rows", [])
    ids = [r.get("condition_id") for r in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate condition_id in matrix")
    for r in rows:
        if r.get("target_ne_judge") and r.get("target_model_id") == r.get("judge_id"):
            errors.append(f"target==judge: {r.get('condition_id')}")
    if not any(r.get("condition_id", "").startswith("COND-TRACK-A") for r in rows):
        errors.append("missing Track A conditions")
    status = "DONE" if not errors else "PARTIAL"
    out = {"phase3_framework": status, "condition_rows": len(rows), "errors": errors}
    (ROOT / "docs/research/PHASE3_COMPLETION.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if status == "DONE" else 1

if __name__ == "__main__":
    sys.exit(main())
