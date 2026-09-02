# EXP-004 — Publication-Grade Real-LLM Evaluation

## Design

- **Dataset:** `datasets/frozen/eval_v1/dataset.jsonl` (SHA-256 verified, immutable)
- **Baselines:** B0 (no defense) vs B6 (ADAPTI-GUARD adaptive)
- **Models:** `openai/gpt-4o-mini`, `qwen/qwen3-30b-a3b`, `deepseek/deepseek-chat-v3-0324`
- **Judge:** Claude Sonnet 4 (blind, independent)
- **Sample size:** 150 stratified episodes per model (paired B0/B6); override with `--n-samples`
- **Mode:** `real_llm_judge` only — no simulated ASR

## API call budget (estimate)

Per model, per baseline, per episode (non-blocked):

- 1 target call + 1 judge call

| Component | Count |
|-----------|------:|
| Episodes per model | 150 |
| Baselines | 2 |
| Models | 3 |
| Max target calls | 900 |
| Max judge calls | 900 |
| **Total max API calls** | **~1,800** |

Blocked episodes (B6 sanitize/block) skip target and judge calls.

Approximate tokens per episode: ~800–2000 (prompt + response + judge).

**Estimated cost:** see `COST_ANALYSIS.md` (~$5–11 USD for n=150 at current OpenRouter list prices).

## Commands

```bash
# Phase 2.7 pilot first
python experiments/PHASE2_7_PILOT/run.py

# Full EXP-004 (resumable)
python experiments/EXP-004/run.py --skip-existing

# Analysis only
python experiments/EXP-004/analyze.py
```

## Limitations

- Frozen eval_v1 is **attack-only** (770 samples, 0 benign). EXP-004 does **not**
  evaluate benign utility, FPR, benign degradation, or legitimate-task preservation.
  Do not claim utility preservation from EXP-004 results.
- OpenRouter responses are not fully deterministic at temperature 0.
- Publication mode disables LLM cache (`cache_enabled=false`) for latency/cost integrity.
- Clear `.llm_cache` before a publication run if prior cached responses exist on disk.
