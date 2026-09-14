# Research log (VNEXT / Layer A)

Append-only. Do not delete prior entries. Do not rewrite frozen packs, AUDIT folders, or `VNEXT-MSID-0.1` in place.

This file is the dated scientific diary for Layer A close-out and the VNEXT confirmation stack. Historical Q1 notes remain in [`docs/RESEARCH_HISTORY.md`](../RESEARCH_HISTORY.md).

---

## 2026-09-14 — Layer A CLOSED; VNEXT Phase 1–3a; Phase 2 harness; pack freeze; confirmation FAIL; manuscript PR32

**Binding outcome.** VNEXT confirmation **STATUS = FAIL**. Qualified win (H1) = **NO**. Layer A remains a **CLOSED diagnostic** (detector lift; adaptive B3_V4 not significant). No retune, no N increase, no frozen-dataset edit, no arXiv/external submit in this log.

Canonical AUDIT: `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md`.

### Layer A closed (CASE B diagnostic)

| Item | Record |
| --- | --- |
| Status | **CLOSED.** Not a defense win. Not CASE A. |
| Detector freeze | `evidence_v4.0` git `46bffe142be334260f767a98c2201ca273c24f71` |
| Intervention wiring | git `3ca86a7a876c3de01c208eea62e736bce33ee422` |
| Frozen TEST | `datasets/frozen/layer_a_v3/test_split.jsonl` SHA-256 `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8` |
| Close-out docs | `docs/experiments/PROJECT_FINAL_STATUS.md`, `docs/experiments/FINAL_SCIENTIFIC_AUDIT.md` |
| Paper-facing diagnostic | PR **#23** `docs/paper/04_results_layer_a_diagnostic.md` + `docs/paper/CLAIMS_CHECKLIST_LAYER_A.md` |
| Allowed detector claim | v4 TEST recall 27/40 = 0.675, AUROC 0.705 vs v3 2/40 = 0.05, AUROC 0.368; no TEST retuning |
| Allowed adaptive claim | B3_V4 ASR 0.625 / U 0.85 vs B0 ASR 0.75 / U 1.00; McNemar p = 0.125; **not** a demonstrated ASR reduction |
| Forbidden | production-ready / SOTA; “B3_V4 beats B0”; treating B2_L3_V4 as adaptive |

Layer A TEST `47b975f7…` was **not** used as the VNEXT confirmation pack and was **not** retuned after FAIL.

### Phase 1 — scientific reset (docs)

| Item | Record |
| --- | --- |
| PR | **#24** `cursor/vnext-protocol-phase1-d8c0` |
| Artifact | `docs/experiments/VNEXT_PROTOCOL.md` (`VNEXT-PROTOCOL-0.1`) |
| Scope | RQ, endpoints, taxonomy, leakage rule P0, tool environment, utility gate \(U \ge 0.95\), statistics, stop rules, claims boundary |
| LLM/API | 0 |

### Phase 2 — harness repair (code, no live eval)

| Item | Record |
| --- | --- |
| PR | **#25** `cursor/vnext-harness-repair-phase2-9b3f` |
| Changes | Gold `is_attack` stripped from adaptive runtime; `tool_loop` in `evaluate_episode`; A2 tool deny; taxonomy persisted; refusals ≠ intervention wins |
| Tests | `tests/test_vnext_phase2_harness.py` (deterministic; no OpenRouter) |
| LLM/API | 0 |

### Phase 3 prep + Phase 3a — power memo and MSID lock (docs)

| Item | Record |
| --- | --- |
| PR #26 | `docs/experiments/VNEXT_POWER_MEMO.md` (`VNEXT-POWER-MEMO-0.1`); hash-gate addendum started |
| PR #27 | Phase 3a: `VNEXT-MSID-0.1` locked δ = 0.20 defense-attributed (Supervisor Option A). Fail rule: effect < MSID **or** McNemar non-significant ⇒ useful-intervention claim **fails** |
| N | n_attack = n_benign = **61** (exact 80% McNemar power). Changing MSID after unblinding is a new experiment ID |
| LLM/API | 0 |

Addendum file `docs/experiments/VNEXT_PROTOCOL_ADDENDUM.md` (`VNEXT-PROTOCOL-ADDENDUM-0.3`) still contains the **freeze-before-score** sentence that Phase 3 live eval was “NOT STARTED.” That sentence is historical pre-registration text. It is **not** the official outcome. The official outcome is AUDIT **FAIL** below. Do not rewrite the addendum in place after unblinding.

### Pack freeze (Phase 3b)

| Item | Record |
| --- | --- |
| PR | **#28** `cursor/vnext-confirm-pack-4d85` |
| Pack | `vnext_confirm_v1.0` — `datasets/frozen/vnext_confirm_v1/dataset.jsonl` (byte-identical `confirmation.jsonl`) |
| SHA-256 | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| Rows | 61 attack + 61 benign; IDs `vnext_c1_atk_*` / `vnext_c1_ben_*` disjoint from Layer A |
| Builder LLM | 0 |
| Tests | `tests/test_vnext_confirm_pack.py` |

**Do not edit this frozen JSONL.** A live or manuscript claim that cites a different confirmation hash is invalid (protocol S3).

### Pre-live checklist (infra only)

| Item | Record |
| --- | --- |
| PR | **#30** `cursor/vnext-prelive-checklist-7aef` |
| Artifact | `docs/experiments/VNEXT_PRELIVE_CHECKLIST.md` — **PRELIVE_PASS** |
| LLM/API | 0 |

PR **#29** (`cursor/vnext-confirm-live-eval-8dd8`) is a **parallel** live-eval request/runner (`scripts/run_vnext_confirm_eval.py`). Official scoring used PR **#31** (`scripts/run_vnext_confirm.py`). Do not merge #29 as if it were the FAIL record.

### VNEXT confirmation (official FAIL)

| Quantity | Value |
| --- | --- |
| PR | **#31** `cursor/vnext-confirm-live-81ad` |
| Run folder | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/` |
| Pack SHA-256 | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` (match=True) |
| N | 61 + 61 scorable after same-ID repair (not extra N) |
| B0 ASR | 0.9508 (58/61) |
| VNEXT-ADAPT ASR | 0.8689 (53/61) |
| McNemar | b10 = 5, b01 = 0, p = 0.0625 (not significant) |
| Effect vs MSID | δ̂ = 0.0820 < 0.20 (`msid_not_met`) |
| Utility | U = 0.9344 < 0.95 (`s4_utility_ineligible`); false blocks = 1 |
| Fail reasons | `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible` |
| b10 taxonomy | 5 × `correct_block` (A3) |
| Residual attacks | `insufficient_intervention` = 53 |
| Target ≠ Judge | `qwen/qwen-2.5-7b-instruct` ≠ `qwen/qwen-2.5-72b-instruct` |
| Cache | off (0 / 0 hits) |
| Spend (list-rate aid) | 0.059016 (~$0.059) |
| Qualified win | **NO** |

Same-ID repair (not extra N): `vnext_c1_atk_031` (B0), `vnext_c1_ben_046` (B0), `vnext_c1_atk_045` (VNEXT-ADAPT). Prior unofficial ~78-episode B0 fragment is discarded.

p = 0.0625 is **not** “marginally confirmed.” This FAIL is **not** PARTIAL and is **not** a trend toward a win.

### Workshop / preprint manuscript (negative result)

| Item | Record |
| --- | --- |
| PR | **#32** `cursor/vnext-fail-workshop-manuscript-de91` |
| Package | `docs/paper/workshop_vnext_fail/` |
| Stance | Negative-result workshop text. Not an arXiv deposit. Not a camera-ready defense paper. |
| Claims map | `docs/paper/workshop_vnext_fail/CLAIMS_MAP.md` (maps checklist A1–A12 + VNEXT V1–V10) |

### What this day does not authorize

- Live LLM eval beyond the recorded FAIL AUDIT
- OpenRouter calls to amend `VNEXT-MSID-0.1`
- Detector / band retune on Layer A TEST
- Increasing N on `vnext_confirm_v1.0`
- Editing frozen JSONL packs
- arXiv or external venue submit
- Merging the PR stack (human-only; see [`docs/paper/workshop_vnext_fail/PR_STACK.md`](../paper/workshop_vnext_fail/PR_STACK.md))
