#!/usr/bin/env python3
"""EAAI compliance contract gate (documentation only; no live execution)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    "docs/research/EAAI_SPECIAL_ISSUE_COMPLIANCE.md",
    "docs/research/EAAI_MANUSCRIPT_ALIGNMENT.md",
    "docs/research/EAAI_TARGET_MODELS.yaml",
]
MARKERS = [
    "Engineering Applications of Artificial Intelligence",
    "Human-Centered and Trustworthy AI for Cybersecurity in Cyber-Physical Systems",
    "PHASE 7 LIVE EXECUTION: BLOCKED",
    "CPS engineering validation",
    "PLANNED",
]


def main() -> int:
    errors = []
    for rel in DOCS:
        if not (ROOT / rel).is_file():
            errors.append(f"missing {rel}")
    comp = ROOT / DOCS[0]
    if comp.is_file():
        text = comp.read_text()
        for m in MARKERS:
            if m not in text:
                errors.append(f"{DOCS[0]}: missing '{m}'")
    models = ROOT / "docs/research/EAAI_TARGET_MODELS.yaml"
    if models.is_file():
        import yaml

        data = yaml.safe_load(models.read_text())
        if data.get("live_evaluated") is True:
            errors.append("EAAI_TARGET_MODELS live_evaluated must not be true")
        for m in data.get("models", []):
            if m.get("status") != "PLANNED":
                errors.append(f"model {m.get('contract_id')} must be PLANNED")
    p7 = ROOT / "docs/research/PHASE7_LIVE_AUTHORIZATION.json"
    if p7.is_file():
        if json.loads(p7.read_text()).get("api_spend_permitted"):
            errors.append("api_spend_permitted must be false")
    elif (ROOT / "scripts/validate_phase7_live_authorization.py").is_file():
        import subprocess

        subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_phase7_live_authorization.py")],
            cwd=ROOT,
            capture_output=True,
        )
        if p7.is_file() and json.loads(p7.read_text()).get("api_spend_permitted"):
            errors.append("api_spend_permitted must be false")
    status = "DONE" if not errors else "PARTIAL"
    out = {"eaai_compliance": status, "errors": errors, "phase7_live": "BLOCKED"}
    (ROOT / "docs/research/EAAI_COMPLIANCE.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if status == "DONE" else 1


if __name__ == "__main__":
    sys.exit(main())
