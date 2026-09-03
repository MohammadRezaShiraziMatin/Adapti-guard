# AdaptiGuard

Adaptive runtime defense framework and **harmonized evaluation protocol** for LLM prompt-injection and related agent attacks.

## Overview

LLM agents that consume untrusted context and invoke tools are vulnerable to prompt injection, jailbreaks, and instruction override. Always-on blocking harms utility; always-off defense fails under attack. **AdaptiGuard** evaluates discrete intervention policies (L0–L3) under a shared security–utility–cost protocol.

```text
Attack / benign episode
        │
   Detection (heuristics)
        │
   Risk Engine (LOW / MEDIUM / HIGH)
        │
   Defense Policy (fixed or adaptive L0–L3)
        │
   Action Layer (A0–A3)
        │
   Target LLM (real) or simulation outcome
        │
   Independent Judge (when available) + Metrics
```

## Research Contributions

- Adaptive runtime intervention policies with escalation / de-escalation and cost gating
- Harmonized comparison of fixed vs adaptive policies on a shared episode population
- Reproducible frozen attack stream + frozen eval dataset with integrity hashes
- Real-LLM Target evaluation path with provenance (judge-dependent ASR when APIs allow)

## Architecture

| Package path | Role |
|--------------|------|
| `src/adapti_guard/attacker/` | Template adaptive attacker / stream generation |
| `src/adapti_guard/detector/` | Prompt-injection heuristics |
| `src/adapti_guard/risk/` | Risk scoring |
| `src/adapti_guard/policy/` | Defense policy engine (`policies` is a compatibility alias) |
| `src/adapti_guard/defense/` | Sanitize / restrict / block actions |
| `src/adapti_guard/adaptation/` | Feedback + level updates |
| `src/adapti_guard/evaluation/` | Metrics, Target/Judge adapters, statistics |
| `src/adapti_guard/experiments/` | Harmonized / real-LLM runners |

Experiment artifacts are organized under `experiments/{real_llm_eval,simulation,ablations,statistics,reports}/` with **legacy path symlinks** (e.g. `experiments/REAL_LLM_EVAL` → `experiments/real_llm_eval/REAL_LLM_EVAL`) so existing scripts keep working.

## Installation

```bash
cd adapti_guard
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-core.txt
# Optional full stack (Garak/Inspect/CUDA): pip install -r requirements.txt
cp .env.example .env        # set GROQ_API_KEY / GEMINI_API_KEY / CEREBRAS_API_KEY as needed
export PYTHONPATH=.
```

## Running Experiments

### Harmonized simulation (frozen stream)

```bash
python scripts/run_q1_harmonized_v1.py
python scripts/run_q1_sensitivity_v1.py
```

Outputs: `results/phase8/`.

### Real LLM evaluation

```bash
PYTHONPATH=. python experiments/REAL_LLM_EVAL/run.py \
  --backend groq --target groq_target --judge groq_judge \
  --n-samples 20 --baselines B0 B3
```

See `experiments/real_llm_eval/README.md`.

### Tests

```bash
PYTHONPATH=. pytest
```

## Dataset

**Frozen primary eval:** `datasets/frozen/eval_v1/dataset.jsonl`  
SHA-256: `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24`  
770 attack-only examples (7×110 categories). **Do not claim utility/FPR from attack-only data.**

**Frozen attack stream:** `results/common_attack_stream.json`  
SHA-256: `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47`

## Metrics

| Metric | Definition |
|--------|------------|
| **ASR** | Successful attacks / valid attack episodes (judge-based for real LLM) |
| **Defense Rate** | `1 − ASR` |
| **Security Score** | Mean episode security score |
| **Utility** | Legitimate-task success rate (requires benign episodes) |
| **Defense Cost / ICS** | Mean intervention cost (A0=0.00, A1=0.10, A2=0.25, A3=0.50) |

Simulation ASR is **not** interchangeable with independent LLM-judge ASR.

## Limitations

- Independent judge availability: Cerebras chat historically HTTP **402**; Gemini free-tier **429** at scale
- Phase 5 multi-key run used a **single** Groq Target model (not three distinct LLMs)
- Incomplete multi-model OpenRouter evaluation without a valid key
- Detector is heuristic (not a calibrated probability / SOTA guard model)
- Mixed real-LLM ablation matrix may be partial under API rate limits
- Some EXP-006 artifacts are `LEGACY_SIMULATION_ONLY`

## Documentation

- Methodology: `docs/methodology.md`
- Threat model: `docs/threat_model.md`
- Reproducibility: `docs/reproducibility.md` / `REPRODUCIBILITY.md`
- Limitations: `docs/limitations.md`
- Results summary: `docs/final_results.md`
- Paper notes: `docs/paper/`

## Citation

See `CITATION.cff`.

## License

MIT — see `LICENSE`.
