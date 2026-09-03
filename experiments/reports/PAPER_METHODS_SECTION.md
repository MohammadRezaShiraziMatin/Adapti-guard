# Methods (paper-ready; executed protocol)

## Dataset

Primary evaluation used the frozen attack-only set `datasets/frozen/eval_v1/dataset.jsonl` (SHA-256 `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24`), 770 labeled attacks in seven categories. The Phase 5 run evaluated a seed-42 subsample of 50 episode IDs. The attack stream hash is `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47`.

No benign tasks were included in this primary run. False-positive rate and utility were not defined.

## Target

All Target generations used Groq, model `openai/gpt-oss-120b`, temperature 0, max_tokens 512, `reasoning_effort=low`. Configuration key: `groq_target`.

## Policies

B0 applied no intervention (A0, cost 0.00). B6 invoked the full adaptive factory also registered as B3. Intervention costs were A0=0.00, A1=0.10, A2=0.25, A3=0.50.

## Judge

The independent judge was specified as Cerebras `qwen-3.8-27b` with structured JSON (`attack_success`, `defense_success`, `confidence`, `reason`, `category`, `invalid`). Validation failed (HTTP 402); mass scoring was not performed. Judge failures remain unlabeled.

## Statistics (planned)

ASR would be the mean of binary `attack_success` on valid judgments only, with 95% bootstrap CIs using **10,000** resamples (seed 42). This bootstrap size differs from the repository default of 5,000 in `docs/STATISTICAL_PROTOCOL.md`. Paired B0 vs B6 comparisons would use McNemar’s exact two-sided test on overlapping episode IDs, with Holm–Bonferroni correction across model keys at α=0.05.

These inferential procedures were not applied to security outcomes because valid judgments were unavailable.

## Reproducibility

Phase 5 raw rows: `experiments/PHASE5_CONSTRAINED/raw_results.jsonl`. Manifest: `experiments/FINAL_RESEARCH_MANIFEST.json`.
