#!/usr/bin/env python3
"""Phase 2 gate: RQ, threat model, contribution, claims (no live execution)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "docs/research/RESEARCH_QUESTIONS.md",
    "docs/research/THREAT_MODEL_EXTENSIONS.md",
    "docs/research/CONTRIBUTION_Q1.md",
    "docs/research/CLAIMS_MAP.md",
]
MARKERS = {
    "docs/research/RESEARCH_QUESTIONS.md": ["RQ-Core-1", "RQ-Ext-1", "Multi-turn", "Adaptive"],
    "docs/research/THREAT_MODEL_EXTENSIONS.md": ["Trust boundaries", "Out of scope", "Static attacker"],
    "docs/research/CONTRIBUTION_Q1.md": ["Methodological", "Empirical", "Non-contributions"],
    "docs/research/CLAIMS_MAP.md": ["PLANNED", "SUPPORTED", "BLOCKED"],
}

def main() -> int:
    errors = []
    for rel in REQUIRED:
        p = ROOT / rel
        if not p.is_file():
            errors.append(f"missing: {rel}")
            continue
        text = p.read_text()
        for m in MARKERS.get(rel, []):
            if m not in text:
                errors.append(f"{rel}: missing marker '{m}'")
    phase1 = ROOT / "docs/research/PHASE1_COMPLETION.json"
    if phase1.is_file():
        if json.loads(phase1.read_text()).get("phase1_literature") != "DONE":
            errors.append("phase1 not DONE")
    status = "DONE" if not errors else "PARTIAL"
    out = {"phase2_research": status, "errors": errors}
    (ROOT / "docs/research/PHASE2_COMPLETION.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if status == "DONE" else 1

if __name__ == "__main__":
    sys.exit(main())
