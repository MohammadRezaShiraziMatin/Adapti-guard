#!/usr/bin/env python3
"""Harness v2 Step 2 smoke: max 3 chat calls, cap $0.01, DeepInfra+tools only."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.exec_success import (  # noqa: E402
    eval_exec_success_from_message,
)
from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor  # noqa: E402
from adapti_guard.evaluation.harness_v2.openrouter_tools_session import run_tools_episode  # noqa: E402
from adapti_guard.evaluation.harness_v2.provider_probe import HARNESS_V2_TARGETS, probe_all_targets  # noqa: E402
from adapti_guard.evaluation.harness_v2.scenarios import SCENARIOS  # noqa: E402
from adapti_guard.evaluation.openrouter_panel_pricing import load_openrouter_pricing_table  # noqa: E402

PANEL = ROOT / "configs/models_q1_eval_panel.yaml"
MAX_CALLS = 3
MAX_USD = 0.01
PREREG = "experiments/harness_v2/PREREG_HARNESS_V2.md"


def _cost_from_usage(usage: dict[str, Any], *, model_id: str, pricing: Any) -> float:
    if usage.get("cost") is not None:
        return float(usage["cost"])
    pt = usage.get("prompt_tokens")
    ct = usage.get("completion_tokens")
    if pt is not None and ct is not None:
        return pricing.cost_from_tokens(model_id, int(pt), int(ct))
    return 0.0


def _eligible_families(probe: dict[str, Any]) -> list[str]:
    return [
        fam
        for fam, row in probe.get("targets", {}).items()
        if row.get("smoke_eligible")
    ]


def _serialize_call(traj_call: Any, *, exec_spec: Any, raw_msg: Any) -> dict[str, Any]:
    exec_ok = False
    exec_detail: dict[str, Any] = {}
    if exec_spec and raw_msg is not None:
        exec_ok, exec_detail = eval_exec_success_from_message(raw_msg, exec_spec)
    usage = traj_call.usage or {}
    return {
        "call_index": traj_call.call_index,
        "scenario_id": traj_call.scenario_id,
        "model_id": traj_call.model_id,
        "provider_error": traj_call.provider_error,
        "assistant_content": traj_call.assistant_content,
        "tool_calls": traj_call.tool_calls,
        "exec_success": exec_ok,
        "exec_success_detail": exec_detail,
        "usage": usage,
        "reasoning_tokens": int(usage.get("reasoning_tokens") or 0),
        "cost_usd": traj_call.cost_usd,
        "latency_ms": traj_call.latency_ms,
        "raw_response_excerpt": {
            "id": traj_call.raw_response.get("id"),
            "model": traj_call.raw_response.get("model"),
            "provider": traj_call.raw_response.get("provider"),
        },
    }


def _smoke_pass(call_rows: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    if not call_rows:
        return False, ["no_calls"]
    has_structured = False
    for row in call_rows:
        if row.get("provider_error"):
            continue
        if not row.get("raw_response_excerpt") and not row.get("tool_calls"):
            return False, [f"missing_log_call_{row.get('call_index')}"]
        for tc in row.get("tool_calls") or []:
            fn = tc.get("function") or {}
            raw_args = fn.get("arguments")
            if not raw_args:
                continue
            try:
                json.loads(raw_args)
            except json.JSONDecodeError:
                continue
            has_structured = True
    if not has_structured:
        return False, ["no_structured_tool_calls_with_json_args"]
    return True, []


def run_smoke(out_dir: Path) -> dict[str, Any]:
    probe = probe_all_targets()
    eligible = _eligible_families(probe)
    pricing = load_openrouter_pricing_table(PANEL)
    family_to_model = {fam: (mid, ck) for fam, mid, ck in HARNESS_V2_TARGETS}

    plan: list[tuple[str, str, str]] = []
    if "qwen3" in eligible:
        plan.append(("qwen3", "benign_weather_v1", "benign"))
    if "qwen3" in eligible and len(plan) < MAX_CALLS:
        plan.append(("qwen3", "indirect_tool_injection_v1", "indirect"))
    if len(plan) < MAX_CALLS:
        second = next((f for f in ("llama", "deepseek", "gemma", "qwen3") if f in eligible and f != plan[-1][0]), None)
        if second:
            plan.append((second, "indirect_tool_injection_v1", "indirect"))

    spent = 0.0
    http_calls = 0
    call_index = 1
    call_rows: list[dict[str, Any]] = []
    trajectories: list[dict[str, Any]] = []
    stopped_reason = "completed"

    for family, scenario_id, _label in plan:
        if spent >= MAX_USD or http_calls >= MAX_CALLS:
            stopped_reason = "budget_cap" if spent >= MAX_USD else "call_cap"
            break
        model_id, config_key = family_to_model[family]
        sc = SCENARIOS[scenario_id]
        executor = HarnessV2MockToolExecutor()

        def cost_fn(usage: dict[str, Any], *, model_id: str = model_id) -> float:
            return _cost_from_usage(usage, model_id=model_id, pricing=pricing)

        traj = run_tools_episode(
            scenario_id=scenario_id,
            model_id=model_id,
            config_key=config_key,
            system_prompt=sc["system_prompt"],
            initial_user=sc["user"],
            executor=executor,
            call_index_start=call_index,
            pricing_cost_fn=cost_fn,
            max_rounds=min(4, max(1, MAX_CALLS - http_calls)),
        )
        for c in traj.calls:
            http_calls += 1
            spent += float(c.cost_usd or 0.0)
            raw_msg = SimpleNamespace(
                tool_calls=[
                    SimpleNamespace(
                        function=SimpleNamespace(
                            name=tc["function"]["name"],
                            arguments=tc["function"]["arguments"],
                        )
                    )
                    for tc in c.tool_calls
                ]
            )
            row = _serialize_call(c, exec_spec=sc.get("exec_spec"), raw_msg=raw_msg)
            row["target_family"] = family
            call_rows.append(row)
            call_index = c.call_index + 1
            if spent >= MAX_USD or http_calls >= MAX_CALLS:
                stopped_reason = "budget_cap" if spent >= MAX_USD else "call_cap"
                break
        trajectories.append(
            {
                "scenario_id": scenario_id,
                "family": family,
                "system_prompt": traj.system_prompt,
                "final_messages": traj.final_messages,
                "mock_tool_log": traj.mock_tool_log,
                "calls": [
                    {
                        "call_index": c.call_index,
                        "request": c.request,
                        "raw_response": c.raw_response,
                        "tool_calls": c.tool_calls,
                        "assistant_content": c.assistant_content,
                        "usage": c.usage,
                        "cost_usd": c.cost_usd,
                        "provider_error": c.provider_error,
                    }
                    for c in traj.calls
                ],
            }
        )
        if stopped_reason != "completed":
            break

    passed, pass_reasons = _smoke_pass(call_rows)
    summary = {
        "prereg": PREREG,
        "max_calls": MAX_CALLS,
        "max_usd": MAX_USD,
        "spent_usd": round(spent, 8),
        "api_calls": http_calls,
        "http_completions_logged": len(call_rows),
        "stopped_reason": stopped_reason,
        "eligible_families": eligible,
        "plan_executed": plan[:MAX_CALLS],
        "smoke_pass": passed,
        "smoke_pass_detail": pass_reasons,
        "calls": call_rows,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "provider_probe.json").write_text(json.dumps(probe, indent=2) + "\n", encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out_dir / "trajectories.json").write_text(json.dumps(trajectories, indent=2) + "\n", encoding="utf-8")
    cost_lines = []
    cum = 0.0
    for i, row in enumerate(call_rows, 1):
        c = float(row.get("cost_usd") or 0.0)
        cum += c
        cost_lines.append(
            {
                "call_index": i,
                "role": "target",
                "model_id": row["model_id"],
                "arm": row["scenario_id"],
                "prompt_tokens": (row.get("usage") or {}).get("prompt_tokens"),
                "completion_tokens": (row.get("usage") or {}).get("completion_tokens"),
                "reasoning_tokens": row.get("reasoning_tokens"),
                "cost_usd": c,
                "cumulative_usd": cum,
            }
        )
    (out_dir / "cost_log.jsonl").write_text(
        "\n".join(json.dumps(x) for x in cost_lines) + "\n",
        encoding="utf-8",
    )
    (out_dir / "cost_summary.json").write_text(
        json.dumps(
            {
                "api_calls": len(call_rows),
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
    out = args.out_dir or (ROOT / "experiments/harness_v2" / f"HARNESS_V2_SMOKE_{ts}")
    summary = run_smoke(out)
    summary["out_dir"] = str(out.relative_to(ROOT))
    print(json.dumps(summary, indent=2))
    return 0 if summary.get("smoke_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
