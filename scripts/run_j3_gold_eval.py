#!/usr/bin/env python3
"""Prepare or run J3 (Claude Haiku 4.5) on GOLD_SET_v2 — default: no live calls.

Computes accuracy, prereg pass checks, Fleiss κ (when J1+J2+J3 labels exist),
and error-type subsets. See experiments/judge_gold/J3_EVAL_CRITERIA_LOCKED.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from adapti_guard.evaluation.anthropic_j3_judge import (  # noqa: E402
    AnthropicJ3Judge,
    J3_MODEL_ID,
)
from adapti_guard.evaluation.llm_judge import JUDGE_SYSTEM_PROMPT  # noqa: E402
from adapti_guard.evaluation.q1_protocol_runner import build_blind_judge_input  # noqa: E402
from run_judge_gold_eval import (  # noqa: E402
    evaluate_predictions,
    load_gold_items,
    load_gold_manifest,
    official_label,
)
from run_judge_gold_v2_ablation import (  # noqa: E402
    APOLOGY_IDS,
    PROSE_IDS,
    prereg_pass,
)

GOLD = ROOT / "experiments/judge_gold/GOLD_SET_v2.jsonl"
CRITERIA = ROOT / "experiments/judge_gold/J3_EVAL_CRITERIA_LOCKED.md"
DEFAULT_J1_PACK = ROOT / "experiments/judge_gold/J1_V2_ABLATION_20260927-070101/per_item.jsonl"

# Anthropic list pricing (USD per token) — update when Anthropic revises; used for estimates only.
HAIKU_45_INPUT_USD_PER_TOKEN = 1.0e-6
HAIKU_45_OUTPUT_USD_PER_TOKEN = 5.0e-6
GROK_J2_INPUT_USD_PER_TOKEN = 1.6e-6
GROK_J2_OUTPUT_USD_PER_TOKEN = 4.8e-6
EST_PROMPT_TOKENS_PER_ITEM = 900
EST_COMPLETION_TOKENS_PER_ITEM = 120


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fleiss_kappa_binary(triplets: list[tuple[bool, bool, bool]]) -> float | None:
    """Fleiss' κ for 3 raters × 2 categories (attack_success false/true)."""
    n_subjects = len(triplets)
    if n_subjects == 0:
        return None
    n_raters = 3
    n_categories = 2
    # rows: [n_false, n_true]
    matrix: list[list[int]] = []
    for a, b, c in triplets:
        s = int(a) + int(b) + int(c)
        matrix.append([n_raters - s, s])

    p_i_sum = 0.0
    for row in matrix:
        inner = sum(n_ij * (n_ij - 1) for n_ij in row)
        p_i_sum += inner / (n_raters * (n_raters - 1))
    p_bar = p_i_sum / n_subjects

    col_totals = [0, 0]
    for row in matrix:
        for j in range(n_categories):
            col_totals[j] += row[j]
    total_assignments = n_subjects * n_raters
    p_j = [col_totals[j] / total_assignments for j in range(n_categories)]
    p_e = sum(x * x for x in p_j)
    if math.isclose(1.0 - p_e, 0.0):
        return None
    return (p_bar - p_e) / (1.0 - p_e)


def load_j1_p0_labels(path: Path, *, strict_parse: bool = False) -> tuple[dict[str, bool], list[str]]:
    out: dict[str, bool] = {}
    parse_errors: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("variant") not in (None, "P0"):
            continue
        gid = row.get("gold_id")
        if not gid:
            continue
        if row.get("j1_parse_ok") is False or row.get("parse_error"):
            parse_errors.append(str(gid))
            if strict_parse:
                raise ValueError(f"J1 parse error on {gid} in {path}")
        out[str(gid)] = bool(row["j1_attack_success"])
    if len(out) != 40:
        raise ValueError(f"expected 40 J1 P0 labels in {path}, got {len(out)}")
    return out, parse_errors


def load_j2_labels(path: Path | None) -> dict[str, bool] | None:
    if path is None or not path.is_file():
        return None
    out: dict[str, bool] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        gid = row.get("gold_id")
        if not gid:
            continue
        key = "j2_attack_success" if "j2_attack_success" in row else "attack_success"
        if row.get("j2_parse_ok") is False or row.get("parse_error"):
            raise ValueError(f"J2 parse error on {gid}")
        out[str(gid)] = bool(row[key])
    return out if out else None


def subset_errors(
    items: list[dict[str, Any]], preds: list[dict[str, Any]], ids: set[str]
) -> dict[str, Any]:
    wrong: list[dict[str, Any]] = []
    for item, pred in zip(items, preds):
        if item["gold_id"] not in ids:
            continue
        human = official_label(item)
        if pred.get("parse_error"):
            wrong.append({"gold_id": item["gold_id"], "kind": "parse_error"})
        elif bool(pred.get("attack_success")) != human:
            wrong.append(
                {
                    "gold_id": item["gold_id"],
                    "kind": "mislabel",
                    "human_label": human,
                    "j3_label": bool(pred.get("attack_success")),
                }
            )
    return {"n": len(ids), "errors": len(wrong), "wrong_items": wrong}


def estimate_j3_cost_usd(n_items: int = 40) -> dict[str, Any]:
    prompt = n_items * EST_PROMPT_TOKENS_PER_ITEM
    completion = n_items * EST_COMPLETION_TOKENS_PER_ITEM
    usd = prompt * HAIKU_45_INPUT_USD_PER_TOKEN + completion * HAIKU_45_OUTPUT_USD_PER_TOKEN
    return {
        "n_items": n_items,
        "assumed_prompt_tokens_per_item": EST_PROMPT_TOKENS_PER_ITEM,
        "assumed_completion_tokens_per_item": EST_COMPLETION_TOKENS_PER_ITEM,
        "estimated_total_usd": round(usd, 4),
        "pricing_note": "Haiku 4.5 list-rate placeholders in script; replace with pinned Anthropic tariff before billing.",
    }


def estimate_j2_cost_usd(n_items: int = 40) -> dict[str, Any]:
    prompt = n_items * EST_PROMPT_TOKENS_PER_ITEM
    completion = n_items * EST_COMPLETION_TOKENS_PER_ITEM
    usd = prompt * GROK_J2_INPUT_USD_PER_TOKEN + completion * GROK_J2_OUTPUT_USD_PER_TOKEN
    return {
        "n_items": n_items,
        "openrouter_model": "x-ai/grok-4.7",
        "panel_pricing": {
            "prompt_usd_per_token": GROK_J2_INPUT_USD_PER_TOKEN,
            "completion_usd_per_token": GROK_J2_OUTPUT_USD_PER_TOKEN,
        },
        "assumed_prompt_tokens_per_item": EST_PROMPT_TOKENS_PER_ITEM,
        "assumed_completion_tokens_per_item": EST_COMPLETION_TOKENS_PER_ITEM,
        "estimated_total_usd": round(usd, 4),
    }


def collect_facts(
    *,
    gold_path: Path,
    j1_pack: Path,
    j2_pack: Path | None,
) -> dict[str, Any]:
    gold_v3_path = ROOT / "experiments/judge_gold/GOLD_SET_v3.jsonl"
    manifest = load_gold_manifest(gold_path)
    j1_labels, parse_err_ids = load_j1_p0_labels(j1_pack)
    j2_labels = load_j2_labels(j2_pack)
    items = load_gold_items(gold_path)
    gold_ids = {it["gold_id"] for it in items}
    j1_missing = sorted(gold_ids - set(j1_labels))
    return {
        "gold_v3_exists": gold_v3_path.is_file(),
        "locked_gold_set": {
            "path": str(gold_path.relative_to(ROOT)),
            "file_sha256": sha256_file(gold_path),
            "manifest_content_sha256": (manifest or {}).get("content_sha256"),
            "n_items": len(items),
        },
        "j1_labels_on_all_40": {
            "present": len(j1_missing) == 0,
            "path": str(j1_pack.relative_to(ROOT)),
            "pack_file_sha256": sha256_file(j1_pack),
            "missing_gold_ids": j1_missing,
            "p0_parse_ok_n": 40 - len(parse_err_ids),
            "p0_parse_error_ids": parse_err_ids,
        },
        "j2_labels_on_all_40": {
            "present": j2_labels is not None and len(j2_labels) == 40 and not (gold_ids - set(j2_labels)),
            "path": str(j2_pack.relative_to(ROOT)) if j2_pack and j2_pack.is_file() else None,
            "missing_note": "No J2 gold pack in repo; Fleiss κ J1/J2/J3 requires ~40 new Grok calls.",
            "j2_cost_estimate_usd": estimate_j2_cost_usd(),
        },
        "anthropic_api_key_in_env": bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
        "j3_cost_estimate_usd": estimate_j3_cost_usd(),
        "criteria_lock_path": str(CRITERIA.relative_to(ROOT)),
    }


def run_live_j3(items: list[dict[str, Any]], *, max_items: int | None) -> list[dict[str, Any]]:
    judge = AnthropicJ3Judge(temperature=0.0)
    preds: list[dict[str, Any]] = []
    subset = items[: max_items or len(items)]
    for item in subset:
        blind = build_blind_judge_input(
            user_prompt=item["user_prompt"],
            model_response=item["model_response"],
            task_context=item.get("task_context") or "",
            success_condition=item.get("success_condition") or "",
            is_benign=False,
        )
        verdict = judge.judge(blind, system_prompt=JUDGE_SYSTEM_PROMPT)
        usage = verdict.usage or {}
        preds.append(
            {
                "attack_success": bool(verdict.attack_success),
                "parse_error": verdict.parse_error,
                "reason": verdict.reason,
                "raw_text": verdict.raw_text,
                "usage": usage,
                "judge_model": verdict.judge_model,
            }
        )
    return preds


def build_report(
    items: list[dict[str, Any]],
    j3_preds: list[dict[str, Any]],
    *,
    j1_labels: dict[str, bool],
    j2_labels: dict[str, bool] | None,
) -> dict[str, Any]:
    report = evaluate_predictions(items, j3_preds)
    checks = prereg_pass(items, j3_preds, report)
    checks.pop("fp_fn_balance_le_2", None)  # J3 lock file omits FP/FN balance gate
    checks["all_pass"] = all(checks.values())

    kappa_block: dict[str, Any] = {"fleiss_kappa_j1_j2_j3": None, "computable": False}
    if j2_labels and len(j2_labels) == 40:
        triplets: list[tuple[bool, bool, bool]] = []
        for item, j3 in zip(items, j3_preds):
            if j3.get("parse_error"):
                continue
            gid = item["gold_id"]
            triplets.append(
                (j1_labels[gid], j2_labels[gid], bool(j3["attack_success"]))
            )
        if len(triplets) == 40:
            kappa_block = {
                "computable": True,
                "fleiss_kappa_j1_j2_j3": fleiss_kappa_binary(triplets),
                "n_items": 40,
            }
        else:
            kappa_block["note"] = "J3 parse errors prevented full 40-item κ"
    else:
        kappa_block["note"] = "J2 labels missing — run J2 on GOLD_SET_v2 first"

    return {
        **report,
        "prereg_checks": checks,
        "prose_claim_without_execution": subset_errors(items, j3_preds, PROSE_IDS),
        "apology_after_execution": subset_errors(items, j3_preds, APOLOGY_IDS),
        "inter_rater": kappa_block,
        "j3_model": J3_MODEL_ID,
    }


def write_pack(
    out_dir: Path,
    *,
    items: list[dict[str, Any]],
    preds: list[dict[str, Any]],
    report: dict[str, Any],
    gold_path: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for item, pred in zip(items, preds):
        rows.append(
            {
                "gold_id": item["gold_id"],
                "gold_category": item.get("gold_category"),
                "human_label": official_label(item),
                "j3_attack_success": pred.get("attack_success"),
                "j3_parse_ok": pred.get("parse_error") is None,
                "j3_parse_error": pred.get("parse_error"),
                "j3_reason": pred.get("reason"),
                "usage": pred.get("usage"),
            }
        )
    (out_dir / "per_item.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )
    manifest = load_gold_manifest(gold_path)
    summary = {
        **report,
        "gold_path": str(gold_path.relative_to(ROOT)),
        "gold_content_sha256": (manifest or {}).get("content_sha256"),
        "criteria_lock": str(CRITERIA.relative_to(ROOT)),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, default=GOLD)
    parser.add_argument("--j1-pack", type=Path, default=DEFAULT_J1_PACK)
    parser.add_argument("--j2-pack", type=Path, default=None, help="Optional J2 per_item.jsonl")
    parser.add_argument(
        "--facts-only",
        action="store_true",
        help="Print Part 2 facts (a)(b)(c) and cost estimates; no J3 calls",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Call Anthropic Messages API (requires ANTHROPIC_API_KEY)",
    )
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--max-items", type=int, default=None)
    args = parser.parse_args()

    facts = collect_facts(gold_path=args.gold, j1_pack=args.j1_pack, j2_pack=args.j2_pack)
    if args.facts_only or not args.live:
        payload = {
            "mode": "facts" if args.facts_only else "prepare_only",
            "facts": facts,
            "schema_diff_md": "experiments/judge_gold/J3_SCHEMA_FIELD_DIFF.md",
            "live_command_hint": (
                "python scripts/run_j3_gold_eval.py --live --out-dir "
                "experiments/judge_gold/J3_GOLD_EVAL_<ts>"
            ),
        }
        print(json.dumps(payload, indent=2))
        return 0

    items = load_gold_items(args.gold)
    if len(items) != 40:
        print(f"expected 40 gold items, got {len(items)}", file=sys.stderr)
        return 2
    j1_labels, _parse_err = load_j1_p0_labels(args.j1_pack)
    j2_labels = load_j2_labels(args.j2_pack)
    preds = run_live_j3(items, max_items=args.max_items)
    if len(preds) != len(items):
        items = items[: len(preds)]
    report = build_report(items, preds, j1_labels=j1_labels, j2_labels=j2_labels)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = args.out_dir or (ROOT / "experiments/judge_gold" / f"J3_GOLD_EVAL_{ts}")
    write_pack(out_dir, items=items, preds=preds, report=report, gold_path=args.gold)
    report["eval_pack_dir"] = str(out_dir.relative_to(ROOT))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
