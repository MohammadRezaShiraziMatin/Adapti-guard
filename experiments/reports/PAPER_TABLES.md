# Paper tables (traceable to Phase 5 + judge status)

**Judge security metrics are N/A.** Cerebras validation returned HTTP 402 on all 10 attempts. Mass rejudge was not executed.

Bootstrap B=10000 would apply to ASR if valid judgments existed.

## Table 1 — Overall security

| Model | Policy | N | Valid Judge N | ASR | 95% CI | Defense Rate | 95% CI | Mean ICS |
|---|---|---:|---:|---|---|---|---|---:|
| model_a | B0 | 50 | 0 | N/A | N/A | N/A | N/A | 0.00 |
| model_a | B6 | 50 | 0 | N/A | N/A | N/A | N/A | 0.10 |
| model_b | B0 | 50 | 0 | N/A | N/A | N/A | N/A | 0.00 |
| model_b | B6 | 50 | 0 | N/A | N/A | N/A | N/A | 0.10 |
| model_c | B0 | 50 | 0 | N/A | N/A | N/A | N/A | 0.00 |
| model_c | B6 | 50 | 0 | N/A | N/A | N/A | N/A | 0.10 |

## Table 2 — Category performance

| Category | Policy | N | ASR | 95% CI | Defense Rate | Mean ICS |
|---|---|---:|---|---|---|---:|
| Context Attack | B0 | 24 | N/A | N/A | N/A | 0.00 |
| Context Attack | B6 | 24 | N/A | N/A | N/A | 0.10 |
| Jailbreak | B0 | 21 | N/A | N/A | N/A | 0.00 |
| Jailbreak | B6 | 21 | N/A | N/A | N/A | 0.10 |
| Prompt Injection | B0 | 21 | N/A | N/A | N/A | 0.00 |
| Prompt Injection | B6 | 21 | N/A | N/A | N/A | 0.10 |
| RAG Security | B0 | 21 | N/A | N/A | N/A | 0.00 |
| RAG Security | B6 | 21 | N/A | N/A | N/A | 0.10 |
| Role Attack | B0 | 21 | N/A | N/A | N/A | 0.00 |
| Role Attack | B6 | 21 | N/A | N/A | N/A | 0.10 |
| System Prompt Leakage | B0 | 21 | N/A | N/A | N/A | 0.00 |
| System Prompt Leakage | B6 | 21 | N/A | N/A | N/A | 0.10 |
| Tool Abuse | B0 | 21 | N/A | N/A | N/A | 0.00 |
| Tool Abuse | B6 | 21 | N/A | N/A | N/A | 0.10 |

Category N is Target observations (not valid judgments). ASR is N/A.

## Table 3 — Model comparison (paired McNemar)

| Model | B0 ASR | B6 ASR | Risk Difference | 95% CI | McNemar p | Holm-adjusted p |
|---|---|---|---|---|---|---|
| model_a | N/A | N/A | N/A | N/A | N/A | N/A |
| model_b | N/A | N/A | N/A | N/A | N/A | N/A |
| model_c | N/A | N/A | N/A | N/A | N/A | N/A |

## Table 4 — Intervention behavior (Target actions)

| Policy | L0 % | L1 % | L2 % | L3 % | Mean ICS |
|---|---:|---:|---:|---:|---:|
| B0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.00 |
| B6 | 0.0 | 100.0 | 0.0 | 0.0 | 0.10 |

## Table 5 — Judge reliability / data quality

| Judge | Attempted | Valid | Failed | 429 | 5xx | Timeout | Invalid | 402 | Valid % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Cerebras qwen-3.8-27b (validation) | 10 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0.0 |
| Cerebras qwen-3.8-27b (mass rejudge) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | N/A |
| Gemini 3.6 Flash (Phase 5, not used for final ASR) | 300 | 2 | 298 | 298 | 0 | 0 | 0 | 0 | 0.67 |

### Notes

- B6 is an alias of B3 (`get_defense_fn`).
- `model_a`, `model_b`, `model_c` used the same Groq Target `openai/gpt-oss-120b`.
- 122/300 Target strings are truncated at 500 characters.
- Utility = NOT AVAILABLE. Reward = NOT COMPUTABLE.
