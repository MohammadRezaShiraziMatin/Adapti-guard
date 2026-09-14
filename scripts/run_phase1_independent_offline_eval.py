#!/usr/bin/env python3
"""Phase-1 independent offline detector + enforcement eval (no LLM/API).

Evaluates locked ``evidence_phase1.0`` on:
  - DEV: Layer A train
  - VAL: Layer A dev
  - TEST: phase1_holdout_v1 (independent)

Does not retune. Does not modify frozen packs. Prints diagnostics + holdout metrics.
``56/61`` on VNEXT is not computed here and remains diagnostic-only elsewhere.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.core.core_pipeline import CoreDefensePipeline
from src.adapti_guard.core.episode import EpisodeInput
from src.adapti_guard.defense.tool_loop import MockToolRegistry
from src.adapti_guard.detector.prompt_injection_detector_phase1 import (
    PromptInjectionDetectorPhase1,
)

LOCK = json.loads((ROOT / "configs/phase1_detector_lock.json").read_text())
HOLDOUT = ROOT / "datasets/frozen/phase1_holdout_v1/dataset.jsonl"
HOLDOUT_SHA = LOCK["independent_test"]["sha256"]
DEV = ROOT / "datasets/frozen/layer_a_v3/train.jsonl"
VAL = ROOT / "datasets/frozen/layer_a_v3/dev.jsonl"
LAYER_A_TEST = ROOT / "datasets/frozen/layer_a_v3/test_split.jsonl"
LAYER_A_TEST_SHA = "47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8"
VNEXT = ROOT / "datasets/frozen/vnext_confirm_v1/dataset.jsonl"
VNEXT_SHA = "523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - margin) / den, (centre + margin) / den)


def _load(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _is_attack(row: dict) -> bool:
    return str(row.get("label") or "").lower() in {"attack", "1", "true"}


def _family(row: dict) -> str:
    md = row.get("metadata") or {}
    return str(md.get("attack_family") or row.get("category") or "UNKNOWN")


def _tool(row: dict):
    blob = row.get("tool_call") or (row.get("metadata") or {}).get("tool_call")
    if isinstance(blob, dict) and blob.get("name"):
        return str(blob["name"]), dict(blob.get("arguments") or {})
    return None, {}


def evaluate_split(name: str, path: Path, expected_sha: str | None = None) -> dict:
    digest = _sha(path)
    if expected_sha and digest != expected_sha:
        raise SystemExit(f"FAIL hash {name}: {digest} != {expected_sha}")
    det = PromptInjectionDetectorPhase1()
    pipe = CoreDefensePipeline()
    assert det.version == LOCK["detector"]["version"]

    tp = fp = tn = fn = 0
    by_fam = defaultdict(lambda: Counter())
    actions = Counter()
    tool_denied = tool_ran = 0
    benign_a2a3 = 0
    hard_neg_fp = 0
    blind = Counter()

    for row in _load(path):
        gold_attack = _is_attack(row)
        fam = _family(row)
        prompt = str(row.get("prompt") or "")
        context = str(row.get("context") or "")
        tname, targs = _tool(row)
        det_hit = det.detect_episode(prompt, context).injection_probability > 0
        if gold_attack and det_hit:
            tp += 1
            by_fam[fam]["tp"] += 1
        elif gold_attack and not det_hit:
            fn += 1
            by_fam[fam]["fn"] += 1
            low = (prompt + " " + context).lower()
            if any(x in low for x in ("l33t", "1337")):
                blind["l33t"] += 1
            if "morse" in low:
                blind["morse"] += 1
            if "reverse" in low:
                blind["reverse"] += 1
            if any(ord(c) > 127 for c in prompt + context):
                blind["unicode_or_encoding"] += 1
            if fam in {"SOCIAL_ENGINEERING"}:
                blind["subtle_social_engineering"] += 1
            if fam in {"INDIRECT_RAG", "TOOL_OUTPUT_INJECTION"}:
                blind["indirect_wording"] += 1
        elif not gold_attack and det_hit:
            fp += 1
            by_fam[fam]["fp"] += 1
            if (row.get("metadata") or {}).get("hard_negative"):
                hard_neg_fp += 1
        else:
            tn += 1
            by_fam[fam]["tn"] += 1

        inp = EpisodeInput(
            prompt=prompt, context=context, tool_name=tname, tool_arguments=targs
        )
        trace = pipe.run(inp, registry=MockToolRegistry())
        actions[trace.policy_action] += 1
        if trace.tool_requested and not trace.tool_executed:
            tool_denied += 1
        if trace.tool_executed:
            tool_ran += 1
        if not gold_attack and trace.policy_action in {"A2", "A3"}:
            benign_a2a3 += 1

    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    rec = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = (
        2 * prec * rec / (prec + rec)
        if prec == prec and rec == rec and (prec + rec) > 0
        else float("nan")
    )
    fpr = fp / (fp + tn) if (fp + tn) else float("nan")
    n_pos, n_neg = tp + fn, fp + tn
    return {
        "split": name,
        "path": str(path),
        "sha256": digest,
        "n": n_pos + n_neg,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "fpr": fpr,
        "recall_ci": _wilson(tp, n_pos),
        "fpr_ci": _wilson(fp, n_neg),
        "per_family": {k: dict(v) for k, v in sorted(by_fam.items())},
        "actions": dict(actions),
        "tool_denied": tool_denied,
        "tool_ran": tool_ran,
        "benign_false_a2_a3": benign_a2a3,
        "hard_negative_detector_fp": hard_neg_fp,
        "blind_spot_fn_tags": dict(blind),
        "claim": "offline_detector_metrics_not_asr",
    }


def main() -> int:
    # Integrity of historical packs (read-only check)
    assert _sha(VNEXT) == VNEXT_SHA
    assert _sha(LAYER_A_TEST) == LAYER_A_TEST_SHA
    src = ROOT / LOCK["detector"]["source"]
    assert _sha(src) == LOCK["detector"]["sha256"], "detector lock broken"

    results = [
        evaluate_split("DEV_layer_a_train", DEV),
        evaluate_split("VAL_layer_a_dev", VAL),
        evaluate_split("TEST_phase1_holdout", HOLDOUT, HOLDOUT_SHA),
        evaluate_split("SECONDARY_layer_a_test_text", LAYER_A_TEST, LAYER_A_TEST_SHA),
    ]
    out = {
        "lock_id": LOCK["lock_id"],
        "detector_version": LOCK["detector"]["version"],
        "llm_api_calls": 0,
        "vnext_diagnostic_note": "56/61 on VNEXT is diagnostic-only; not recomputed as performance",
        "splits": results,
    }
    out_path = ROOT / "docs/experiments/artifacts/phase1_independent_offline_metrics.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    print(f"WROTE {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
