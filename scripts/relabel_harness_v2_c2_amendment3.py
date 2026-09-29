#!/usr/bin/env python3
"""Offline C2 relabel for harness v2 smokes under Amendment 3 (no API)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.c2_episode_state import (  # noqa: E402
    classify_c2_episode,
    http_rows_from_trajectory_calls,
)

RUN_DIRS = [
    ROOT / "experiments/harness_v2/HARNESS_V2_SMOKE_20260927-124451",
    ROOT / "experiments/harness_v2/HARNESS_V2_SMOKE2_20260927-125041",
    ROOT / "experiments/harness_v2/HARNESS_V2_SMOKE2_20260927-125200",
    ROOT / "experiments/harness_v2/HARNESS_V2_SMOKE3_20260927-131707",
]

ATTACK_SCENARIO = "indirect_tool_injection_v1"


def _old_label(run_dir: Path, family: str, summary: dict[str, Any] | None) -> str | None:
    if not summary:
        return None
    if "per_model_C2_state" in summary:
        return (summary.get("per_model_C2_state") or {}).get(family)
    if "per_model_C2_detail" in summary:
        d = (summary.get("per_model_C2_detail") or {}).get(family) or {}
        return d.get("C2_state")
    if "per_model_criteria" in summary:
        d = (summary.get("per_model_criteria") or {}).get(family) or {}
        return d.get("C2_attack_outcome_valid")
    return None


def relabel_run(run_dir: Path) -> dict[str, Any]:
    traj_path = run_dir / "trajectories.json"
    summary_path = run_dir / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else None
    trajectories = json.loads(traj_path.read_text())
    rows_out: list[dict[str, Any]] = []

    for block in trajectories:
        scenario = block.get("scenario_id")
        if scenario != ATTACK_SCENARIO:
            continue
        family = block.get("family") or block.get("target_family")
        calls = block.get("calls") or []
        http_rows = http_rows_from_trajectory_calls(calls)
        new = classify_c2_episode(
            final_messages=block.get("final_messages") or [],
            mock_tool_log=block.get("mock_tool_log") or [],
            http_rows=http_rows,
        )
        old = _old_label(run_dir, family, summary)
        if old is None and family == "llama" and "SMOKE_20260927-124451" in str(run_dir):
            old = "legacy_call6_text_claim_only"
        rows_out.append(
            {
                "run_dir": str(run_dir.relative_to(ROOT)),
                "model_family": family,
                "scenario_id": scenario,
                "old_C2_label": old,
                "new_C2_state": new["C2_state"],
                "text_claim_candidate": new["text_claim_candidate"],
                "explicit_refusal": new["explicit_refusal"],
                "exec_success": new.get("exec_success"),
                "reason": new.get("delivery_detail") or new.get("precedence") or "amendment3_full_trajectory",
                "amendment3_detail": new,
            }
        )

    payload = {
        "amendment": 3,
        "prereg": "experiments/harness_v2/PREREG_HARNESS_V2.md",
        "episodes": rows_out,
    }
    out_path = run_dir / "C2_RELABEL_AMENDMENT3.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    for d in RUN_DIRS:
        if not d.exists():
            print("skip missing", d)
            continue
        relabel_run(d)
        print("wrote", d / "C2_RELABEL_AMENDMENT3.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
