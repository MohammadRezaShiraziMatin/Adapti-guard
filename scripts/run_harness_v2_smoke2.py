#!/usr/bin/env python3
"""Harness v2 smoke #2: gemma + deepseek only, max 4 HTTP, cap $0.005."""
from __future__ import annotations

import asyncio
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.exec_success import eval_exec_success_from_message  # noqa: E402
from adapti_guard.evaluation.harness_v2.finish_reason import finish_metadata_from_raw_response  # noqa: E402
from adapti_guard.evaluation.harness_v2.http_budget import HttpCompletionBudget  # noqa: E402
from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor  # noqa: E402
from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import run_tools_episode_async  # noqa: E402
from adapti_guard.evaluation.harness_v2.provider_probe import HARNESS_V2_TARGETS  # noqa: E402
from adapti_guard.evaluation.harness_v2.scenarios import SCENARIOS  # noqa: E402
from adapti_guard.evaluation.harness_v2.smoke_criteria import (  # noqa: E402
    eval_c1_function_calling_works,
    eval_c2_attack_outcome_valid,
)
from adapti_guard.evaluation.openrouter_panel_pricing import load_openrouter_pricing_table  # noqa: E402

PANEL = ROOT / "configs/models_q1_eval_panel.yaml"
MAX_HTTP = 4
MAX_USD = 0.005
SMOKE_FAMILIES = ("gemma", "deepseek")
PREREG = "experiments/harness_v2/PREREG_HARNESS_V2.md"


def _cost_from_usage(usage: dict[str, Any], *, model_id: str, pricing: Any) -> float:
    if usage.get("cost") is not None:
        return float(usage["cost"])
    pt = usage.get("prompt_tokens")
    ct = usage.get("completion_tokens")
    if pt is not None and ct is not None:
        return pricing.cost_from_tokens(model_id, int(pt), int(ct))
    return 0.0


def _row_from_call(c: Any, *, family: str, scenario_id: str, exec_spec: Any) -> dict[str, Any]:
    finish_meta = finish_metadata_from_raw_response(c.raw_response)
    raw_msg = SimpleNamespace(
        tool_calls=[
            SimpleNamespace(
                function=SimpleNamespace(name=tc["function"]["name"], arguments=tc["function"]["arguments"])
            )
            for tc in c.tool_calls
        ]
    )
    exec_ok = False
    if exec_spec:
        exec_ok, _ = eval_exec_success_from_message(raw_msg, exec_spec)
    usage = c.usage or {}
    return {
        "call_index": c.call_index,
        "target_family": family,
        "scenario_id": scenario_id,
        "model_id": c.model_id,
        "provider_error": c.provider_error,
        "provider": (c.raw_response or {}).get("provider"),
        "assistant_content": c.assistant_content,
        "tool_calls": c.tool_calls,
        "finish_reason": finish_meta["finish_reason"],
        "native_finish_reason": finish_meta["native_finish_reason"],
        "episode_incomplete": c.episode_incomplete,
        "exec_success": exec_ok if exec_spec else None,
        "usage": usage,
        "reasoning_tokens": int(usage.get("reasoning_tokens") or 0),
        "cost_usd": c.cost_usd,
        "latency_ms": c.latency_ms,
    }


def run_smoke2(out_dir: Path) -> dict[str, Any]:
    pricing = load_openrouter_pricing_table(PANEL)
    family_to_model = {fam: (mid, ck) for fam, mid, ck in HARNESS_V2_TARGETS}
    budget = HttpCompletionBudget(MAX_HTTP)
    spent = 0.0
    call_index = 1
    all_rows: list[dict[str, Any]] = []
    trajectories: list[dict[str, Any]] = []
    stopped_reason = "completed"

    plan = []
    for fam in SMOKE_FAMILIES:
        plan.append((fam, "benign_weather_v1"))
        plan.append((fam, "indirect_tool_injection_v1"))

    for family, scenario_id in plan:
        if budget.exhausted or spent >= MAX_USD:
            stopped_reason = "call_cap" if budget.exhausted else "budget_cap"
            break
        model_id, config_key = family_to_model[family]
        sc = SCENARIOS[scenario_id]
        executor = HarnessV2MockToolExecutor()

        def cost_fn(usage: dict[str, Any], *, model_id: str = model_id) -> float:
            return _cost_from_usage(usage, model_id=model_id, pricing=pricing)

        traj = asyncio.run(
            run_tools_episode_async(
                scenario_id=scenario_id,
                model_id=model_id,
                config_key=config_key,
                system_prompt=sc["system_prompt"],
                initial_user=sc["user"],
                executor=executor,
                call_index_start=call_index,
                pricing_cost_fn=cost_fn,
                max_rounds=1,
                http_budget=budget,
            )
        )
        for c in traj.calls:
            spent += float(c.cost_usd or 0.0)
            row = _row_from_call(c, family=family, scenario_id=scenario_id, exec_spec=sc.get("exec_spec"))
            all_rows.append(row)
            if spent >= MAX_USD:
                stopped_reason = "budget_cap"
                break
        if traj.calls:
            call_index = traj.calls[-1].call_index + 1
        trajectories.append(
            {
                "family": family,
                "scenario_id": scenario_id,
                "episode_incomplete": any(x.episode_incomplete for x in traj.calls),
                "calls": [
                    {
                        "call_index": c.call_index,
                        "request": c.request,
                        "raw_response": c.raw_response,
                        "finish_reason": c.finish_reason,
                        "native_finish_reason": c.native_finish_reason,
                        "episode_incomplete": c.episode_incomplete,
                    }
                    for c in traj.calls
                ],
                "final_messages": traj.final_messages,
                "mock_tool_log": traj.mock_tool_log,
            }
        )
        if stopped_reason != "completed":
            break

    per_model: dict[str, Any] = {}
    for fam in SMOKE_FAMILIES:
        benign = [r for r in all_rows if r["target_family"] == fam and r["scenario_id"] == "benign_weather_v1"]
        attack = [r for r in all_rows if r["target_family"] == fam and r["scenario_id"] == "indirect_tool_injection_v1"]
        c1_ok, c1_reason = eval_c1_function_calling_works(benign)
        c2 = eval_c2_attack_outcome_valid(attack)
        per_model[fam] = {
            "C1_function_calling_works": c1_ok,
            "C1_detail": c1_reason,
            "C2_attack_outcome_valid": c2["C2_PASS"],
            "C2_detail": c2,
        }

    summary = {
        "smoke_wave": 2,
        "prereg": PREREG,
        "max_http_requests": MAX_HTTP,
        "http_requests_used": budget.used,
        "max_usd": MAX_USD,
        "spent_usd": round(spent, 8),
        "stopped_reason": stopped_reason,
        "targets": list(SMOKE_FAMILIES),
        "per_model_criteria": per_model,
        "calls": all_rows,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out_dir / "trajectories.json").write_text(json.dumps(trajectories, indent=2) + "\n", encoding="utf-8")
    cum = 0.0
    cost_lines = []
    for i, row in enumerate(all_rows, 1):
        c = float(row.get("cost_usd") or 0.0)
        cum += c
        cost_lines.append(
            {
                "call_index": i,
                "role": "target",
                "model_id": row["model_id"],
                "arm": row["scenario_id"],
                "finish_reason": row.get("finish_reason"),
                "native_finish_reason": row.get("native_finish_reason"),
                "prompt_tokens": (row.get("usage") or {}).get("prompt_tokens"),
                "completion_tokens": (row.get("usage") or {}).get("completion_tokens"),
                "reasoning_tokens": row.get("reasoning_tokens"),
                "cost_usd": c,
                "cumulative_usd": cum,
            }
        )
    (out_dir / "cost_log.jsonl").write_text("\n".join(json.dumps(x) for x in cost_lines) + "\n", encoding="utf-8")
    (out_dir / "cost_summary.json").write_text(
        json.dumps(
            {
                "api_calls": budget.used,
                "spent_usd": round(spent, 8),
                "cap_usd": MAX_USD,
                "stopped_reason": stopped_reason,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = args.out_dir or (ROOT / "experiments/harness_v2" / f"HARNESS_V2_SMOKE2_{ts}")
    if not out.is_absolute():
        out = ROOT / out
    summary = run_smoke2(out)
    summary["out_dir"] = str(out.relative_to(ROOT))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
