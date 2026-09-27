# Phase 5 — Human-Centered / Trustworthy AI Layer

**Status:** **DONE** (design + measurement hooks; **no empirical human study**, **no CPS validation**).  
**Canonical code:** `src/adapti_guard/evaluation/human_review_packet.py`  
**Upstream:** Phase 3 `EVIDENCE_SCHEMA.yaml` · Phase 4 `evidence_record.json` / `EpisodeTrace`  
**Downstream:** Phase 6 readiness gate · Phase 7 live (human metrics remain **EVIDENCE-BLOCKED**)

---

## 1. Human-Centered Security Decision Layer

At decision time the **existing** runtime stack already exposes (label-blind):

| Signal | Source | Human-facing use |
| --- | --- | --- |
| Detection outcome | `EpisodeTrace.detector_*` / `DetectionResult` | Show hit + indicators (not gold labels) |
| Risk | `RiskAssessment` / `EpisodeTrace.risk_*` | Score + `RiskLevel` + `reasons` |
| Policy / defense | `DefenseDecision` / `EpisodeTrace.policy_*` | Recommended machine action A0–A3 + `policy_reason` |
| Tool gate | `EpisodeTrace.tool_*` | Allow/deny/execute + privileged tool flag |
| Evidence / provenance | `evidence_record.json`, `raw_evidence.json` | condition_id, attack_id, defense_id, hashes, revision |

**Not available as calibrated operator UX today:** human trust score, override workflow persistence, recommended action beyond policy output, calibrated uncertainty beyond detector probability + risk score.

`human_review_packet` serializes **machine decision** + **human-reviewable evidence** only (`packet_from_episode_trace`, `packet_from_evidence_record`).

---

## 2. Trustworthy AI Dimensions (project-defensible)

| Dimension | Operationalization in AdaptiGuard | Status |
| --- | --- | --- |
| **Security** | Judge-ASR, Tool-HASR, defense-attributed outcomes (Track A/B AUDIT) | **SUPPORTED** (live confirmatory, scoped) |
| **Utility** | Utility U + gates (protocol) | **PARTIALLY SUPPORTED** |
| **Reliability / robustness** | Target/judge/verifier failure semantics; offline harness | **PARTIAL** (design + offline); live ext **PLANNED** |
| **Transparency / explainability** | `policy_reason`, risk reasons, trace dict, evidence schema | **DESIGN_ONLY** (+ trace export); not user-study validated |
| **Human oversight** | Insertion point after machine assessment (below) | **DESIGN_ONLY** |
| **Uncertainty awareness** | Detector probability + risk score (bounded [0,1]) | **DESIGN_ONLY** (not calibrated epistemic uncertainty) |
| **Auditability** | condition → attack → defense → target → raw → derived → provenance | **SUPPORTED** (Phase 3–4 contract) |
| **Reproducibility** | `REPRODUCIBILITY.md` + config/dataset hashes | **SUPPORTED** (metadata); full campaign **Phase 6/7** |
| **Cost** | Cost fields in AUDIT / execution metadata where recorded | **PARTIALLY SUPPORTED** |

Removed / not claimed: CPS field validation, automation-bias effect sizes, human trust calibration.

---

## 3. Human-in-the-loop (design)

```text
LLM / Agent output
    ↓
Security Assessment (detector → risk → policy → action/tool gate)  [implemented: CoreDefensePipeline / EpisodeTrace]
    ↓
Risk + Evidence + Explanation (trace + human_review_packet)
    ↓
Human Decision / Review  [NOT IMPLEMENTED — no HITL product layer]
    ↓
Allow / Block / Escalate  [operator action — EVIDENCE-BLOCKED]
```

Phase 5 does **not** add HITL UI or override logging; hooks are documented for Phase 7+ / separate study.

---

## 4. Automation bias / trust calibration

| Concept | Repository support | Status |
| --- | --- | --- |
| Automation bias | No operator study, no override rate data | **EVIDENCE-BLOCKED** |
| Trust calibration | No human trust labels | **EVIDENCE-BLOCKED** |
| Over-reliance on machine risk | Discussed as limitation only | **DESIGN-LEVEL** |

No metrics or empirical results invented.

---

## 5. Explainability / evidence (schema-aligned)

Human reviewer can trace (from existing artifacts):

- attack_id, condition_id, defense_id, target_model_id, judge_id (`evidence_record`)
- target execution block (`raw_evidence.target_execution`)
- defense / verifier outcomes (`raw_evaluation`, episode traces)
- failure semantics (`target_failure`, `judge_status`, protocol § failure)
- derived metrics (separate file; raw not overwritten)
- reproducibility: `repository_revision`, `config_hash`, `dataset_hash`, seed, trial, run_id

Distinctions (see `EVIDENCE_SCHEMA.yaml`):

```text
machine decision ≠ human decision
human-reviewable evidence ≠ empirical human outcome
machine explanation ≠ human understanding
confidence/risk score ≠ human trust
```

---

## 6. CPS / critical infrastructure

Repository has **no** OT/CPS deployment, physical control loop, or critical-infrastructure environment evidence.

| Claim | Status |
| --- | --- |
| Validated for CPS | **FORBIDDEN** (no evidence) |
| Future compatibility (cyber-agent + operator sketch) | **DESIGN-LEVEL** only in this doc |

---

## 7. RQ alignment (no RQ text changes)

| RQ | Human-centered relevance | Trustworthy dimension | Metric / observable | Evidence path | Status |
| --- | --- | --- | --- | --- | --- |
| RQ-Core-1 | Operator needs ASR/utility context | Security, utility | Judge-ASR, Tool-HASR, U | Track A/B AUDIT | **SUPPORTED** (scoped) |
| RQ-Core-2 | Trade-off transparency | Security, utility, cost | ASR, U, cost | AUDIT | **PARTIALLY SUPPORTED** |
| RQ-Ext-1–3 | MT/adaptive/agent review complexity | Reliability, auditability | Per-turn / tool metrics | Offline harness + Phase 7 TBD | **PLANNED** / offline **DESIGN_ONLY** |
| RQ-Ext-4 | — | — | — | Q2 bundle missing | **EVIDENCE_BLOCKED** |
| RQ-Ext-5–6 | — | Auditability | CI / baseline metrics | Design / registry | **PLANNED** |
| **RQ-Trust-1** | Where oversight fits without breaking eval | Human oversight, transparency | Override rate, explainability hooks (TBD) | This doc + `human_review_packet.py` | **DESIGN_ONLY** |

---

## 8. Claims map touchpoint

| Claim | RQ | Dimension | Evidence required | Existing | Status |
| --- | --- | --- | --- | --- | --- |
| C-TRUST-1 | RQ-Trust-1 | Human oversight / CPS | Human study or CPS deployment evidence | Phase 5 design + packet helper only | **DESIGN_ONLY** (not CPS validated) |

Track A/B verdicts and C-CORE-* unchanged.

---

## 9. Implementation scope (Phase 5)

| Component | Action |
| --- | --- |
| `human_review_packet.py` | **Added** — serialize trace / evidence_record |
| `offline_experiment_runner.py` | Writes `human_review_packet.json` from evidence_record |
| Parallel decision engine / UI / human study | **Not added** |

---

## 10. Phase 5 completion gate

- Human-centered layer defined from **real** pipeline fields  
- Trustworthy dimensions bounded by evidence  
- HITL flow design-only where not implemented  
- No fabricated human or CPS empirical claims  
- Phase 1–4 contracts preserved  
