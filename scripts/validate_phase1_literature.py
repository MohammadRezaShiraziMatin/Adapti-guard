#!/usr/bin/env python3
"""Phase 1 completion gate (literature only)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "docs/research/LITERATURE_CORPUS.yaml"
EXTR = ROOT / "docs/research/LITERATURE_EXTRACTIONS.yaml"

def main() -> int:
    import yaml
    corpus = yaml.safe_load(CORPUS.read_text())
    extr = yaml.safe_load(EXTR.read_text())
    records = extr.get("records", [])
    errors = []
    if len(records) != 19:
        errors.append(f"expected 19 records, got {len(records)}")
    for r in records:
        if not r.get("verification", {}).get("source_verified"):
            errors.append(f"source_verified false: {r['id']}")
        for f in ["problem", "threat_model", "attack", "dataset", "model", "defense",
                  "evaluation_protocol", "metrics", "limitations_research_gap"]:
            if f not in r.get("extraction", {}):
                errors.append(f"missing field {f} on {r['id']}")
    status = "DONE" if not errors else "PARTIAL"
    out = {"phase1_literature": status, "record_count": len(records), "errors": errors}
    (ROOT / "docs/research/PHASE1_COMPLETION.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if status == "DONE" else 1

if __name__ == "__main__":
    sys.exit(main())
