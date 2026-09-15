# Statistical Protocol

## Unit of analysis

| Experiment | Primary unit |
|------------|--------------|
| EXP-002 (detector) | labeled prompt |
| EXP-003–006 (E2E) | episode (one prompt through defense → target → judge) |
| EXP-004 (cross-model) | episode × model (report per model; do not pool as independent) |
| EXP-009 (latency) | request |

**Rule:** Multiple judge calls on the same prompt are **not** independent observations.

## Seeds

Recommended: 42, 123, 2024, 31415, 271828

If `temperature=0` and API is deterministic, repeated identical calls are **not** independent samples — document accordingly.

## Methods (implemented in `statistics.py`)

- 95% bootstrap CI for proportions/means (`n_bootstrap=5000`)
- McNemar exact test for paired binary outcomes (method A vs B on same prompts)
- Wilcoxon signed-rank for paired continuous metrics

## Multiple comparisons

Apply Holm correction when comparing >1 baseline against adaptive policy.

## Reporting

Always report: N, point estimate, 95% CI, p-value (if tested), effect direction.

If p ≥ 0.05: state **not statistically significant**.

Status: helpers implemented; **EXP-004 multi-model analysis ready**; no valid experiment results yet.
