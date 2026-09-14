# Contribution Statement

## Research contributions

1. **Harmonized runtime intervention evaluation** for LLM applications: discrete defense levels
   (L0–L3 / A0–A3) compared under a shared real-LLM + independent-judge protocol with
   reproducible manifests (seed, env, model config, dataset hash).
2. **Adaptive defense controller (B3 / ADAPTI-GUARD)** that escalates/de-escalates intervention
   from risk and feedback, evaluated against no-defense (B0), simple rule blocking (B1), and
   fixed layered policies (B2_L1–L3).
3. **Security–utility–cost metric suite** for mixed workloads: ASR / Defense Rate / FNR / FPR /
   Precision / Recall / F1 / balanced accuracy / reward, with bootstrap ASR CIs, category and
   robustness-family breakdowns, latency, tokens, and API cost estimates.

## Novelty argument

Existing prompt-injection defenses are often detector-only (block/allow) or training-time
alignments. ADAPTI-GUARD focuses on **policy-level runtime adaptation** with explicit
**security–utility–cost** accounting and a **judge-based** outcome definition that separates
Target generation from Attack Success labeling. Novelty is systems/evaluation of adaptive
intervention policies—not a claim of a new SOTA detector architecture.

## Experimental comparison (intended paper framing)

| Family | IDs | Claim tested |
|--------|-----|--------------|
| None | B0 | Target refusal / undefended ASR floor |
| Simple | B1 | Rule detector + block |
| Layered fixed | B2_L1–L3 | Constant intervention intensity |
| Adaptive | B3 | Risk-aware level selection vs fixed |
