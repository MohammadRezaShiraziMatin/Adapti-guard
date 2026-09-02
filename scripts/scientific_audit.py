#!/usr/bin/env python3
"""Automated scientific audit for ADAPTI-GUARD Q1 readiness.

Scans experiment artifacts, validates provenance, classifies simulation vs
real LLM results, and writes an auditable report.

Usage:
    python scripts/scientific_audit.py
    python scripts/scientific_audit.py --output docs/SCIENTIFIC_AUDIT_REPORT.json
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.evaluation.experiment_logging import sha256_file
from src.adapti_guard.evaluation.provenance import (
    ExperimentValidity,
    ProvenanceRecord,
    classify_real_llm_validity,
)
from src.adapti_guard.experiments.env_loader import load_project_env, validate_openrouter_key

load_project_env()

# Known experiment artifact locations
EXPERIMENT_PATHS: list[tuple[str, Path, str]] = [
    ("EXP-000", ROOT / "results/experiment_runs/EXP-000", "api_smoke"),
    ("EXP-002", ROOT / "experiments/EXP002_REAL_LLM", "real_llm"),
    ("EXP-002-target_3", ROOT / "experiments/EXP002_REAL_LLM/target_3", "real_llm"),
    ("EXP-003", ROOT / "experiments/EXP003_BASELINES", "real_llm"),
    ("EXP-005", ROOT / "experiments/EXP005_ADAPTATION", "simulation"),
    ("EXP-008", ROOT / "experiments/EXP008_ADAPTIVE_ATTACK", "simulation"),
    ("EXP-004", ROOT / "experiments/EXP004_MULTI_MODEL", "real_llm"),
    ("REAL-LLM-EVAL", ROOT / "experiments/REAL_LLM_EVAL", "real_llm"),
    ("EXP-017", ROOT / "experiments/runs/EXP-017_V17", "legacy"),
]


def git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=ROOT,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return "UNKNOWN"


def load_metrics(path: Path) -> dict | None:
    metrics_file = path / "metrics.json"
    if not metrics_file.exists():
        return None
    try:
        return json.loads(metrics_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"status": "CORRUPT", "error": "invalid JSON"}


def find_run_provenance(exp_id: str) -> dict:
    """Load latest run provenance from results/experiment_runs/."""
    runs_root = ROOT / "results" / "experiment_runs" / exp_id
    if not runs_root.exists():
        return {}
    run_dirs = sorted(runs_root.glob("RUN-*"), reverse=True)
    if not run_dirs:
        return {}
    latest = run_dirs[0]
    prov = {}
    for name in ("config.json", "dataset_manifest.json", "model_config.json", "environment.json"):
        p = latest / name
        if p.exists():
            prov[name] = json.loads(p.read_text(encoding="utf-8"))
    prov["run_dir"] = str(latest)
    if (latest / "git_commit.txt").exists():
        prov["git_commit"] = (latest / "git_commit.txt").read_text().strip()
    return prov


def audit_experiment(exp_id: str, path: Path, exp_type: str) -> ProvenanceRecord:
    metrics = load_metrics(path)
    issues: list[str] = []
    notes: list[str] = []

    if metrics is None:
        return ProvenanceRecord(
            experiment_id=exp_id,
            path=str(path),
            status="NOT_RUN",
            validity=ExperimentValidity.NOT_RUN,
            evaluation_mode="unknown",
            issues=["No metrics.json found"],
        )

    status = str(metrics.get("status", "UNKNOWN"))
    eval_mode = str(
        metrics.get("evaluation_mode")
        or metrics.get("note", "")
        or metrics.get("metrics", {}).get("evaluation_mode", "")
    )

    if exp_type == "simulation":
        validity = ExperimentValidity.SIMULATION
        if "HARMONIZED" in eval_mode.upper() or metrics.get("per_seed"):
            eval_mode = "HARMONIZED_SIMULATION"
        elif "DETECTOR" in eval_mode.upper():
            eval_mode = "DETECTOR_SIMULATION"
        notes.append("Simulation results — not valid for real LLM security claims")
    elif exp_type == "real_llm":
        validity, issues = classify_real_llm_validity(metrics)
        eval_mode = eval_mode or "real_llm_judge"
    else:
        validity = ExperimentValidity.PARTIAL
        eval_mode = "legacy"

    inner = metrics.get("metrics", metrics)
    n_attack = int(inner.get("n_attack", 0))
    n_benign = int(inner.get("n_benign", 0))
    n_samples = n_attack + n_benign or int(metrics.get("n_samples", 0))
    n_judge_errors = int(inner.get("n_judge_errors", 0))

    prov = find_run_provenance(exp_id.split("-")[0])
    ds_manifest = prov.get("dataset_manifest.json", {})
    model_cfg = prov.get("model_config.json", {})

    record = ProvenanceRecord(
        experiment_id=exp_id,
        path=str(path),
        status=status,
        validity=validity,
        evaluation_mode=eval_mode,
        n_samples=n_samples,
        n_judge_errors=n_judge_errors,
        dataset=ds_manifest.get("path", metrics.get("benchmark_dir", "")),
        dataset_hash=ds_manifest.get("sha256", ""),
        seed=int(metrics.get("seed", prov.get("config.json", {}).get("seed", 0)) or 0) or None,
        git_commit=prov.get("git_commit", ""),
        timestamp=str(metrics.get("timestamp", "")),
        target_model=str(metrics.get("target_model", model_cfg.get("target", ""))),
        judge_model=str(model_cfg.get("judge", "judge")),
        metrics_usable_for_publication=(validity == ExperimentValidity.VALID),
        issues=issues,
        notes=notes,
    )

    # Flag mislabeled COMPLETED with all API failures
    if status == "COMPLETED" and validity == ExperimentValidity.INVALID:
        record.issues.append(
            "MISLABELED: status=COMPLETED but metrics are scientifically invalid"
        )

    return record


def audit_datasets() -> dict:
    datasets = {}
    bench_q1 = ROOT / "datasets" / "benchmark_q1"
    if bench_q1.exists():
        hashes_path = bench_q1 / "hashes.json"
        stats = {}
        if hashes_path.exists():
            stats = json.loads(hashes_path.read_text(encoding="utf-8"))
        for split in ("train", "validation", "test"):
            p = bench_q1 / f"{split}.jsonl"
            if p.exists():
                n = sum(1 for _ in p.open(encoding="utf-8"))
                datasets[f"benchmark_q1/{split}"] = {
                    "path": str(p),
                    "sha256": stats.get("files", {}).get(split, sha256_file(p)),
                    "n_records": n,
                }

    unified = Path.home() / "datasets/q1_llm_security/ADAPTI_GUARD_Benchmark_v2/processed/unified_security_dataset.jsonl"
    if unified.exists():
        n = sum(1 for _ in unified.open(encoding="utf-8"))
        datasets["unified_security_dataset"] = {
            "path": str(unified),
            "sha256": sha256_file(unified),
            "n_records": n,
        }
    return datasets


def compute_readiness(records: list[ProvenanceRecord]) -> dict:
    real_valid = [r for r in records if r.validity == ExperimentValidity.VALID]
    real_invalid = [r for r in records if r.validity == ExperimentValidity.INVALID]
    simulation = [r for r in records if r.validity == ExperimentValidity.SIMULATION]
    blocked = [r for r in records if r.validity == ExperimentValidity.BLOCKED]

    api_ok, api_reason = validate_openrouter_key()

    scores = {
        "infrastructure": 8 if api_ok else 6,
        "real_llm_results": min(10, len(real_valid) * 3),
        "simulation_separated": 9 if simulation else 5,
        "provenance": 7,
        "statistical_validation": 4,
        "human_validation": 1,
        "dataset_coverage": 8,
    }
    overall = round(sum(scores.values()) / len(scores), 1)

    return {
        "overall_readiness": overall,
        "q1_threshold": 8.0,
        "submission_ready": overall >= 8.0 and len(real_valid) >= 2,
        "component_scores": scores,
        "counts": {
            "real_valid": len(real_valid),
            "real_invalid": len(real_invalid),
            "simulation": len(simulation),
            "blocked": len(blocked),
        },
        "api_status": {"ok": api_ok, "reason": api_reason},
    }


def write_markdown_summary(report: dict, path: Path) -> None:
    readiness = report["readiness"]
    records = report["experiments"]
    datasets = report["datasets"]

    lines = [
        "# Scientific Audit Report (Auto-Generated)",
        "",
        f"**Generated:** {report['generated_at']}",
        f"**Git commit:** `{report['git_commit']}`",
        f"**Overall readiness:** {readiness['overall_readiness']}/10 "
        f"(Q1 threshold: {readiness['q1_threshold']})",
        f"**Submission ready:** {'YES' if readiness['submission_ready'] else 'NO'}",
        "",
        "## API Status",
        "",
        f"- OpenRouter: {'PASS' if readiness['api_status']['ok'] else 'BLOCKED'} — "
        f"{readiness['api_status']['reason']}",
        "",
        "## Experiment Inventory",
        "",
        "| ID | Status | Validity | Mode | N | Publication-ready | Issues |",
        "|---|---|---|---|---:|---|---|",
    ]

    for r in records:
        issues = "; ".join(r["issues"][:2]) if r["issues"] else "—"
        lines.append(
            f"| {r['experiment_id']} | {r['status']} | {r['validity']} | "
            f"{r['evaluation_mode'][:20]} | {r['n_samples']} | "
            f"{'✅' if r['metrics_usable_for_publication'] else '❌'} | {issues} |"
        )

    lines.extend([
        "",
        "## Datasets",
        "",
        "| Dataset | Records | SHA256 (prefix) |",
        "|---|---:|---|",
    ])
    for name, info in datasets.items():
        h = info.get("sha256", "")[:16]
        lines.append(f"| {name} | {info.get('n_records', '?')} | `{h}...` |")

    lines.extend([
        "",
        "## Component Scores",
        "",
    ])
    for k, v in readiness["component_scores"].items():
        lines.append(f"- **{k}:** {v}/10")

    lines.extend([
        "",
        "## Critical Gaps",
        "",
        "1. No VALID real-LLM experiment with publication sample size (≥50)",
        "2. EXP-002 artifacts marked COMPLETED but contain 100% API/judge errors",
        "3. All adaptation/ablation results are simulation-only",
        "4. Human judge validation not executed",
        "5. SOTA baselines (Llama Guard) use regex fallback",
        "",
        "---",
        "*Regenerate: `python scripts/scientific_audit.py`*",
    ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="ADAPTI-GUARD scientific audit")
    parser.add_argument(
        "--output",
        default="docs/SCIENTIFIC_AUDIT_REPORT.json",
        help="JSON report path",
    )
    parser.add_argument(
        "--markdown",
        default="docs/SCIENTIFIC_AUDIT_REPORT.md",
        help="Markdown summary path",
    )
    args = parser.parse_args()

    records = [audit_experiment(eid, path, etype) for eid, path, etype in EXPERIMENT_PATHS]
    datasets = audit_datasets()
    readiness = compute_readiness(records)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "audit_version": "1.0.0",
        "readiness": readiness,
        "datasets": datasets,
        "experiments": [r.to_dict() for r in records],
        "rules": {
            "no_fabricated_results": True,
            "simulation_separated": True,
            "provenance_required": [
                "dataset_hash", "seed", "git_commit", "model_version", "timestamp",
            ],
        },
    }

    out_json = ROOT / args.output
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    out_md = ROOT / args.markdown
    write_markdown_summary(report, out_md)

    # Update registry summary
    reg_path = ROOT / "docs" / "EXPERIMENT_STATUS.md"
    _update_experiment_status(reg_path, records, readiness)

    print(f"Audit complete: {out_json}")
    print(f"Summary:        {out_md}")
    print(f"Readiness:      {readiness['overall_readiness']}/10")
    print(f"Submission:     {'YES' if readiness['submission_ready'] else 'NO'}")
    return 0


def _update_experiment_status(
    path: Path,
    records: list[ProvenanceRecord],
    readiness: dict,
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# Experiment Status",
        "",
        f"**Last updated:** {ts} (auto-generated by `scripts/scientific_audit.py`)",
        "",
        "| ID | File Status | Scientific Validity | Mode | N | Pub-ready |",
        "|---|---|---|---|---:|---|",
    ]
    for r in records:
        pub = "✅" if r.metrics_usable_for_publication else "❌"
        lines.append(
            f"| {r.experiment_id} | {r.status} | {r.validity.value} | "
            f"{r.evaluation_mode[:24]} | {r.n_samples} | {pub} |"
        )
    lines.extend([
        "",
        "## Readiness",
        "",
        f"- Overall: **{readiness['overall_readiness']}/10**",
        f"- Submission ready: **{'YES' if readiness['submission_ready'] else 'NO'}**",
        f"- Real VALID experiments: **{readiness['counts']['real_valid']}**",
        f"- API: {'PASS' if readiness['api_status']['ok'] else 'BLOCKED'}",
        "",
        "See `docs/SCIENTIFIC_AUDIT.md` for full audit. "
        "See `docs/SIMULATION_VS_REAL_LLM.md` for evidence classification.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
