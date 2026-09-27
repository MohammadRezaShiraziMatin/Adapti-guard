#!/usr/bin/env python3
"""Phase 4 gate: condition resolver + offline runner present."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

MODULES = [
    "src/adapti_guard/evaluation/condition_resolver.py",
    "src/adapti_guard/evaluation/component_resolver.py",
    "src/adapti_guard/evaluation/offline_experiment_runner.py",
]
TESTS = "tests/test_phase4_infrastructure.py"


def main() -> int:
    errors = []
    for rel in MODULES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing {rel}")
    if not (ROOT / TESTS).is_file():
        errors.append(f"missing {TESTS}")
    try:
        from adapti_guard.evaluation.component_resolver import resolve_attack, resolve_defense
        from adapti_guard.evaluation.condition_resolver import resolve_condition

        resolve_condition("COND-E1-STATEFUL-OFFLINE")
        resolve_attack("fixture")
        resolve_defense("runtime_fixture")
    except Exception as exc:
        errors.append(f"resolve smoke: {exc}")
    status = "DONE" if not errors else "PARTIAL"
    out = {"phase4_infrastructure": status, "errors": errors}
    (ROOT / "docs/research/PHASE4_COMPLETION.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if status == "DONE" else 1


if __name__ == "__main__":
    sys.exit(main())
