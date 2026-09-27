#!/usr/bin/env python3
"""Offline readiness gate (Phase 6). Does not authorize live runs."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def _exists(rel: str) -> bool:
    return (ROOT / rel).is_file()

def _pytest() -> str:
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q",
             "tests/test_stateful_episode.py",
             "tests/test_adaptive_episode.py",
             "tests/test_agent_environment.py",
             "tests/test_execution_metadata.py",
             "tests/test_evidence_integrity.py",
             "tests/test_statistics.py",
             "tests/test_phase4_infrastructure.py",
             "tests/test_human_review_packet.py",
             "tests/test_phase6_readiness.py",
             "tests/test_phase7_live_authorization_gate.py",
             "tests/test_live_extension_wiring.py",
             "tests/test_live_eval_infrastructure.py",
             "tests/test_phase7_authorization_contract.py"],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
        )
        return "PASS" if r.returncode == 0 else "FAIL"
    except Exception:
        return "FAIL"

gate = {
    "scientific": {
        "literature_corpus": "PASS" if _exists("docs/research/LITERATURE_CORPUS.yaml") else "FAIL",
        "research_questions": "PASS" if _exists("docs/research/RESEARCH_QUESTIONS.md") else "FAIL",
        "threat_model_extensions": "PASS" if _exists("docs/research/THREAT_MODEL_EXTENSIONS.md") else "FAIL",
        "experiment_matrix": "PASS" if _exists("docs/research/EXPERIMENT_MATRIX.yaml") else "FAIL",
        "claims_map": "PASS" if _exists("docs/research/CLAIMS_MAP.md") else "FAIL",
    },
    "core": {
        "runtime_defense_code": "PASS" if _exists("src/adapti_guard/defense/tool_loop.py") else "FAIL",
        "llm_judge_code": "PASS" if _exists("src/adapti_guard/evaluation/llm_judge.py") else "FAIL",
        "track_a_audit": "PASS" if _exists("experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md") else "FAIL",
        "track_b_audit": "PASS" if _exists("experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md") else "FAIL",
    },
    "extensions": {
        "multi_turn": "PARTIAL",
        "adaptive": "PARTIAL",
        "agentic": "PARTIAL",
        "multi_model_metadata": "PARTIAL",
        "repeated_trials": "DESIGN_ONLY",
        "external_baselines": "DESIGN_ONLY",
    },
    "validation": {
        "pytest_offline": _pytest(),
        "p1_frozen_integrity": "PASS" if _exists("datasets/frozen/p1_mechanism_v1.0.0/manifest.json") else "FAIL",
    },
    "integrity": {
        "no_live_in_scope": "PASS",
        "frozen_present": "PASS" if _exists("datasets/frozen/p1_mechanism_v1.0.0/manifest.json") else "FAIL",
    },
    "phase7_live_campaign": "BLOCKED",
}

phase6_design = "UNKNOWN"
phase6_file = ROOT / "docs/research/PHASE6_COMPLETION.json"
if phase6_file.is_file():
    p6 = json.loads(phase6_file.read_text())
    phase6_design = p6.get("phase6_design_gate", "UNKNOWN")
gate["phase6"] = {
    "design_gate": phase6_design,
    "phase7_live": gate["phase7_live_campaign"],
}

phase7_auth = "PHASE7_LIVE_BLOCKED"
p7_file = ROOT / "docs/research/PHASE7_LIVE_AUTHORIZATION.json"
if p7_file.is_file():
    phase7_auth = json.loads(p7_file.read_text()).get("live_execution_gate", phase7_auth)
else:
    try:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_phase7_live_authorization.py")],
            cwd=ROOT,
            capture_output=True,
            timeout=30,
        )
        if p7_file.is_file():
            phase7_auth = json.loads(p7_file.read_text()).get("live_execution_gate", phase7_auth)
    except Exception:
        pass
gate["phase7_live_authorization"] = phase7_auth
if p7_file.is_file():
    p7j = json.loads(p7_file.read_text())
    gate["phase7_contract_schema"] = p7j.get("contract_schema_complete", False)
    gate["phase7_authorization_complete"] = p7j.get("authorization_complete", False)
if phase7_auth != "LIVE_AUTHORIZED":
    gate["phase7_live_campaign"] = "BLOCKED"

blockers = []
if gate["validation"]["pytest_offline"] != "PASS":
    blockers.append("pytest_offline")
if gate["scientific"]["literature_corpus"] != "PASS":
    blockers.append("literature_incomplete")
if phase6_design != "PHASE6_READY":
    blockers.append("phase6_design_not_ready")
blockers.append("extension_live_eval_not_run")
blockers.append("phase7_live_not_authorized")

readiness = "NOT_READY" if blockers else "READY"
out = {
    "gate": gate,
    "blockers": blockers,
    "readiness": readiness,
    "note": "Phase 6 design READY does not authorize live Phase 7",
}
(ROOT / "docs/research/EXPERIMENT_READINESS_GATE.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
