# Results Analysis

Generated: 2026-09-03T23:13:51.742006+00:00

## Source artifacts

- Attack-only: `experiments/REAL_LLM_EVAL/` (reference run `results/experiment_runs/REAL-LLM-EVAL/RUN-20260903-225156-b46b86`)
- Mixed (when present): `experiments/REAL_LLM_EVAL_MIXED/`
- Tables: `results/tables/baseline_comparison.csv`
- Attack-only table: `results/tables/baseline_comparison_attack_only.csv`
- Figures: `results/figures/`

## Headline (merged — prefer mixed when available)

| Baseline | Mode | ASR | Defense | Utility | FPR | Reward | N_a | N_b |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| B0 | mixed | 0.000 | 1.000 | 0.700 | 0.300 | 0.640 | 20 | 20 |
| B1 | mixed | 0.000 | 1.000 | 0.700 | 0.300 | 0.639 | 20 | 20 |
| B2_L1 | attack_only | 0.050 | 0.950 | N/A | N/A | N/A | 20 | 0 |
| B2_L2 | attack_only | 0.050 | 0.950 | N/A | N/A | N/A | 20 | 0 |
| B2_L3 | attack_only | 0.050 | 0.950 | N/A | N/A | N/A | 20 | 0 |
| B3 | attack_only | 0.050 | 0.950 | N/A | N/A | N/A | 20 | 0 |

## Attack-only comparison (complete B0–B3, n=20 attacks)

| Baseline | ASR | Defense Rate | Judge errors |
|---|---:|---:|---:|
| B0 | 0.050 | 0.950 | 0 |
| B1 | 0.050 | 0.950 | 0 |
| B2_L1 | 0.050 | 0.950 | 0 |
| B2_L2 | 0.050 | 0.950 | 0 |
| B2_L3 | 0.050 | 0.950 | 0 |
| B3 | 0.050 | 0.950 | 0 |

## Interpretation

- On the attack-only Groq run, **ASR ≈ 0.05** for every baseline including B0. The Target
  model itself refuses most sampled attacks; layered/adaptive defenses show **no ASR separation**
  on this 20-sample pilot.
- Mixed eval (available for some baselines): enables utility,
  FPR, balanced accuracy, and reward. Early mixed B0/B1 show ASR=0.0 with utility≈0.7 (FPR≈0.3)
  on seed=42, 20+20 samples — still underpowered for superiority claims.
- Do **not** claim B3 superiority from current real-LLM numbers; use them as methodology validation.
- Latency near 0 ms in attack-only artifacts indicates **cache hits**; mixed B0 shows real wall-clock
  (~7.5 s mean). Prefer non-cache latency for efficiency claims.
- Prefer a **distinct judge** from the Target for publication independence.

## Category robustness (B0, merged source)

- `adaptive_attacks`: n=3, ASR=0.000
- `agent_tool_injection`: n=1, ASR=0.000
- `indirect_prompt_injection`: n=3, ASR=0.000
- `jailbreak`: n=9, ASR=0.000
- `rag_injection`: n=4, ASR=0.000

## What would strengthen the paper

1. Finish mixed eval for B2_L1–B3 under the same seed (utility–security Pareto).
2. Distinct judge model; disable cache for latency studies.
3. Larger n and multi-seed runs for CI stability.
4. Stronger / adaptive attack strata where Target refusal is not near-ceiling.
