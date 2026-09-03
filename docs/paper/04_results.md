# Results

Only values present in repository artifacts are listed. Missing cells are omitted, not invented.

## Harmonized simulation summaries

| Method | ASR | Defense Rate | Utility | Cost |
|---|---:|---:|---:|---:|
| fixed_l0 | 1.000 | 0.000 | 1.000 | 0.000 |
| fixed_l1 | 0.000 | 1.000 | 1.000 | 0.100 |
| fixed_l2 | 1.000 | 0.000 | 1.000 | 0.250 |
| fixed_l3 | 0.000 | 1.000 | 0.000 | 0.500 |
| full_adaptive | 0.027 | 0.973 | 1.000 | 0.379 |
| escalation_only | 0.027 | 0.973 | 1.000 | 0.379 |
| de_escalation_only | 0.013 | 0.987 | 1.000 | 0.082 |
| no_cost_gate | 0.333 | 0.667 | 1.000 | 0.318 |

> Simulation outcomes — not independent LLM-judge ASR.

## REAL_LLM_EVAL aggregate

```json
{
  "evaluation_mode": "real_llm_judge",
  "status": "COMPLETED"
}
```

## REAL_LLM_EVAL B0

```json
{
  "asr": 0.05,
  "defense_rate": 0.95,
  "utility": null,
  "fpr": null,
  "defense_cost": 0.0,
  "n_attack": 20,
  "n_benign": 0,
  "n_judge_errors": 0,
  "evaluation_mode": "real_llm_judge",
  "baseline": "B0"
}
```

## Mixed real-LLM status

- Status: `ABORTED_PARTIAL`
- Reason: Groq rate limit / API connection errors during mixed attack+benign real-LLM evaluation; process was aborted before B2_L2 completion and before B2_L3/B3.
