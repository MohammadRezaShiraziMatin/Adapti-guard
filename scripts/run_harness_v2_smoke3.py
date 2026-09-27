#!/usr/bin/env python3
"""Harness v2 smoke #3: indirect injection, 3 models, max 9 HTTP, cap $0.005."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.c2_episode_state import classify_c2_episode  # noqa: E402
from adapti_guard.evaluation.harness_v2.finish_reason import finish_metadata_from_raw_response  # noqa: E402
from adapti_guard.evaluation.harness_v2.http_budget import HttpCompletionBudget  # noqa: E402
from adapti_guard.evaluation.harness_v2.http_preflight import preflight_http_budget  # noqa: E402
from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop  # noqa: E402
from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import run_tools_episode_async  # noqa: E402
from adapti_guard.evaluation.harness_v2.provider_probe import HARNESS_V2_TARGETS  # noqa: E402
from adapti_guard.evaluation.harness_v2.scenarios import SCENARIOS  # noqa: E402
from adapti_guard.evaluation.harness_v2.trajectory_store import serialize_trajectory_call  # noqa: E402
from adapti_guard.evaluation.openrouter_panel_pricing import load_openrouter_pricing_table  # noqa: E402

PANEL = ROOT / "configs/models_q1_eval_panel.yaml"
PREREG = "experiments/harness_v2/PREREG_HARNESS_V2.md"
SMOKE_FAMILIES = ("gemma", "deepseek", "qwen3")
SCENARIO_ID = "indirect_tool_injection_v1"
N_MODELS = len(SMOKE_FAMILIES)
N_SCENARIOS = 1
MAX_ROUNDS = 3
HTTP_CAP = 9
MAX_USD = 0.005
CONTENT_TRUNC = 300


def _cost_from_usage(usage: dict[str, Any], *, model_id: str, pricing: Any) -> float:
    if usage.get("cost") is not None:
        return float(usage["cost"])
    pt = usage.get("prompt_tokens")
    ct = usage.get("completion_tokens")
    if pt is not None and ct is not None:
        return pricing.cost_from_tokens(model_id, int(pt), int(ct))
    return 0.0


def _content_for_report(text: str) -> dict[str, Any]:
    if len(text) <= CONTENT_TRUNC:
        return {"content": text, "content_truncated": False}
    return {
        "content": text[:CONTENT_TRUNC],
        "content_truncated": True,
        "content_full_length": len(text),
    }


def _row_from_call(c: Any, *, family: str, global_index: int) -> dict[str, Any]:
    finish_meta = finish_metadata_from_raw_response(c.raw_response)
    usage = c.usage or {}
    content_info = _content_for_report(c.assistant_content or "")
    return {
        "http_index": global_index,
        "call_index": c.call_index,
        "episode_round": c.episode_round,
        "target_family": family,
        "scenario_id": c.scenario_id,
        "model_id": c.model_id,
        "provider_error": c.provider_error,
        "provider": (c.raw_response or {}).get("provider"),
        "finish_reason": finish_meta["finish_reason"],
        "native_finish_reason": finish_meta["native_finish_reason"],
        "tool_calls": c.tool_calls,
        **content_info,
        "usage": usage,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": int(usage.get("reasoning_tokens") or 0),
        "cost_usd": c.cost_usd,
        "latency_ms": c.latency_ms,
        "episode_incomplete": c.episode_incomplete,
    }


def run_smoke3(out_dir: Path) -> dict[str, Any]:
    preflight = preflight_http_budget(
        n_models=N_MODELS,
        n_scenarios=N_SCENARIOS,
        max_rounds_per_episode=MAX_ROUNDS,
        http_cap=HTTP_CAP,
    )
    pricing = load_openrouter_pricing_table(PANEL)
    family_to_model = {fam: (mid, ck) for fam, mid, ck in HARNESS_V2_TARGETS}
    budget = HttpCompletionBudget(HTTP_CAP)
    spent = 0.0
    http_index = 0
    all_rows: list[dict[str, Any]] = []
    trajectories: list[dict[str, Any]] = []
    per_model_c2: dict[str, Any] = {}
    sc = SCENARIOS[SCENARIO_ID]
    stopped_reason = "completed"

    for family in SMOKE_FAMILIES:
        if budget.exhausted or spent >= MAX_USD:
            stopped_reason = "call_cap" if budget.exhausted else "budget_cap"
            break
        model_id, config_key = family_to_model[family]
        executor = HarnessV2MockToolExecutor()
        episode_rows: list[dict[str, Any]] = []

        def cost_fn(usage: dict[str, Any], *, model_id: str = model_id) -> float:
            return _cost_from_usage(usage, model_id=model_id, pricing=pricing)

        traj = _run_episode_sync(
            scenario_id=SCENARIO_ID,
            model_id=model_id,
            config_key=config_key,
            system_prompt=sc["system_prompt"],
            initial_user=sc["user"],
            executor=executor,
            max_rounds=MAX_ROUNDS,
            http_budget=budget,
            pricing_cost_fn=cost_fn,
            call_index_start=1,
        )
        for c in traj.calls:
            http_index += 1
            spent += float(c.cost_usd or 0.0)
            row = _row_from_call(c, family=family, global_index=http_index)
            all_rows.append(row)
            episode_rows.append(row)
            if spent >= MAX_USD:
                stopped_reason = "budget_cap"
                break
        c2 = classify_c2_episode(
            final_messages=traj.final_messages,
            mock_tool_log=traj.mock_tool_log,
            http_rows=episode_rows,
        )
        per_model_c2[family] = c2
        trajectories.append(
            {
                "family": family,
                "scenario_id": SCENARIO_ID,
                "C2": c2,
                "final_messages": traj.final_messages,
                "mock_tool_log": traj.mock_tool_log,
                "calls": [
                    serialize_trajectory_call(
                        c,
                        http_index=r["http_index"],
                        content=r.get("content"),
                    )
                    for r, c in zip(episode_rows, traj.calls)
                ],
            }
        )
        if stopped_reason != "completed":
            break

    summary = {
        "smoke_wave": 3,
        "prereg": PREREG,
        "preflight": preflight,
        "max_http_cap": HTTP_CAP,
        "http_requests_used": budget.used,
        "max_usd": MAX_USD,
        "spent_usd": round(spent, 8),
        "stopped_reason": stopped_reason,
        "targets": list(SMOKE_FAMILIES),
        "scenario_id": SCENARIO_ID,
        "max_rounds_per_episode": MAX_ROUNDS,
        "per_model_C2_state": {k: v["C2_state"] for k, v in per_model_c2.items()},
        "per_model_C2_detail": per_model_c2,
        "http_requests": all_rows,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out_dir / "trajectories.json").write_text(json.dumps(trajectories, indent=2) + "\n", encoding="utf-8")
    cum = 0.0
    cost_lines = []
    for row in all_rows:
        c = float(row.get("cost_usd") or 0.0)
        cum += c
        cost_lines.append(
            {
                "call_index": row["http_index"],
                "role": "target",
                "model_id": row["model_id"],
                "arm": row["scenario_id"],
                "episode_round": row["episode_round"],
                "finish_reason": row.get("finish_reason"),
                "native_finish_reason": row.get("native_finish_reason"),
                "prompt_tokens": row.get("prompt_tokens"),
                "completion_tokens": row.get("completion_tokens"),
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
                "http_cap": HTTP_CAP,
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
    out = args.out_dir or (ROOT / "experiments/harness_v2" / f"HARNESS_V2_SMOKE3_{ts}")
    if not out.is_absolute():
        out = ROOT / out
    summary = run_smoke3(out)
    summary["out_dir"] = str(out.relative_to(ROOT))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
