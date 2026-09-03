# Results

We report only quantities computed from executed observations.

## Target-side experiment (Phase 5)

The constrained primary run collected **300** generations from Groq `openai/gpt-oss-120b` on **50** frozen-eval attack episodes (seed 42), crossed with policies **B0** and **B6** and three configuration keys (`model_a`, `model_b`, `model_c`). All 300 Target API calls completed with `api_status=ok`. The three keys used the **same** Target model; they are not distinct LLM architectures.

**Intervention actions (observed):**

- B0 selected A0 (L0) on 150/150 episodes. Mean ICS = **0.00**.
- B6 selected A1 (L1) on 150/150 episodes. Mean ICS = **0.10**.
- L2 and L3 were never selected.

B6 is implemented as an alias of B3 (full adaptive). In this subsample the adaptive controller did not escalate beyond sanitize-level intervention.

**Target text storage:** 122 of 300 stored `target_response` strings have length 500, matching a `[:500]` truncation in the Phase 5 runner. Full completions were not retained.

## Independent judge (Cerebras)

We attempted to score saved Target outputs with Cerebras `qwen-3.8-27b` (temperature 0). A validation set of **10** diverse saved cases was run first. **All 10 calls failed** with HTTP **402** (`payment_required`). Per protocol, the 300-case rejudge was **not** executed. Failed calls are not treated as attack failures or defense successes.

Therefore **ASR, Defense Rate, McNemar tests, Holm-adjusted p-values, and ASR effect sizes are not reported.**

Gemini judgments from Phase 5 (2 valid, 298 failed with 429) are **not** used as publication security labels.

## Utility and reward

The frozen primary dataset is attack-only. **Utility is not available. Reward is not computable.** We do not impute utility.

## Ablations

Real-LLM EXP-006 ablations were **not executed**. Existing `experiments/EXP006_ABLATION` metrics are marked `LEGACY_SIMULATION_ONLY` and are not used here.

## What can be concluded

This run documents a complete Target factorial and a fully observed cost gap of 0.10 ICS between B0 and B6. It does **not** establish whether B6 changed attack success relative to B0.
