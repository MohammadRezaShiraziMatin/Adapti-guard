# REAL-LLM-EVAL

Publication-grade evaluation: Target LLM + Independent Judge.

## Status

**BLOCKED** until `OPENROUTER_API_KEY` or Ollama is available.  
Never produces simulated metrics.

## Run

```bash
python experiments/REAL_LLM_EVAL/run.py --n-samples 5 --baselines B0 B3
```

See `docs/REAL_LLM_EVALUATION.md` for full documentation.
