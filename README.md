# Harmonized Security–Utility–Cost Evaluation of Runtime LLM-Agent Defenses

**ADAPTI-GUARD** — research implementation and evaluation codebase.

## Overview

LLM-based agents that consume external context and invoke tools face prompt-injection and related manipulation risks. Runtime defenses can reduce attack success but may also affect legitimate-task utility and intervention cost. Attack success rate alone is insufficient when comparing policies under mixed attack and benign workloads.

This repository implements **ADAPTI-GUARD**, a modular runtime defense testbed with discrete intervention levels (L0–L3), risk-aware policy control, and cost-aware escalation/de-escalation pathways. It also provides a **harmonized evaluation protocol** (`harmonized_v1.0.0`) that compares fixed and adaptive policies on a shared episode population using unified security, utility, and cost metrics.

The study is evaluation-oriented: it documents implemented mechanisms, measured outcomes on defined workloads, and explicit limitations. It does not claim guaranteed security, universal robustness, or superiority over external methods.

> **Historical project title:** *Adaptive and Utility-Aware Defense Against Evolving Prompt Injection Attacks in LLM-Based Agents* — earlier terminology for the same implementation lineage.

---

## Research Focus

The study evaluates runtime defense behavior across five primary policy families:

| Policy | Implementation |
|--------|----------------|
| **Fixed L0** | Constant defense level 0 (`fixed_l0`) |
| **Fixed L1** | Constant defense level 1 (`fixed_l1`) |
| **Fixed L2** | Constant defense level 2 (`fixed_l2`) |
| **Fixed L3** | Constant defense level 3 (`fixed_l3`) |
| **Adaptive** | Dynamic level updates via `PolicyUpdateEngine` (`full_adaptive` and ablations) |

### Defense levels (implementation)

Levels L0–L3 map to actions A0–A3 in `core/models.py` and `defense/action_layer.py`:

| Level | Action | Behavior |
|-------|--------|----------|
| L0 | A0 — NO_INTERVENTION | No modification; full tool access |
| L1 | A1 — SANITIZE | Content sanitization; tool access retained |
| L2 | A2 — TOOL_RESTRICTION | Tool access restricted |
| L3 | A3 — BLOCK | Interaction blocked |

`DefensePolicyEngine` selects the applied action from the current defense level and risk assessment (LOW / MEDIUM / HIGH). For MEDIUM risk, applied intervention escalates with level; HIGH risk triggers strong protection regardless of adaptive level.

Adaptation (`FeedbackEngine`, `PolicyUpdateEngine`) adjusts the discrete level after sustained attack pressure (escalation) or legitimate pressure (de-escalation, subject to a cost gate). Both pathways are implemented; documented harmonized results under default thresholds show escalation on the primary workload and **no empirically activated de-escalation** under those conditions.

---

## Evaluation Framework

Harmonized evaluation (`src/adapti_guard/experiments/harmonized_runner.py`) runs all compared policies through one shared execution path; policy selection is the intentional difference between methods.

Supported elements (where implemented in this repository):

| Element | Description |
|---------|-------------|
| **Mixed workloads** | Attack and legitimate episodes on a fixed schedule (default W1: 75% attack / 25% legitimate, `A A A L`) |
| **Legitimate tasks** | Fixed benign task pool (`BENIGN_TASKS` in harmonized runner) |
| **Attack tasks** | Payloads from a frozen stream (`results/common_attack_stream.json`) |
| **Frozen attack stream** | Generated once by `scripts/generate_attack_stream.py`; SHA256 recorded in `REPRODUCIBILITY.md` |
| **Evolving attack generation** | `AdaptiveAttacker` evolves families and within-family sophistication during stream generation only |
| **Harmonized replay** | Primary comparison replays the frozen stream identically for every policy |
| **Sensitivity analysis** | Threshold and workload sweeps via `scripts/run_q1_sensitivity_v1.py` |
| **De-escalation diagnostic** | `scripts/run_q1_deescalation_diagnostic_v1.py` |
| **Ablations** | `escalation_only`, `de_escalation_only`, `no_cost_gate` |
| **Validation** | Fairness checks, Pareto analysis, transition statistics (`harmonized_validation.py`) |

**Not part of the primary harmonized protocol:**

- Defense-aware adaptive attackers (attacker does not observe defense policy during replay)
- Multi-seed variance analysis for the primary harmonized bundle (seed identifier 42 marks a deterministic protocol; population inference from seed variance is not established)
- External published defense systems as primary baselines

### Attack evaluation categories

| Category | Role in this repository |
|----------|-------------------------|
| **Known / template attacks** | `AdaptiveAttacker` families: direct injection, indirect injection, context manipulation, tool output injection |
| **Frozen stream attacks** | Fixed episode payloads in `common_attack_stream.json` used for harmonized comparison |
| **Evolving attacks** | Attacker state evolves during stream **generation**; harmonized evaluation **replays** the frozen result |

---

## Metrics

Definitions: `src/adapti_guard/evaluation/metrics.py` (`metrics.py@v1`). Harmonized denominators: `harmonized_validation.py`.

### Security

| Metric | Status |
|--------|--------|
| Attack Success Rate (ASR) | Implemented |
| Defense Rate | Implemented (1 − ASR) |
| Precision, Recall, F1 | Implemented |
| FPR | Implemented |
| FNR | Implemented in harmonized summaries (`FN / N_a`) |
| Security Score | Implemented (mean episode security score) |
| Balanced Accuracy | Implemented |

### Utility

| Metric | Status |
|--------|--------|
| Utility (legitimate success rate) | Implemented |
| Legitimate-task failure / degradation | Captured via legitimate success flags and FPR |
| Reward | Implemented (composite episode reward) |

### Adaptivity

| Metric | Status |
|--------|--------|
| Escalation count | Recorded in transition statistics |
| De-escalation count | Recorded in transition statistics |
| Transition count | Recorded in transition statistics |
| Recovery behavior | Not reported as a standalone primary metric |

### Cost / efficiency

| Metric | Status |
|--------|--------|
| Defense cost | Implemented (mean per-episode intervention cost) |
| Latency | Field exists on episode model (`latency_ms`); **not** a primary harmonized reported outcome |
| Token / compute overhead | **Not** implemented as a primary harmonized metric |

---

## Experimental Design

### Baseline / fixed policies

Four constant-level policies (`fixed_l0`–`fixed_l3`) hold defense level fixed for all episodes.

### Adaptive policy and ablations

| Configuration | Purpose |
|---------------|---------|
| `full_adaptive` | Escalation + de-escalation with cost gate |
| `escalation_only` | De-escalation pathway disabled |
| `de_escalation_only` | Escalation pathway disabled (ablation label) |
| `no_cost_gate` | Cost gate removed (ablation) |

### Evaluation tracks

| Track | Entry point | Artifact location |
|-------|-------------|-------------------|
| Harmonized primary | `scripts/run_q1_harmonized_v1.py` | `results/phase8/q1_harmonized_v1/` |
| Threshold sensitivity | `scripts/run_q1_sensitivity_v1.py` | `results/phase8/q1_threshold_sensitivity_v1/` |
| Workload sensitivity | `scripts/run_q1_sensitivity_v1.py` | `results/phase8/q1_workload_sensitivity_v1/` |
| De-escalation diagnostic | `scripts/run_q1_deescalation_diagnostic_v1.py` | `results/phase8/q1_deescalation_diagnostic_v1/` |
| Final validation assembly | `scripts/assemble_q1_final_validation_v1.py` | `results/phase8/q1_final_validation_v1/` |
| MVP simulator run | `run_mvp.py` | `results/` (regenerable) |
| NotInject detector validation | `scripts/evaluate_notinject_validation.py` | `experiments/runs/` |

Detector development runs are tracked separately in `experiments/registry.csv` and `experiments/runs/EXP-XXX_VX/`.

Primary harmonized configuration (from `REPRODUCIBILITY.md`):

- 100 episodes, W1 schedule (75 attack / 25 legitimate)
- Thresholds: attack=2, legitimate=2
- Seed identifier: 42 (deterministic given frozen stream)
- Runner: `harmonized_v1.0.0`

---

## Results and Artifacts

Numerical outcomes are stored in versioned artifact bundles — not duplicated here.

| Category | Location | Notes |
|----------|----------|-------|
| **Primary harmonized results** | `results/phase8/q1_harmonized_v1/` | Eight internal policies, shared population |
| **Sensitivity results** | `results/phase8/q1_threshold_sensitivity_v1/`, `q1_workload_sensitivity_v1/` | Threshold and workload sweeps |
| **Diagnostic results** | `results/phase8/q1_deescalation_diagnostic_v1/` | De-escalation pathway analysis |
| **Consolidated validation** | `results/phase8/q1_final_validation_v1/` | Assembled validation summary |
| **Attack stream** | `results/common_attack_stream.json` | Frozen; do not modify |
| **Experiment provenance** | `experiments/runs/` | Git commit, hashes, commands, environment |

Typical bundle contents include `run_manifest.json`, `harmonized_results.json`, `validation.json` or `consolidated_validation.json`, and transition statistics where applicable.

**Interpretation constraints** (from validation outputs; see artifacts for details):

- Escalation was observed on the primary W1 workload; de-escalation was not activated under default conditions.
- `full_adaptive` matched `escalation_only` for observed transitions under default settings on W1.
- Pareto and pairwise comparisons are limited to the evaluated stream and workloads.
- Generalization beyond the frozen stream is not established.

Frozen artifacts (Phase 7, Phase 8A/8B bundles, `common_attack_stream.json`) must not be overwritten. New runs require versioned output directories.

---

## Reproducibility

Authoritative reference: **`REPRODUCIBILITY.md`**

### Environment setup

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Unix:     source .venv/bin/activate
pip install -r requirements.txt
```

Tested with Python 3.12 (see `REPRODUCIBILITY.md` for recorded environment). The pinned dependency set is large; platform-specific packages (e.g., PyTorch/CUDA) may require local verification.

### Testing

```bash
# Windows PowerShell
$env:PYTHONPATH="."
pytest

# Unix
PYTHONPATH=. pytest
```

Tests verify software behavior and research infrastructure; they are not substitutes for full evaluation runs.

### Experiment execution

```bash
python scripts/run_q1_harmonized_v1.py
python scripts/run_q1_sensitivity_v1.py
python scripts/run_q1_deescalation_diagnostic_v1.py
```

Re-running experiments creates new artifacts. Local `results/` is gitignored by default (see `.gitignore`). External datasets under `dataset/` are gitignored and may be required for NotInject scripts.

---

## External Evaluation Integrations

### Garak

`garak_adapter.py` provides a Garak `Generator` adapter around `DefensePipeline`. `garak==0.16.0` is listed in `requirements.txt`.

Garak is an **optional** external evaluation hook. It is **not** the primary harmonized evaluation path, and verified Garak benchmark results are **not** bundled as the primary result set.

### Inspect

`inspect-test/adapti_guard_eval.py` defines an Inspect AI task, solver, and scorer using `DefensePipeline`. This is an optional integration; primary harmonized results use the internal simulator.

### Promptfoo

The former `promptfoo-test/` integration has been **removed** and is not documented as active.

---

## Scientific Scope

This repository evaluates runtime defense behavior under the implemented experimental protocols and artifact bundles described above.

In scope:

- Discrete L0–L3 intervention under a rule-based detector and risk engine
- Fixed-vs-adaptive comparison on harmonized mixed workloads
- Security–utility–cost tradeoff analysis with explicit metric definitions
- Sensitivity and ablation studies on documented configurations
- Reproducible provenance for tracked experiment runs

Out of scope / not supported by primary evidence:

- Universal prompt-injection protection
- Robustness against defense-aware adaptive attackers
- State-of-the-art claims against external methods
- Generalization beyond evaluated attack populations and workloads

---

## Limitations

- **Evaluation population:** Primary harmonized runs use a single deterministic protocol on a frozen 100-episode stream.
- **Attack coverage:** Template families and frozen payloads; limited real-world variant coverage.
- **Adaptive attacker scope:** Attacker evolution occurs at stream generation; harmonized replay is non-interactive and not defense-aware.
- **External benchmarks:** Garak and Inspect hooks exist; primary reported outcomes use the internal harmonized path.
- **Model dependence:** Rule- and heuristic-based detection and simulation; transfer to LLM-backed production stacks requires re-validation.
- **Statistical scope:** Seed-variance and population-level inference are not established for the primary harmonized bundle.
- **Adaptation:** De-escalation is implemented but was not empirically supported under default evaluation conditions in documented bundles.
- **Computational metrics:** Latency and token overhead are not primary harmonized outcomes.

---

## Research Contributions

Conservative framing supported by implementation and artifacts:

1. **Runtime defense evaluation framework** — modular pipeline (detection, risk, policy, action, adaptation) with discrete intervention levels L0–L3.
2. **Harmonized Security–Utility–Cost comparison** — versioned protocol comparing fixed and adaptive policies on identical episode populations with unified metrics and validation checks.
3. **Empirical analysis of adaptive intervention** — measured escalation, ablation behavior, sensitivity sweeps, and documented null results (e.g., absent de-escalation under default conditions) under mixed workloads.

These describe what the repository implements and measures; they are not claims of guaranteed security or dominance over all existing defenses.

---

## Repository Structure

```text
.
├── README.md
├── REPRODUCIBILITY.md
├── requirements.txt
├── garak_adapter.py              # optional Garak integration
├── pytest.ini
├── run_mvp.py
├── src/adapti_guard/             # core implementation
├── scripts/                      # experiment and dataset scripts
├── tests/                        # unit and integration tests
├── experiments/                  # registry, protocols, run provenance
│   ├── registry.csv
│   └── runs/EXP-XXX_VX/
├── inspect-test/                 # optional Inspect AI hook
└── results/                      # evaluation artifacts (gitignored)
    ├── common_attack_stream.json
    └── phase8/
```

Gitignored local directories (`dataset/`, `backups/`, `BIPIA/`) may exist for development but are not required to understand the harmonized evaluation layout.

---

## Status

| Area | Status |
|------|--------|
| **Implementation** | Core pipeline, harmonized runner, sensitivity and diagnostic scripts present |
| **Evaluation** | Primary harmonized bundle and sensitivity/diagnostic artifact paths documented in `REPRODUCIBILITY.md` |
| **Artifacts** | Frozen bundles under `results/phase8/`; provenance under `experiments/runs/` |
| **Reproducibility** | Scripts, manifests, and `REPRODUCIBILITY.md` provided; local `results/` and external datasets may need to be present or regenerated |

---

## Citation

Citation information will be added with the final manuscript. Until then, refer to this repository and the artifact paths listed in `REPRODUCIBILITY.md`.
