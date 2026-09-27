# Unified experiment protocol (Phase 3)

**Framework:** [`UNIFIED_RESEARCH_FRAMEWORK.md`](UNIFIED_RESEARCH_FRAMEWORK.md) · **Matrix:** [`EXPERIMENT_MATRIX.yaml`](EXPERIMENT_MATRIX.yaml) · **Evidence:** [`EVIDENCE_SCHEMA.yaml`](EVIDENCE_SCHEMA.yaml).

**No live execution** from this document. Phase 7 requires gates below.

---

## 1. Preconditions

| Check | Contract |
| --- | --- |
| Configuration valid | `config_hash` recorded; schema fields in `EVIDENCE_SCHEMA.yaml` |
| `condition_id` valid | Row in `EXPERIMENT_MATRIX.yaml` |
| Dataset valid | `dataset_id` + hash for frozen packs; no mutation of `datasets/frozen/**` |
| Target identified | `target_model_id` |
| Judge / verifier identified | `judge_id`; **Target ≠ Judge** on confirmatory live (`target_ne_judge: true`) |
| Deterministic verifier | Tool outcome / `success_condition` where Tool-HASR applies (P1 threat model) |
| LLM judge | `real_llm_judge` mode per archive metrics doc — diagnostic ASR |
| Seed / trial | Required for repeated designs (Phase 7); logged when run |
| Evidence destination | `evidence_path` writable; `evidence_type` set |

---

## 2. Execution sequence

```text
Load Configuration
→ Resolve condition_id (matrix)
→ Prepare Attack (attack_id / episode)
→ Apply Defense (defense_id)
→ Execute Target (target_model_id)
→ Evaluate (deterministic verifier + optional LLM judge)
→ Record Raw Evidence (evidence_type: live_raw | offline_fixture)
→ Compute Metrics (derived)
→ Compute Statistics (derived; label fixtures non-empirical)
→ Produce Finding
→ Map to RQ / Claim (CLAIMS_MAP.md)
```

**Target vs Judge**

| Role | Responsibility | Leakage control |
| --- | --- | --- |
| Target | Generation / tool request | No access to gold labels at runtime |
| Judge | `attack_success`, utility scoring | Different `model_id`; no treatment arm labels (confirmatory) |
| Verifier | Tool allow/deny, privileged tool harm | Rule-based; independent of judge prompt |

Config enforcement: `configs/models.yaml` separates keys; `execution_metadata.py` records role + id (Phase 4).

---

## 3. Failure semantics

Failures are recorded; **never** silently mapped to scientific PASS/FAIL.

| Failure | Record as | Affects verdict? |
| --- | --- | --- |
| Provider / API error | `outcome: provider_failure` | Run excluded or BLOCKED |
| Timeout | `outcome: timeout` | Run excluded |
| Invalid model response | `outcome: invalid_response` | Per protocol |
| Missing evidence file | `outcome: missing_evidence` | BLOCKED analysis |
| Judge failure | `outcome: judge_failure` | Run excluded |
| Verifier failure | `outcome: verifier_failure` | Run excluded |
| Config / condition mismatch | `outcome: config_mismatch` | BLOCKED |
| Budget / gate | `outcome: budget_or_gate` | No live spend |

---

## 4. Metrics & statistics (mapping)

Definitions: [`METRICS_AND_STATISTICS.md`](METRICS_AND_STATISTICS.md) → archive SAP.

| Class | Examples | Aggregation | Stats |
| --- | --- | --- | --- |
| Security | Judge-ASR, Tool-HASR, defense rate | Per episode / arm | McNemar, δ̂, MSID |
| Utility | Utility U, benign preservation | Per episode | Co-primary gate |
| Cost | Tokens, latency, API cost | Per run | Descriptive / paired (Phase 7) |
| Robustness | Cross-condition deltas | Per condition_id | CI, effect size (when designed) |

`tests/test_statistics.py` validates **pipeline only** — not empirical results.

---

## 5. RQ → condition map (summary)

| RQ | condition_id(s) | Evidence today |
| --- | --- | --- |
| RQ-Core-1/2 | COND-TRACK-A-*, COND-TRACK-B-* | LIVE historical AUDIT |
| RQ-Ext-1 | COND-E1-STATEFUL-OFFLINE | OFFLINE tests |
| RQ-Ext-2 | COND-E2-ADAPTIVE-OFFLINE | OFFLINE tests |
| RQ-Ext-3 | COND-E3-AGENT-OFFLINE | OFFLINE tests |
| RQ-Ext-4 | COND-EXT4-CROSSMODEL | BLOCKED |
| RQ-Ext-6 | COND-EXT6-BASELINE | PLANNED |
| Phase 7 extensions | COND-PHASE7-CAMPAIGN | BLOCKED |

---

## 6. Live execution gate (Phase 7 only)

All must pass before API spend:

```text
Phase 1–3 contracts valid (validators)
Experiment matrix + condition_id locked
Target ≠ Judge configured
Evidence schema + paths defined
Dataset locked (hash)
Budget human-authorized (LIVE_EVALUATION_GATE.md / Q1 budget locks)
Provider configured
Run configuration hash recorded
```

**Current:** `MASTER_PROMPT` API=0; Phase 7 **BLOCKED**.

---

## 7. Layer reference (status)

| Layer | Doc / path | Status |
| --- | --- | --- |
| Confirmatory | Track A/B AUDITs | LIVE (immutable) |
| P1 mechanism live | `LIVE_EVALUATION_PROTOCOL.md` | DESIGN |
| Extensions | `EXTENSION_STATUS_AUDIT.md` | OFFLINE harness |
