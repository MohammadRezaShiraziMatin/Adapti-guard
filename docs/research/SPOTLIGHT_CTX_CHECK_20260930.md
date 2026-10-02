# Live check: spotlighting applied to the untrusted context (2026-09-30)

**Question.** The held-out application (`SECOND_DATASET_MT1_RULES_20260930.md`) found that the MT1 spotlighting arm wraps the *user prompt*, leaving the untrusted *context* unmarked, and that its whole effect was on direct injections. Does marking the context change indirect-injection success?
**Design.** Same pack (`datasets/frozen/layer_a_v2`), seed 42, sampling, judge (qwen-2.5-72b, temperature 0) and pipeline as MT1 r1, on 3 targets (gemma-4-31b-it, llama-3.1-8b, qwen3-30b). New arm `SPOTLIGHT_CTX` (delimiters and an "untrusted external content" instruction around the context; user prompt unchanged; `make_spotlight_context`, hook `transform_context` in `evaluate_episode`, inert by default and covered by tests). A fresh undefended replicate `B0_REP` measures run-to-run noise. 20 attacks + 10 benign per model per arm, 180 episodes. Compared offline with the stored MT1 r1 B0 and SPOTLIGHT rows. **Spend $0.0669** (380 requests; cap $0.15). Data: `experiments/real_llm_eval/MT1/spotlight_ctx_check_20260930/`; analysis `scripts/analyze_spotlight_ctx_check.py` → `docs/research/artifacts/spotlight_ctx_check_20260930.json`.
**Status:** exploratory, small n. The budget gate required prices for the judge and llama-3.1-8b that the panel table lacks; published OpenRouter rates read on 2026-09-30 are pinned in the runner.

## Results (attack episodes, judge-scored; 57 attacks = 30 direct, 18 indirect, 9 encoded)
| channel | B0 (MT1 r1) | B0 replicate | Spotlight on **prompt** (MT1 r1) | Spotlight on **context** (new) |
|---|---|---|---|---|
| direct (prompt) | 22/30 | 25/30 | **6/30** | 22/30 |
| **indirect (context)** | 8/18 | 6/18 | 7/18 | **1/18** |
| encoded | 5/9 | 6/9 | 0/9 | 3/9 |
| all | 35/57 | 37/57 | 13/57 | 26/57 |
Paired vs MT1 B0 (judge b10/b01; canary emission in brackets): prompt-wrapped, direct 16/0 [15/1], indirect 3/2 [3/2]; **context-wrapped, direct 1/1 [2/2], indirect 7/0 [6/0]** (exact McNemar on the 7/0: p = 0.016). Indirect by model (B0 → context-wrapped, n = 6 each): gemma 4 → 0, llama 1 → 0, qwen3 3 → 1. Benign utility on the 10 benign tasks per model: context-wrapped 10/10 for each model (B0 10, 10, 9).

## Reading
1. **The wrong-channel finding is confirmed by a re-run.** The prompt-wrapped arm lowers direct injections (22 → 6) and does nothing for indirect ones (8 → 7); the context-wrapped arm does the reverse (direct 22 → 22, indirect 8 → 1). Spotlighting as published targets untrusted data [cite: `[VERIFY]` Hines et al.]; the historical MT1 arm is not a test of that.
2. **Direction is consistent across the three models**, and benign tasks were not harmed in this small sample.
3. **Noise floor, larger than in the tool harness.** The fresh undefended replicate differs from the earlier undefended run in 8 of 57 attack pairs by the judge (3 vs 5 wins, 14%) and 5 of 57 by canary emission (1 vs 4, 9%) at temperature 0. The 7/0 indirect result exceeds this noise, but with 18 episodes it is fragile.

## Caveats
- 18 indirect episodes (6 per model), one arm run once, three models, one synthetic single-turn pack; encoded attacks (n = 9) are inconsistent between judge and canary and are not interpreted.
- `B0_REP` for qwen3 has 6 benign episodes with `judge_api_error` (provider 504); its benign utility (4/10) is an infrastructure artefact, not a measurement, and is excluded. No attack episode had a target or judge error.
- Comparisons use stored MT1 r1 arms generated earlier; provider behaviour may have drifted, which the B0 replicate partly captures.
- Not independent of the project; the canary is a text-level analogue of an executed effect.

## Consequences
Manuscript: §4.7 (channel check) moves from "candidate rule discovered on held-out data" to "confirmed by a targeted re-run (n = 18 indirect episodes)"; §6.5 gets the table above; §8 records the caveats and the larger noise floor (9–14% in this pack). Do not present either spotlighting arm as a finding about spotlighting in general.
