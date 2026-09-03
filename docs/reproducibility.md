# Reproducibility

Authoritative short reference: also see root `REPRODUCIBILITY.md`.

## Environment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-core.txt
export PYTHONPATH=.
cp .env.example .env   # add provider keys locally; never commit .env
```

## Integrity hashes

| Artifact | SHA-256 |
|----------|---------|
| `datasets/frozen/eval_v1/dataset.jsonl` | `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` |
| `results/common_attack_stream.json` | `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47` |

## Simulation

```bash
python scripts/run_q1_harmonized_v1.py
python scripts/run_q1_sensitivity_v1.py
```

Seed identifier: **42**. Runner: `harmonized_v1.0.0`.

## Real LLM

Requires provider keys. Prefer reusing saved Target responses when re-judging; do not invent metrics.

Primary entry: `experiments/REAL_LLM_EVAL/run.py` (symlink-stable path).

## Layout note

Experiment directories live under categorical folders (`experiments/real_llm_eval/`, …) with **legacy symlinks** at historical paths for script compatibility.
