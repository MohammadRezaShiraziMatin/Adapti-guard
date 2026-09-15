# Simulation vs Real LLM Evidence Classification

**Rule:** Only experiments with `evaluation_mode: real_llm_judge` and `validity: VALID` may support LLM security claims in publications.

---

## Evaluation Modes

| Mode | Code Path | ASR Source | Publication use |
|---|---|---|---|
| `real_llm_judge` | `real_llm_pipeline.py`, `attack_success.py` | Independent LLM judge | **YES** (if VALID) |
| `LEGACY_SIMULATION_ONLY` | `harmonized_runner.py`, EXP-005/008 | `attack_outcome.py` heuristics | **NO** |
| `HARMONIZED_SIMULATION` | (deprecated alias) | Same as above | **NO** |
| `DETECTOR_SIMULATION` | `EXP008`, detector metrics | Block rate only | **NO** (detector only) |
| `defense_simulation` | Benchmark v2 experiments | Defense bypass heuristics | **NO** |

---

## Validity States

| State | Meaning | May cite in paper? |
|---|---|---|
| `VALID` | Real target + judge, sufficient samples, low error rate | **YES** |
| `INVALID` | Artifacts exist but scientifically unusable (e.g. 100% API errors) | **NO** |
| `BLOCKED` | Could not execute | **NO** |
| `SIMULATION` | Correct simulation run | **NO** (methods/engineering only) |
| `PARTIAL` | Ran but insufficient sample size or provenance | **NO** (pilot notes only) |
| `NOT_RUN` | No artifacts | **NO** |

---

## Experiment Classification

### Real LLM (require VALID for claims)

| Experiment | Current Validity | Notes |
|---|---|---|
| EXP-002 target_3 | **INVALID** | 5/5 API errors, mislabeled COMPLETED |
| EXP-003 | NOT_RUN | — |
| REAL-LLM-EVAL | BLOCKED | Invalid API key |

### Simulation (engineering evidence only)

| Experiment | Mode | What it measures |
|---|---|---|
| EXP-005 | HARMONIZED_SIMULATION | Adaptive policy under heuristic ASR |
| EXP-008 | DETECTOR_SIMULATION | Detector block rate on evolved attacks |
| harmonized_runner | HARMONIZED_SIMULATION | All PolicyMode comparisons |
| Benchmark v2 Phase 9 | defense_simulation | Defense-layer bypass rate |

### Supported non-LLM evidence

| Experiment | Metric | Valid for |
|---|---|---|
| EXP-017/018 | Detector F1 | Detector quality claims only |
| benchmark_q1 build | n=15,053, hashes | Dataset scale claims |

---

## How to Label Results in Papers

### Correct

> "Under simulation-based evaluation (harmonized runner), adaptive policy achieved ASR ≤ 0.027 across 5 seeds."

> "Real LLM evaluation (Qwen2.5-7B target, Gemma-2-9B judge, n=500, seed=42) showed ASR reduction of X% vs no-defense baseline."

### Incorrect

> "ADAPTI-GUARD achieves ASR of 0.0." (without specifying real LLM + judge + n)

> "Our method outperforms Llama Guard." (when regex fallback was used)

> Citing EXP-002 target_3 results (all API errors)

---

## File Conventions

Real LLM experiment outputs MUST include:

```json
{
  "status": "COMPLETED",
  "evaluation_mode": "real_llm_judge",
  "metrics": {
    "n_judge_errors": 0,
    "prompt_tokens_total": 50000,
    "asr": 0.12
  }
}
```

Simulation outputs MUST include:

```json
{
  "evaluation_mode": "HARMONIZED_SIMULATION",
  "note": "Not valid for real LLM security claims"
}
```

---

## Validation

```bash
# Classify all experiment artifacts
python scripts/scientific_audit.py

# Check specific result
python -c "
from src.adapti_guard.evaluation.provenance import classify_real_llm_validity
import json
m = json.load(open('experiments/EXP002_REAL_LLM/target_3/metrics.json'))
print(classify_real_llm_validity(m))
"
```

---

## Migration: Re-labeling Legacy Artifacts

| Artifact | Old label | Correct label |
|---|---|---|
| `EXP002_REAL_LLM/target_3/metrics.json` | COMPLETED | **INVALID** |
| `EXP005_ADAPTATION/metrics.json` | COMPLETED | SIMULATION (already tagged) |
| `EXP008_ADAPTIVE_ATTACK/metrics.json` | COMPLETED | SIMULATION (already tagged) |

Do not delete legacy artifacts — preserve with corrected validity classification.
