# ADAPTI-GUARD — Phase 2 Data Split Policy (LOCKED)

**Policy ID:** `PHASE2-SPLIT-0.1`  
**Protocol:** `PHASE2-PROTOCOL-0.1`  
**Date (UTC):** 2026-09-14  

This policy defines how Phase-2 multi-turn episode data must be constructed, split, hashed, and protected against contamination. It is a **documentation lock**. It does not create datasets and does not modify frozen historical packs.

---

## 1. Mandatory independence

Phase 2 **MUST** define a genuinely independent evaluation set.

### Forbidden sources for Phase-2 TEST / HOLDOUT

| Source | SHA-256 (binding) | Allowed use in Phase 2 |
| --- | --- | --- |
| VNEXT confirmation pack | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` | **Historical citation only.** Not TEST. Not fitting. Not “extended” into holdout. |
| Layer A TEST split | `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8` | **Not** Phase-2 TEST. Not for fitting Phase-2 thresholds. |
| Phase-1 diagnostic iterations on VNEXT | n/a | Explains **PACK-FIT RISK = HIGH**; must not seed TEST paraphrases of fitted items |

### Required

- New episode IDs  
- New trajectories (multi-turn state machines), not single-prompt clones of VNEXT  
- Documented provenance and generation procedure  
- Holdout untouched until protocol + construction decisions are locked  

---

## 2. Split definitions

| Split | Purpose | May influence detector/policy? | May be used for threshold fitting? | Unblind for confirmatory analysis? |
| --- | --- | --- | --- | --- |
| **DEVELOPMENT (DEV)** | Trajectory design, mock-tool debugging, taxonomy pilots, harness checks | Only for **future** Phase-2 development experiments with new IDs — **not** silent edits to frozen Phase-1 detector justified by Phase-2 TEST | Yes, for exploratory work **before** VAL freeze of any tunable | No (not confirmatory) |
| **VALIDATION (VAL)** | Sanity checks, redundancy analysis of taxonomy, power-assumption pilots, scoring dry-runs **without** LLM if possible | No changes promoted to confirmatory config after VAL peek without new experiment ID | Soft: calibration only if pre-registered; prefer freeze-from-DEV | No |
| **TEST / HOLDOUT** | Confirmatory paired B0 vs ADAPT evaluation | **Never** | **Never** | Only after run completion under locked protocol |

**Ordering lock:** Finalize protocol → construct DEV → (optional) VAL pilots → **freeze TEST hash** → human approval → (only then) live eval.

---

## 3. Provenance requirements

Every episode must record in the manifest (scorer-facing; stripped from runtime):

| Field | Description |
| --- | --- |
| `episode_id` | Stable opaque ID (no family encoding) |
| `split` | `dev` / `val` / `test` |
| `taxonomy_family` | A–H codes from protocol |
| `provenance` | authoring method (human-authored / template+review / synthetic+review) |
| `generation_procedure` | short procedure ID + version |
| `attack_or_benign` | gold |
| `tool_plan` | requested tools, privileges |
| `harmful_action` | gold (attacks) |
| `success_condition` | gold binary rule |
| `safe_alternative` | optional |
| `seed` | if any stochastic mock behavior |
| `content_hash` | SHA-256 of canonical episode JSON (runtime-visible fields only + gold block hashed separately) |

### Generation procedure (normative outline)

1. Author episode skeleton: goals, tools, privilege path, success condition.  
2. Expand to turn list with state updates and tool observations.  
3. Adversarial review: ensure family label matches mechanism (persistence vs delayed, etc.).  
4. Contamination review: no VNEXT ID reuse; no near-duplicate of VNEXT prompts used in Phase-1 evidence fitting.  
5. Hard-negative review for family H.  
6. Assign split by **pre-registered rules** (§5), not by observed difficulty under ADAPT.  
7. Hash and freeze.

---

## 4. Allocation

### Attack-family allocation

Provisional TEST targets follow `PHASE2-SAP-0.1` (§6). DEV/VAL should oversample difficult mechanisms (C, B, E, F) for harness stress **without** copying those exact trajectories into TEST.

### Benign allocation

- **G:** legitimate multi-step tool workflows (retrieve, write, send with valid business intent).  
- **H:** attack-like wording (quotes, analysis, red-team discussion) with benign requested behavior.

### Hard-negative rules

Hard negatives must remain `workflow_completed`-scorable under A0. If ADAPT over-blocks H, that counts toward utility / unnecessary_intervention — not toward security wins.

---

## 5. Split rules (pre-registered)

1. **ID disjointness:** No episode_id in more than one split.  
2. **Trajectory disjointness:** No shared turn sequences across splits (including paraphrase clones of the same skeleton). Skeleton templates may be shared **only** if surface forms and tool-observation payloads differ materially and review documents independence.  
3. **Family balance:** Each split contains all families intended for confirmatory reporting, unless a family is dropped globally before TEST freeze.  
4. **Difficulty assignment:** Must not use ADAPT or detector scores on candidate TEST items to decide inclusion.  
5. **VNEXT exclusion:** String-level and ID-level exclusion list against VNEXT confirmation prompts; document near-duplicate screen.  
6. **Author blinding (recommended):** Trajectory authors for TEST do not receive Phase-1 residual-miss lists as a checklist to reverse-engineer the detector for TEST construction aimed at “making ADAPT look good.” TEST may include hard cases, but construction must not be fitted to Phase-1 evidence codes.

---

## 6. Contamination / leakage rules

### Runtime must not receive

- `split`, `taxonomy_family`, `is_attack`, `harmful_action`, `success_condition`, gold judge labels  
- Category names, MSID text, claims, audit narratives  
- Future turn content  
- Attack IDs that embed gold (e.g. `atk_persist_...` is discouraged; prefer opaque `p2_ep_00042`)

### Allowed runtime inputs

- Current user utterance  
- Conversation / observation history as defined by state model  
- Declared tool name + privilege tier (environment truth, not gold attack flag)  
- Defense/risk/action history produced by the runtime itself  

### Scorer may receive

- Full gold block  
- Success condition checkers  
- Taxonomy for stratified tables  

### Leakage tests (required before live eval)

Deterministic tests asserting gold keys are rejected by context builders / defense entrypoints (extend Phase-1 label-blindness tests to multi-turn state).

---

## 7. Hashes and freeze procedure

At TEST freeze, record:

```text
phase2_dataset_id
phase2_manifest_sha256
phase2_dev_sha256
phase2_val_sha256
phase2_test_sha256
episode_count_by_split_and_family
exclusion_list_sha256 (VNEXT + Layer A references)
protocol_id = PHASE2-PROTOCOL-0.1
sap_id = PHASE2-SAP-0.1
split_policy_id = PHASE2-SPLIT-0.1
```

Any edit to TEST content after freeze requires a **new dataset version ID** and invalidates prior approvals for that hash.

---

## 8. PACK-FIT control linkage

Phase-1 evidence detector was iterated using diagnostics on the frozen VNEXT pack → **PACK-FIT RISK = HIGH**.

Therefore:

- Phase-2 TEST is the **generalization** instrument.  
- DEV may study failure modes, but improving Phase-1 weights using Phase-2 TEST outcomes is a protocol violation.  
- Diagnostic coverage figures (e.g. historical `56/61`) must not be restated as Phase-2 performance.

---

## 9. What this policy does not do yet

- Does not ship JSONL files  
- Does not run generators  
- Does not call LLMs  
- Does not modify `datasets/frozen/**`  

Dataset construction is a **later** gated step after human approval of this protocol lock.
