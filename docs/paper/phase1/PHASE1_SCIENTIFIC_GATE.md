# Phase 1 Scientific Gate (SH1–SH8)

**ID:** `PHASE1-SCI-GATE-0.1`  
**Date (UTC):** 2026-09-14  
**Live LLM/API during hardening:** **0**

Official VNEXT confirmation remains **FAIL** (pack `523c8818…`, MSID 0.20, `qualified_win=false`).

---

## Gate table

| Stage | Requirement | Classification | Evidence |
| --- | --- | --- | --- |
| SH1 RQ + contribution | One RQ; 2–4 falsifiable Hs; eng vs sci split; no unsupported novelty | **CLOSED** | `PHASE1_SCIENTIFIC_SPEC.md` |
| SH2 Threat model | Capabilities, limits, surfaces, assets, harmful-action, trust boundary; family mapping | **CLOSED** | `PHASE1_THREAT_MODEL.md` |
| SH3 Benchmark | DEV→VAL→LOCKED TEST; independent; powered N; no VNEXT/LayerA mutation | **CLOSED** | `phase1_confirm_v1` SHA `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` (61/61); holdout retained as pilot |
| SH4 Detector study | Independent metrics; lock before confirm live; no TEST tuning | **CONTROLLED** | Lock + DET study; offline metrics exist for pilot/LayerA; confirm offline report optional/no-tune |
| SH5 Baselines + ablations | Fair B0/STATIC-A*; pre-registered ablations | **CLOSED** | Factories + `PHASE1_ABLATION_PROTOCOL.md` |
| SH6 Cost + power | MSID 0.20; costs locked; prospective N=61 | **CLOSED** | `PHASE1_STATISTICAL_PLAN.md` (`PHASE1-SAP-0.2`) |
| SH7 Generalization | ≥1 independent axis designed; no overclaim | **CONTROLLED** | `PHASE1_GENERALIZATION_PLAN.md` (design; not live-run) |
| SH8 Final audit | Claims ≤ evidence; frozen integrity | **CLOSED** (hardening) | This file |

---

## Gap taxonomy

| Gap | Class |
| --- | --- |
| Confirmatory live defense evaluation | **OPEN** (needs human approval) |
| External published baselines beyond STATIC-A* | **OPEN** (not required to start live; note limitation) |
| Novelty vs literature | **OPEN** (explicitly not claimed) |
| Confirm-pack semantic depth vs large human red-team corpora | **CONTROLLED** (template-authored; contamination-screened; threat-mapped) |
| Pack-fit from VNEXT diagnostics | **CONTROLLED** (VNEXT not confirm TEST) |

**BLOCKER for live API:** none scientific beyond **explicit human approval**.

---

## Integrity checks

| Artifact | Status |
| --- | --- |
| VNEXT `523c8818…` | Unchanged; FAIL preserved |
| Layer A TEST `47b975f7…` | Unchanged |
| MSID 0.20 | Preserved |
| Detector lock | In force |
| Confirm TEST | Frozen `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` |
| Multi-turn | Not implemented |

---

## Next action

`READY_FOR_HUMAN_APPROVAL — no live API executed.`
