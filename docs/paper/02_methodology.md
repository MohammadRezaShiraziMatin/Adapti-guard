# Methodology

AdaptiGuard evaluates **runtime intervention policies** for LLM agents under prompt-injection-style threats.

## Pipeline

1. **Detection** — heuristic pattern scores (`PromptInjectionDetector`)
2. **Risk** — LOW / MEDIUM / HIGH (`RiskEngine`)
3. **Policy** — maps risk + defense level → action A0–A3 (`DefensePolicyEngine`)
4. **Action** — no-op / sanitize / tool restriction / block (`DefenseActionLayer`)
5. **Adaptation** — escalate/de-escalate discrete level after pressure thresholds (`PolicyUpdateEngine`), with cost-gated de-escalation
6. **Evaluation** — simulation outcomes or real Target LLM + independent Judge

## Policies

| Label | Behavior |
|-------|----------|
| Fixed L0–L3 | Constant defense level |
| Full adaptive (B3/B6) | Counter-based level updates |
| Ablations | escalation-only, de-escalation-only, no-cost-gate |

B6 is an **implementation alias** of B3 (`get_defense_fn`).

## Evaluation tracks

| Track | Entry | Notes |
|-------|-------|-------|
| Harmonized simulation | `scripts/run_q1_harmonized_v1.py` | Frozen stream replay; labeled simulation |
| Real LLM | `experiments/REAL_LLM_EVAL/run.py` | Target + Judge when APIs allow |
| Statistics | `src/adapti_guard/evaluation/statistics.py` | Bootstrap, McNemar, Holm |

## Costs

A0=0.00, A1=0.10, A2=0.25, A3=0.50.

## Scientific rules

- Do not convert failed Judge calls into ASR=0 / Defense=1
- Attack-only datasets cannot support utility/FPR claims
- Simulation ASR ≠ judge ASR
