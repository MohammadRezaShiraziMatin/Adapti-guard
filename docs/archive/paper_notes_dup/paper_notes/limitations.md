# Limitations

1. **Small-n pilot**: n≈20 attacks is underpowered; identical ASR across baselines may be a
   Target refusal ceiling, not proof that defenses are equivalent.
2. **Attack-only runs** cannot support utility, FPR, balanced accuracy, or reward claims.
3. **Incomplete mixed coverage**: Groq tokens-per-day limits interrupted B2/B3 mixed runs;
   mixed utility results currently cover B0/B1 only until resumed.
4. **Judge–target coupling**: same Groq model family for Target and Judge weakens independence.
5. **Latency artifacts**: cached Target calls yield near-zero timings in some attack-only rows.
6. **Detector quality**: B1/B2/B3 depend on heuristic detection; held-out detector F1 may be weak.
7. **No multi-seed / multi-model** confirmation in the current artifact set.
8. Simulation harmonized results must not be mixed into real-LLM result tables without labels.
