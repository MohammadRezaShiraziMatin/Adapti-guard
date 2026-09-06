
```markdown
# AdaptiGuard

**Cost-aware adaptive runtime defense** and a harmonized evaluation protocol for **prompt injection** (and related instruction-override attacks) in **LLM agents**.

> Untrusted context and tool outputs can hijack agents. Always-on blocking hurts utility; always-off defense fails under attack. AdaptiGuard evaluates discrete interventions (**L0–L3**) under a shared **security–utility–cost** protocol.

## Pipeline

```text
Attack / benign episode
        │
        ▼
Detection (heuristics)
        │
        ▼
Risk Engine (LOW / MEDIUM / HIGH)
        │
        ▼
Defense Policy (fixed or adaptive L0–L3)
        │
        ▼
Action Layer (A0–A3)
        │
        ▼
Target LLM (real)  or  simulation outcome
        │
        ▼
Independent Judge (when available) + Metrics
```

## Research contributions

- Adaptive runtime intervention with escalation / de-escalation and cost gating
- Harmonized comparison of **fixed vs adaptive** policies on a shared episode population
- Reproducible frozen attack stream + frozen eval dataset with integrity hashes
- Real-LLM Target path with provenance (judge-based ASR when APIs allow)

## Repository layout

| Path | Role |
|------|------|
| `src/adapti_guard/attacker/` | Template adaptive attacker / stream generation |
| `src/adapti_guard/detector/` | Prompt-injection heuristics |
| `src/adapti_guard/risk/` | Risk scoring |
| `src/adapti_guard/policy/` | Defense policy engine (`policies` = compatibility alias) |
| `src/adapti_guard/defense/` | Sanitize / restrict / block actions |
| `src/adapti_guard/adaptation/` | Feedback + level updates |
| `src/adapti_guard/evaluation/` | Metrics, Target/Judge adapters, statistics |
| `src/adapti_guard/experiments/` | Harmonized / real-LLM runners |
| `experiments/` | Run artifacts (`real_llm_eval`, `simulation`, `ablations`, …) |
| `paper/` | Working paper (PDF/TeX) when present |
| `docs/` | Methodology, threat model, reproducibility, limitations |

Legacy path symlinks (e.g. `experiments/REAL_LLM_EVAL` → `experiments/real_llm_eval/REAL_LLM_EVAL`) keep older scripts working.

## Installation

```bash
cd adapti_guard
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-core.txt
# Optional full stack: pip install -r requirements.txt
cp .env.example .env               # GROQ_API_KEY / GEMINI_API_KEY / …
export PYTHONPATH=.
```

Never commit `.env` or API keys.

## Running experiments

### Harmonized simulation (frozen stream)

```bash
python scripts/run_q1_harmonized_v1.py
python scripts/run_q1_sensitivity_v1.py
```

Outputs: `results/phase8/`.  
**Label:** simulation-only — not interchangeable with independent LLM-judge ASR.

### Real-LLM evaluation

```bash
PYTHONPATH=. python experiments/REAL_LLM_EVAL/run.py \
  --backend groq --target groq_target --judge groq_judge \
  --n-samples 20 --baselines B0 B3
```

Prefer an **independent Judge** (e.g. Gemini) when available.  
See `experiments/real_llm_eval/README.md`.

## Tests

```bash
PYTHONPATH=. pytest
```

## Datasets (integrity)

| Artifact | SHA-256 |
|----------|---------|
| `datasets/frozen/eval_v1/dataset.jsonl` | `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` |
| `results/common_attack_stream.json` | `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47` |

Frozen primary eval: **770 attack-only** examples (7×110 categories).  
**Do not claim utility/FPR from attack-only data** — use mixed attack+benign runs.

## Metrics

| Metric | Definition |
|--------|------------|
| **ASR** | Successful attacks / valid attack episodes (judge-based for real LLM) |
| **Defense rate** | `1 − ASR` |
| **Utility** | Legitimate-task success rate (**requires benign episodes**) |
| **FPR** | Legitimate failures / valid legitimate episodes |
| **Defense cost** | Mean intervention cost (`A0=0.00`, `A1=0.10`, `A2=0.25`, `A3=0.50`) |

Judge/API failures are **excluded** from scored denominators (not counted as successful defenses).

## Limitations

- Independent Judge can be blocked by quotas (e.g. Gemini 429) or billing limits
- Some real-LLM runs used same-provider Target/Judge configurations — report explicitly
- Detector is **heuristic**, not a calibrated probability / SOTA guard model
- Small-N / budget-limited runs are **observational**, not universal robustness proofs
- Some artifacts are `LEGACY_SIMULATION_ONLY`

## Documentation

- [Methodology](docs/methodology.md)
- [Threat model](docs/threat_model.md)
- [Reproducibility](docs/reproducibility.md)
- [Limitations](docs/limitations.md)
- [Results summary](docs/final_results.md)

## Author

**Seyed Mohammadreza Shirazi Matin**  
AI Security · LLM-agent defense  
Email: `shirazimatin@gmail.com`

## Citation

See [`CITATION.cff`](CITATION.cff).

## License

MIT — see [`LICENSE`](LICENSE).
```
