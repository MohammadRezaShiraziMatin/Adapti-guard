# Reproducibility report (2026-10-07)

Produced by a model on the draft branch on top of PR #108 (base 2b82c74). It reports what was run and what the output was. It does not claim the study is reproducible beyond the offline path below.

## 1. State of the public tree (verified, not assumed)
| item | state |
|---|---|
| remote tags | one: `historical-packages-recovery-20260920`. `case-study-v1` (named in `REPRODUCIBILITY.md`) **does not exist**. |
| harness (`src/adapti_guard/evaluation/harness_v2/`), E2/E3/calibration/external run scripts, attack templates | **not in the tree** of this branch (`git ls-files` finds no `harness_v2/` source, no template files) |
| commits bea82347 (original templates), e5135a6 (independent templates), 1ae0fb4d, dfbea801 (harness) | **all four fetchable today by full SHA** from the public remote (`git fetch origin <full sha>`), not reachable from any ref. 1ae0fb4d and dfbea801 contain `src/adapti_guard/evaluation/harness_v2/` and `scripts/run_harness_v2_*.py`. No template content was opened or copied in this work. |
| consequence | The manuscript's §10 statement (harness not publicly released; templates retrievable by SHA, not withheld) is accurate. Nothing was pushed, tagged or released. |

## 2. What ran and the output
**Offline reproduction, `bash scripts/reproduce_negative_result.sh` (needs matplotlib; installed with pip).** Exit 0. Steps that ran: Tracks A/B re-scoring, harness v2 exploratory analysis, E3 defended analysis, MT1 held-out application, spotlight channel check, E3 delivery audit, figures 1 to 3, manuscript assembly, number ledger (54 entries), `tests/test_manuscript_number_ledger.py` (1 passed). Final lines: `OK: manuscript numbers regenerate from committed artifacts.` The script's last check prints a "regenerated files differ from the committed copies" warning when run before committing the revised files, and because the installed matplotlib re-renders the figure binaries; the figure files were restored from git and not committed. The InjecAgent steps were skipped by the script (external checkout and scripts absent), so §6.6 and §6.7 numbers were **not** regenerated.

**Additional scripts added in this revision:** `scripts/audit_e3_defense_activity.py` (E3 defense actions, user-turn identity; output `docs/research/artifacts/e3_defense_activity_20261007.json`), `scripts/make_e1_audit_sample.py` (seeded sample for a human audit; nothing labeled).

**Independent re-tallies (not via the repo scripts):** E2 per-arm and per-scenario executed counts from `HARNESS_V2_EXPLORATORY_20260930/episodes.jsonl` (A0 66/72, B3 65/72, CORE 36/72, TOOLDENY 0/72; valid scenario 30/29/0/0 of 36) match §6.2. Benign tasks per arm: 45. InjecAgent final-run records match §6.6 (A0 23/186 for both targets; hit sets differ, 6 shared).

**Tests, public tree (`python3 -m pytest -q`):**
| condition | result |
|---|---|
| no `PYTHONPATH`, deps: matplotlib, pytest, scipy only | 281 passed, 5 failed (3 need `openai`/`google.genai`; 2 subprocess tests fail with `No module named 'adapti_guard'`) |
| `PYTHONPATH=src`, same deps | 283 passed, 3 failed (`test_gemini_provider.py` x2, `test_groq_provider.py` x1: missing `google.genai` / `openai`) |
| `PYTHONPATH=src`, plus httpx, scikit-learn, openai, google-genai | **287 passed, 0 failed** |

**Tests, archive commits (scratch worktrees outside the repo, deps as in the last row):** 1ae0fb4d and dfbea801 each gave 670 passed, 24 failed, 5 skipped, the same 24 failures. Without httpx and scikit-learn, collection fails (26 errors).
Failures by file: test_b2_campaign_preflight 9, test_b2_campaign_batch 6, test_b2_batch_runner 3, one each in test_b2_matrix_contract, test_harness_v2_amendment9_final, test_harness_v2_amendment9_round5, test_q1_evaluation_contract, test_q1_p1_ledger_order, test_q1_protocol_runner. The dominant cause is `ValueError: invalid literal for int() with base 10: 'PENDING_BUDGET_APPROVAL'` (15 tests); the rest were not diagnosed. They were not repaired. The earlier figures in the manuscript (661 passed / 32 failed) were **not reproduced**; they came from a different environment and date.

## 3. What did not run
* The harness itself (no live model calls, no spend; none was intended).
* The InjecAgent live and calibration analyses (runner and analysis scripts are not public).
* LaTeX/PDF builds (no LaTeX engine in this environment; pandoc exists). The arXiv zips and PDFs are stale (see `docs/paper/negative_result/arxiv/STALE_20261007.md`).
* A human audit of E1 disagreements.

## 4. What the report supports
The E1 to E4 tables, figures and the number ledger regenerate offline from committed traces, and the public tree's test suite passes once its dependencies are installed. It does **not** support a claim that the live experiments can be re-run from this repository, or that §6.6 and §6.7 are regenerable.

## 5. Blocked on the owner (not done by design)
Adding the harness, run scripts and templates to a public branch, creating the `case-study-v1` tag, or any release. These are irreversible and the release policy is undecided.

## 6. Failing archive tests (list)
- tests/test_b2_batch_runner.py::test_all_auth_true_runs_mock_b01
- tests/test_b2_batch_runner.py::test_ledger_target_judge_counted
- tests/test_b2_batch_runner.py::test_same_ledger_across_episodes
- tests/test_b2_campaign_batch.py::test_aggregate_five_episodes_no_double_count
- tests/test_b2_campaign_batch.py::test_batch_ids_unique
- tests/test_b2_campaign_batch.py::test_batch_plan_2_2_1_partition
- tests/test_b2_campaign_batch.py::test_batch_preflight_scenario_e
- tests/test_b2_campaign_batch.py::test_batch_worst_requests_8_8_4
- tests/test_b2_campaign_batch.py::test_partial_campaign_4_of_5
- tests/test_b2_campaign_preflight.py::test_campaign_size_tbd_when_unspecified
- tests/test_b2_campaign_preflight.py::test_case_a_n1_preflight
- tests/test_b2_campaign_preflight.py::test_case_b_n2_preflight
- tests/test_b2_campaign_preflight.py::test_case_c_n3_blocked
- tests/test_b2_campaign_preflight.py::test_case_d_n5_blocked_single_invocation
- tests/test_b2_campaign_preflight.py::test_comparable_to_b1_false
- tests/test_b2_campaign_preflight.py::test_hypothetical_n2_preflight_passes_budget
- tests/test_b2_campaign_preflight.py::test_n3_blocked_by_request_cap
- tests/test_b2_campaign_preflight.py::test_yaml_n_episodes_conflicts_single_invocation_cap
- tests/test_b2_matrix_contract.py::test_budget_preflight_rejects_single_invocation_accepts_split
- tests/test_harness_v2_amendment9_final.py::test_all_proxy_forwards_body_with_wire_rows
- tests/test_harness_v2_amendment9_round5.py::test_main_proxy_run_every_stream_row_has_wire_bytes
- tests/test_q1_evaluation_contract.py::test_q1_contract_offline_validation
- tests/test_q1_p1_ledger_order.py::test_p1_preflight_dry_worst_case_under_cap
- tests/test_q1_protocol_runner.py::test_phase_preflight_model_aware_within_two_dollars
