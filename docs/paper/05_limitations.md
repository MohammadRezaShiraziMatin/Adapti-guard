# Limitations

1. **Judge availability** — Independent judging may fail (e.g., Cerebras HTTP 402; Gemini free-tier 429). Failed judgments must not be treated as defense success.
2. **Single-Target Phase 5 keys** — `model_a/b/c` labels may share one Groq Target; not a true multi-architecture comparison.
3. **Incomplete multi-model OpenRouter track** without a valid API key.
4. **Heuristic detector** — `injection_probability` is not a calibrated probability; held-out generalization can be weak.
5. **Attack-only frozen primary set** — utility / FPR / full reward require benign episodes that were actually executed.
6. **Simulation vs real LLM** — Harmonized simulation ASR is circular with detector/defense logic; not publication ASR for Target behavior.
7. **Truncated storage** — Some Phase 5 Target strings were stored at 500 characters.
8. **Partial mixed real-LLM matrices** may abort under rate limits (`REAL_LLM_EVAL_MIXED` status).
9. **B6 ≡ B3** in `get_defense_fn`.
10. **No AgentDojo-class tool loop** in the primary harness.

Do not overclaim. Prefer `docs/final_results.md` and experiment `metrics.json` over narrative summaries.
