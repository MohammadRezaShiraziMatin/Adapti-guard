## Appendix D E3 detailed results: per-family and per-model breakdown

Experiment E3 tested seven partially independent attack families on three models with the B3 adaptive stack and the PHASE1-CORE deterministic defense. Both defenses produced zero blocks across all 336 episodes. The tables below provide the breakdown by family and model; in every table, the difference is A0 minus the defended arm, counted over paired episodes (the opposite sign to the `mean_diff` of Fig. 3, which is defended minus A0).

Data source: `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json`

### E3.1 B3 adaptive stack

**Summary statistics:**
- Paired episodes: 167 (of 168 A0 episodes; the one B3 episode with run status `INVALID_PROVIDER_ERROR` recorded an executed attacker call, as did its undefended pair, and is dropped from the pairing)
- A0 (undefended) executed: 56/167
- B3 executed: 57/167
- Blocks by B3: 0
- Paired comparison (n=167): McNemar exact p = 1.0

### E3.2 PHASE1-CORE deterministic defense

**Summary statistics:**
- Total episodes: 168
- A0 (undefended) executed: 57/168
- CORE executed: 57/168
- Blocks by CORE: 0
- Paired comparison (n=168): McNemar exact p = 1.0

#### Per-family and per-model results, B3 and PHASE1-CORE

The B3 comparison uses 167 pairs and the CORE comparison 168 pairs (see the summary statistics above), so the A0 column is given for each pairing; where the two differ (second instruction doc, 7/23 vs 8/24; deepseek-v3.2, 40/55 vs 41/56) the denominators differ by one.

| Attack family | A0 executed (B3 pairing) | B3 executed | Difference (A0 − B3) | A0 executed (CORE pairing) | CORE executed | Difference (A0 − CORE) |
|---|---|---|---|---|---|---|
| authority claim doc | 23/24 | 22/24 | +1 | 23/24 | 23/24 | 0 |
| important instructions doc | 9/24 | 8/24 | +1 | 9/24 | 8/24 | +1 |
| important instructions weather | 8/24 | 8/24 | 0 | 8/24 | 8/24 | 0 |
| second instruction doc | 7/23 | 7/23 | 0 | 8/24 | 9/24 | −1 |
| split address doc | 4/24 | 5/24 | −1 | 4/24 | 3/24 | +1 |
| unrequested write doc | 5/24 | 7/24 | −2 | 5/24 | 6/24 | −1 |
| workflow footer doc | 0/24 | 0/24 | 0 | 0/24 | 0/24 | 0 |

| Model | A0 executed (B3 pairing) | B3 executed | Difference (A0 − B3) | A0 executed (CORE pairing) | CORE executed | Difference (A0 − CORE) |
|---|---|---|---|---|---|---|
| deepseek-v3.2 | 40/55 | 43/55 | −3 | 41/56 | 41/56 | 0 |
| gemma-4-31b-it | 8/56 | 6/56 | +2 | 8/56 | 7/56 | +1 |
| qwen3-30b-a3b | 8/56 | 8/56 | 0 | 8/56 | 9/56 | −1 |

### E3.3 Non-delivered episodes and delivery-restricted pairs

The pairing above uses run status `COMPLETE` on both sides and keeps episodes the harness labeled `INVALID_NOT_DELIVERED` (they count as executed only if the executor log records an executed attacker call). Of the 168 undefended episodes, 14 carry that label: 10 because the tool carrying the payload was never called (9 `retrieve_document`, 1 `get_weather`; all qwen3, 8 of them in the split-address family), 3 because of a provider error with an executed call recorded (deepseek), and 1 truncated episode (deepseek, split-address). Among the `COMPLETE` defended episodes, 18 (B3) and 13 (CORE) carry the label, 8 each for the same never-called carrier tool and the rest provider errors. The table restricts the pairs; it is a sensitivity analysis, not the primary comparison (source: `docs/research/artifacts/e3_delivery_audit_20261003.json`, `scripts/audit_e3_delivery.py`).

| arm | pairs used | pairs | A0 executed | defended executed | b10/b01 |
|---|---|---|---|---|---|
| B3 | published | 167 | 56 | 57 | 3/4 |
| B3 | carrier tool never ran (either side) dropped | 157 | 56 | 56 | 3/3 |
| B3 | any `INVALID_NOT_DELIVERED` (either side) dropped | 144 | 48 | 46 | 3/1 |
| B3 | published plus the `INVALID_PROVIDER_ERROR` episode | 168 | 57 | 58 | 3/4 |
| CORE | published | 168 | 57 | 57 | 4/4 |
| CORE | carrier tool never ran (either side) dropped | 158 | 57 | 56 | 4/3 |
| CORE | any `INVALID_NOT_DELIVERED` (either side) dropped | 149 | 49 | 47 | 4/2 |

No restriction produces a significant difference (exact McNemar p ≥ 0.625 in every row); the sample is small and these are descriptive.

### Interpretation

Neither defense produced a block or a consistent reduction in attack execution across the independent families. The per-family and per-model differences are small and within the range of run-to-run noise documented in §6.3 (8 of 168 paired outcomes differed at temperature 0 for CORE; 7 of 167 for B3), so differences of this size cannot be attributed to a defense.
