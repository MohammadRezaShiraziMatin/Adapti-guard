# Phase 1 Scientific Spec (Hardening)

**ID:** `PHASE1-SCI-SPEC-0.1`  
**Date (UTC):** 2026-09-14  
**Scope:** Single-turn tool-using agent defense only. Multi-turn out of scope.  
**Live LLM/API:** Forbidden until explicit human approval after this hardening gate.

---

## 1. Primary research question

> Does a **label-blind**, **evidence→risk→policy** runtime that adapts intervention **A0–A3** by **evidence strength**, **risk band**, and **tool/action sensitivity** reduce **harmful tool/action success** versus no defense on a locked independent single-turn benchmark, while keeping benign workflow completion \(U\ge 0.95\) and reporting intervention cost?

---

## 2. Falsifiable hypotheses

| ID | Claim | Falsified if |
| --- | --- | --- |
| **H1** | PHASE1-CORE reduces defense-attributed harmful-action success vs B0 on `phase1_confirm_v1` (McNemar exact two-sided \(p<0.05\) and \(\hat\delta\ge\) MSID 0.20). | Non-significant McNemar, or \(\hat\delta<0.20\), or wins mostly `target_refusal`. |
| **H2** | Under H1 security, PHASE1-CORE retains \(U\ge 0.95\) on benign confirm episodes. | \(U<0.95\) (utility-ineligible). |
| **H3** | PHASE1-CORE is not dominated on (security, utility, mean cost) by every STATIC-A{1,2,3} arm on the same paired episodes. | Some STATIC-A* matches/exceeds security with \(U\ge 0.95\) and \(\le\) mean cost (pre-registered dominance rule in SAP). |
| **H4** | Ablation removing tool-sensitivity or evidence gating worsens security–utility attribution vs full CORE (directional; confirmatory only if pre-registered secondary). | Ablation equals CORE on primary security and utility within pre-registered equivalence margin (secondary). |

No hypothesis claims “solves prompt injection,” SOTA, production readiness, or broad robustness.

---

## 3. Contribution (split)

### Engineering contribution (implemented)

Causal single-turn stack: observable context → Phase-1 evidence detector → risk bands → action-sensitive A0–A3 → real mock-tool deny/block → label-blind traces; paired baseline factories; frozen packs + locks.

### Scientific contribution (to be tested, not assumed)

An **evaluable protocol** for **cost-aware adaptive runtime intervention** on **tool-mediated harmful actions**, with intervention-attributed endpoints (refusal ≠ win), independent confirm TEST, ablations for attribution, and pre-registered MSID/power.

### Novelty

**Not claimed** in this spec. Literature positioning remains audit-only until a cited related-work pass supports a narrow novelty claim.

---

## 4. Non-goals

Multi-turn; live API in this hardening pass; rewriting VNEXT FAIL; detector/policy fit on confirm TEST; inflating N after outcomes.

---

## 5. Binding companions

| Doc | Role |
| --- | --- |
| `PHASE1_THREAT_MODEL.md` | Threat model |
| `PHASE1_STATISTICAL_PLAN.md` | Endpoints, MSID, N, costs |
| `PHASE1_DETECTOR_STUDY.md` | Detector-only metrics |
| `PHASE1_ABLATION_PROTOCOL.md` | Attribution arms |
| `PHASE1_GENERALIZATION_PLAN.md` | Secondary generalization |
| `PHASE1_SCIENTIFIC_GATE.md` | Final SH1–SH8 audit |
| `configs/phase1_detector_lock.json` | Detector lock |
| `datasets/frozen/phase1_confirm_v1/` | Confirmatory TEST |
