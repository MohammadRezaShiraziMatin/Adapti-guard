#!/usr/bin/env python3
"""Execute owner-authorized Q1 P1_rq1_primary_j1_j2 live phase only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from adapti_guard.evaluation.q1_p1_live_runner import fetch_openrouter_key_snapshot, run_q1_p1_live


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Pack directory under experiments/real_llm_eval/",
    )
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    root = args.output_root or Path(f"experiments/real_llm_eval/Q1_P1_RQ1_{stamp}")
    root.mkdir(parents=True, exist_ok=True)
    or_before = fetch_openrouter_key_snapshot()
    (root / "openrouter_key_before.json").write_text(
        __import__("json").dumps(or_before, indent=2),
        encoding="utf-8",
    )
    summary = run_q1_p1_live(root, repo_root=Path("."), openrouter_before=or_before)
    print(summary.get("stop_reason"))
    print(f"episodes_completed={summary.get('episodes_completed')}")
    print(f"spent_usd={summary.get('ledger', {}).get('spent_usd')}")
    print(f"pack={root}")


if __name__ == "__main__":
    main()
