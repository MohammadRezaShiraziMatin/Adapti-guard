"""Exploratory four-arm harness_v2 run (A0, B3, CORE, TOOLDENY). NOT confirmatory.

Default mode prints the plan and makes no network call. A live run additionally needs
``--live``, ``--approved-usd-cap`` (owner budget sign-off) and a clean worktree.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.exploratory_schedule import (  # noqa: E402
    EXPLORATORY_ARMS,
    OPTIONAL_ARMS,
    exploratory_plan,
    exploratory_schedule,
    independent_screening_schedule,
)

MAX_USD_CAP = 0.20


def _load_pilot_runner():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot", ROOT / "scripts" / "run_harness_v2_pilot.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--k-attack", type=int, default=None, help="default 12 (exploratory) or 8 (independent-screen)")
    p.add_argument("--k-benign", type=int, default=5)
    p.add_argument("--arms", default=",".join(EXPLORATORY_ARMS), help="Comma list, e.g. A0,ARGALLOW")
    p.add_argument(
        "--scenario-set",
        choices=("exploratory", "independent-screen"),
        default="exploratory",
        help="independent-screen: A0-only screening of the independent attack set (Amendment 10 s5)",
    )
    p.add_argument("--live", action="store_true", help="Send real HTTP requests (needs approval flag)")
    p.add_argument(
        "--approved-usd-cap",
        type=float,
        default=None,
        help=f"Owner-approved soft USD cap (max {MAX_USD_CAP}); required with --live",
    )
    p.add_argument("--pilot-label", default="harness_v2_pilot_9001")
    p.add_argument("--out-dir", type=Path, default=None)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    if args.k_attack is None:
        args.k_attack = 8 if args.scenario_set == "independent-screen" else 12
    arms = tuple(a.strip().upper() for a in args.arms.split(",") if a.strip())
    unknown = set(arms) - set(EXPLORATORY_ARMS) - set(OPTIONAL_ARMS)
    if unknown:
        print(f"refused: unknown arms {sorted(unknown)}", file=sys.stderr)
        return 1
    runner = _load_pilot_runner()
    if args.scenario_set == "independent-screen":
        sched = independent_screening_schedule(k=args.k_attack, arms=("A0",))
        n = len(sched)
        plan = {
            "episodes": n,
            "arms": ["A0"],
            "scenario_set": "independent-screen",
            "http_cap": n * runner.MAX_ROUNDS,
            "expected_usd_pilot3_rate": round(n * 0.03454372 / 160, 4),
        }
    else:
        sched = None
        plan = exploratory_plan(
            max_rounds=runner.MAX_ROUNDS, k_attack=args.k_attack, k_benign=args.k_benign, arms=arms
        )
    print(json.dumps({"plan": plan, "max_usd_cap": MAX_USD_CAP}, indent=2))
    if not args.live:
        return 0
    if args.approved_usd_cap is None or not (0 < args.approved_usd_cap <= MAX_USD_CAP):
        print(
            f"refused: --live needs --approved-usd-cap in (0, {MAX_USD_CAP}]", file=sys.stderr
        )
        return 1
    if plan["expected_usd_pilot3_rate"] > args.approved_usd_cap:
        print("refused: expected cost exceeds approved cap", file=sys.stderr)
        return 1
    if runner.is_worktree_dirty(ROOT):
        print("refused: runner worktree is dirty", file=sys.stderr)
        return 3
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = args.out_dir or (ROOT / "experiments/harness_v2" / f"HARNESS_V2_EXPLORATORY_{ts}")
    if not out.is_absolute():
        out = ROOT / out
    schedule = sched if sched is not None else exploratory_schedule(k_attack=args.k_attack, k_benign=args.k_benign, arms=arms)

    async def _go():
        return await runner.run_pilot_async(
            out,
            pilot_label=args.pilot_label,
            usd_cap=args.approved_usd_cap,
            schedule_override=schedule,
            skip_preflight=True,
            http_cap_override=plan["http_cap"],
        )

    summary = runner.run_harness_event_loop(_go)
    print(json.dumps({k: v for k, v in summary.items() if k != "episodes"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
