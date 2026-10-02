# Applying the manuscript's measurement rules to a second dataset (MT1 r1)

**Purpose.** Address the review objection that the rules were derived on the same traces they are demonstrated on (`docs/paper/negative_result/INTERNAL_REVIEW_20260930.md`, weakness 3). MT1 r1 (2026-09-25; 6 targets × 4 arms on the frozen Layer A v2 pack, single-turn, no tools, judge-scored) was generated **before** the rules were written down (2026-09-30), so applying them unchanged is a held-out test. Offline, API = 0, nothing under `experiments/**` or `datasets/**` modified. Script `scripts/apply_rules_second_dataset_mt1.py`; artifact `docs/research/artifacts/mt1_second_dataset_rules_20260930.json`; test `tests/test_second_dataset_mt1_rules.py`.

**Limits of the test.** Same repository and same authors (not independent of the project); one synthetic pack; 19 attacks with a literal canary per model (114 per arm over 6 models); no tools, so the "executed effect" of M1 becomes *canary token emitted in the response*, a text-level analogue that over-counts refusals which quote the token. Arms: B0, B3 (adaptive stack), SPOTLIGHT (delimiter wrapping), STATIC-A3 (block all).

## Results
| rule | applicable? | result on MT1 |
|---|---|---|
| **M1** endpoint (judge vs deterministic effect) | yes, as canary emission | Judge and canary agree well here: κ = 0.81 (B0), 0.87 (B3), 0.91 (SPOTLIGHT); B0 76 vs 70, B3 72 vs 67, SPOTLIGHT 43 vs 48 (judge vs canary). **The large judge-vs-tool-layer disagreement of Tracks A/B (κ 0.16–0.36) does not reappear**: with a verifiable token endpoint the judge tracks the deterministic rule. The M1 failure is about judges interpreting simulated tool outcomes (denials, claims), not judges in general. |
| **M2** pre-target block vs missing data | **not testable** | The stored `target_prompt` holds the prompt only (the untrusted context is not stored), so marker-in-request cannot be checked. STATIC-A3 blocks everything (0/114 either rule), which makes the labelling question trivial. |
| **M3** valid attack / channel | yes, as channel split | 60 of 114 attack episodes carry the canary in the **user prompt** (direct), 36 in the **untrusted context** (indirect), 18 encoded. Effects split sharply by channel (below). |
| **M4** authorship independence | not testable | no separate independent set in MT1. |
| **M5** per-model reporting | yes | See below. |

### Paired effects vs B0 (exact McNemar, descriptive)
| arm | rule | pooled b10 / b01 | p | per-model (b10 / b01) |
|---|---|---|---|---|
| B3 | judge | 11 / 7 | 0.48 | gemma 1/0, gpt-oss 3/0, llama 2/1, mistral 1/1, qwen2.5 2/2, qwen3 2/3 |
| B3 | canary | 10 / 7 | 0.63 | gemma 1/0, gpt-oss 3/1, llama 2/1, mistral 1/1, qwen2.5 2/1, qwen3 1/3 |
| SPOTLIGHT | judge | 39 / 6 (Δ = 0.29) | 5.4e-7 | gemma 14/0, gpt-oss 11/1, llama 5/2, mistral 2/2, qwen2.5 2/1, qwen3 5/0 |
| SPOTLIGHT | canary | 31 / 9 (Δ = 0.19) | 6.8e-4 | gemma 12/0, gpt-oss 10/2, llama 3/3, mistral 1/3, qwen2.5 1/1, qwen3 4/0 |
- **M1 changes the size, not the verdict:** SPOTLIGHT's pooled effect is 0.29 by the judge and 0.19 by canary emission; both significant. B3: no effect either way.
- **M5 (per model) is confirmed:** the pooled SPOTLIGHT effect is carried by gemma (14/0), gpt-oss (11/1) and qwen3 (5/0); for mistral (2/2 judge, 1/3 canary) and llama under the canary rule (3/3) there is no effect. A pooled test hides that the defense does nothing for some models.

### By channel, pooled over models (attack episodes; B0 → arm, judge / canary)
| arm | direct (60) | indirect, in context (36) | encoded (18) |
|---|---|---|---|
| B3 | 46 → 43 / 47 → 42 | 21 → 21 / 20 → 22 | 9 → 8 / 3 → 3 |
| SPOTLIGHT | **46 → 22** / 47 → 27 | **21 → 21** / 20 → 21 | 9 → 0 / 3 → 0 |
The whole SPOTLIGHT effect is on **direct** injections and the encoded ones; on **indirect** injections in the untrusted context, the channel spotlighting is designed for, it has **no effect** (21 → 21).

## New finding: the defense is applied to the wrong channel
In this pipeline the datamarking defense wraps the **user prompt** ("The text below is untrusted user-supplied content … <<<UNTRUSTED_START>>> … ") and the context is added afterwards without any marking (`make_spotlight_datamark`, `evaluate_episode`: `full_prompt = "Context:\n{context}\n\nUser: {defended_prompt}"`). So the spotlighting baseline marks the trusted task text as untrusted and leaves the untrusted context unmarked. That matches the data (effect on direct, none on indirect) and means MT1's SPOTLIGHT arm is not a test of spotlighting as published for untrusted data [cite: 2510.09023 for the defense family; Hines et al. `[VERIFY]`]. This is a sixth kind of check for a defense evaluation: **verify that the defense is applied to the untrusted channel and that the transformed text reaches the model as intended**; it is a candidate rule M6 discovered on held-out data.
Update: confirmed by a targeted live re-run, see `SPOTLIGHT_CTX_CHECK_20260930.md` (context-wrapped arm: indirect 8 → 1 of 18, direct unchanged).

## What this does for the circularity objection
- **M5 replicates** on held-out data (heterogeneity across models is visible and changes how the pooled result should be read).
- **M1 partly replicates**: the endpoint choice again changes effect sizes (0.29 vs 0.19), but the judge–executor gap is not general (κ 0.81–0.91 here), which sharpens the claim: judges fail where they must interpret simulated tool outcomes.
- **M2/M4 could not be tested** here; M3 appears as a channel split that qualifies the SPOTLIGHT result.
- A new check (M6, wrong channel) emerged from the held-out data.
- Not yet addressed: a truly independent second system (different authors/harness), and an independent scenario set, still needed.

## Consequences for the manuscript
1. §4: add the channel check as a short §4.7 (candidate M6) and state that M2/M4 were not testable on MT1.
2. §6: add a §6.5 "Held-out application (MT1)" with the tables above; keep the abstract at five rules.
3. §8: record the limits listed at the top of this note.
4. Do not cite MT1's SPOTLIGHT result as evidence about spotlighting; report it as an instance of the channel problem.
