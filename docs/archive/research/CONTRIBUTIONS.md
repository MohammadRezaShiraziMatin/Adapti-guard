# ADAPTI-GUARD — Contribution Audit

**Phase 1 Audit | Date:** 2026-09-02

Contributions classified as **Strong / Moderate / Weak / Unsupported**.  
Engineering artifacts are separated from scientific claims.

---

## Claimed vs Defensible Contributions

### C1 — Harmonized mixed-workload evaluation protocol

| Type | Methodological |
|------|----------------|
| **Claim** | Unified episode path comparing policies on shared attack stream + benign schedule |
| **Evidence** | `harmonized_runner.py`, W1/W2/W3 schedules, frozen stream |
| **Rating** | **Moderate** |
| **Caveat** | Simulation ASR is circular (regex markers); fixed vs adaptive paths differ (risk gating bypass for fixed levels) |
| **Publication gate** | Real LLM judge on same schedule |

### C2 — Counter-based defense-level adaptation (L0–L3)

| Type | Scientific (mechanism) |
|------|------------------------|
| **Claim** | Hysteresis controller escalates/de-escalates discrete defense level |
| **Evidence** | `PolicyUpdateEngine`, `FeedbackEngine` — code complete |
| **Rating** | **Weak** as novelty (hysteresis is classical); **Moderate** as empirical question |
| **Caveat** | Not Bayesian; reward unused; de-escalation structurally blocked on LOW-risk benign |
| **Publication gate** | Real LLM ablation showing adaptive beats fixed |

### C3 — Utility-aware cost gate

| Type | Scientific |
|------|------------|
| **Claim** | De-escalation gated on defense cost to preserve utility |
| **Evidence** | `cost_penalty >= 0.50` in FeedbackEngine |
| **Rating** | **Weak** — single hardcoded threshold tied to BLOCK cost only |
| **Publication gate** | Ablation C vs A on real LLM with FPR + utility |

### C4 — benchmark_q1 dataset (15K samples)

| Type | Methodological |
|------|----------------|
| **Claim** | Multi-category security corpus with provenance |
| **Evidence** | `statistics.json`, verified hashes, 15,053 samples |
| **Rating** | **Moderate** (aggregation, not novel collection) |
| **Caveat** | Agent/tool underrepresented; 5 upstream sources UNAVAILABLE |
| **Publication gate** | Dataset card + DOI; fix category gaps |

### C5 — Blind LLM-judge evaluation pipeline

| Type | Methodological |
|------|----------------|
| **Claim** | Independent judge without defense metadata leakage |
| **Evidence** | `llm_judge.py`, tests in `test_blind_judge.py` |
| **Rating** | **Moderate** — good practice, not novel method |
| **Caveat** | Judge fail-open on API error; no human κ validation |
| **Publication gate** | Successful EXP-004 + human calibration subset |

### C6 — Adaptive defense against evolving attacks

| Type | Scientific |
|------|------------|
| **Claim** | Defense adapts to evolving adversary |
| **Evidence** | `AdaptiveAttacker` — 12 static templates; frozen replay |
| **Rating** | **Unsupported** |
| **Action** | **Remove or downgrade** to "diverse attack corpus" |

### C7 — Agent / tool security defense

| Type | Scientific |
|------|------------|
| **Claim** | Protects tool-using agents |
| **Evidence** | A2 action exists; `tool_sensitive=False` everywhere |
| **Rating** | **Unsupported** |
| **Action** | **Remove from title** until AgentDojo eval |

### C8 — Strong detection / SOTA performance

| Type | Scientific |
|------|------------|
| **Claim** | High F1 detection |
| **Evidence** | EXP-017 F1=0.80 smoke; EXP-018 F1=0.41 held-out |
| **Rating** | **Unsupported** for generalization claim |
| **Action** | Scope to "heuristic pre-filter" not "detector SOTA" |

---

## Engineering Contributions (Not Scientific Novelty)

| Artifact | Value | Scientific novelty |
|----------|-------|-------------------|
| Python package structure | High for reproducibility | None |
| EXP-004 orchestrator | High | None |
| Statistical tooling | Moderate | None |
| Config YAML | Standard | None |
| Documentation / audit trail | High integrity | None |

---

## Rewritten Defensible Contribution List (for manuscript)

1. **(Methodological — Moderate)** A harmonized evaluation protocol for runtime LLM defenses that couples attack ASR (LLM-judge labeled) with benign utility under explicit mixed workloads (W1: 75/25), with frozen attack streams and provenance-tracked datasets.

2. **(Scientific — Weak/Moderate, evidence pending)** A counter-based defense-level controller (L0–L3) with cost-gated de-escalation that adjusts intervention intensity based on sustained attack vs benign pressure — evaluated against fixed-level policies on real LLM outputs.

3. **(Methodological — Moderate)** benchmark_q1: a 15,053-sample, hash-verified aggregation of prompt injection, jailbreak, RAG, and benign tasks with documented category imbalance and split hygiene.

4. **(Methodological — Moderate)** An open reproduction package with blind judge protocol, provenance classification (`real_llm_judge` vs `LEGACY_SIMULATION_ONLY`), and pre-registered statistical tests.

**Do not list as contributions:** Bayesian adaptation, agent tool defense, SOTA beating, evolving attacker co-training.

---

## Contribution Strength Summary

| # | Contribution | Strength |
|---|--------------|----------|
| 1 | Harmonized eval protocol | Moderate |
| 2 | Counter-based adaptation | Weak (pending real LLM) |
| 3 | Cost gate | Weak |
| 4 | benchmark_q1 | Moderate |
| 5 | Judge pipeline | Moderate |
| 6 | Evolving attack defense | Unsupported |
| 7 | Agent security | Unsupported |
| 8 | Detection SOTA | Unsupported |
