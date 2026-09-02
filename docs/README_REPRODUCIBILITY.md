# Reproducibility Guide (Q1 Upgrade)

## 1. Environment

```bash
cd adapti_guard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-core.txt
```

Python 3.12+ recommended. Full lockfile: `requirements.txt` (optional, heavy).

## 2. API configuration

```bash
cp .env.example .env
# Edit .env — set OPENROUTER_API_KEY (never commit)
```

## 3. Datasets

```bash
PYTHONPATH=. python scripts/build_benchmark_v2.py
```

Place external datasets under paths in `scripts/build_dataset_inventory.py` before rebuilding.

## 4. API gate (required before large eval)

```bash
PYTHONPATH=. python scripts/run_exp000_api_smoke.py
```

Must return `status: PASS`.

## 5. Model configuration

Edit `configs/models.yaml` — no secrets in this file.

## 6. Experiments

Artifacts: `results/experiment_runs/<EXP-ID>/<RUN-ID>/`

Registry: `experiments/registry.csv`

## 7. Tests

```bash
PYTHONPATH=. pytest
# API tests (opt-in):
RUN_LLM_TESTS=1 PYTHONPATH=. pytest -m llm
```

## 8. Caching

LLM responses cached under `.llm_cache/` (gitignored). Report `cache_hit` in results.

## 9. What is committed vs ignored

| Committed | Ignored |
|-----------|---------|
| `results/summaries/`, `manifests/` | `results/experiment_runs/` raw logs |
| `datasets/benchmark_v2/manifest.json`, `schema.json` | `*.jsonl` splits, `.llm_cache/`, `.env` |
