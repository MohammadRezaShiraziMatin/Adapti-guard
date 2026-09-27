#!/usr/bin/env python3
"""Amendment 4 Step 2: qwen3 reasoning-off smoke (max 2 HTTP, cap $0.002)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.http_budget import HttpCompletionBudget  # noqa: E402
from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop  # noqa: E402
from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import run_tools_episode_async  # noqa: E402
from adapti_guard.evaluation.harness_v2.provider_probe import HARNESS_V2_TARGETS  # noqa: E402
from adapti_guard.evaluation.harness_v2.scenarios import SCENARIOS  # noqa: E402
from adapti_guard.evaluation.harness_v2.trajectory_store import serialize_trajectory_call  # noqa: E402
from adapti_guard.evaluation.openrouter_panel_pricing import load_openrouter_pricing_table  # noqa: E402

PANEL = ROOT / "configs/models_q1_eval_panel.yaml"
PREREG = "experiments/harness_v2/PREREG_HARNESS_V2.md"
MODEL_FAMILY = "qwen3"
SCENARIO_ID = "benign_weather_v1"
HTTP_CAP = 2
MAX_USD = 0.002
MAX_ROUNDS = 2


def _run_episode_sync(**kwargs: Any) -> Any:
    async def _coro() -> Any:
        return await run_tools_episode_async(**kwargs)

    return run_harness_event_loop(_coro)


def _cost_from_usage(usage: dict[str, Any], *, model_id: str, pricing: Any) -> float:
    if usage.get("cost") is not None:
        return float(usage["cost"])
    pt = usage.get("prompt_tokens")
    ct = usage.get("completion_tokens")
    if pt is not None and ct is not None:
        return pricing.cost_from_tokens(model_id, int(pt), int(ct))
    return 0.0


def _eval_reasoning_off(raw: dict[str, Any], usage: dict[str, Any]) -> tuple[bool, list[str]]:
    fails: list[str] = []
    rt = usage.get("reasoning_tokens")
    if rt is not None and int(rt) > 0:
        fails.append(f"reasoning_tokens={rt}")
    msg = (raw.get("choices") or [{}])[0].get("message") or {}
    if "reasoning" in msg:
        text = str(msg.get("reasoning") or "")
        if text.strip():
            fails.append("message.reasoning_non_empty")
        else:
            fails.append("message.reasoning_key_present")
    return len(fails) == 0, fails


def run_reasoning_smoke(out_dir: Path) -> dict[str, Any]:
    model_id, config_key = next((mid, ck) for fam, mid, ck in HARNESS_V2_TARGETS if fam == MODEL_FAMILY)
    sc = SCENARIOS[SCENARIO_ID]
    pricing = load_openrouter_pricing_table(PANEL)
    budget = HttpCompletionBudget(HTTP_CAP)
    spent = 0.0
    http_index = 0
    evidence: list[dict[str, Any]] = []
    traj_calls_serialized: list[dict[str, Any]] = []

    def cost_fn(usage: dict[str, Any], *, model_id: str = model_id) -> float:
        return _cost_from_usage(usage, model_id=model_id, pricing=pricing)

    executor = HarnessV2MockToolExecutor()
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
    )
    all_pass = True
    for c in traj.calls:
        http_index += 1
        spent += float(c.cost_usd or 0.0)
        raw = c.raw_response or {}
        usage = dict(c.usage or {})
        raw_usage = raw.get("usage") or usage
        ok, fail_reasons = _eval_reasoning_off(raw, raw_usage if isinstance(raw_usage, dict) else usage)
        if not ok:
            all_pass = False
        msg = (raw.get("choices") or [{}])[0].get("message") or {}
        evidence.append(
            {
                "http_index": http_index,
                "pass": ok,
                "fail_reasons": fail_reasons,
                "request": c.request,
                "raw_usage": raw_usage,
                "message_keys": sorted(msg.keys()),
                "reasoning_field_preview": str(msg.get("reasoning") or "")[:120],
            }
        )
        traj_calls_serialized.append(serialize_trajectory_call(c, http_index=http_index))
        if spent >= MAX_USD:
            break

    summary = {
        "smoke_wave": "reasoning_off_amendment4_step2",
        "prereg": PREREG,
        "amendment": 4,
        "model_family": MODEL_FAMILY,
        "model_id": model_id,
        "scenario_id": SCENARIO_ID,
        "http_cap": HTTP_CAP,
        "http_used": budget.used,
        "max_usd": MAX_USD,
        "spent_usd": round(spent, 8),
        "reasoning_off_pass": all_pass,
        "evidence": evidence,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out_dir / "trajectories.json").write_text(
        json.dumps(
            [
                {
                    "family": MODEL_FAMILY,
                    "scenario_id": SCENARIO_ID,
                    "calls": traj_calls_serialized,
                    "final_messages": traj.final_messages,
                    "mock_tool_log": traj.mock_tool_log,
                }
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    cum = 0.0
    lines = []
    for row in traj_calls_serialized:
        u = row.get("usage") or {}
        cst = float(row.get("cost_usd") or 0.0)
        cum += cst
        lines.append(
            {
                "call_index": row["http_index"],
                "role": "target",
                "model_id": model_id,
                "arm": SCENARIO_ID,
                "prompt_tokens": u.get("prompt_tokens"),
                "completion_tokens": u.get("completion_tokens"),
                "reasoning_tokens": int(u.get("reasoning_tokens") or 0),
                "cost_usd": cst,
                "cumulative_usd": cum,
            }
        )
    (out_dir / "cost_log.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8")
    (out_dir / "cost_summary.json").write_text(
        json.dumps(
            {
                "api_calls": budget.used,
                "spent_usd": round(spent, 8),
                "cap_usd": MAX_USD,
                "stopped_reason": "completed" if all_pass else "reasoning_off_fail",
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
    out = args.out_dir or (ROOT / "experiments/harness_v2" / f"HARNESS_V2_REASONING_SMOKE_{ts}")
    if not out.is_absolute():
        out = ROOT / out
    summary = run_reasoning_smoke(out)
    summary["out_dir"] = str(out.relative_to(ROOT))
    print(json.dumps(summary, indent=2))
    return 0 if summary["reasoning_off_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
