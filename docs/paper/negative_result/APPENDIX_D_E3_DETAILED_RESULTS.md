## Appendix D E3 detailed results: Per-family and per-model breakdown

Experiment E3 tested seven attack families authored with partial independence from the detector (§4.4) on three models with the B3 adaptive stack and the PHASE1-CORE deterministic defense. Both defenses produced zero blocks across all 336 episodes. The tables below provide the breakdown by family and model; in every table, the difference is A0 minus the defended arm, counted over paired episodes.

Data source: `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json`

### E3.1 B3 adaptive stack

**Summary statistics:**
- Paired episodes: 167 (of 168 A0 episodes; one B3 episode incomplete)
- A0 (undefended) executed: 56/167
- B3 executed: 57/167
- Blocks by B3: 0
- Paired comparison (n=167): McNemar exact p = 1.0

#### Per-family results (B3)

| Attack Family | A0 Executed | B3 Executed | Difference |
|---|---|---|---|
| authority claim doc | 23/24 | 22/24 | +1 |
| important instructions doc | 9/24 | 8/24 | +1 |
| important instructions weather | 8/24 | 8/24 | 0 |
| second instruction doc | 7/23 | 7/23 | 0 |
| split address doc | 4/24 | 5/24 | −1 |
| unrequested write doc | 5/24 | 7/24 | −2 |
| workflow footer doc | 0/24 | 0/24 | 0 |

#### Per-model results (B3)

| Model | A0 Executed | B3 Executed | Difference |
|---|---|---|---|
| deepseek-v3.2 | 40/55 | 43/55 | −3 |
| gemma-4-31b-it | 8/56 | 6/56 | +2 |
| qwen3-30b-a3b | 8/56 | 8/56 | 0 |

### E3.2 PHASE1-CORE deterministic defense

**Summary statistics:**
- Total episodes: 168
- A0 (undefended) executed: 57/168
- CORE executed: 57/168
- Blocks by CORE: 0
- Paired comparison (n=168): McNemar exact p = 1.0

#### Per-family results (CORE)

| Attack Family | A0 Executed | CORE Executed | Difference |
|---|---|---|---|
| authority claim doc | 23/24 | 23/24 | 0 |
| important instructions doc | 9/24 | 8/24 | +1 |
| important instructions weather | 8/24 | 8/24 | 0 |
| second instruction doc | 8/24 | 9/24 | −1 |
| split address doc | 4/24 | 3/24 | +1 |
| unrequested write doc | 5/24 | 6/24 | −1 |
| workflow footer doc | 0/24 | 0/24 | 0 |

#### Per-model results (CORE)

| Model | A0 Executed | CORE Executed | Difference |
|---|---|---|---|
| deepseek-v3.2 | 41/56 | 41/56 | 0 |
| gemma-4-31b-it | 8/56 | 7/56 | +1 |
| qwen3-30b-a3b | 8/56 | 9/56 | −1 |

### Interpretation

Neither defense produced a block or a consistent reduction in attack execution across the independent families. The per-family and per-model differences are small and within the range of run-to-run noise documented in §6.3 (8 of 168 paired outcomes differed at temperature 0 for CORE; 7 of 167 for B3), so differences of this size cannot be attributed to a defense.
