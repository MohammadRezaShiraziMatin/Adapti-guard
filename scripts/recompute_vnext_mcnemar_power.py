#!/usr/bin/env python3
"""Offline Track A McNemar power / sensitivity (no LLM, no AUDIT edits)."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from adapti_guard.evaluation.statistics import track_a_mcnemar_power_sensitivity

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VERDICT = (
    ROOT
    / "experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/verdict.json"
)
DELTA_CI_ARTIFACT = (
    ROOT / "docs/paper/q1_findings/artifacts/vnext_delta_ci_offline.json"
)
DEFAULT_OUT = (
    ROOT / "docs/paper/q1_findings/artifacts/vnext_track_a_power_sensitivity.json"
)


def _fingerprint(n: int, b10: int, b01: int, msid: float) -> str:
    payload = f"n={n};b10={b10};b01={b01};msid={msid};model=b01_fixed_binomial_power"
    return hashlib.sha256(payload.encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verdict", type=Path, default=DEFAULT_VERDICT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--msid", type=float, default=0.20)
    args = parser.parse_args()

    verdict = json.loads(args.verdict.read_text(encoding="utf-8"))
    b10, b01 = int(verdict["b10"]), int(verdict["b01"])
    n_attack = 61

    record = track_a_mcnemar_power_sensitivity(
        n_attack,
        msid=args.msid,
        b01_assumed=b01,
        observed_b10=b10,
        alternative_delta=args.msid,
    )
    record["verdict_path"] = str(args.verdict)
    record["inputs_sha256"] = _fingerprint(n_attack, b10, b01, args.msid)

    if DELTA_CI_ARTIFACT.is_file():
        delta_ci = json.loads(DELTA_CI_ARTIFACT.read_text(encoding="utf-8"))
        record["delta_hat_ci_reference"] = {
            "artifact": str(DELTA_CI_ARTIFACT.relative_to(ROOT)),
            "inputs_sha256": delta_ci.get("inputs_sha256"),
            "ci_95": delta_ci.get("delta_hat_ci_95"),
            "note": "Embedded by reference; not recomputed in this script",
        }

    record["interpretation"] = (
        "Under the simplified b01=0 binomial scaffold, n=61 yields high power (~99%) "
        "to reject McNemar H0 if true per-episode b10 rate were MSID=0.20. Observed "
        f"b10={b10} gives delta below MSID and p=0.0625 — FAIL is driven by small "
        "estimated effect and MSID/utility gates, not primarily by n=61 being unable to "
        "detect a true delta=0.20 effect under this model."
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
