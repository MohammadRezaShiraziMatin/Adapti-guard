# Integrity report: Stage 1 and Stage 2 (attack pack v4)

Reference commit: `e5949bc` (`origin/main`, Stage-0 audit). Work branch: `claude/adoring-turing-4z5aol`, created from `e5949bc`.
All results below come from commands run in the repository on the date of this report. None are assumed.

## 1. Frozen-artifact integrity (checked)

| check | command | result |
|---|---|---|
| Protected paths changed since `e5949bc` | `git diff --name-only e5949bc -- datasets/frozen datasets/attackset_hard_v1 results docs/baseline/BASELINE_SHA256.txt experiments` filtered to protected patterns | **empty: no change** |
| Experiment AUDIT files | count of `experiments/**/AUDIT*` in `e5949bc` vs working tree | 17 vs 17, no change |
| Baseline hash manifest | `sha256sum -c docs/baseline/BASELINE_SHA256.txt` | **91 of 91 OK** |
| Commits on the work branch beyond `e5949bc` | `git log e5949bc..HEAD` | none yet (see section 5) |
| Working tree | `git status --short --untracked-files=all` | only new, untracked files listed in section 4 |

No frozen file, result, audit file or baseline hash was modified.

## 2. Repository state (before work)

- The clone at the path in the protocol, `/home/claude/mohammadrezashirazimatin/adapti-guard`, **does not exist**. The clone at `/home/user/adapti-guard` was used.
- Local `main` was at `efd4e12`, **behind** `origin/main` (`e5949bc`). The working tree was clean, so `main` was fast-forwarded (`--ff-only`). No local commit was lost.
- `docs/baseline/` was absent from `efd4e12` and present after the fast-forward.
- The designated branch `claude/adoring-turing-4z5aol` did not exist locally or on `origin`. It was created from `e5949bc`.

## 3. Discrepancies found in the existing records

| # | item | evidence | status |
|---|---|---|---|
| I1 | `vnext_confirm_v1` attack breakdown | `docs/baseline/BASELINE_2026-10-10.md` section 4 says "attacks: 112 single, 10 multi". 61 + 112 + 10 ≠ 122. Recount of `datasets/frozen/vnext_confirm_v1/confirmation.jsonl`: **51 single + 10 multi = 61 attacks**. | **Baseline document is wrong**; the data file is authoritative. Needs correction in a separate, approved commit. Not edited here (baseline files are protected). |
| I2 | `layer_a_v3` attack breakdown | Baseline says "attacks: 144 single, 16 multi". Recount of `datasets/frozen/layer_a_v3/dataset.jsonl`: **64 single + 16 multi = 80 attacks**; 80 benign. | **Baseline document is wrong**. Same handling as I1. |
| I3 | Hard-negative labels | Verified: 40 rows with `attack_type = hard_negative` in `layer_a_v3` and 25 in `vnext_confirm_v1`, **all labelled `benign`**. Matches the Stage-0 audit. | Confirmed. |
| I4 | `eval_v1` attack-only, empty `injection_location` | Verified: 770 rows, `injection_location` empty in 770, `user_task` empty in 770, `attack_objective` empty in 497, no `label`, no `success_condition`, no `tool_call`. 7 categories × 110; sources as stated. Also: 770 unique `id`, `sha256` and `text`. | Confirmed. Not measurable under v4 (SCHEMA_v4.md section 7; decision D7). |
| I5 | `attackset_hard_v1` | Only `FREEZE_RECORD.json` present (verified). MANIFEST and item files absent. | Confirmed unverifiable. Decision D3. |
| I6 | Stage-0 audit reproducibility | Re-counted all labels and categories from the frozen files; they match `attack_audit_stage0_2026-10-10.txt` except I1 and I2, which concern the baseline document, not the audit. | Confirmed. |
| I7 | Existing `src/adapti_guard/data/schema.py`, `validator.py` | Unused stubs with a different schema (`dataset`, `split`, `StandardRecord`). No imports found. | Left untouched; the new validator is a separate module. |
| I8 | `datasets/external_samples/` | No licence file in the folder (per baseline section 4; not separately verified beyond that). | Open; decision D10. |

## 4. Files added (no existing file modified)

- `src/adapti_guard/data/attack_schema_v4.py` (validator, Stage 1)
- `tests/test_attack_schema_v4.py` (74 tests, Stage 1)
- `tests/test_dataset_upgrade_coverage.py` (7 tests, Stage 2)
- `scripts/dataset_upgrade/coverage_matrix.py` (Stage 2 generator; writes only inside `docs/dataset_upgrade/generated/` when run)
- `docs/dataset_upgrade/SCHEMA_v4.md`, `PLAN_AND_COVERAGE_v4.md`, `OWNER_DECISIONS_v4.md`, `INTEGRITY_REPORT_STAGE1_2.md`
- `docs/dataset_upgrade/generated/` (coverage CSV, coverage summary JSON, power JSON)

No dataset example was generated. `datasets/drafts/` does not exist. The test fixtures are synthetic validator inputs, not dataset examples.

## 5. Verification run

- `python3 -m pytest tests/test_attack_schema_v4.py tests/test_dataset_upgrade_coverage.py` → **81 passed**. (Two failures found during the run were bugs in my tests, not in the validator; both were corrected and the validator was not changed.)
- Spot check of existing tests (`test_provenance.py`, `test_artifacts.py`) → 6 passed.
- **Full suite not run.** The baseline records 661 passed / 32 failed (2026-10-01), but that figure is not re-verified here (legacy claim L13). The new modules are not imported by any existing module, so they should not affect other tests; this is an inference, not a verified result.
- No model was run, no API call was made, no cost was incurred.

## 6. Limitations of this work

- The validator checks structure, label rules, the reserved-domain safety rule, the sha256 and dataset-level pairing. It does **not** check whether an injection reaches the model, whether a tool call executes, duplicates, or content quality. Those are Stage 4.
- Power numbers use a normal approximation and assume a comparison of two independent proportions. They are design guidance, not a pre-registered analysis.
- Time estimates in the plan are my estimates.
- The baseline document (I1, I2) is inconsistent with the data and must be corrected in a separately approved commit.
