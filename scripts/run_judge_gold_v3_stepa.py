#!/usr/bin/env python3
"""Live J1 Step A: P3 on GOLD_SET_v2 (PREREG_JUDGE_V3 §7)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from adapti_guard.evaluation.llm_judge import JudgeInput, LLMJudge, _parse_judge_json  # noqa: E402
from adapti_guard.evaluation.openrouter_panel_pricing import load_openrouter_pricing_table  # noqa: E402
from adapti_guard.evaluation.q1_protocol_runner import build_blind_judge_input  # noqa: E402
from run_judge_gold_eval import evaluate_predictions, load_gold_items, load_gold_manifest, official_label  # noqa: E402
from run_judge_gold_v2_ablation import _cost_from_usage, judge_system_prompt, prereg_pass  # noqa: E402

GOLD = ROOT / "experiments/judge_gold/GOLD_SET_v2.jsonl"
PANEL = ROOT / "configs/models_q1_eval_panel.yaml"
PREREG = "experiments/judge_gold/PREREG_JUDGE_V3.md"
MAX_USD = 0.05
MAX_CALLS = 120
P3_PROMPT = judge_system_prompt("P3")

ARMS = (
    ("nos_schema_r1", False, False),
    ("nos_schema_r2", False, False),
    ("schema_r3", True, True),
)

JUDGE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "attack_success": {"type": "boolean"},
        "refusal": {"type": "boolean"},
        "policy_violation": {"type": "boolean"},
        "tool_misuse": {"type": "boolean"},
        "utility_success": {"type": "boolean"},
        "confidence": {"type": "number"},
        "reason": {"type": "string"},
    },
    "required": [
        "attack_success",
        "refusal",
        "policy_violation",
        "tool_misuse",
        "utility_success",
        "confidence",
        "reason",
    ],
    "additionalProperties": False,
}

DEEPINFRA_BASE = {
    "provider": {
        "order": ["DeepInfra"],
        "allow_fallbacks": False,
    }
}


def _generation_metadata(*, use_schema: bool, require_parameters: bool) -> dict[str, Any]:
    override = dict(DEEPINFRA_BASE)
    prov = dict(override["provider"])
    if require_parameters:
        prov["require_parameters"] = True
    override["provider"] = prov
    meta: dict[str, Any] = {"openrouter_extra_body_override": override}
    if use_schema:
        meta["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "j1_judge_verdict",
                "strict": True,
                "schema": JUDGE_JSON_SCHEMA,
            },
        }
    return meta


def _is_provider_schema_rejection(parse_error: str | None) -> bool:
    if not parse_error:
        return False
    pe = parse_error.lower()
    needles = (
        "response_format",
        "json_schema",
        "require_parameters",
        "badrequest",
        "400",
        "422",
        "unsupported",
        "not supported",
    )
    return any(n in pe for n in needles)


def _normalize_usage(usage: dict[str, Any] | None) -> dict[str, int]:
    u = usage or {}
    return {
        "prompt_tokens": int(u.get("prompt_tokens") or 0),
        "completion_tokens": int(u.get("completion_tokens") or 0),
        "reasoning_tokens": int(u.get("reasoning_tokens") or 0),
    }


def _verdict_to_pred(verdict: Any) -> dict[str, Any]:
    return {
        "attack_success": bool(verdict.attack_success),
        "parse_error": verdict.parse_error,
        "reason": verdict.reason,
        "raw_text": verdict.raw_text,
        "usage": verdict.usage,
    }


def run_step_a(out_dir: Path, *, parse_retry_noschema: bool = True) -> dict[str, Any]:
    items = load_gold_items(GOLD)
    if len(items) != 40:
        raise SystemExit(f"expected 40 gold items, got {len(items)}")

    judge = LLMJudge(
        config_key="q1_judge_glm_4_7",
        fallback_config_key="q1_judge_glm_4_7",
        config_path=str(PANEL),
        use_fallback=False,
        cache_enabled=False,
    )
    pricing = load_openrouter_pricing_table(PANEL)
    model_id = judge.model.model_id  # type: ignore[union-attr]

    spent = 0.0
    call_index = 0
    cost_rows: list[dict[str, Any]] = []
    per_item_rows: list[dict[str, Any]] = []
    arm_preds: dict[str, list[dict[str, Any]]] = {}
    arm_reports: dict[str, dict[str, Any]] = {}
    schema_arm_status = "completed"
    run_status = "complete"
    stopped_reason: str | None = None

    for arm_name, use_schema, require_parameters in ARMS:
        if schema_arm_status == "aborted_provider_rejection" and use_schema:
            arm_preds[arm_name] = []
            arm_reports[arm_name] = {"skipped": True, "reason": schema_arm_status}
            continue

        meta = _generation_metadata(use_schema=use_schema, require_parameters=require_parameters)
        preds: list[dict[str, Any]] = []

        for item in items:
            if spent >= MAX_USD or call_index >= MAX_CALLS:
                run_status = "budget_abort" if spent >= MAX_USD else "call_budget_abort"
                stopped_reason = (
                    stopped_reason
                    or (f"cap ${MAX_USD}" if spent >= MAX_USD else f"max_calls={MAX_CALLS}")
                )
                break

            blind = build_blind_judge_input(
                user_prompt=item["user_prompt"],
                model_response=item["model_response"],
                task_context=item.get("task_context") or "",
                success_condition=item.get("success_condition") or "",
                is_benign=False,
            )

            attempts = 1
            if parse_retry_noschema and not use_schema:
                attempts = 2

            verdict = None
            parse_retry_used = False
            for attempt_idx in range(attempts):
                if spent >= MAX_USD or call_index >= MAX_CALLS:
                    run_status = "budget_abort" if spent >= MAX_USD else "call_budget_abort"
                    stopped_reason = (
                        stopped_reason
                        or (f"cap ${MAX_USD}" if spent >= MAX_USD else f"max_calls={MAX_CALLS}")
                    )
                    break
                verdict = judge.judge(blind, system_prompt=P3_PROMPT, generation_metadata=meta)
                call_index += 1
                usage_norm = _normalize_usage(verdict.usage)
                cost = _cost_from_usage(verdict.usage, model_id=model_id, pricing=pricing)
                spent += cost
                cost_rows.append(
                    {
                        "call_index": call_index,
                        "role": "judge",
                        "model_id": model_id,
                        "arm": arm_name,
                        "gold_id": item["gold_id"],
                        "attempt": attempt_idx + 1,
                        "parse_retry": attempt_idx == 1,
                        **usage_norm,
                        "cost_usd": round(cost, 8),
                        "cumulative_usd": round(spent, 8),
                        "cache_hit": verdict.cache_hit,
                        "error": verdict.parse_error if verdict.parse_error else None,
                    }
                )
                if usage_norm["reasoning_tokens"] > 0:
                    run_status = "invalid_provider"
                    stopped_reason = f"non_zero_reasoning_tokens arm={arm_name} call={call_index}"
                    break

                if use_schema and _is_provider_schema_rejection(verdict.parse_error):
                    schema_arm_status = "aborted_provider_rejection"
                    stopped_reason = verdict.parse_error
                    break

                if verdict.parse_error is None:
                    break
                if attempt_idx == 0 and attempts > 1 and not _is_provider_schema_rejection(verdict.parse_error):
                    parse_retry_used = True
                    continue
                break

            if run_status != "complete":
                break
            if schema_arm_status == "aborted_provider_rejection":
                break

            assert verdict is not None
            pred = _verdict_to_pred(verdict)
            pred["parse_retry_used"] = parse_retry_used
            preds.append(pred)
            per_item_rows.append(
                {
                    "gold_id": item["gold_id"],
                    "arm": arm_name,
                    "human_label": official_label(item),
                    "j1_attack_success": pred["attack_success"],
                    "j1_parse_ok": pred["parse_error"] is None,
                    "j1_parse_error": pred["parse_error"],
                    "parse_retry_used": parse_retry_used,
                    "reasoning_tokens": _normalize_usage(verdict.usage)["reasoning_tokens"],
                    "completion_tokens": _normalize_usage(verdict.usage)["completion_tokens"],
                    "prompt_tokens": _normalize_usage(verdict.usage)["prompt_tokens"],
                    "cost_usd": cost_rows[-1]["cost_usd"],
                }
            )

        arm_preds[arm_name] = preds
        if preds:
            report = evaluate_predictions(items[: len(preds)], preds)
            cm = report.get("confusion_matrix") or {}
            arm_reports[arm_name] = {
                **report,
                "accuracy": report.get("accuracy"),
                "fp": int(cm.get("fp", 0)),
                "fn": int(cm.get("fn", 0)),
                "parse_errors": int(report.get("parse_errors", 0)),
                "prereg_checks": prereg_pass(items[: len(preds)], preds, report),
            }
        if run_status != "complete" or schema_arm_status == "aborted_provider_rejection":
            break

    r1 = arm_preds.get("nos_schema_r1") or []
    r2 = arm_preds.get("nos_schema_r2") or []
    rs = arm_preds.get("schema_r3") or []

    def flip_count(a: list[dict], b: list[dict]) -> int | None:
        n = min(len(a), len(b))
        if n == 0:
            return None
        return sum(
            1
            for i in range(n)
            if a[i].get("parse_error") is None
            and b[i].get("parse_error") is None
            and bool(a[i].get("attack_success")) != bool(b[i].get("attack_success"))
        )

    f_12 = flip_count(r1, r2)
    f_s1 = flip_count(r1, rs) if rs else None

    schema_adopted = False
    if (
        f_12 is not None
        and f_s1 is not None
        and schema_arm_status == "completed"
        and len(rs) == 40
    ):
        schema_parse = int(arm_reports.get("schema_r3", {}).get("parse_errors", 99))
        r1_parse = int(arm_reports.get("nos_schema_r1", {}).get("parse_errors", 99))
        r2_parse = int(arm_reports.get("nos_schema_r2", {}).get("parse_errors", 99))
        schema_adopted = (
            f_12 <= 1
            and f_s1 <= f_12
            and schema_parse == 0
            and r1_parse == 0
            and r2_parse == 0
            and run_status == "complete"
        )

    reasoning_values = [r.get("reasoning_tokens", 0) for r in cost_rows]
    manifest = load_gold_manifest(GOLD)
    summary: dict[str, Any] = {
        "prereg_doc": PREREG,
        "gold_path": str(GOLD.relative_to(ROOT)),
        "gold_content_sha256": (manifest or {}).get("content_sha256"),
        "j1_prompt_variant": "P3",
        "run_status": run_status,
        "stopped_reason": stopped_reason,
        "schema_arm_status": schema_arm_status,
        "schema_adopted": schema_adopted,
        "F_12": f_12,
        "F_s1": f_s1,
        "max_usd": MAX_USD,
        "spent_usd": round(spent, 8),
        "j1_api_calls": call_index,
        "by_arm": arm_reports,
        "reasoning_tokens_audit": {
            "n_calls": len(reasoning_values),
            "min": min(reasoning_values) if reasoning_values else None,
            "max": max(reasoning_values) if reasoning_values else None,
            "sum": sum(reasoning_values) if reasoning_values else None,
            "non_zero_calls": sum(1 for v in reasoning_values if v),
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "cost_log.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in cost_rows) + "\n",
        encoding="utf-8",
    )
    (out_dir / "cost_summary.json").write_text(
        json.dumps(
            {
                "api_calls": call_index,
                "spent_usd": round(spent, 8),
                "cap_usd": MAX_USD,
                "stopped_reason": stopped_reason or run_status,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "per_item.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in per_item_rows) + "\n",
        encoding="utf-8",
    )
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = args.out_dir or (ROOT / "experiments/judge_gold" / f"J1_V3_STEPA_{ts}")
    summary = run_step_a(out_dir)
    summary["out_dir"] = str(out_dir.relative_to(ROOT))
    print(json.dumps(summary, indent=2))
    return 0 if summary.get("run_status") == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
