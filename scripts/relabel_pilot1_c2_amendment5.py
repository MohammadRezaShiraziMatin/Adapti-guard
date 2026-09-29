#!/usr/bin/env python3
"""Offline C2 relabel for pilot 1 pack under Amendment 5 (no API)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.c2_episode_state import (  # noqa: E402
    classify_c2_episode,
    http_rows_from_trajectory_calls,
)
from adapti_guard.evaluation.harness_v2.scenario_catalog import ATTACK_SCENARIOS  # noqa: E402

PILOT1 = ROOT / "experiments/harness_v2/HARNESS_V2_PILOT_20260927-135005"


def main() -> int:
    summary = json.loads((PILOT1 / "pilot_summary.json").read_text())
    rows = []
    for ep in summary.get("episodes", []):
        if ep.get("status") != "COMPLETE":
            continue
        calls = ep.get("calls") or []
        traj_path = PILOT1 / "trajectories" / f"{ep['episode_id'].replace('/', '_')}.json"
        if traj_path.exists() and not calls:
            blob = json.loads(traj_path.read_text())
            calls = blob.get("calls") or []
        http_rows = http_rows_from_trajectory_calls(calls)
        spec = ep.get("exec_spec")
        from adapti_guard.evaluation.harness_v2.exec_success import ExecSuccessSpec

        exec_spec = None
        if spec:
            exec_spec = ExecSuccessSpec(
                tool_name=spec["tool_name"],
                required_args=spec.get("required_args") or {},
                body_marker=spec.get("body_marker"),
            )
        marker = (spec or {}).get("body_marker")
        new = classify_c2_episode(
            final_messages=ep.get("final_messages") or [],
            mock_tool_log=ep.get("mock_tool_log") or [],
            http_rows=http_rows,
            spec=exec_spec,
            scenario_id=ep.get("scenario_id"),
            instance_marker=marker,
            http_calls=calls,
            benign_meta={
                "allowlisted_email_to": None,
                "expected_create_kind": None,
            }
            if ep.get("scenario_id", "").startswith("benign_")
            else None,
        )
        old = (ep.get("C2") or {}).get("C2_state")
        rows.append(
            {
                "episode_id": ep["episode_id"],
                "scenario_id": ep.get("scenario_id"),
                "family": ep.get("family"),
                "condition": ep.get("condition"),
                "old_C2_state": old,
                "new_C2_state": new["C2_state"],
                "delivery_detail": new.get("delivery_detail"),
                "delivery_evidence": new.get("delivery_evidence"),
                "benign_valid": new.get("benign_valid"),
                "amendment5_detail": new,
            }
        )

    out = {
        "amendment": 5,
        "source_pilot_dir": str(PILOT1.relative_to(ROOT)),
        "source_pilot_commit": "1af54c1",
        "note": "Relabel only; pilot 1 artifacts untouched except new JSON file.",
        "episodes": rows,
    }
    path = PILOT1 / "C2_RELABEL_AMENDMENT5.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", path, "n=", len(rows))
    poisoned = [r for r in rows if r["scenario_id"] == "poisoned_benign_tool_v1"]
    print("poisoned sample new states:", {r["episode_id"]: r["new_C2_state"] for r in poisoned[:4]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
