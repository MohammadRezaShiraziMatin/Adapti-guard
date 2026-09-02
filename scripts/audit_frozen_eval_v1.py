#!/usr/bin/env python3
"""Audit eval_v1 candidates and promote to frozen/ only if PASS.

Usage:
    python scripts/audit_frozen_eval_v1.py
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_DIR = ROOT / "datasets" / "benchmark_q1"
PROCESSED = ROOT / "datasets" / "processed"
FROZEN = ROOT / "datasets" / "frozen" / "eval_v1"
AUDIT = ROOT / "datasets" / "audit" / "phase2_5_remediation"

MIN_PER_CATEGORY = 110
TARGET_TOTAL = 770
REQUIRED_FIELDS = [
    "id", "text", "category", "source", "provenance", "sha256",
]

CATEGORY_ORDER = [
    "prompt_injection", "jailbreak", "rag_security", "context_attack",
    "role_attack", "tool_abuse", "system_prompt_leakage",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def audit() -> dict[str, Any]:
    candidates_path = PROCESSED / "eval_v1_candidates.jsonl"
    manifest_path = PROCESSED / "eval_v1_build_manifest.json"
    if not candidates_path.exists():
        return {"verdict": "FREEZE_BLOCKED", "reason": "missing eval_v1_candidates.jsonl — run build_frozen_eval_v1.py"}

    rows = load_jsonl(candidates_path)
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    # benchmark immutability
    expected = json.loads((BENCHMARK_DIR / "hashes.json").read_text())["files"]
    hash_ok = sha256_file(BENCHMARK_DIR / "test.jsonl") == expected["test"]

    train_val_hashes = set()
    for split in ["train", "validation"]:
        for r in load_jsonl(BENCHMARK_DIR / f"{split}.jsonl"):
            train_val_hashes.add(normalize_text(r.get("prompt", "") + "\n" + r.get("context", "")))

    infra_ids = set()
    infra_path = ROOT / "experiments" / "INFRA-SMOKE-001" / "config.json"
    if infra_path.exists():
        infra_ids = set(json.loads(infra_path.read_text())["dataset_meta"]["sample_ids"])

    issues: list[str] = []
    checks: dict[str, bool] = {}

    # basic counts
    checks["hash_benchmark_test_unchanged"] = hash_ok
    if not hash_ok:
        issues.append("benchmark_q1 test hash mismatch vs hashes.json")

    cat_counts = Counter(r["category"] for r in rows)
    for cat in CATEGORY_ORDER:
        n = cat_counts.get(cat, 0)
        checks[f"category_{cat}_gte_{MIN_PER_CATEGORY}"] = n >= MIN_PER_CATEGORY
        if n < MIN_PER_CATEGORY:
            issues.append(f"CATEGORY_GAP: {cat} has {n} < {MIN_PER_CATEGORY}")

    checks["total_gte_target"] = len(rows) >= TARGET_TOTAL
    if len(rows) < TARGET_TOTAL:
        issues.append(f"TOTAL_GAP: {len(rows)} < {TARGET_TOTAL}")

    # uniqueness
    ids = [r["id"] for r in rows]
    hashes = [r["sha256"] for r in rows]
    checks["unique_ids"] = len(ids) == len(set(ids))
    checks["unique_sha256"] = len(hashes) == len(set(hashes))
    if len(ids) != len(set(ids)):
        issues.append("DUPLICATE_IDS")
    if len(hashes) != len(set(hashes)):
        issues.append("DUPLICATE_SHA256")

    # provenance / fields
    missing_prov = 0
    empty_text = 0
    for r in rows:
        for f in REQUIRED_FIELDS:
            if f not in r or r[f] in (None, ""):
                missing_prov += 1
        if not str(r.get("text", "")).strip():
            empty_text += 1
    checks["no_missing_provenance"] = missing_prov == 0
    checks["no_empty_text"] = empty_text == 0
    if missing_prov:
        issues.append(f"MISSING_PROVENANCE_FIELDS: {missing_prov}")
    if empty_text:
        issues.append(f"EMPTY_TEXT: {empty_text}")

    # leakage
    leak_train_val = sum(
        1 for r in rows if normalize_text(r.get("text", "")) in train_val_hashes
    )
    leak_infra = sum(
        1 for r in rows
        if r.get("benchmark_q1_id") in infra_ids
    )
    checks["no_train_val_leakage"] = leak_train_val == 0
    checks["no_infra_smoke_overlap"] = leak_infra == 0
    if leak_train_val:
        issues.append(f"TRAIN_VAL_LEAKAGE: {leak_train_val}")
    if leak_infra:
        issues.append(f"INFRA_SMOKE_OVERLAP: {leak_infra}")

    # evaluation_mode metadata
    checks["all_real_sources"] = all(
        r.get("source") in {
            "benchmark_q1", "injecagent", "agentdojo", "garak", "trustllm",
        }
        for r in rows
    )

    passed = all(checks.values()) and not issues
    verdict = "FREEZE" if passed else "FREEZE_BLOCKED"

    report = {
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "verdict": verdict,
        "checks": checks,
        "issues": issues,
        "n_samples": len(rows),
        "category_counts": dict(cat_counts),
        "manifest_summary": {
            "available_after_dedupe": manifest.get("available_after_dedupe"),
            "adaptive_template_derived_count": manifest.get("adaptive_template_derived_count"),
        },
        "source_distribution": dict(Counter(r["source"] for r in rows)),
    }

    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT / "eval_v1_audit_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    if passed:
        FROZEN.mkdir(parents=True, exist_ok=True)
        dataset_path = FROZEN / "dataset.jsonl"
        shutil.copy2(candidates_path, dataset_path)
        # backward-compatible alias
        shutil.copy2(candidates_path, FROZEN / "eval_v1.jsonl")

        dataset_sha = sha256_file(dataset_path)
        per_sample_hashes = {r["id"]: r["sha256"] for r in rows}
        frozen_manifest = {
            **manifest,
            "frozen_at": report["audit_timestamp"],
            "audit_verdict": "FREEZE",
            "dataset_sha256": dataset_sha,
            "n_samples": len(rows),
            "category_counts": dict(cat_counts),
            "source_distribution": dict(Counter(r["source"] for r in rows)),
        }
        (FROZEN / "manifest.json").write_text(
            json.dumps(frozen_manifest, indent=2), encoding="utf-8"
        )
        (FROZEN / "hashes.json").write_text(
            json.dumps({
                "dataset.jsonl": dataset_sha,
                "per_sample_sha256": per_sample_hashes,
            }, indent=2),
            encoding="utf-8",
        )
        with (FROZEN / "provenance.jsonl").open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps({
                    "id": r["id"],
                    "category": r["category"],
                    "source": r["source"],
                    "sha256": r["sha256"],
                    "provenance": r.get("provenance", {}),
                }, ensure_ascii=False) + "\n")
        (FROZEN / "dataset_card.md").write_text(
            "# eval_v1 — Frozen Evaluation Dataset\n\n"
            f"**Frozen at:** {report['audit_timestamp']}\n\n"
            f"**Verdict:** FREEZE\n\n"
            f"**Samples:** {len(rows)}\n\n"
            f"**SHA-256 (dataset.jsonl):** `{dataset_sha}`\n\n"
            "## Category counts\n\n"
            + "\n".join(f"- {cat}: {cat_counts.get(cat, 0)}" for cat in CATEGORY_ORDER)
            + "\n\n## Sources\n\n"
            + "\n".join(
                f"- {src}: {cnt}"
                for src, cnt in sorted(Counter(r["source"] for r in rows).items())
            )
            + "\n\n## Integrity\n\n"
            "- benchmark_q1 immutable (verified at build time)\n"
            "- No train/validation leakage\n"
            "- Unique IDs and SHA-256 hashes\n"
            "- Full per-sample provenance in `provenance.jsonl`\n",
            encoding="utf-8",
        )
        (FROZEN / "README.md").write_text(
            "# eval_v1 — Frozen Evaluation Set\n\n"
            f"Frozen at: {report['audit_timestamp']}\n"
            f"Samples: {len(rows)}\n"
            f"SHA-256: {dataset_sha}\n",
            encoding="utf-8",
        )
        blocked_readme = ROOT / "datasets" / "frozen" / "README.md"
        blocked_readme.write_text(
            f"# Frozen Evaluation Datasets\n\n**Status:** `FREEZE`\n\n"
            f"See `{FROZEN.relative_to(ROOT)}/dataset_card.md`\n",
            encoding="utf-8",
        )
    else:
        # ensure frozen README reflects blocked state
        blocked_readme = ROOT / "datasets" / "frozen" / "README.md"
        blocked_readme.write_text(
            f"# Frozen Evaluation Datasets\n\n**Status:** `{verdict}`\n\n"
            f"See `{AUDIT.relative_to(ROOT)}/eval_v1_audit_report.json`\n\n"
            f"Candidates (not frozen): `{PROCESSED.relative_to(ROOT)}/eval_v1_candidates.jsonl`\n",
            encoding="utf-8",
        )

    with (AUDIT / "mutation_audit_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "operation": "AUDIT_EVAL_V1",
            "verdict": verdict,
            "issues": issues,
            "timestamp": report["audit_timestamp"],
            "code_version": "scripts/audit_frozen_eval_v1.py",
        }) + "\n")

    return report


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] == "FREEZE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
