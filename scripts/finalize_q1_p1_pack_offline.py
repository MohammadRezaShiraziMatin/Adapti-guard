#!/usr/bin/env python3
"""Finalize Q1 P1 pack from episodes.jsonl only (no target/judge API calls)."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from adapti_guard.evaluation.live_budget_gate import BudgetLedger
from adapti_guard.evaluation.q1_cost_preflight import estimate_q1_phase_preflight
from adapti_guard.evaluation.q1_evaluation_contract import load_q1_contract
from adapti_guard.evaluation.q1_p1_live_runner import (
    PHASE_ID,
    _post_run_analysis,
    fetch_openrouter_key_snapshot,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pack_dir", type=Path)
    parser.add_argument("--stop-reason", default="process_incomplete_offline_finalize")
    parser.add_argument("--run-incomplete", action="store_true")
    args = parser.parse_args()
    pack = args.pack_dir.resolve()
    repo = Path(".").resolve()
    episodes_path = pack / "episodes.jsonl"
    if not episodes_path.is_file():
        raise SystemExit(f"missing {episodes_path}")

    rows = [json.loads(l) for l in episodes_path.read_text().splitlines() if l.strip()]
    contract = load_q1_contract(repo / "configs/q1_evaluation_contract.yaml")
    preflight = estimate_q1_phase_preflight(contract, repo_root=repo)
    import yaml

    auth = yaml.safe_load((repo / "docs/research/live_budget_authorization.yaml").read_text())
    spent = float(rows[-1].get("ledger_spent_usd_after", 0)) if rows else 0.0
    ledger = BudgetLedger(hard_stop=True, max_usd=2.0)
    ledger.spent_usd = spent
    ledger.requests_used = int(rows[-1].get("ledger_requests_after", 0)) if rows else 0

    stop = args.stop_reason
    if args.run_incomplete:
        stop = "INCOMPLETE_RUN_PROCESS_DIED"

    p1_pref = next(
        (p for p in preflight.get("phases", []) if p.get("phase_id") == PHASE_ID),
        {},
    )
    post = _post_run_analysis(
        episodes_path,
        repo_root=repo,
        stop_reason=stop,
        planned_episodes=488,
        ledger_spent_usd=spent,
        preflight_worst_usd=float(p1_pref.get("worst_case_usd_estimate", 0)),
    )
    before_path = pack / "openrouter_key_before.json"
    before = json.loads(before_path.read_text()) if before_path.is_file() else {}
    after = fetch_openrouter_key_snapshot()
    delta = {
        "before": before,
        "after": after,
        "usage_delta_usd": float(after.get("usage") or 0) - float(before.get("usage") or 0),
        "ledger_spent_usd": spent,
    }
    (pack / "budget_ledger.json").write_text(json.dumps(ledger.to_dict(), indent=2))
    (pack / "openrouter_usage_delta.json").write_text(json.dumps(delta, indent=2))
    (pack / "preflight_vs_actual.json").write_text(
        json.dumps(
            {
                "preflight": preflight,
                "actual_spent_usd": spent,
                "actual_episodes": len(rows),
                "stop_reason": stop,
            },
            indent=2,
        )
    )
    summary = {
        "phase_id": PHASE_ID,
        "stop_reason": stop,
        "episodes_planned": 488,
        "episodes_completed": len(rows),
        "ledger": ledger.to_dict(),
        "preflight_estimate": preflight,
        "post_analysis": post,
        "openrouter_usage_delta": delta,
        "authorization": {
            "contract_sha256": auth.get("contract_sha256"),
            "manifest_sha256": auth.get("manifest_sha256"),
            "code_git_commit": auth.get("code_git_commit"),
        },
    }
    (pack / "run_summary.json").write_text(json.dumps(summary, indent=2))
    (pack / "AUDIT.json").write_text(
        json.dumps(
            {
                "verdict": post.get("audit_verdict"),
                "reasons": post.get("audit_reasons"),
                "phase_id": PHASE_ID,
                "episodes_completed": len(rows),
                "episodes_planned": 488,
                "stop_reason": stop,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
