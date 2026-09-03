# Final scientific audit (evidence-backed)

1. Target observations: **300** (`raw_results.jsonl`).
2. Valid Cerebras Judge observations: **0**.
3. Judge failures (validation): **10** of 10; mass rejudge failures: **0 attempts**.
4. Cause: Cerebras **HTTP 402 payment_required** on chat completions (model list succeeded).
5. ASR B0: **NOT COMPUTABLE**.
6. ASR B6: **NOT COMPUTABLE**.
7. 95% CI ASR: **NOT COMPUTABLE**.
8. Defense Rate: **NOT COMPUTABLE**.
9. Mean ICS: B0=**0.00**, B6=**0.10** (from actions).
10. Paired McNemar: **NOT COMPUTABLE**.
11. Holm-adjusted: **NOT COMPUTABLE**.
12. ASR effect size: **NOT COMPUTABLE**. ICS difference B6−B0 = **0.10**.
13. By category: ICS pattern identical; ASR N/A.
14. By model: ICS pattern identical; same Groq Target; ASR N/A.
15. B6 levels: **100% L1**.
16. Utility measurable? **No.**
17. Reward computable? **No.**
18. Hypotheses supported: none of H1–H5 as security/utility claims. Cost observation: B6 > B0 ICS.
19. Hypotheses not supported / untested: H1–H5 as stated.
20. Incomplete: Cerebras rejudge, full 770, distinct models, benign utility, real ablations, B4/B5/B7.
21. Traceable numbers: ICS and counts from Phase 5 jsonl; hashes verified; ASR not claimed.
22. Reproduce analysis: yes for ICS/QC from frozen files; no for ASR until judge billing works.

PROJECT STATUS is therefore **INCOMPLETE for publication security claims**, **COMPLETE for Target collection + honest blocker documentation**.
