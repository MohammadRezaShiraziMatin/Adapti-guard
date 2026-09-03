# Limitations

1. **No valid independent judge scores for the 300 Groq outputs.** Cerebras chat completions returned HTTP 402 during validation; ASR is undefined.
2. **Do not interpret Phase 5 Gemini `judge_attack_success=false` on failed calls as defense success.** 298 Gemini calls failed (429).
3. **Attack-only frozen eval.** Utility, FPR, and the 0.5/0.4/−0.1 reward are not computable from this experiment.
4. **Target responses truncated to 500 characters** in stored jsonl (122/300 at the cap).
5. **Single Target LLM.** `model_a/b/c` are labels over the same Groq `gpt-oss-120b` endpoint.
6. **B6 never left L1** in 150 episodes, so adaptive escalation/de-escalation was not observed.
7. **Policy families B1, B2, B4, B5, B7** were not included in the 300-call matrix.
8. **EXP-006 ablations** were not executed as real-LLM experiments; simulation artifacts are out of scope.
9. **n=50 episodes**, not the full 770.
10. **B6 is an alias of B3** in `get_defense_fn`; results cannot be read as a distinct B6 algorithm.
