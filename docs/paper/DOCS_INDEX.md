# Docs index (dual-track era)

Canonical scientific status is [`DUAL_TRACK_STATUS.md`](DUAL_TRACK_STATUS.md), not older PHASE/Q1 closeouts. **Do not delete files listed as ARCHIVE / SUPERSEDED** — they are historical evidence. This index does not rewrite the workshop manuscript.

Contributor entry: [`docs/START_HERE.md`](../START_HERE.md).

---

## ACTIVE (keep)

Use these for current claims, merge advice, and workshop FAIL text.

### Dual-track (current)

| Path | Role |
| --- | --- |
| [`../START_HERE.md`](../START_HERE.md) | Read order |
| [`DUAL_TRACK_STATUS.md`](DUAL_TRACK_STATUS.md) | Track A FAIL vs Track B scoped LIVE |
| [`CLAIMS_DUAL_TRACK.md`](CLAIMS_DUAL_TRACK.md) | Allowed / forbidden dual-track wording |
| [`RELEASE_NEXT_FA.md`](RELEASE_NEXT_FA.md) | Matin next-step note + CLOSE / SKIP |
| [`../experiments/MASTER_PROMPT.md`](../experiments/MASTER_PROMPT.md) | Durable supervisor constraints |
| [`../experiments/RESEARCH_LOG.md`](../experiments/RESEARCH_LOG.md) | Dated diary (including 2026-09-14 dual-track) |

### Workshop packet (`workshop_vnext_fail/` core)

Track A negative-result package. Numbers must match the VNEXT AUDIT. Not a venue submit.

| Path | Role |
| --- | --- |
| [`workshop_vnext_fail/README.md`](workshop_vnext_fail/README.md) | Packet hub |
| [`workshop_vnext_fail/MANUSCRIPT.md`](workshop_vnext_fail/MANUSCRIPT.md) | Workshop/preprint text |
| [`workshop_vnext_fail/CLAIMS_MAP.md`](workshop_vnext_fail/CLAIMS_MAP.md) | Track A + Layer A allowed/forbidden |
| [`workshop_vnext_fail/APPENDIX_HASHES.md`](workshop_vnext_fail/APPENDIX_HASHES.md) | Frozen-pack hashes |
| [`workshop_vnext_fail/CONFIGS_SNAPSHOT.md`](workshop_vnext_fail/CONFIGS_SNAPSHOT.md) | YAML / Target≠Judge / cache |
| [`workshop_vnext_fail/CITATION.md`](workshop_vnext_fail/CITATION.md) | Citation for the FAIL packet |
| [`workshop_vnext_fail/PR_STACK.md`](workshop_vnext_fail/PR_STACK.md) | PR roles + CLOSE / SKIP (no merge) |
| [`workshop_vnext_fail/SUBMISSION_PACKET.md`](workshop_vnext_fail/SUBMISSION_PACKET.md) | Human cover letter (not an upload) |
| [`workshop_vnext_fail/SUBMIT_NEXT_FA.md`](workshop_vnext_fail/SUBMIT_NEXT_FA.md) | Track A Persian submit note |
| [`workshop_vnext_fail/DONE_CHECKLIST.md`](workshop_vnext_fail/DONE_CHECKLIST.md) | Agent-closable workshop items |
| [`workshop_vnext_fail/verify_manuscript_facts.py`](workshop_vnext_fail/verify_manuscript_facts.py) | Offline fact verifier |

Layer A CLOSED wording still in force: [`CLAIMS_CHECKLIST_LAYER_A.md`](CLAIMS_CHECKLIST_LAYER_A.md), [`04_results_layer_a_diagnostic.md`](04_results_layer_a_diagnostic.md).

Track B protocol locks (not LIVE numbers): `docs/experiments/PHASE1_SCIENTIFIC_SPEC.md`, `PHASE1_THREAT_MODEL.md`, `PHASE1_STATISTICAL_PLAN.md`, `PHASE1_SCIENTIFIC_GATE.md`, `PHASE1_ABLATION_PROTOCOL.md`, `VNEXT_PROTOCOL.md` / addendum / MSID (Track A protocol).

### Live AUDIT pointers only (do not edit)

| Track | Path |
| --- | --- |
| A FAIL | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` |
| B scoped | `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md` |

Do not edit those folders, JSONL under `experiments/real_llm_eval/`, or VNEXT FAIL numbers.

---

## ARCHIVE / SUPERSEDED (do not delete)

Historical or overlapping status notes. They are **not** the current dual-track claim surface. Keep on disk.

| Path | Why historical |
| --- | --- |
| [`../experiments/PHASE1_FINAL_CLOSEOUT.md`](../experiments/PHASE1_FINAL_CLOSEOUT.md) | Pre-live Phase-1 closeout; live Track B is in `DUAL_TRACK_STATUS.md` |
| [`../experiments/PHASE1_CORE_RESULTS.md`](../experiments/PHASE1_CORE_RESULTS.md) | Offline architectural diagnostics, not confirmatory LIVE |
| [`../experiments/PHASE1_FINAL_QUALITY_GATE.md`](../experiments/PHASE1_FINAL_QUALITY_GATE.md) | Offline quality gate; superseded as “current status” |
| [`../experiments/PHASE1_CORE_AUDIT.md`](../experiments/PHASE1_CORE_AUDIT.md) | Offline core audit |
| [`../experiments/PROJECT_FINAL_STATUS.md`](../experiments/PROJECT_FINAL_STATUS.md) | Layer A CASE B project status (not Track A/B confirmation) |
| [`../experiments/PROJECT_COMPLETION_AUDIT.md`](../experiments/PROJECT_COMPLETION_AUDIT.md) | Layer A v4 completion audit |
| [`../experiments/FINAL_SCIENTIFIC_AUDIT.md`](../experiments/FINAL_SCIENTIFIC_AUDIT.md) | Layer A CASE B scientific audit |
| [`../experiments/LAYER_A_V4_FORENSIC_AUDIT.md`](../experiments/LAYER_A_V4_FORENSIC_AUDIT.md) | Layer A forensic note |
| [`../EXPERIMENT_STATUS.md`](../EXPERIMENT_STATUS.md) | Q1 auto-status (2026-09-01); not dual-track |
| [`../EXP004_COMPLETION_STATUS.md`](../EXP004_COMPLETION_STATUS.md) | EXP-004 blocked completion note |
| [`../research/PHASE2_7_EXP004_STATUS.md`](../research/PHASE2_7_EXP004_STATUS.md) | Older EXP-004 / Phase 2.7 status |
| [`RESULTS_RECONCILIATION.md`](RESULTS_RECONCILIATION.md) | Phase 11 Layer A claim map; not VNEXT/Phase-1 LIVE |
| [`04_results.md`](04_results.md) | Historical simulation / `REAL_LLM_EVAL` body (pointer only in FAIL packet) |
| [`README.md`](README.md) | Older paper-facing index; prefer this `DOCS_INDEX.md` |
| [`../Q1_FINAL_READINESS_REPORT.md`](../Q1_FINAL_READINESS_REPORT.md) and other `docs/Q1_*` | Q1 readiness; not current confirmatory evidence |
| [`../archive/`](../archive/) | Already-moved Q1/audit duplicates |

Q1 reports, simulation tables, and Layer A CASE B audits remain evidence of what was tried. They must not be revived as “AdaptiGuard works” or as a VNEXT reversal.

No files in this table were deleted by the hygiene pass.
