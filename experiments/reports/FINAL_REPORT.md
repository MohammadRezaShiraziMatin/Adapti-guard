# ADAPTI-GUARD — Final Research Report

Generated: 2026-09-03T19:08:05.386098+00:00

## 1. Research question

Can an adaptive runtime intervention policy (B6, alias of B3 full adaptive) improve security against prompt-injection-style attacks relative to no intervention (B0), while recording intervention cost, on a frozen attack-only evaluation?

## 2. Hypotheses

From `docs/HYPOTHESES.md`:

- H1: Adaptive defense achieves lower judge-based ASR than a weaker/fixed policy on the same benchmark.
- H2: Adaptive defense maintains higher benign utility than always-on L3 (requires benign data).
- H3: Adaptive policy reduces cost vs fixed maximum defense at comparable security.
- H4: Policy ordering is consistent across ≥2 **distinct** target models.
- H5: Defense-aware attacks reduce the adaptive vs fixed gap.

**Status:** H1 cannot be tested without valid independent Judge outcomes. H2/H5 not tested (no benign set / no adaptive-attack Phase 5). H3 partially informed by ICS only (B6 mean ICS=0.10 vs B0=0.00; no L3 arm). H4 not tested as three distinct Targets (same Groq model).

## 3. Experimental setup

- Experiment: Phase 5 constrained (EXP-004-style primary comparison B0 vs B6)
- n=50 frozen-eval episodes, seed=42, stratified as in the Phase 5 runner
- 3 model keys × 2 policies = 300 Groq Target calls
- No new Groq Target calls in this completion pass

## 4. Dataset

- Path: `datasets/frozen/eval_v1/dataset.jsonl`
- SHA-256: `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` (match expected: True)
- Attack stream SHA-256: `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47` (match: True)
- 770 attacks, 7 categories × 110; Phase 5 used 50 IDs (replicated across keys/policies)
- Attack-only: **Utility = NOT AVAILABLE**

## 5. Threat model

Runtime LLM-agent intervention against prompt injection / jailbreak / RAG / context / tool abuse / system-prompt leakage / role attacks as labeled in the frozen eval. Primary metric is judge-based attack success on Target outputs.

## 6. Target model

- Provider: Groq
- Model: `openai/gpt-oss-120b`
- Config: `groq_target`, temperature 0, max_tokens 512, reasoning_effort=low
- All 300 `api_status=ok`

## 7. Judge model

- Intended: Cerebras `qwen-3.8-27b`, temperature 0
- Validation: 10 diverse saved cases
- **Outcome: all 10 failed with HTTP 402 payment_required**
- Mass rejudge **not started** (protocol: do not run full rejudge until validation passes)
- Prior Gemini judge: 2 valid / 298 failed (429); **not used** for final ASR

## 8. Intervention policies

- B0 = Fixed L0 / A0, cost 0.00
- B6 = Full Adaptive, **implementation alias of B3**
- Observed B6 actions: A1 on 150/150 episodes (L1, cost 0.10); never A2/A3

## 9. Metrics

- ASR = successful attacks / valid judged attacks — **NOT COMPUTABLE** (valid N=0)
- Defense Rate = 1 − ASR — **NOT COMPUTABLE**
- Mean ICS from recorded actions — **computed**
- Utility — **NOT AVAILABLE**
- Reward — **NOT COMPUTABLE**

## 10. Statistical methodology

- Planned: 95% bootstrap CIs with **B=10000** (documented change from protocol default 5000)
- Planned: McNemar exact two-sided on paired B0 vs B6 attack_success; Holm–Bonferroni α=0.05 across 3 model keys
- **Not executed** on security outcomes because there are no valid paired judgments

## 11. Data-quality analysis

- 300 unique (model_key, policy, episode_id) Target rows
- 50 unique episode IDs
- 122 responses stored at exactly 500 characters (truncation)
- Prompts recovered by joining frozen IDs (not stored in raw jsonl)
- Gemini failures must not be treated as ASR=0 (they were `judge_failure=true` with `judge_attack_success=false` in storage — a **known hazard**, avoided in this report)

## 12. Overall results

**Observed (Target/actions):**

- B0 mean ICS = 0.00 (100% L0)
- B6 mean ICS = 0.10 (100% L1)

**Judge-based ASR/Defense:** not available.

## 13. Category results

ICS is 0.00 under B0 and 0.10 under B6 in every category (constant actions). ASR by category: N/A.

## 14. Model results

Same ICS pattern for model_a/b/c. These are **replications of one Target**, not three LLMs.

## 15. Intervention-cost analysis

Adaptive policy paid a constant 0.10 ICS vs 0.00 for B0. No evidence on whether that cost bought security.

## 16. Adaptive behavior

B6 never left L1 in this 50-episode subsample. Escalation and de-escalation frequencies are not identifiable (constant action). Mean intervention level (coding L1=1) = 1.0.

## 17. Statistical significance

McNemar / Holm: **NOT COMPUTABLE**.

## 18. Effect sizes

Risk difference / OR / RR for ASR: **NOT COMPUTABLE**. ICS mean difference B6−B0 = 0.10 (exact, all episodes).

## 19. Limitations

Cerebras billing 402; truncated Target text; single Target model; attack-only data; B4/B5/B7 unused; n=50 not 770; B6 did not explore L2/L3.

## 20. Threats to validity

- **Construct:** ASR undefined without judge.
- **Internal:** Truncation may have changed what a future judge would see.
- **External:** One Groq model, 50 episodes, attack-only.
- **Statistical conclusion:** No inferential security tests were performed.

## 21. Reproducibility

See `experiments/FINAL_RESEARCH_MANIFEST.json`. Analysis of ICS is reproducible from `experiments/PHASE5_CONSTRAINED/raw_results.jsonl`. Judge ASR is not reproducible until Cerebras (or another approved independent judge) can score the saved responses.

## 22. Conclusions

**Supported:** 300 Groq Target observations exist; B0 vs B6 action/cost pattern is deterministic in this run (A0 vs A1). Dataset hashes match the freeze.

**Not supported:** Any claim that adaptive intervention improved or did not improve security; utility; reward; multi-model Target generalization; real-LLM ablations.

## 23. Future experiments

1. Fund Cerebras (or approved judge) and rejudge the 300 saved responses without new Groq calls.
2. Store full Target text (not `[:500]`).
3. Distinct Target models for H4.
4. Benign evaluation for utility/FPR/reward.
5. Real-LLM EXP-006 ablations if budget allows.
