#!/usr/bin/env python3
"""Run detector-only evaluation on Layer A packs (no target/judge API calls)."""

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

from src.adapti_guard.evaluation.detector_eval import (
    evaluate_detector_pack,
    load_jsonl,
    write_detector_eval_artifacts,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip()
        )
    except Exception:
        return "unknown"


def _pick_dev_threshold(dev_result: dict) -> dict:
    """Select threshold on DEV only: maximize F1, break ties by higher recall."""
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pack-dir",
        default="datasets/frozen/layer_a_v3",
        help="Frozen pack directory",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Output directory (default: experiments/.../LAYER_A_V3_DETECTOR/<stamp>)",
    )
    parser.add_argument(
        "--default-threshold",
        type=float,
        default=0.25,
        help="Project-default decision threshold (not tuned on test)",
    )
    args = parser.parse_args()

    pack = ROOT / args.pack_dir
    train = pack / "train.jsonl"
    dev = pack / "dev.jsonl"
    test = pack / "test_split.jsonl"
    for path in (train, dev, test):
        if not path.is_file():
            raise SystemExit(f"missing {path}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = Path(args.output) if args.output else (
        ROOT
        / "experiments"
        / "real_llm_eval"
        / "LAYER_A_V3_DETECTOR"
        / stamp
    )
    if not out.is_absolute():
        out = ROOT / out
    out.mkdir(parents=True, exist_ok=True)

    splits = {
        "train": load_jsonl(train),
        "dev": load_jsonl(dev),
        "test": load_jsonl(test),
    }
    results = {}
    for name, rows in splits.items():
        result = evaluate_detector_pack(rows, threshold=args.default_threshold)
        split_dir = out / name
        write_detector_eval_artifacts(result, split_dir)
        # drop bulky scores from summary pointer
        slim = {k: v for k, v in result.items() if k != "scores"}
        results[name] = slim

    selection = _pick_dev_threshold(results["dev"])
    test_at_dev = evaluate_detector_pack(
        splits["test"], threshold=float(selection["threshold"])
    )
    write_detector_eval_artifacts(test_at_dev, out / "test_at_dev_selected_threshold")
    results["test_at_dev_selected_threshold"] = {
        k: v for k, v in test_at_dev.items() if k != "scores"
    }

    summary = {
        "status": "VALID",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "pack_dir": str(pack.relative_to(ROOT)),
        "pack_hashes": {
            "train.jsonl": _sha(train),
            "dev.jsonl": _sha(dev),
            "test_split.jsonl": _sha(test),
            "dataset.jsonl": _sha(pack / "dataset.jsonl"),
        },
        "default_threshold": args.default_threshold,
        "dev_threshold_selection": selection,
        "note": (
            "Default threshold 0.25 is the historical project operating point. "
            "DEV-selected threshold is reported separately and applied once to TEST; "
            "TEST was not used for selection."
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
            for name in ("train", "dev", "test", "test_at_dev_selected_threshold")
        },
        "test_slices_default_threshold": {
            "by_attack_family": results["test"]["by_attack_family"],
            "by_difficulty": results["test"]["by_difficulty"],
        },
        "manuscript_results_edited": False,
        "historical_v2_artifacts_edited": False,
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Layer A v3 detector-only evaluation",
        "",
        f"**Status:** VALID  ",
        f"**Pack:** `{pack}`  ",
        f"**test_split SHA-256:** `{summary['pack_hashes']['test_split.jsonl']}`  ",
        f"**Git commit:** `{summary['git_commit']}`",
        "",
        "## Headline (TEST, threshold=0.25 project default)",
        "",
        (
            "Attack recall={recall:.3f} ({tp}/{n_attack}), "
            "benign FPR={fpr:.3f}, F1={f1}, AUROC={auroc}, hard-negative FPR={hn}."
        ).format(
            recall=results["test"]["overall"]["recall"] or 0.0,
            tp=results["test"]["overall"]["tp"],
            n_attack=results["test"]["n_attack"],
            fpr=results["test"]["overall"]["fpr"] or 0.0,
            f1=results["test"]["overall"]["f1"],
            auroc=results["test"]["auroc"],
            hn=results["test"]["hard_negatives"]["fpr"],
        ),
        "",
        "This is a **detector** result, not an intervention ASR result.",
        "",
        "## Threshold discipline",
        "",
        f"- Project default threshold: `{args.default_threshold}` (not tuned on TEST).",
        (
            "- DEV-selected threshold (max F1 then recall): "
            f"`{selection['threshold']}` "
            f"(dev F1={selection['dev_f1']}, recall={selection['dev_recall']}, "
            f"FPR={selection['dev_fpr']})."
        ),
        "- TEST metrics at the DEV-selected threshold are reported in "
        "`test_at_dev_selected_threshold/` and were not used for selection.",
        "",
        "## Split summary (default threshold)",
        "",
        "| Split | n | Attack recall | Benign FPR | F1 | AUROC | HN FPR |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ("train", "dev", "test"):
        o = results[name]["overall"]
        lines.append(
            "| {name} | {n} | {rec} | {fpr} | {f1} | {auroc} | {hn} |".format(
                name=name,
                n=results[name]["n"],
                rec=o["recall"],
                fpr=o["fpr"],
                f1=o["f1"],
                auroc=results[name]["auroc"],
                hn=results[name]["hard_negatives"]["fpr"],
            )
        )
    o = results["test_at_dev_selected_threshold"]["overall"]
    lines.append(
        "| test@dev_thr | {n} | {rec} | {fpr} | {f1} | {auroc} | {hn} |".format(
            n=results["test_at_dev_selected_threshold"]["n"],
            rec=o["recall"],
            fpr=o["fpr"],
            f1=o["f1"],
            auroc=results["test_at_dev_selected_threshold"]["auroc"],
            hn=results["test_at_dev_selected_threshold"]["hard_negatives"]["fpr"],
        )
    )
    lines.extend(
        [
            "",
            "## TEST attack-family recall (threshold=0.25)",
            "",
            "| Family | n | Recall |",
            "| --- | ---: | ---: |",
        ]
    )
    for fam, m in results["test"]["by_attack_family"].items():
        lines.append(f"| {fam} | {m['n']} | {m['recall']} |")
    lines.extend(
        [
            "",
            "## TEST difficulty recall (threshold=0.25)",
            "",
            "| Difficulty | n | Recall |",
            "| --- | ---: | ---: |",
            "",
        ]
    )
    # fix: add difficulty rows before blank
    diff_lines = []
    for diff, m in results["test"]["by_difficulty"].items():
        diff_lines.append(f"| {diff} | {m['n']} | {m['recall']} |")
    # rebuild tail cleanly
    text = "\n".join(lines)
    text = text.replace(
        "| Difficulty | n | Recall |\n| --- | ---: | ---: |\n\n",
        "| Difficulty | n | Recall |\n| --- | ---: | ---: |\n"
        + "\n".join(diff_lines)
        + "\n\n",
    )
    text += (
        "## Scientific reading\n\n"
        "Under the current regex detector, Layer A v3 TEST attack recall is near floor "
        "while hard-negative FPR is high. Adaptive escalation that depends on this "
        "detector cannot be expected to outperform weak sanitization on missed attacks.\n\n"
        "Manuscript Results were not modified.\n"
    )
    (out / "AUDIT.md").write_text(text, encoding="utf-8")
    print(json.dumps({"out_dir": str(out), "test_recall": results["test"]["overall"]["recall"], "test_fpr": results["test"]["overall"]["fpr"], "dev_selected_threshold": selection["threshold"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
