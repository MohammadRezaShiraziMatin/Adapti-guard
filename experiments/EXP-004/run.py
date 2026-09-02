#!/usr/bin/env python3
"""EXP-004: Publication-grade real-LLM evaluation on frozen eval_v1.

Paired B0 vs B6 across three required OpenRouter models.

Usage:
    python experiments/EXP-004/run.py
    python experiments/EXP-004/run.py --skip-existing
    python experiments/EXP-004/analyze.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.env_loader import load_project_env

load_project_env()

from src.adapti_guard.experiments.multi_model_eval import (
    DEFAULT_TARGET_KEYS,
    MultiModelConfig,
    run_multi_model_evaluation,
)
from src.adapti_guard.experiments.real_llm_pipeline import EvaluationBackend


def main() -> int:
    parser = argparse.ArgumentParser(description="EXP-004 frozen eval real LLM experiment")
    parser.add_argument("--n-samples", type=int, default=150)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--targets", nargs="*", default=None)
    args = parser.parse_args()

    output = ROOT / "experiments" / "EXP-004"
    config = MultiModelConfig(
        experiment_id="EXP-004",
        output_dir=output,
        target_keys=args.targets or list(DEFAULT_TARGET_KEYS),
        backend=EvaluationBackend.OPENROUTER,
        baselines=["B0", "B6"],
        n_samples=args.n_samples,
        seed=args.seed,
        use_frozen_eval=True,
        frozen_dataset="datasets/frozen/eval_v1/dataset.jsonl",
        reference_baseline="B0",
        treatment_baseline="B6",
        skip_existing=args.skip_existing,
        publication_mode=True,
        cache_enabled=False,
    )

    result = run_multi_model_evaluation(config)
    print(json.dumps(result, indent=2))

    if result.get("status") in ("COMPLETED", "PARTIAL"):
        subprocess.run(
            [sys.executable, str(ROOT / "experiments" / "EXP-004" / "analyze.py")],
            check=False,
        )
    return 0 if result.get("status") == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
