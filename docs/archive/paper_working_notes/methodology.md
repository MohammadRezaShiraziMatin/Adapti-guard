# Methodology

## Threat model

Untrusted user/RAG/tool text may override instructions (prompt injection, jailbreak, roleplay,
context/RAG injection). The defender applies a discrete intervention before the Target LLM.

## Baselines

| ID | Role | Mechanism |
|----|------|-----------|
| B0 | No defense | Pass-through |
| B1 | Simple | Rule/regex detector → block if score ≥ threshold |
| B2_L1 | Layered | Fixed defense level 1 (sanitize) |
| B2_L2 | Layered | Fixed level 2 (tool restriction) |
| B2_L3 | Layered | Fixed level 3 (block) |
| B3 | Adaptive | Risk + feedback updates level over episodes |

## Pipeline

```
prompt → defense(Bi) → Target LLM → Judge LLM → metrics
```

ASR is taken **only** from the judge (or blocked-by-defense ⇒ attack failure), never from
simulation regex outcomes in `real_llm_judge` mode. Judge/API failures are **excluded** from
ASR/utility denominators and counted as `n_judge_errors`.

## Dataset

`datasets/benchmark_q1` (train/validation/test). Mixed evaluation uses seeded sampling:

```bash
PYTHONPATH=. python experiments/REAL_LLM_EVAL/run.py \
  --backend groq --target groq_target --judge groq_judge \
  --attack-n 20 --benign-n 20 --seed 42
```

Attack-only smoke (`--n-samples 20`) remains supported for quick security pilots.

## Metrics

Security: ASR, Defense Rate, FNR, Precision/Recall/F1 (when benign present), bootstrap 95% CI.
Utility: benign success rate, FPR, balanced accuracy, reward `0.5·sec + 0.4·util − 0.1·cost`.
Robustness: per-category ASR; families jailbreak / prompt_injection / role_attack / context_attack.
Efficiency: latency mean/p95, token totals, optional USD estimate.

## Reproducibility

Each experiment run under `results/experiment_runs/` stores `environment.json`,
`model_config.json`, `config.json`, `dataset_manifest.json`, `git_commit.txt`, and metrics.
