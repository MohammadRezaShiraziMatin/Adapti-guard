#!/usr/bin/env python3
"""Offline recompute: Track A VNEXT delta_hat 95% CI from McNemar contingency.

Reads b10, b01, n_attack from the official VNEXT verdict.json by default.
Does not call LLM APIs. Does not modify AUDIT.md or frozen packs.

Authority for b10/b01/n: experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from adapti_guard.evaluation.statistics import (
    delta_hat_ci_bootstrap_from_mcnemar_contingency,
    delta_hat_from_mcnemar_contingency,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VERDICT = (
    ROOT
    / "experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/verdict.json"
)
DEFAULT_OUT = ROOT / "docs/paper/q1_findings/artifacts/vnext_delta_ci_offline.json"


def _inputs_fingerprint(b10: int, b01: int, n_attack: int, seed: int) -> str:
    payload = f"b10={b10};b01={b01};n_attack={n_attack};seed={seed};method=bootstrap5000"
    return hashlib.sha256(payload.encode()).hexdigest()


def load_contingency(verdict_path: Path) -> tuple[int, int, int]:
    data = json.loads(verdict_path.read_text(encoding="utf-8"))
    b10 = int(data["b10"])
    b01 = int(data["b01"])
    # n_attack not in verdict; fixed by AUDIT n_scorable_attack = 61
    n_attack = 61
    return b10, b01, n_attack


def build_record(
    b10: int,
    b01: int,
    n_attack: int,
    *,
    seed: int = 42,
    n_bootstrap: int = 5000,
    verdict_path: Path | None,
) -> dict:
    point = delta_hat_from_mcnemar_contingency(b10, b01, n_attack)
    ci = delta_hat_ci_bootstrap_from_mcnemar_contingency(
        b10, b01, n_attack, n_bootstrap=n_bootstrap, seed=seed
    )
    return {
        "label": "recomputed_offline_not_in_original_AUDIT",
        "estimand": "delta_hat = (b10 - b01) / n_attack",
        "audit_path": "experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md",
        "verdict_path": str(verdict_path) if verdict_path else None,
        "inputs": {"b10": b10, "b01": b01, "n_attack": n_attack},
        "delta_hat_point": round(point, 10),
        "delta_hat_ci_95": {
            "lower": round(float(ci["ci_lower"]), 6),
            "upper": round(float(ci["ci_upper"]), 6),
            "method": ci["method"],
            "n_bootstrap": n_bootstrap,
            "seed": seed,
        },
        "inputs_sha256": _inputs_fingerprint(b10, b01, n_attack, seed),
        "note": (
            "Official AUDIT reports delta_hat point only; this JSON is a post-hoc "
            "offline interval from frozen McNemar integers."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verdict", type=Path, default=DEFAULT_VERDICT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--b10", type=int, default=None)
    parser.add_argument("--b01", type=int, default=None)
    parser.add_argument("--n-attack", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-bootstrap", type=int, default=5000)
    args = parser.parse_args()

    if args.b10 is not None and args.b01 is not None and args.n_attack is not None:
        b10, b01, n_attack = args.b10, args.b01, args.n_attack
        verdict_path = None
    else:
        b10, b01, n_attack = load_contingency(args.verdict)
        verdict_path = args.verdict

    record = build_record(
        b10,
        b01,
        n_attack,
        seed=args.seed,
        n_bootstrap=args.n_bootstrap,
        verdict_path=verdict_path,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
