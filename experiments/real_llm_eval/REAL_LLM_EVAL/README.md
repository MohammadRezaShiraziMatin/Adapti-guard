# REAL-LLM-EVAL — ADAPTI-GUARD

Publication-oriented evaluation: **Defense → Target LLM → Independent Judge → Metrics**.

ASR comes **only** from the judge (or from hard blocks). Simulation/regex ASR is never used in this mode.

## Problem definition

LLM applications that ingest untrusted text are vulnerable to prompt injection and related
instruction-override attacks. Static defenses trade security against utility. ADAPTI-GUARD
evaluates **discrete runtime interventions** (L0–L3) and an **adaptive** controller (B3)
under a shared real-LLM protocol.

## Architecture (evaluation path)

```
benchmark_q1 sample
        │
        ▼
┌───────────────────┐
│ Defense baseline  │  B0 / B1 / B2_L* / B3
│ (A0–A3 action)    │
└─────────┬─────────┘
          │ defended or blocked prompt
          ▼
┌───────────────────┐
│ Target LLM (Groq) │
└─────────┬─────────┘
          │ model response
          ▼
┌───────────────────┐
│ Judge LLM         │  structured attack_success / utility_success
└─────────┬─────────┘
          ▼
     metrics + predictions JSONL + run manifest
```

## Installation

```bash
cd 01_BASE_Q1/adapti_guard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-core.txt
cp .env.example .env   # set GROQ_API_KEY
```

## Running experiments

### Attack-only smoke (backward compatible)

```bash
PYTHONPATH=. python experiments/REAL_LLM_EVAL/run.py \
  --backend groq \
  --target groq_target \
  --judge groq_target \
  --n-samples 20 \
  --baselines B0 B3
```

### Mixed attack + benign (utility / FPR)

```bash
PYTHONPATH=. python experiments/REAL_LLM_EVAL/run.py \
  --backend groq \
  --target groq_target \
  --judge groq_judge \
  --attack-n 20 \
  --benign-n 20 \
  --seed 42 \
  --baselines B0 B1 B2_L1 B2_L2 B2_L3 B3
```

> Prefer `--judge groq_judge` (or a stronger distinct model) rather than the same key as the Target.

### Publish tables / figures / paper notes

```bash
PYTHONPATH=. python experiments/REAL_LLM_EVAL/analyze_and_publish.py
```

Outputs:

- `results/tables/baseline_comparison.csv`
- `results/tables/baseline_comparison_latex.tex`
- `results/figures/{asr,security,latency}_comparison.{png,pdf,svg}`
- `paper_notes/*.md`

## Evaluation methodology

| Metric | Definition |
|--------|------------|
| ASR | Successful attacks / attack episodes (judge) |
| Defense Rate | 1 − ASR |
| FNR | ASR on attacks |
| FPR | Failed benign / benign episodes |
| Utility | Successful benign / benign episodes |
| Precision/Recall/F1 | Defense confusion counts when benign present |
| Balanced accuracy | 0.5 × (Recall + TNR) |
| Reward | 0.5·security + 0.4·utility − 0.1·ICS (needs benign) |
| Bootstrap CI | 95% CI on ASR (B=10000 in analysis script) |

## Baselines

| ID | Role |
|----|------|
| **B0** | No defense |
| **B1** | Simple rule-based block |
| **B2_L1/L2/L3** | Fixed layered intervention |
| **B3** | Adaptive ADAPTI-GUARD controller |

## Reproducibility

Each pipeline run writes under `results/experiment_runs/REAL-LLM-EVAL/RUN-*/`:

- `config.json`, `environment.json`, `model_config.json`
- `dataset_manifest.json`, `git_commit.txt`, `command.txt`
- `metrics.json`, logs

Use a fixed `--seed`. Do not overwrite raw prediction JSONL by hand.

## Results (current artifact snapshot)

See `paper_notes/results_analysis.md` and `results/experiment_runs/REAL-LLM-EVAL/RUN-20260903-225156-b46b86/`.

**Do not claim utility/FPR from attack-only runs.**
