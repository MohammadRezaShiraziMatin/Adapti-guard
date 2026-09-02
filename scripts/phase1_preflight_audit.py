#!/usr/bin/env python3
"""Phase 1: Pre-experiment scientific audit gate.

Inspects infrastructure integrity BEFORE any real LLM experiments run.
Produces a gate report — experiments must not start until critical gates pass.

Usage:
    python scripts/phase1_preflight_audit.py
    python scripts/phase1_preflight_audit.py --json docs/PHASE1_AUDIT_REPORT.json
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@dataclass
class AuditGate:
    id: str
    category: str
    name: str
    status: str  # PASS | FAIL | WARN | BLOCKED
    detail: str
    blocking: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
            "blocking": self.blocking,
        }


@dataclass
class Phase1AuditReport:
    generated_at: str
    git_commit: str
    gates: list[AuditGate] = field(default_factory=list)
    experiments_cleared: bool = False
    blocking_failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "git_commit": self.git_commit,
            "experiments_cleared": self.experiments_cleared,
            "blocking_failures": self.blocking_failures,
            "summary": {
                "pass": sum(1 for g in self.gates if g.status == "PASS"),
                "fail": sum(1 for g in self.gates if g.status == "FAIL"),
                "warn": sum(1 for g in self.gates if g.status == "WARN"),
                "blocked": sum(1 for g in self.gates if g.status == "BLOCKED"),
            },
            "gates": [g.to_dict() for g in self.gates],
        }


def git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, cwd=ROOT, timeout=5,
        )
        return r.stdout.strip()
    except Exception:
        return "UNKNOWN"


def _gate(gates: list[AuditGate], gate: AuditGate) -> None:
    gates.append(gate)
    if gate.blocking and gate.status in ("FAIL", "BLOCKED"):
        pass  # collected later


def inspect_metric_source_integrity(gates: list[AuditGate]) -> None:
    """Ensure real LLM paths use judge, not simulation."""
    from src.adapti_guard.evaluation.evaluation_modes import (
        LEGACY_SIMULATION_ONLY,
        REAL_LLM_JUDGE,
    )

    # Real pipeline modules must reference real_llm_judge
    real_paths = [
        ROOT / "src/adapti_guard/evaluation/attack_success.py",
        ROOT / "src/adapti_guard/experiments/real_llm_pipeline.py",
        ROOT / "src/adapti_guard/experiments/multi_model_eval.py",
    ]
    for p in real_paths:
        text = p.read_text(encoding="utf-8")
        uses_judge = any(
            token in text
            for token in ("LLMJudge", "build_judge", "judge=judge", "judge: LLMJudge")
        )
        no_regex_asr = "llm_response_attack_success" not in text and "attack_outcome" not in text
        _gate(gates, AuditGate(
            id=f"METRIC-{p.stem[:8]}",
            category="metric_integrity",
            name=f"Real path: {p.name}",
            status="PASS" if uses_judge and no_regex_asr else "FAIL",
            detail=f"LLMJudge={uses_judge}, no_simulation_asr={no_regex_asr}",
            blocking=True,
        ))

    # Legacy paths must be labeled
    legacy_paths = [
        ROOT / "src/adapti_guard/experiments/harmonized_runner.py",
        ROOT / "experiments/EXP005_ADAPTATION/run.py",
    ]
    for p in legacy_paths:
        text = p.read_text(encoding="utf-8")
        labeled = LEGACY_SIMULATION_ONLY in text or "LEGACY_SIMULATION" in text
        _gate(gates, AuditGate(
            id=f"LEGACY-{p.stem[:8]}",
            category="metric_integrity",
            name=f"Legacy labeled: {p.name}",
            status="PASS" if labeled else "WARN",
            detail=f"LEGACY_SIMULATION_ONLY present={labeled}",
            blocking=False,
        ))


def inspect_judge_blindness(gates: list[AuditGate]) -> None:
    from src.adapti_guard.evaluation.llm_judge import FORBIDDEN_JUDGE_FIELDS, JudgeInput

    sample = JudgeInput(
        user_prompt="test", model_response="response", is_benign=False,
    )
    payload = sample.to_blind_payload()
    leaked = [f for f in FORBIDDEN_JUDGE_FIELDS if f in payload]
    _gate(gates, AuditGate(
        id="JUDGE-001",
        category="judge",
        name="Blind judge payload",
        status="PASS" if not leaked else "FAIL",
        detail=f"forbidden_fields_in_payload={leaked}",
        blocking=True,
    ))

    cfg = ROOT / "configs/models.yaml"
    text = cfg.read_text(encoding="utf-8")
    has_primary = "judge_primary" in text and "claude-sonnet-4" in text
    has_fallback = "judge_fallback" in text and "gpt-4o" in text
    _gate(gates, AuditGate(
        id="JUDGE-002",
        category="judge",
        name="Judge model config",
        status="PASS" if has_primary and has_fallback else "FAIL",
        detail="primary=Claude Sonnet 4, fallback=GPT-4o",
        blocking=True,
    ))


def inspect_target_models(gates: list[AuditGate]) -> None:
    import yaml

    cfg = yaml.safe_load((ROOT / "configs/models.yaml").read_text(encoding="utf-8"))
    models = cfg.get("models", {})
    required = {
        "model_a": "gpt-4o-mini",
        "model_b": "qwen3-30b-a3b",
        "model_c": "deepseek",
    }
    for key, fragment in required.items():
        spec = models.get(key, {})
        model_id = str(spec.get("model", ""))
        ok = fragment.lower() in model_id.lower()
        _gate(gates, AuditGate(
            id=f"MODEL-{key}",
            category="models",
            name=f"Target {key}",
            status="PASS" if ok else "FAIL",
            detail=model_id or "missing",
            blocking=True,
        ))


def inspect_api_readiness(gates: list[AuditGate]) -> None:
    from src.adapti_guard.experiments.env_loader import load_project_env, validate_openrouter_key

    load_project_env()
    ok, reason = validate_openrouter_key()
    _gate(gates, AuditGate(
        id="API-001",
        category="api",
        name="OpenRouter API key",
        status="PASS" if ok else "BLOCKED",
        detail=reason,
        blocking=True,
    ))

    try:
        from src.adapti_guard.evaluation.target_model import OllamaTargetModel
        ollama_ok = OllamaTargetModel.is_available()
    except Exception as exc:
        ollama_ok = False
        reason_ollama = str(exc)
    else:
        reason_ollama = "available" if ollama_ok else "not running"
    _gate(gates, AuditGate(
        id="API-002",
        category="api",
        name="Ollama fallback",
        status="PASS" if ollama_ok else "WARN",
        detail=reason_ollama,
        blocking=False,
    ))


def inspect_datasets(gates: list[AuditGate]) -> None:
    from src.adapti_guard.evaluation.experiment_logging import sha256_file

    datasets = [
        ("benchmark_q1/test", ROOT / "datasets/benchmark_q1/test.jsonl", 100),
        ("unified", Path.home() / "datasets/q1_llm_security/ADAPTI_GUARD_Benchmark_v2/processed/unified_security_dataset.jsonl", 1000),
    ]
    for name, path, min_records in datasets:
        if not path.exists():
            _gate(gates, AuditGate(
                id=f"DATA-{name}",
                category="dataset",
                name=f"Dataset {name}",
                status="FAIL",
                detail=f"not found: {path}",
                blocking=True,
            ))
            continue
        n = sum(1 for _ in path.open(encoding="utf-8"))
        h = sha256_file(path)
        _gate(gates, AuditGate(
            id=f"DATA-{name}",
            category="dataset",
            name=f"Dataset {name}",
            status="PASS" if n >= min_records else "WARN",
            detail=f"n={n}, sha256={h[:16]}...",
            blocking=n < min_records,
        ))


def inspect_existing_artifacts(gates: list[AuditGate]) -> None:
    from src.adapti_guard.evaluation.provenance import classify_real_llm_validity

    artifact_paths = [
        ("EXP-002", ROOT / "experiments/EXP002_REAL_LLM/target_3/metrics.json"),
        ("EXP-004", ROOT / "experiments/EXP004_MULTI_MODEL/metrics.json"),
        ("EXP-005", ROOT / "experiments/EXP005_ADAPTATION/metrics.json"),
        ("REAL-LLM-EVAL", ROOT / "experiments/REAL_LLM_EVAL/metrics.json"),
    ]
    for exp_id, path in artifact_paths:
        if not path.exists():
            _gate(gates, AuditGate(
                id=f"ART-{exp_id}",
                category="artifacts",
                name=f"Artifact {exp_id}",
                status="WARN",
                detail="no metrics.json",
                blocking=False,
            ))
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        status = str(data.get("status", "UNKNOWN"))
        eval_mode = str(data.get("evaluation_mode", ""))
        validity, issues = classify_real_llm_validity(data, min_samples=50)

        if eval_mode == "LEGACY_SIMULATION_ONLY" or "SIMULATION" in eval_mode:
            gate_status = "WARN"
            detail = f"LEGACY_SIMULATION_ONLY — not for publication ({status})"
        elif validity.value == "VALID":
            gate_status = "PASS"
            detail = f"VALID real LLM results (n={data.get('n_samples', '?')})"
        elif status == "BLOCKED":
            gate_status = "BLOCKED"
            detail = data.get("reason", "blocked")
        elif validity.value == "INVALID":
            gate_status = "FAIL"
            detail = "; ".join(issues) or "invalid metrics"
        else:
            gate_status = "WARN"
            detail = f"status={status}, validity={validity.value}"

        _gate(gates, AuditGate(
            id=f"ART-{exp_id}",
            category="artifacts",
            name=f"Artifact {exp_id}",
            status=gate_status,
            detail=detail,
            blocking=(validity.value == "INVALID" and status == "COMPLETED"),
        ))


def inspect_statistical_framework(gates: list[AuditGate]) -> None:
    modules = [
        "src.adapti_guard.evaluation.statistics",
        "src.adapti_guard.evaluation.multi_model_statistics",
    ]
    for mod in modules:
        try:
            m = importlib.import_module(mod.replace("/", ".").replace("src.", "src."))
            has_bootstrap = hasattr(m, "bootstrap_ci") or "bootstrap" in dir(m)
            has_mcnemar = hasattr(m, "mcnemar_test") or hasattr(m, "paired_baseline_comparison")
            _gate(gates, AuditGate(
                id=f"STAT-{mod.split('.')[-1][:8]}",
                category="statistics",
                name=f"Module {mod.split('.')[-1]}",
                status="PASS" if has_bootstrap or has_mcnemar else "WARN",
                detail="bootstrap + mcnemar available",
                blocking=False,
            ))
        except ImportError as exc:
            _gate(gates, AuditGate(
                id=f"STAT-{mod}",
                category="statistics",
                name=f"Module {mod}",
                status="FAIL",
                detail=str(exc),
                blocking=False,
            ))


def inspect_sota_baselines(gates: list[AuditGate]) -> None:
    sota_files = ["baselines/llama_guard.py", "baselines/prompt_guard.py", "baselines/nemo_guardrails.py"]
    for rel in sota_files:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        uses_fallback = "fallback" in text.lower() or "regex" in text.lower()
        _gate(gates, AuditGate(
            id=f"SOTA-{path.stem}",
            category="sota",
            name=f"SOTA baseline {path.stem}",
            status="WARN" if uses_fallback else "PASS",
            detail="uses regex fallback when model unavailable — NOT valid SOTA comparison",
            blocking=False,
        ))


def inspect_tests(gates: list[AuditGate]) -> None:
    test_files = [
        "tests/test_blind_judge.py",
        "tests/test_provenance.py",
        "tests/test_real_llm_pipeline.py",
        "tests/test_multi_model_statistics.py",
    ]
    missing = [t for t in test_files if not (ROOT / t).exists()]
    _gate(gates, AuditGate(
        id="TEST-001",
        category="tests",
        name="Scientific integrity tests",
        status="PASS" if not missing else "FAIL",
        detail=f"missing={missing}" if missing else f"{len(test_files)} test modules present",
        blocking=bool(missing),
    ))


def run_phase1_audit() -> Phase1AuditReport:
    gates: list[AuditGate] = []

    inspect_metric_source_integrity(gates)
    inspect_judge_blindness(gates)
    inspect_target_models(gates)
    inspect_api_readiness(gates)
    inspect_datasets(gates)
    inspect_existing_artifacts(gates)
    inspect_statistical_framework(gates)
    inspect_sota_baselines(gates)
    inspect_tests(gates)

    blocking = [g for g in gates if g.blocking and g.status in ("FAIL", "BLOCKED")]
    cleared = len(blocking) == 0

    return Phase1AuditReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        git_commit=git_commit(),
        gates=gates,
        experiments_cleared=cleared,
        blocking_failures=[f"{g.id}: {g.name} — {g.detail}" for g in blocking],
    )


def write_markdown(report: Phase1AuditReport, path: Path) -> None:
    lines = [
        "# Phase 1: Pre-Experiment Scientific Audit",
        "",
        f"**Generated:** {report.generated_at}",
        f"**Git commit:** `{report.git_commit}`",
        f"**Experiments cleared to run:** {'YES' if report.experiments_cleared else 'NO'}",
        "",
    ]
    if report.blocking_failures:
        lines.append("## Blocking Failures")
        lines.append("")
        for b in report.blocking_failures:
            lines.append(f"- {b}")
        lines.append("")

    categories = sorted(set(g.category for g in report.gates))
    for cat in categories:
        lines.append(f"## {cat.replace('_', ' ').title()}")
        lines.append("")
        lines.append("| Gate | Status | Detail |")
        lines.append("|---|---|---|")
        for g in report.gates:
            if g.category == cat:
                block = " ⛔" if g.blocking else ""
                lines.append(f"| {g.name}{block} | {g.status} | {g.detail[:80]} |")
        lines.append("")

    lines.extend([
        "## Pre-Run Checklist",
        "",
        "Before executing EXP-004 multi-model evaluation:",
        "",
        "1. [ ] `python scripts/phase1_preflight_audit.py` — all blocking gates PASS",
        "2. [ ] `python scripts/preflight_api.py` — API key valid",
        "3. [ ] Smoke test: `python experiments/EXP004_MULTI_MODEL/run.py --n-samples 5 --targets model_a --baselines B0 B3`",
        "4. [ ] Verify `validity: VALID` in output metrics",
        "5. [ ] Full run only after smoke test passes",
        "",
        "---",
        "*Regenerate: `python scripts/phase1_preflight_audit.py`*",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 1 pre-experiment audit")
    parser.add_argument("--json", default="docs/PHASE1_AUDIT_REPORT.json")
    parser.add_argument("--markdown", default="PHASE1_SCIENTIFIC_AUDIT.md")
    args = parser.parse_args()

    report = run_phase1_audit()

    json_path = ROOT / args.json
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")

    md_path = ROOT / args.markdown
    write_markdown(report, md_path)

    s = report.to_dict()["summary"]
    print(f"Phase 1 Audit: {json_path}")
    print(f"Markdown:      {md_path}")
    print(f"Gates: PASS={s['pass']} FAIL={s['fail']} WARN={s['warn']} BLOCKED={s['blocked']}")
    print(f"Cleared:       {'YES' if report.experiments_cleared else 'NO'}")

    if report.blocking_failures:
        print("\nBlocking failures:")
        for b in report.blocking_failures:
            print(f"  - {b}")

    return 0 if report.experiments_cleared else 1


if __name__ == "__main__":
    raise SystemExit(main())
