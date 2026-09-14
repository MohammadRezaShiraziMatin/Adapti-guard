#!/usr/bin/env python3
"""Detector-only v4 evaluation. Thresholds chosen on DEV. TEST is optional and one-shot."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.adapti_guard.detector.prompt_injection_detector_v4 import (
    PromptInjectionDetectorV4,
)
from src.adapti_guard.evaluation.detector_eval import (
    evaluate_detector_pack,
    load_jsonl,
    write_detector_eval_artifacts,
)
from src.adapti_guard.risk.risk_engine_v4 import RiskEngineV4

TEST_SPLIT_SHA = "47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def _pick_dev_threshold(dev_result: dict) -> dict:
    best = None
    for row in dev_result["threshold_sweep"]:
        f1 = row.get("f1")
        if f1 is None:
            continue
        cand = (f1, row.get("recall") or 0.0, -row["threshold"], row)
        if best is None or cand[:3] > best[:3]:
            best = cand
    assert best is not None
    row = best[3]
    return {
        "rule": "max_f1_then_recall_on_dev",
        "threshold": row["threshold"],
        "dev_f1": row["f1"],
        "dev_recall": row["recall"],
        "dev_fpr": row["fpr"],
        "dev_precision": row["precision"],
    }


def _slim(result: dict) -> dict:
    return {k: v for k, v in result.items() if k != "scores"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-dir", default="datasets/frozen/layer_a_v3")
    parser.add_argument("--output", default="")
    parser.add_argument("--default-threshold", type=float, default=0.25)
    parser.add_argument(
        "--include-test",
        action="store_true",
        help="Run frozen TEST once. Do not pass until DEV gate is inspected.",
    )
    args = parser.parse_args()

    pack = ROOT / args.pack_dir
    train_p, dev_p, test_p = pack / "train.jsonl", pack / "dev.jsonl", pack / "test_split.jsonl"
    for path in (train_p, dev_p):
        if not path.is_file():
            raise SystemExit(f"missing {path}")
    if args.include_test:
        got = _sha(test_p)
        if got != TEST_SPLIT_SHA:
            raise SystemExit(f"TEST hash mismatch: {got}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = Path(args.output) if args.output else (
        ROOT / "experiments" / "real_llm_eval" / "LAYER_A_V4_DETECTOR" / stamp
    )
    if not out.is_absolute():
        out = ROOT / out
    out.mkdir(parents=True, exist_ok=True)

    detector = PromptInjectionDetectorV4()
    risk = RiskEngineV4()
    splits = {"train": load_jsonl(train_p), "dev": load_jsonl(dev_p)}
    if args.include_test:
        splits["test"] = load_jsonl(test_p)

    results = {}
    for name, rows in splits.items():
        result = evaluate_detector_pack(
            rows,
            threshold=args.default_threshold,
            detector=detector,
            risk_engine=risk,
        )
        write_detector_eval_artifacts(result, out / name)
        results[name] = _slim(result)

    selection = _pick_dev_threshold(results["dev"])
    if args.include_test:
        test_at_dev = evaluate_detector_pack(
            splits["test"],
            threshold=float(selection["threshold"]),
            detector=detector,
            risk_engine=risk,
        )
        write_detector_eval_artifacts(test_at_dev, out / "test_at_dev_selected_threshold")
        results["test_at_dev_selected_threshold"] = _slim(test_at_dev)

    summary = {
        "status": "VALID",
        "detector_version": detector.version,
        "risk_version": risk.version,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "include_test": bool(args.include_test),
        "pack_dir": str(pack.relative_to(ROOT)),
        "pack_hashes": {
            "train.jsonl": _sha(train_p),
            "dev.jsonl": _sha(dev_p),
            "test_split.jsonl": _sha(test_p) if test_p.is_file() else None,
            "dataset.jsonl": _sha(pack / "dataset.jsonl"),
        },
        "default_threshold": args.default_threshold,
        "dev_threshold_selection": selection,
        "note": (
            "Thresholds are selected on DEV only. TEST is evaluated at most once "
            "when --include-test is set. TEST text is not used for rule design."
        ),
        "splits": {
            name: {
                "n": results[name]["n"],
                "n_attack": results[name]["n_attack"],
                "n_benign": results[name]["n_benign"],
                "overall": results[name]["overall"],
                "auroc": results[name]["auroc"],
                "auprc": results[name]["auprc"],
                "hard_negatives": results[name]["hard_negatives"],
                "risk_level_counts": results[name]["risk_level_counts"],
                "calibration_ece": (results[name]["calibration"] or {}).get("ece"),
            }
            for name in results
        },
        "manuscript_results_edited": False,
        "historical_v2_artifacts_edited": False,
        "historical_v3_artifacts_edited": False,
    }
    if "test" in results:
        summary["test_slices_default_threshold"] = {
            "by_attack_family": results["test"]["by_attack_family"],
            "by_difficulty": results["test"]["by_difficulty"],
        }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    def _row(name: str) -> str:
        o = results[name]["overall"]
        return (
            f"| {name} | {results[name]['n']} | {o['recall']} | {o['fpr']} | "
            f"{o['f1']} | {results[name]['auroc']} | {results[name]['hard_negatives']['fpr']} |"
        )

    lines = [
        "# Layer A v4 detector-only evaluation",
        "",
        f"**Status:** VALID  ",
        f"**Detector:** `{detector.version}`  ",
        f"**Risk:** `{risk.version}`  ",
        f"**include_test:** `{args.include_test}`  ",
        f"**Git commit:** `{summary['git_commit']}`",
        "",
        "## Threshold discipline",
        "",
        f"- Default threshold `{args.default_threshold}` is the project operating point.",
        (
            f"- DEV-selected threshold `{selection['threshold']}` "
            f"(F1={selection['dev_f1']}, recall={selection['dev_recall']}, "
            f"FPR={selection['dev_fpr']})."
        ),
        "- TEST was not used for selection.",
        "",
        "| Split | n | Attack recall | Benign FPR | F1 | AUROC | HN FPR |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in results:
        if name.startswith("test_at_dev"):
            continue
        lines.append(_row(name))
    if "test_at_dev_selected_threshold" in results:
        lines.append(_row("test_at_dev_selected_threshold").replace(
            "test_at_dev_selected_threshold", "test@dev_thr"
        ))
    lines.extend(
        [
            "",
            "Manuscript Results were not modified. Historical v2/v3 artifacts were not overwritten.",
            "",
        ]
    )
    (out / "AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "out_dir": str(out),
                "include_test": args.include_test,
                "dev_recall": results["dev"]["overall"]["recall"],
                "dev_fpr": results["dev"]["overall"]["fpr"],
                "dev_auroc": results["dev"]["auroc"],
                "dev_hn_fpr": results["dev"]["hard_negatives"]["fpr"],
                "dev_selected_threshold": selection["threshold"],
                "test_recall": (results.get("test") or {}).get("overall", {}).get("recall"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
