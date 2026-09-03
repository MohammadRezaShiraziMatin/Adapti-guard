# EXP-003: Baseline Comparison

## Methods
1. No Defense
2. Regex Detector
3. TF-IDF ML Detector
4. Llama Guard (regex fallback if model unavailable)
5. Prompt Guard (regex fallback)
6. NeMo Guard (regex fallback)
7. ADAPTI-GUARD

## Run
```bash
python experiments/EXP003_BASELINES/run.py --n-samples 100
```

## Outputs
- `baseline_comparison.csv`
- `baseline_comparison.json`
- `figures/baseline_comparison.png`
