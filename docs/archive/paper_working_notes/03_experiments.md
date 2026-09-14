# Experiments

## Simulation (harmonized)

- Entry: `scripts/run_q1_harmonized_v1.py`
- Artifacts: `results/phase8/q1_harmonized_v1/`
- Population: 100 episodes, W1 schedule (75 attack / 25 legitimate), seed 42
- Mode label: `LEGACY_SIMULATION_ONLY` for outcome semantics tied to detector/defense

## Sensitivity

- Threshold and workload sweeps: `results/phase8/q1_threshold_sensitivity_v1/`, `q1_workload_sensitivity_v1/`

## Real LLM

- Primary runner: `experiments/REAL_LLM_EVAL/`
- Phase 5 constrained Targets: `experiments/PHASE5_CONSTRAINED/` (300 Groq Target observations; judge historically incomplete)
- Mixed attack+benign: may be partial under rate limits — see `experiments/REAL_LLM_EVAL_MIXED_STATUS.json`

## Ablations

- Config: `configs/experiments/ablation_study.yaml`
- Historical EXP-006 metrics may be simulation-only — do not cite as real-LLM evidence without checking `evaluation_mode`
