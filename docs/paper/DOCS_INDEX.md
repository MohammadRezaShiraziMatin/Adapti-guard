# Docs index (dual-track era)

Canonical scientific status is [`dual_track/DUAL_TRACK_STATUS.md`](dual_track/DUAL_TRACK_STATUS.md), not older PHASE/Q1 closeouts. **Do not delete files listed as ARCHIVE / SUPERSEDED** — they are historical evidence. This index does not rewrite the workshop manuscript.

Contributor entry: [`docs/START_HERE.md`](../START_HERE.md).

---

## ACTIVE (keep)

Use these for current claims, merge advice, and workshop FAIL text.

### Dual-track (current)

| Path | Role |
| --- | --- |
| [`../START_HERE.md`](../START_HERE.md) | Read order + tree |
| [`dual_track/DUAL_TRACK_STATUS.md`](dual_track/DUAL_TRACK_STATUS.md) | Track A FAIL vs Track B scoped LIVE |
| [`dual_track/CLAIMS_DUAL_TRACK.md`](dual_track/CLAIMS_DUAL_TRACK.md) | Allowed / forbidden dual-track wording |
| [`dual_track/RELEASE_NEXT_FA.md`](dual_track/RELEASE_NEXT_FA.md) | Matin next-step note + CLOSE / SKIP |
| [`../experiments/MASTER_PROMPT.md`](../experiments/MASTER_PROMPT.md) | Durable supervisor constraints |
| [`../experiments/RESEARCH_LOG.md`](../experiments/RESEARCH_LOG.md) | Dated diary (including 2026-09-14 dual-track) |

Stubs remain at `docs/paper/DUAL_TRACK_STATUS.md` and `docs/paper/CLAIMS_DUAL_TRACK.md`.

### Workshop packet (`workshop_vnext_fail/` core)

Track A negative-result package. Numbers must match the VNEXT AUDIT. Not a venue submit. **Folder name kept** for citations.

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

Track B protocol locks (not LIVE numbers): [`phase1/PHASE1_SCIENTIFIC_SPEC.md`](phase1/PHASE1_SCIENTIFIC_SPEC.md), [`PHASE1_THREAT_MODEL.md`](phase1/PHASE1_THREAT_MODEL.md), [`PHASE1_STATISTICAL_PLAN.md`](phase1/PHASE1_STATISTICAL_PLAN.md), [`PHASE1_SCIENTIFIC_GATE.md`](phase1/PHASE1_SCIENTIFIC_GATE.md), [`PHASE1_ABLATION_PROTOCOL.md`](phase1/PHASE1_ABLATION_PROTOCOL.md). Track A protocol: [`../experiments/protocols/VNEXT_PROTOCOL.md`](../experiments/protocols/VNEXT_PROTOCOL.md) / addendum / MSID. Phase-2 protocol lock (docs only; unevaluated): [`../experiments/protocols/PHASE2_PROTOCOL.md`](../experiments/protocols/PHASE2_PROTOCOL.md). Stubs remain at the old `docs/experiments/PHASE1_*.md`, `docs/experiments/VNEXT_*.md`, and `docs/experiments/PHASE2_*.md` paths.

### Live AUDIT pointers only (do not edit)

| Track | Path |
| --- | --- |
| A FAIL | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` |
| B scoped | `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md` |

Do not edit those folders, JSONL under `experiments/real_llm_eval/`, or VNEXT FAIL numbers. Frozen packs stay at `datasets/frozen/**`.

---

## ARCHIVE / SUPERSEDED (do not delete)

Historical or overlapping status notes. They are **not** the current dual-track claim surface. Keep on disk. One-line stubs remain at old paths.

| Path | Why historical |
| --- | --- |
| [`../archive/phase1_closeouts/PHASE1_FINAL_CLOSEOUT.md`](../archive/phase1_closeouts/PHASE1_FINAL_CLOSEOUT.md) | Pre-live Phase-1 closeout; live Track B is in `DUAL_TRACK_STATUS.md` |
| [`../archive/phase1_closeouts/PHASE1_CORE_RESULTS.md`](../archive/phase1_closeouts/PHASE1_CORE_RESULTS.md) | Offline architectural diagnostics, not confirmatory LIVE |
| [`../archive/phase1_closeouts/PHASE1_FINAL_QUALITY_GATE.md`](../archive/phase1_closeouts/PHASE1_FINAL_QUALITY_GATE.md) | Offline quality gate; superseded as “current status” |
| [`../archive/phase1_closeouts/PHASE1_CORE_AUDIT.md`](../archive/phase1_closeouts/PHASE1_CORE_AUDIT.md) | Offline core audit |
| [`../archive/layer_a/PROJECT_FINAL_STATUS.md`](../archive/layer_a/PROJECT_FINAL_STATUS.md) | Layer A CASE B project status (not Track A/B confirmation) |
| [`../archive/layer_a/PROJECT_COMPLETION_AUDIT.md`](../archive/layer_a/PROJECT_COMPLETION_AUDIT.md) | Layer A v4 completion audit |
| [`../archive/layer_a/FINAL_SCIENTIFIC_AUDIT.md`](../archive/layer_a/FINAL_SCIENTIFIC_AUDIT.md) | Layer A CASE B scientific audit |
| [`../archive/layer_a/LAYER_A_V4_FORENSIC_AUDIT.md`](../archive/layer_a/LAYER_A_V4_FORENSIC_AUDIT.md) | Layer A forensic note |
| [`../archive/q1/EXPERIMENT_STATUS.md`](../archive/q1/EXPERIMENT_STATUS.md) | Q1 auto-status (2026-09-01); not dual-track |
| [`../archive/q1/EXP004_COMPLETION_STATUS.md`](../archive/q1/EXP004_COMPLETION_STATUS.md) | EXP-004 blocked completion note |
| [`../archive/research/PHASE2_7_EXP004_STATUS.md`](../archive/research/PHASE2_7_EXP004_STATUS.md) | Older EXP-004 / Phase 2.7 status |
| [`../archive/paper_working_notes/RESULTS_RECONCILIATION.md`](../archive/paper_working_notes/RESULTS_RECONCILIATION.md) | Phase 11 Layer A claim map; not VNEXT/Phase-1 LIVE |
| [`04_results.md`](04_results.md) | Historical simulation / `REAL_LLM_EVAL` body (pointer only in FAIL packet) |
| [`README.md`](README.md) | Older paper-facing index; prefer this `DOCS_INDEX.md` |
| [`../archive/q1/Q1_FINAL_READINESS_REPORT.md`](../archive/q1/Q1_FINAL_READINESS_REPORT.md) and other `docs/archive/q1/Q1_*` | Q1 readiness; not current confirmatory evidence |
| [`../archive/`](../archive/) | Q1/audit duplicates, research notes, detector local backups |

Q1 reports, simulation tables, and Layer A CASE B audits remain evidence of what was tried. They must not be revived as “AdaptiGuard works” or as a VNEXT reversal.

No files in this table were deleted by the hygiene pass.
