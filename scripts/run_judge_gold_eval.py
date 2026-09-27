#!/usr/bin/env python3
"""Evaluate J1 on judge gold set (mock or live). Default: mock only."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DEFAULT_GOLD = ROOT / "experiments/judge_gold/GOLD_SET_v0.jsonl"


def load_gold_items(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("_manifest"):
            continue
        rows.append(row)
    return rows


def _confusion(
    gold: list[bool], pred: list[bool]
) -> dict[str, int]:
    tp = sum(1 for g, p in zip(gold, pred) if g and p)
    tn = sum(1 for g, p in zip(gold, pred) if (not g) and (not p))
    fp = sum(1 for g, p in zip(gold, pred) if (not g) and p)
    fn = sum(1 for g, p in zip(gold, pred) if g and (not p))
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def evaluate_predictions(items: list[dict[str, Any]], preds: list[dict[str, Any]]) -> dict[str, Any]:
    if len(items) != len(preds):
        raise ValueError("items/preds length mismatch")
    scored = []
    parse_errors = 0
    for item, pred in zip(items, preds):
        if pred.get("parse_error"):
            parse_errors += 1
            continue
        scored.append((item, pred))
    if not scored:
        return {"error": "no_scored_predictions", "parse_error_rate": 1.0}

    gold = [bool(it["label_attack_success"]) for it, _ in scored]
    pred_ok = [bool(pr.get("attack_success")) for _, pr in scored]
    correct = sum(g == p for g, p in zip(gold, pred_ok))
    conf = _confusion(gold, pred_ok)

    by_cat: dict[str, list[tuple[bool, bool]]] = {}
    for item, pred in scored:
        cat = str(item.get("gold_category", "unknown"))
        by_cat.setdefault(cat, []).append(
            (bool(item["label_attack_success"]), bool(pred.get("attack_success")))
        )
    per_category = {}
    for cat, pairs in by_cat.items():
        per_category[cat] = {
            "n": len(pairs),
            "accuracy": sum(g == p for g, p in pairs) / len(pairs),
        }

    return {
        "n_items": len(items),
        "n_scored": len(scored),
        "parse_error_rate": parse_errors / len(items),
        "parse_errors": parse_errors,
        "accuracy": correct / len(scored),
        "per_category_accuracy": per_category,
        "confusion_matrix": conf,
        "false_positive_bias": conf["fp"] > conf["fn"],
        "false_negative_bias": conf["fn"] > conf["fp"],
        "fp_minus_fn": conf["fp"] - conf["fn"],
    }


def run_mock(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Perfect oracle on labels (validates metric plumbing)."""
    return [
        {"attack_success": bool(it["label_attack_success"]), "parse_error": None, "reason": "mock_oracle"}
        for it in items
    ]


def run_live(items: list[dict[str, Any]], *, config_key: str, panel_path: Path) -> list[dict[str, Any]]:
    from adapti_guard.evaluation.llm_judge import LLMJudge
    from adapti_guard.evaluation.q1_protocol_runner import build_blind_judge_input

    judge = LLMJudge(
        config_key=config_key,
        fallback_config_key=config_key,
        config_path=str(panel_path),
        use_fallback=False,
        cache_enabled=False,
    )
    out = []
    for item in items:
        blind = build_blind_judge_input(
            user_prompt=item["user_prompt"],
            model_response=item["model_response"],
            task_context=item.get("task_context") or "",
            success_condition=item.get("success_condition") or "",
            is_benign=False,
        )
        verdict = judge.judge(blind)
        out.append(
            {
                "attack_success": bool(verdict.attack_success),
                "parse_error": verdict.parse_error,
                "reason": verdict.reason,
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--mock", action="store_true", help="Offline oracle (default path)")
    parser.add_argument("--live", action="store_true", help="Call OpenRouter J1 (requires auth)")
    parser.add_argument(
        "--j1-config-key",
        default="q1_judge_glm_4_7",
        help="Panel config key for J1",
    )
    parser.add_argument(
        "--panel",
        type=Path,
        default=ROOT / "configs/models_q1_eval_panel.yaml",
    )
    args = parser.parse_args()

    if args.live and args.mock:
        print("Choose only one of --mock or --live", file=sys.stderr)
        return 2
    if not args.live:
        args.mock = True

    items = load_gold_items(args.gold)
    if args.mock:
        preds = run_mock(items)
    else:
        preds = run_live(items, config_key=args.j1_config_key, panel_path=args.panel)

    report = evaluate_predictions(items, preds)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
