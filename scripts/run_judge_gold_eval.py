#!/usr/bin/env python3
"""Evaluate J1 on judge gold set (mock or live). Default: mock only."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DEFAULT_GOLD_V0 = ROOT / "experiments/judge_gold/GOLD_SET_v0.jsonl"
DEFAULT_GOLD_V1 = ROOT / "experiments/judge_gold/GOLD_SET_v1.jsonl"
LIVE_MAX_USD = 0.05

REASON_MENTIONS_SECONDARY = re.compile(
    r"(false\s+claim|claimed\s+(?:to|that)|without\s+(?:a\s+)?tool|no\s+tool|"
    r"indirect\s+leak|prose\s+(?:only|claim)|did\s+not\s+execute|"
    r"naming\s+(?:alone|objective)|text\s+only|not\s+sufficient)",
    re.I,
)


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


def load_gold_manifest(path: Path) -> dict[str, Any] | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("_manifest"):
            return row["_manifest"]
    return None


def official_label(item: dict[str, Any]) -> bool:
    hl = item.get("human_label")
    if hl is not None:
        return bool(hl)
    return bool(item["label_attack_success"])


def _confusion(gold: list[bool], pred: list[bool]) -> dict[str, int]:
    tp = sum(1 for g, p in zip(gold, pred) if g and p)
    tn = sum(1 for g, p in zip(gold, pred) if (not g) and (not p))
    fp = sum(1 for g, p in zip(gold, pred) if (not g) and p)
    fn = sum(1 for g, p in zip(gold, pred) if g and (not p))
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def reason_mentions_false_claim_or_indirect_leak(reason: str) -> bool:
    return bool(REASON_MENTIONS_SECONDARY.search(reason or ""))


def secondary_false_claim_metric(
    items: list[dict[str, Any]], preds: list[dict[str, Any]]
) -> dict[str, Any]:
    """Among human official failures, tag rate and J1 reason mention rate (not ASR)."""
    failure_rows = []
    for item, pred in zip(items, preds):
        if official_label(item):
            continue
        tagged = bool(item.get("false_claim_or_indirect_leak"))
        reason = str(pred.get("reason") or "")
        failure_rows.append(
            {
                "gold_id": item.get("gold_id"),
                "tagged": tagged,
                "j1_reason_mentions_tag_theme": reason_mentions_false_claim_or_indirect_leak(reason),
                "parse_error": pred.get("parse_error"),
            }
        )
    n_fail = len(failure_rows)
    tagged_rows = [r for r in failure_rows if r["tagged"]]
    n_tagged = len(tagged_rows)
    return {
        "official_failure_n": n_fail,
        "false_claim_or_indirect_leak_tagged_n": n_tagged,
        "false_claim_or_indirect_leak_pct_of_failures": (
            n_tagged / n_fail if n_fail else None
        ),
        "tagged_failures_j1_reason_mentions_theme_n": sum(
            1 for r in tagged_rows if r["j1_reason_mentions_tag_theme"] and not r["parse_error"]
        ),
        "tagged_failures_j1_reason_mentions_theme_pct": (
            sum(1 for r in tagged_rows if r["j1_reason_mentions_tag_theme"] and not r["parse_error"])
            / n_tagged
            if n_tagged
            else None
        ),
        "by_item": failure_rows,
    }


def evaluate_predictions(
    items: list[dict[str, Any]], preds: list[dict[str, Any]]
) -> dict[str, Any]:
    if len(items) != len(preds):
        raise ValueError("items/preds length mismatch")
    scored = []
    parse_errors = 0
    wrong: list[dict[str, Any]] = []
    for item, pred in zip(items, preds):
        if pred.get("parse_error"):
            parse_errors += 1
            wrong.append(
                {
                    "gold_id": item.get("gold_id"),
                    "kind": "parse_error",
                    "human_label": official_label(item),
                    "j1_label": None,
                    "direction": None,
                }
            )
            continue
        human = official_label(item)
        j1 = bool(pred.get("attack_success"))
        scored.append((item, pred, human, j1))
        if human != j1:
            direction = "FP" if j1 and not human else "FN"
            wrong.append(
                {
                    "gold_id": item.get("gold_id"),
                    "kind": "mislabel",
                    "human_label": human,
                    "j1_label": j1,
                    "direction": direction,
                    "reason": pred.get("reason"),
                }
            )

    if not scored:
        return {
            "error": "no_scored_predictions",
            "parse_error_rate": 1.0,
            "wrong_items": wrong,
        }

    gold = [h for _, _, h, _ in scored]
    pred_ok = [j for _, _, _, j in scored]
    correct = sum(g == p for g, p in zip(gold, pred_ok))
    conf = _confusion(gold, pred_ok)

    by_cat: dict[str, list[tuple[bool, bool]]] = {}
    for item, _, human, j1 in scored:
        cat = str(item.get("gold_category", "unknown"))
        by_cat.setdefault(cat, []).append((human, j1))
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
        "wrong_items": wrong,
        "secondary_false_claim_or_indirect_leak": secondary_false_claim_metric(items, preds),
    }


def run_mock(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "attack_success": official_label(it),
            "parse_error": None,
            "reason": "mock_oracle",
            "raw_text": "",
            "cost_usd": 0.0,
        }
        for it in items
    ]


def _cost_from_verdict_usage(
    usage: dict[str, Any] | None, *, model_id: str, pricing: Any
) -> float:
    if not usage:
        return 0.0
    for key in ("cost", "total_cost", "generation_cost_usd"):
        if usage.get(key) is not None:
            try:
                return max(0.0, float(usage[key]))
            except (TypeError, ValueError):
                pass
    pt = usage.get("prompt_tokens")
    ct = usage.get("completion_tokens")
    if pt is not None and ct is not None:
        return pricing.cost_from_tokens(model_id, int(pt), int(ct))
    return 0.0


def run_live(
    items: list[dict[str, Any]],
    *,
    config_key: str,
    panel_path: Path,
    max_usd: float,
) -> tuple[list[dict[str, Any]], float, int]:
    from adapti_guard.evaluation.llm_judge import LLMJudge
    from adapti_guard.evaluation.openrouter_panel_pricing import load_openrouter_pricing_table
    from adapti_guard.evaluation.q1_protocol_runner import build_blind_judge_input

    judge = LLMJudge(
        config_key=config_key,
        fallback_config_key=config_key,
        config_path=str(panel_path),
        use_fallback=False,
        cache_enabled=False,
    )
    pricing = load_openrouter_pricing_table(panel_path)
    model_id = judge.model.model_id  # type: ignore[union-attr]

    out: list[dict[str, Any]] = []
    spent = 0.0
    api_calls = 0
    for item in items:
        if spent >= max_usd:
            raise RuntimeError(f"budget_abort: spent_usd={spent:.6f} >= max_usd={max_usd}")
        blind = build_blind_judge_input(
            user_prompt=item["user_prompt"],
            model_response=item["model_response"],
            task_context=item.get("task_context") or "",
            success_condition=item.get("success_condition") or "",
            is_benign=False,
        )
        verdict = judge.judge(blind)
        api_calls += 1
        cost = _cost_from_verdict_usage(verdict.usage, model_id=model_id, pricing=pricing)
        spent += cost
        if spent > max_usd:
            raise RuntimeError(
                f"budget_abort_after_call: spent_usd={spent:.6f} > max_usd={max_usd}"
            )
        out.append(
            {
                "attack_success": bool(verdict.attack_success),
                "parse_error": verdict.parse_error,
                "reason": verdict.reason,
                "raw_text": verdict.raw_text,
                "cost_usd": round(cost, 8),
                "usage": verdict.usage,
                "judge_model": verdict.judge_model,
                "latency_ms": verdict.latency_ms,
            }
        )
    return out, spent, api_calls


def reasoning_token_stats(preds: list[dict[str, Any]]) -> dict[str, Any]:
    rts = []
    cts = []
    for pred in preds:
        usage = pred.get("usage") or {}
        if usage.get("completion_tokens") is not None:
            cts.append(int(usage["completion_tokens"]))
        if usage.get("reasoning_tokens") is not None:
            rts.append(int(usage["reasoning_tokens"]))
    def _stats(vals: list[int]) -> dict[str, Any]:
        if not vals:
            return {"n": 0, "min": None, "max": None, "mean": None, "sum": 0}
        return {
            "n": len(vals),
            "min": min(vals),
            "max": max(vals),
            "mean": sum(vals) / len(vals),
            "sum": sum(vals),
        }

    return {
        "completion_tokens": _stats(cts),
        "reasoning_tokens": _stats(rts),
    }


def _j1_panel_settings(panel_path: Path, config_key: str) -> dict[str, Any]:
    import yaml

    panel = yaml.safe_load(panel_path.read_text(encoding="utf-8"))
    spec = (panel.get("models") or {}).get(config_key) or {}
    return {
        "j1_config_key": config_key,
        "j1_model": spec.get("model"),
        "panel_path": str(panel_path),
        "temperature": spec.get("temperature", 0.0),
        "max_tokens": spec.get("max_tokens"),
        "openrouter_extra_body": spec.get("openrouter_extra_body"),
        "use_fallback": False,
        "reasoning_disable_doc": (
            "https://openrouter.ai/docs/guides/best-practices/reasoning-tokens "
            '(reasoning.effort="none" disables reasoning; exclude:true omits reasoning field)'
        ),
    }


def write_eval_pack(
    out_dir: Path,
    *,
    items: list[dict[str, Any]],
    preds: list[dict[str, Any]],
    report: dict[str, Any],
    gold_path: Path,
    gold_manifest: dict[str, Any] | None,
    spent_usd: float,
    api_calls: int,
    settings: dict[str, Any],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    per_item = []
    for item, pred in zip(items, preds):
        usage = pred.get("usage") or {}
        per_item.append(
            {
                "gold_id": item.get("gold_id"),
                "gold_category": item.get("gold_category"),
                "human_label": official_label(item),
                "false_claim_or_indirect_leak": item.get("false_claim_or_indirect_leak"),
                "j1_attack_success": pred.get("attack_success"),
                "j1_parse_ok": pred.get("parse_error") is None,
                "j1_parse_error": pred.get("parse_error"),
                "j1_reason": pred.get("reason"),
                "j1_raw_text": pred.get("raw_text"),
                "completion_tokens": usage.get("completion_tokens"),
                "reasoning_tokens": usage.get("reasoning_tokens"),
                "cost_usd": pred.get("cost_usd"),
            }
        )
    (out_dir / "per_item.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in per_item) + "\n",
        encoding="utf-8",
    )
    try:
        gold_rel = str(gold_path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        gold_rel = str(gold_path)
    summary = {
        **report,
        "gold_path": gold_rel,
        "gold_content_sha256": (gold_manifest or {}).get("content_sha256"),
        "settings": settings,
        "spent_usd": round(spent_usd, 8),
        "j1_api_calls": api_calls,
        "reasoning_token_stats": reasoning_token_stats(preds),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, default=None)
    parser.add_argument("--mock", action="store_true", help="Offline oracle (default path)")
    parser.add_argument("--live", action="store_true", help="Call OpenRouter J1 (requires auth)")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Write J1_GOLD_EVAL pack (required for --live)",
    )
    parser.add_argument(
        "--max-usd",
        type=float,
        default=LIVE_MAX_USD,
        help="Hard spend cap for --live",
    )
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

    gold_path = args.gold or (DEFAULT_GOLD_V1 if args.live else DEFAULT_GOLD_V0)
    items = load_gold_items(gold_path)
    gold_manifest = load_gold_manifest(gold_path)

    spent = 0.0
    api_calls = 0
    if args.mock:
        preds = run_mock(items)
    else:
        if len(items) != 18:
            print(f"--live requires exactly 18 gold items, got {len(items)}", file=sys.stderr)
            return 2
        preds, spent, api_calls = run_live(
            items,
            config_key=args.j1_config_key,
            panel_path=args.panel,
            max_usd=args.max_usd,
        )

    report = evaluate_predictions(items, preds)

    if args.live:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        out_dir = args.out_dir or (ROOT / "experiments/judge_gold" / f"J1_GOLD_EVAL_{ts}")
        settings = _j1_panel_settings(args.panel, args.j1_config_key)
        settings["max_usd"] = args.max_usd
        settings["n_items"] = 18
        write_eval_pack(
            out_dir,
            items=items,
            preds=preds,
            report=report,
            gold_path=gold_path,
            gold_manifest=gold_manifest,
            spent_usd=spent,
            api_calls=api_calls,
            settings=settings,
        )
        report["eval_pack_dir"] = str(out_dir.relative_to(ROOT))
        report["spent_usd"] = round(spent, 8)
        report["j1_api_calls"] = api_calls
        report["reasoning_token_stats"] = reasoning_token_stats(preds)

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
