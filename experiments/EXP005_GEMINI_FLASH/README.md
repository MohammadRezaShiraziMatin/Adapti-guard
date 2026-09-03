# EXP005 — Real LLM evaluation (Gemini 3.6 Flash)

**Label:** Real LLM Evaluation (not simulation)

Canonical conditions:

| Key | Meaning |
|-----|---------|
| B0 | No defense |
| B1 | Rule-based |
| B2_L1 | Fixed defense level 1 |
| B3 | ADAPTI-GUARD adaptive |

Dataset: `datasets/benchmark_q1` held-out **test** split.

```bash
python experiments/EXP005_GEMINI_FLASH/run.py --preflight-only
python experiments/EXP005_GEMINI_FLASH/run.py --smoke-only
python experiments/EXP005_GEMINI_FLASH/run.py
```
