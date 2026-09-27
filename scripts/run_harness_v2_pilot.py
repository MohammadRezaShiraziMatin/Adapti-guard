#!/usr/bin/env python3
"""Harness v2 controlled pilot (Matin-approved, cap $0.05 / 640 HTTP)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.c2_episode_state import (  # noqa: E402
    classify_c2_episode,
    http_rows_from_trajectory_calls,
)
from adapti_guard.evaluation.harness_v2.harness_v2_b3_pretarget_wrapper import (  # noqa: E402
    HarnessV2B3EpisodeContext,
    count_user_tool_messages,
)
from adapti_guard.evaluation.harness_v2.http_budget import HttpCompletionBudget  # noqa: E402
from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import (  # noqa: E402
    run_tools_episode_async,
)
from adapti_guard.evaluation.harness_v2.episode_wall_clock import EpisodeWallClock  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_rate_limit_retry import (  # noqa: E402
    HARNESS_RATE_LIMIT_BACKOFF_S,
)
from adapti_guard.evaluation.harness_v2.openrouter_async_attempt import (  # noqa: E402
    DEFAULT_HTTP_ATTEMPT_WALL_TIMEOUT_S,
)
from adapti_guard.evaluation.harness_v2.pilot_preflight import (  # noqa: E402
    pilot_scope_constants,
    preflight_pilot_plan,
)
from adapti_guard.evaluation.harness_v2.provider_probe import HARNESS_V2_TARGETS  # noqa: E402
from adapti_guard.evaluation.harness_v2.scenario_catalog import (  # noqa: E402
    ALL_SCENARIOS,
    ATTACK_SCENARIOS,
    build_mock_executor_config,
    exec_spec_for_instance,
    get_instance,
    load_templates,
    materialize_user_prompt,
    scenario_meta,
    templates_sha256,
)
from adapti_guard.evaluation.harness_v2.scenario_mock_executor import ScenarioMockToolExecutor  # noqa: E402
from adapti_guard.evaluation.harness_v2.trajectory_store import serialize_trajectory_call  # noqa: E402
from adapti_guard.evaluation.harness_v2.usage_tokens import reasoning_tokens_from_usage  # noqa: E402
from adapti_guard.evaluation.harness_v2.pilot_incremental_store import (  # noqa: E402
    PilotIncrementalStore,
    serialize_call_for_stream,
)
from adapti_guard.evaluation.harness_v2.run_manifest import write_pip_freeze, write_run_manifest  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop  # noqa: E402
from adapti_guard.evaluation.harness_v2.pilot_run_lock import PilotRunLock  # noqa: E402
from adapti_guard.evaluation.openrouter_panel_pricing import load_openrouter_pricing_table  # noqa: E402

PANEL = ROOT / "configs/models_q1_eval_panel.yaml"
HTTP_CAP = 640
USD_CAP = 0.05
MAX_ROUNDS = 4
PILOT_INSTANCES = (0, 1)
PREREG = "experiments/harness_v2/PREREG_HARNESS_V2_FULL.md"
CRITERIA = "experiments/harness_v2/PILOT2_CRITERIA_LOCKED.md"
PILOT_RUN_LABEL = "harness_v2_pilot_2"

MODEL_ORDER = ("qwen3", "gemma", "llama", "deepseek")
# reasoning-off $/HTTP for P5 estimate (Rev 2 prereg + reasoning smoke)
COST_PER_HTTP = {
    "qwen3": 0.0000649,
    "llama": 0.0000740,
    "gemma": 0.0000528,
    "deepseek": 0.0001530,
}
E_ROUNDS_PER_EPISODE = 2.43


from adapti_guard.evaluation.harness_v2.pilot_budget import PilotBudgetExceeded  # noqa: E402
from adapti_guard.evaluation.harness_v2.cancelled_timeout_reconcile import (  # noqa: E402
    reconcile_cancelled_timeout_rows,
)


def _cost_from_usage(usage: dict[str, Any], *, model_id: str, pricing: Any) -> float:
    if usage.get("cost") is not None:
        return float(usage["cost"])
    pt = usage.get("prompt_tokens")
    ct = usage.get("completion_tokens")
    if pt is not None and ct is not None:
        return pricing.cost_from_tokens(model_id, int(pt), int(ct))
    return 0.0


def pilot_episode_schedule() -> list[dict[str, Any]]:
    """Rotate by (scenario, instance) then model; A0 then B3 per model — not all models globally batched."""
    schedule = []
    for scenario_id in ALL_SCENARIOS:
        for inst in PILOT_INSTANCES:
            for family in MODEL_ORDER:
                for condition in ("A0", "B3"):
                    schedule.append(
                        {
                            "scenario_id": scenario_id,
                            "instance_index": inst,
                            "family": family,
                            "condition": condition,
                        }
                    )
    scope = pilot_scope_constants()
    if len(schedule) != scope["episodes_total"]:
        raise RuntimeError(f"schedule len {len(schedule)} != {scope['episodes_total']}")
    return schedule


def _episode_id(row: dict[str, Any]) -> str:
    return (
        f"{row['scenario_id']}/i{row['instance_index']}/"
        f"{row['family']}/{row['condition']}"
    )


def estimate_pilot_costs() -> dict[str, float]:
    scope = pilot_scope_constants()
    e_http = scope["episodes_total"] * E_ROUNDS_PER_EPISODE
    e_usd = 0.0
    worst_usd = 0.0
    for row in pilot_episode_schedule():
        c = COST_PER_HTTP[row["family"]]
        e_usd += E_ROUNDS_PER_EPISODE * c
        worst_usd += MAX_ROUNDS * c
    return {
        "expected_http": e_http,
        "worst_http": scope["http_cap"],
        "expected_usd": e_usd,
        "worst_usd": worst_usd,
    }


def run_pilot(
    out_dir: Path,
    *,
    resume: bool = False,
    usd_cap: float = USD_CAP,
    http_client: Any | None = None,
    schedule_override: list[dict[str, Any]] | None = None,
    wall_timeout_s: float | None = None,
    rate_limit_backoffs: tuple[float, ...] | None = None,
) -> dict[str, Any]:
    return run_harness_event_loop(
        lambda: run_pilot_async(
            out_dir,
            resume=resume,
            usd_cap=usd_cap,
            http_client=http_client,
            schedule_override=schedule_override,
            wall_timeout_s=wall_timeout_s,
            rate_limit_backoffs=rate_limit_backoffs,
        )
    )


async def run_pilot_async(
    out_dir: Path,
    *,
    resume: bool = False,
    usd_cap: float = USD_CAP,
    http_client: Any | None = None,
    schedule_override: list[dict[str, Any]] | None = None,
    wall_timeout_s: float | None = None,
    rate_limit_backoffs: tuple[float, ...] | None = None,
    loop_id_probe: list[int] | None = None,
    episode_wall_x_override: float | None = None,
    skip_preflight: bool = False,
    reconcile_at_end: bool = True,
) -> dict[str, Any]:
    return await _run_pilot_async(
        out_dir,
        resume=resume,
        usd_cap=usd_cap,
        http_client=http_client,
        schedule_override=schedule_override,
        wall_timeout_s=wall_timeout_s,
        rate_limit_backoffs=rate_limit_backoffs,
        loop_id_probe=loop_id_probe,
        episode_wall_x_override=episode_wall_x_override,
        skip_preflight=skip_preflight,
        reconcile_at_end=reconcile_at_end,
    )


async def _run_pilot_async(
    out_dir: Path,
    *,
    resume: bool = False,
    usd_cap: float = USD_CAP,
    http_client: Any | None = None,
    schedule_override: list[dict[str, Any]] | None = None,
    wall_timeout_s: float | None = None,
    rate_limit_backoffs: tuple[float, ...] | None = None,
    loop_id_probe: list[int] | None = None,
    episode_wall_x_override: float | None = None,
    skip_preflight: bool = False,
    reconcile_at_end: bool = True,
) -> dict[str, Any]:
    if not skip_preflight:
        preflight_pilot_plan(http_cap=HTTP_CAP, usd_cap=usd_cap, planned_http_cap=HTTP_CAP)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_run_manifest(
        out_dir,
        pilot=PILOT_RUN_LABEL,
        runner="scripts/run_harness_v2_pilot.py",
        resume=resume,
    )
    try:
        write_pip_freeze(out_dir)
    except (OSError, subprocess.CalledProcessError):
        pass
    store = PilotIncrementalStore(out_dir, usd_cap=usd_cap, http_cap=HTTP_CAP)
    store.reconcile_http_stream_from_ledger()
    store.log_progress(f"pilot_start out_dir={out_dir} resume={resume} pid={os.getpid()}")
    templates = load_templates()
    tpl_sha = templates_sha256()
    crit_sha = hashlib.sha256((ROOT / CRITERIA).read_bytes()).hexdigest()
    pricing = load_openrouter_pricing_table(PANEL)
    family_to_model = {fam: (mid, ck) for fam, mid, ck in HARNESS_V2_TARGETS}
    http_budget = HttpCompletionBudget(HTTP_CAP, initial_used=store.http_used())
    schedule = schedule_override if schedule_override is not None else pilot_episode_schedule()
    completed_ids = store.completed_episode_ids()
    episodes_out: list[dict[str, Any]] = []
    owns_http = http_client is None
    if http_client is None:
        import httpx

        http_client = httpx.AsyncClient()
    attempt_wall = wall_timeout_s if wall_timeout_s is not None else DEFAULT_HTTP_ATTEMPT_WALL_TIMEOUT_S
    backoffs = rate_limit_backoffs if rate_limit_backoffs is not None else HARNESS_RATE_LIMIT_BACKOFF_S
    if loop_id_probe is not None:
        import asyncio

        loop_id_probe.append(id(asyncio.get_running_loop()))
    if resume and store.episodes_jsonl.exists():
        for line in store.episodes_jsonl.read_text(encoding="utf-8").splitlines():
            if line.strip():
                episodes_out.append(json.loads(line))
    stop_point: dict[str, Any] | None = None
    stopped_reason = "completed"

    for slot, plan in enumerate(schedule):
        eid = _episode_id(plan)
        if eid in completed_ids:
            continue
        if store.usd_budget_exhausted() or store.http_budget_exhausted():
            stopped_reason = "budget_cap" if store.usd_budget_exhausted() else "http_cap"
            stop_point = {"schedule_index": slot, **plan, "episode_id": eid}
            for rest in schedule[slot:]:
                rid = _episode_id(rest)
                if rid in completed_ids:
                    continue
                episodes_out.append(
                    {"episode_id": rid, "status": "NOT_RUN", "reason": stopped_reason, **rest}
                )
            break

        scenario_id = plan["scenario_id"]
        inst = get_instance(scenario_id, plan["instance_index"], templates=templates)
        family = plan["family"]
        condition = plan["condition"]
        model_id, config_key = family_to_model[family]
        meta = scenario_meta(scenario_id)
        user_prompt = materialize_user_prompt(scenario_id, inst)
        exec_spec = exec_spec_for_instance(scenario_id, inst)
        executor = ScenarioMockToolExecutor(
            scenario_id=scenario_id,
            config=build_mock_executor_config(scenario_id, inst),
        )
        b3_ctx = HarnessV2B3EpisodeContext.for_condition(condition)

        def cost_fn(usage: dict[str, Any], *, model_id: str = model_id) -> float:
            return _cost_from_usage(usage, model_id=model_id, pricing=pricing)

        episode_attempt_id = str(uuid.uuid4())
        if resume and store.episode_has_active_http_rows(eid):
            store.mark_episode_rows_superseded(
                eid, superseded_by_attempt_id=episode_attempt_id
            )

        def on_http_record(rec: Any) -> None:
            if loop_id_probe is not None:
                import asyncio

                loop_id_probe.append(id(asyncio.get_running_loop()))
            ser = serialize_call_for_stream(rec, http_index=rec.call_index)
            store.append_http_call(
                episode_id=eid,
                record=rec,
                serialized=ser,
                episode_attempt_id=episode_attempt_id,
            )
            http_budget.used = store.http_used()
            store.log_progress(
                f"http call={rec.call_index} episode={eid} spent_usd={store.spent_usd()} "
                f"http_used={http_budget.used}"
            )
            if store.usd_budget_exhausted():
                raise PilotBudgetExceeded("usd_cap")

        store.log_progress(f"episode_begin {eid} attempt={episode_attempt_id}")
        try:
            wall = EpisodeWallClock(family)
            if episode_wall_x_override is not None and slot == len(schedule) - 1:
                wall.x_seconds = episode_wall_x_override
            traj = await run_tools_episode_async(
                scenario_id=scenario_id,
                model_id=model_id,
                config_key=config_key,
                system_prompt=meta["system_prompt"],
                initial_user=user_prompt,
                executor=executor,
                family=family,
                max_rounds=MAX_ROUNDS,
                http_budget=http_budget,
                pricing_cost_fn=cost_fn,
                pricing_table=pricing,
                b3_context=b3_ctx,
                on_http_record=on_http_record,
                http_client=http_client,
                wall_timeout_s=attempt_wall,
                rate_limit_backoffs=backoffs,
                episode_wall=wall,
            )
        except PilotBudgetExceeded:
            stopped_reason = "budget_cap"
            stop_point = {"schedule_index": slot, **plan, "episode_id": eid, "mid_episode": True}
            break

        serialized_calls = [
            serialize_trajectory_call(c, http_index=c.call_index) for c in traj.calls
        ]
        http_rows = http_rows_from_trajectory_calls(
            [
                {
                    "call_index": c.call_index,
                    "http_index": c.call_index,
                    "finish_reason": c.finish_reason,
                    "provider_error": c.provider_error,
                    "tool_calls": c.tool_calls,
                    "assistant_content": c.assistant_content,
                    "raw_response": c.raw_response,
                }
                for c in traj.calls
            ]
        )
        benign_meta = None
        if scenario_id.startswith("benign_"):
            benign_meta = {
                "allowlisted_email_to": inst.get("allowlisted_email_to"),
                "expected_create_kind": inst.get("expected_create_kind"),
            }
        c2 = classify_c2_episode(
            final_messages=traj.final_messages,
            mock_tool_log=traj.mock_tool_log,
            http_rows=http_rows,
            spec=exec_spec,
            scenario_id=scenario_id,
            instance_marker=str(inst.get("marker") or "") or None,
            http_calls=serialized_calls,
            benign_meta=benign_meta,
        )
        expected_defense = count_user_tool_messages(traj.final_messages) if condition == "B3" else 0
        episode_row = {
            "episode_id": eid,
            "status": "INVALID_TIMEOUT" if traj.invalid_timeout else "COMPLETE",
            **plan,
            "model_id": model_id,
            "exec_spec": None
            if exec_spec is None
            else {
                "tool_name": exec_spec.tool_name,
                "required_args": exec_spec.required_args,
                "body_marker": exec_spec.body_marker,
            },
            "C2": c2,
            "b3_log": traj.b3_log,
            "defense_fn_calls": b3_ctx.defense_fn_call_count,
            "expected_defense_fn_calls": expected_defense,
            "http_count": len(traj.calls),
            "calls": serialized_calls,
            "final_messages": traj.final_messages,
            "mock_tool_log": traj.mock_tool_log,
        }
        episodes_out.append(episode_row)
        store.write_episode_complete(episode_row)
        if store.usd_budget_exhausted():
            stopped_reason = "budget_cap"
            stop_point = {"schedule_index": slot + 1, "after_episode": eid, **plan}
            for rest in schedule[slot + 1 :]:
                rid = _episode_id(rest)
                if rid in completed_ids:
                    continue
                episodes_out.append(
                    {"episode_id": rid, "status": "NOT_RUN", "reason": stopped_reason, **rest}
                )
            break

    spent = store.spent_usd()
    led = store.ledger()
    estimates = estimate_pilot_costs()
    summary = {
        "pilot": PILOT_RUN_LABEL,
        "pilot_number": 2,
        "incremental_persistence": "amendment_6",
        "resume_policy": "amendment_7c_superseded_by_resume",
        "prereg": PREREG,
        "criteria_doc": CRITERIA,
        "criteria_doc_sha256": crit_sha,
        "templates_sha256": tpl_sha,
        "preflight": pilot_scope_constants(),
        "http_cap": HTTP_CAP,
        "usd_cap": usd_cap,
        "http_used": store.http_used(),
        "spent_usd": round(spent, 8),
        "billed_spent_usd": led.get("billed_spent_usd", round(spent, 8)),
        "analysis_spent_usd": led.get("analysis_spent_usd", round(spent, 8)),
        "billed_http_used": led.get("billed_http_used", store.http_used()),
        "analysis_http_used": led.get("analysis_http_used", store.http_used()),
        "stopped_reason": stopped_reason,
        "stop_point": stop_point,
        "cost_estimates": estimates,
        "episodes": episodes_out,
    }
    (out_dir / "pilot_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out_dir / "episodes.jsonl").write_text(
        "\n".join(json.dumps({k: v for k, v in ep.items() if k != "calls"}) for ep in episodes_out) + "\n",
        encoding="utf-8",
    )
    cum = 0.0
    lines = []
    idx = 0
    if store.http_stream_path.exists():
        for line in store.http_stream_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            c = json.loads(line)
            idx += 1
            u = c.get("usage") or {}
            cst = float(c.get("cost_usd") or 0.0)
            cum += cst
            rt = reasoning_tokens_from_usage(u)
            lines.append(
                {
                    "call_index": idx,
                    "episode_id": c.get("episode_id"),
                    "role": "target",
                    "model_id": c.get("model_id"),
                    "prompt_tokens": u.get("prompt_tokens"),
                    "completion_tokens": u.get("completion_tokens"),
                    "reasoning_tokens": rt if rt is not None else 0,
                    "cost_usd": cst,
                    "cumulative_usd": cum,
                }
            )
    (out_dir / "cost_log.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8")
    (out_dir / "cost_summary.json").write_text(
        json.dumps(
            {
                "api_calls": store.http_used(),
                "spent_usd": round(spent, 8),
                "cap_usd": usd_cap,
                "http_cap": HTTP_CAP,
                "stopped_reason": stopped_reason,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    store.log_progress(f"pilot_finalize spent_usd={spent} http_used={store.http_used()} reason={stopped_reason}")
    if owns_http:
        await http_client.aclose()
    if reconcile_at_end:
        # Reconciliation disabled unless live generation lookup + per-attempt key windows are supplied.
        reconcile_cancelled_timeout_rows(
            out_dir,
            generation_cost_lookup=lambda _gid: None,
            attempt_key_windows={},
        )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--resume", action="store_true", help="Resume into existing out-dir")
    parser.add_argument(
        "--usd-cap",
        type=float,
        default=USD_CAP,
        help="Soft USD cap checked after each HTTP (default 0.05)",
    )
    args = parser.parse_args()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = args.out_dir or (ROOT / "experiments/harness_v2" / f"HARNESS_V2_PILOT_{ts}")
    if not out.is_absolute():
        out = ROOT / out
    lock = None
    try:
        lock = PilotRunLock.try_acquire(out_dir=out, pilot_label=PILOT_RUN_LABEL)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    async def _async_pilot_main() -> dict[str, Any]:
        return await run_pilot_async(out, resume=args.resume, usd_cap=args.usd_cap)

    try:
        summary = run_harness_event_loop(_async_pilot_main)
    finally:
        if lock is not None:
            lock.release()
    summary["out_dir"] = str(out.relative_to(ROOT))
    print(json.dumps({k: summary[k] for k in summary if k != "episodes"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
