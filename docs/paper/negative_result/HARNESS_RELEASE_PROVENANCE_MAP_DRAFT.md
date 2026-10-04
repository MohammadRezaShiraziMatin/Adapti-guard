# Harness release provenance map (DRAFT; nothing has been created, tagged, released or archived)

**Status.** Draft, 2026-10-04. It describes a **future** clean, sanitized release subtree (Option B). No release branch, tag, DOI or archive exists, and none is claimed. Historical evidence is not rewritten to achieve this; the original-history objects stay as they are and are only described.

## 1. Relationship to the manuscript
The manuscript cites runner and repository commits from the original history. They are not reachable from any public branch or tag; all ten were confirmed fetchable by full SHA from the public remote on 2026-10-03 and 2026-10-04 and may not persist. The release cannot make them reachable. It substitutes a **content identity**: git tree and blob object IDs of the harness package and the runner script, which anyone can recompute from the cited commits while they remain fetchable and from the release afterwards.

| cited SHA | role in the manuscript | harness package tree OID (`src/adapti_guard/evaluation/harness_v2`) | `scripts/run_harness_v2_pilot.py` blob OID |
|---|---|---|---|
| `caa7ad89` | E2 repository head at launch | `94e124e3da728b66190917e68c8606eb8b41a1a8` | not recorded here |
| `bea82347` | E2 runner commit | `94e124e3da728b66190917e68c8606eb8b41a1a8` | `07b7fc2d062fe0509bee99fdc09dd844101e71f9` |
| `e5135a61` | E3 scenario-set commit | `2571d14ef82596104b278a8d79073ae814d838df` | not recorded here |
| `44830fa2` | E3 runner commit | `2571d14ef82596104b278a8d79073ae814d838df` | `07b7fc2d062fe0509bee99fdc09dd844101e71f9` |
| `1ae0fb4d` | original-history tip (source of the release content) | `2571d14ef82596104b278a8d79073ae814d838df` | `07b7fc2d062fe0509bee99fdc09dd844101e71f9` |

Consequences: the harness package in a release built from `1ae0fb4d` is **byte-identical to the package used for E3** (same tree OID as `44830fa2`), and the runner script is identical in all three versions. It is **not** the package used for E2: E2 ran on `94e124e3…`.

## 2. The E2 six-file delta
Changes between the E2 runner (`bea82347`) and the E3 runner (`44830fa2`) inside the package: 6 files, +131 −14 lines.
- `argallow_policy.py` (+44, new)
- `delivery_verification.py` (+7 −2)
- `exploratory_schedule.py` (+30 −3)
- `harness_v2_b3_pretarget_wrapper.py` (+17 −3)
- `openrouter_tools_session_async.py` (+2 −3)
- `scenario_catalog.py` (+31 −3)

The release would ship this difference as a patch (`E2_to_E3_harness_delta.patch`, generated from the two commits and hashed) so the E2 version can be reconstructed by reverse-applying it. The release must not be described as the E2 harness.

## 3. Included files (as audited on scratch copies of `1ae0fb4d`)
Static import closure from the runner and the 44 harness tests, plus the files the tests load: **158 files, about 0.9 MB of content** (98 under `src/`, 46 under `tests/` of which 44 are test files and 2 fixtures, 10 scripts, 2 configs, one mock-test script and `pytest.ini`). The two template files (0.26 MB) and the three protocol documents the runner reads are not in this list; see §4. With the closure in a scratch git repository and proxy variables unset, 158 of 159 offline harness tests passed (3 skipped) once `scripts/analyze_harness_v2_pilot.py` (missed by the import scan, now listed) was added; the one failure needs the optional `openai` package. Final list to be regenerated and hashed at release time:

```
configs/models.yaml
configs/models_q1_eval_panel.yaml
experiments/harness_v2/amendment7b_obfuscated_mock_test.py
pytest.ini
scripts/analyze_harness_v2_exploratory.py
scripts/analyze_harness_v2_pilot.py
scripts/analyze_independent_defended.py
scripts/build_harness_v2_independent_templates.py
scripts/run_harness_v2_exploratory.py
scripts/run_harness_v2_pilot.py
scripts/run_harness_v2_reasoning_smoke.py
scripts/run_harness_v2_smoke.py
scripts/run_harness_v2_smoke2.py
scripts/run_harness_v2_smoke3.py
src/adapti_guard/__init__.py
src/adapti_guard/adaptation/__init__.py
src/adapti_guard/adaptation/feedback_engine.py
src/adapti_guard/adaptation/policy_update_engine.py
src/adapti_guard/attacker/__init__.py
src/adapti_guard/attacker/adaptive_attacker.py
src/adapti_guard/attacker/fixed_sequence_attacker.py
src/adapti_guard/core/__init__.py
src/adapti_guard/core/core_pipeline.py
src/adapti_guard/core/episode.py
src/adapti_guard/core/models.py
src/adapti_guard/defense/__init__.py
src/adapti_guard/defense/action_layer.py
src/adapti_guard/defense/tool_loop.py
src/adapti_guard/defense/tool_permission.py
src/adapti_guard/detector/__init__.py
src/adapti_guard/detector/prompt_injection_detector.py
src/adapti_guard/detector/prompt_injection_detector_phase1.py
src/adapti_guard/detector/prompt_injection_detector_v4.py
src/adapti_guard/evaluation/__init__.py
src/adapti_guard/evaluation/adaptive_episode.py
src/adapti_guard/evaluation/agent_environment.py
src/adapti_guard/evaluation/attack_success.py
src/adapti_guard/evaluation/b2_adaptive_contract.py
src/adapti_guard/evaluation/b2_attack_mode_contract.py
src/adapti_guard/evaluation/b2_campaign_protocol.py
src/adapti_guard/evaluation/b2_matrix_contract.py
src/adapti_guard/evaluation/evaluation_modes.py
src/adapti_guard/evaluation/experiment_logging.py
src/adapti_guard/evaluation/harness_v2/__init__.py
src/adapti_guard/evaluation/harness_v2/amendment9_smoke_controls.py
src/adapti_guard/evaluation/harness_v2/amendment9_smoke_schedule.py
src/adapti_guard/evaluation/harness_v2/argallow_policy.py
src/adapti_guard/evaluation/harness_v2/benign_validity.py
src/adapti_guard/evaluation/harness_v2/c2_episode_state.py
src/adapti_guard/evaluation/harness_v2/cancelled_timeout_billing.py
src/adapti_guard/evaluation/harness_v2/cancelled_timeout_ledger.py
src/adapti_guard/evaluation/harness_v2/cancelled_timeout_reconcile.py
src/adapti_guard/evaluation/harness_v2/delivery_verification.py
src/adapti_guard/evaluation/harness_v2/episode_wall_clock.py
src/adapti_guard/evaluation/harness_v2/episode_wall_runner.py
src/adapti_guard/evaluation/harness_v2/exec_success.py
src/adapti_guard/evaluation/harness_v2/exploratory_schedule.py
src/adapti_guard/evaluation/harness_v2/finish_reason.py
src/adapti_guard/evaluation/harness_v2/harness_event_loop.py
src/adapti_guard/evaluation/harness_v2/harness_rate_limit_retry.py
src/adapti_guard/evaluation/harness_v2/harness_v2_b3_pretarget_wrapper.py
src/adapti_guard/evaluation/harness_v2/harness_v2_http_client.py
src/adapti_guard/evaluation/harness_v2/http_budget.py
src/adapti_guard/evaluation/harness_v2/http_preflight.py
src/adapti_guard/evaluation/harness_v2/mock_tool_executor.py
src/adapti_guard/evaluation/harness_v2/openrouter_async_attempt.py
src/adapti_guard/evaluation/harness_v2/openrouter_chat_http.py
src/adapti_guard/evaluation/harness_v2/openrouter_request_policy.py
src/adapti_guard/evaluation/harness_v2/openrouter_tools_session.py
src/adapti_guard/evaluation/harness_v2/openrouter_tools_session_async.py
src/adapti_guard/evaluation/harness_v2/pilot_budget.py
src/adapti_guard/evaluation/harness_v2/pilot_incremental_store.py
src/adapti_guard/evaluation/harness_v2/pilot_preflight.py
src/adapti_guard/evaluation/harness_v2/pilot_run_lock.py
src/adapti_guard/evaluation/harness_v2/provider_incomplete_response_policy.py
src/adapti_guard/evaluation/harness_v2/provider_probe.py
src/adapti_guard/evaluation/harness_v2/run_manifest.py
src/adapti_guard/evaluation/harness_v2/scenario_catalog.py
src/adapti_guard/evaluation/harness_v2/scenario_mock_executor.py
src/adapti_guard/evaluation/harness_v2/scenarios.py
src/adapti_guard/evaluation/harness_v2/smoke_criteria.py
src/adapti_guard/evaluation/harness_v2/token_limits.py
src/adapti_guard/evaluation/harness_v2/tool_definitions.py
src/adapti_guard/evaluation/harness_v2/trajectory_store.py
src/adapti_guard/evaluation/harness_v2/usage_tokens.py
src/adapti_guard/evaluation/harness_v2/wire_request_body.py
src/adapti_guard/evaluation/live_b0_report.py
src/adapti_guard/evaluation/live_budget_gate.py
src/adapti_guard/evaluation/live_eval_trace.py
src/adapti_guard/evaluation/live_extension_wiring.py
src/adapti_guard/evaluation/live_model_resolver.py
src/adapti_guard/evaluation/llm_cache.py
src/adapti_guard/evaluation/llm_judge.py
src/adapti_guard/evaluation/metrics.py
src/adapti_guard/evaluation/openrouter_panel_pricing.py
src/adapti_guard/evaluation/outcome_evaluator.py
src/adapti_guard/evaluation/provider_errors.py
src/adapti_guard/evaluation/secret_safe.py
src/adapti_guard/evaluation/stateful_episode.py
src/adapti_guard/evaluation/stateful_target_adapter.py
src/adapti_guard/evaluation/target_model.py
src/adapti_guard/experiments/__init__.py
src/adapti_guard/experiments/defense_baselines.py
src/adapti_guard/experiments/dns_workaround.py
src/adapti_guard/experiments/env_loader.py
src/adapti_guard/policy/__init__.py
src/adapti_guard/policy/core_policy.py
src/adapti_guard/policy/policy_engine.py
src/adapti_guard/risk/__init__.py
src/adapti_guard/risk/risk_engine.py
src/adapti_guard/risk/risk_engine_core.py
src/adapti_guard/risk/risk_engine_v4.py
tests/fixtures/pilot3_gemma_reasoning_tokens_2_raw_response.json
tests/fixtures/synthetic_empty_content_reasoning_raw_response.json
tests/harness_v2_http_stream_assertions.py
tests/harness_v2_local_openrouter_server.py
tests/test_analyze_harness_v2_pilot_auth_key.py
tests/test_harness_v2_amendment7c.py
tests/test_harness_v2_amendment8_429_billing.py
tests/test_harness_v2_amendment8_cancelled_timeout.py
tests/test_harness_v2_amendment8_combined_integration.py
tests/test_harness_v2_amendment8_delayed_inject.py
tests/test_harness_v2_amendment8_episode_wall.py
tests/test_harness_v2_amendment8_event_loop.py
tests/test_harness_v2_amendment8_http_budget_per_attempt.py
tests/test_harness_v2_amendment8_http_cap_mid_429.py
tests/test_harness_v2_amendment8_http_cap_remaining_invalid.py
tests/test_harness_v2_amendment8_http_cap_tool_round_cut.py
tests/test_harness_v2_amendment8_incomplete_response_matrix.py
tests/test_harness_v2_amendment8_legacy_wrapper.py
tests/test_harness_v2_amendment8_llama_max_tokens.py
tests/test_harness_v2_amendment8_per_attempt_client.py
tests/test_harness_v2_amendment8_provider_error.py
tests/test_harness_v2_amendment8_python_manifest.py
tests/test_harness_v2_amendment8_reconcile.py
tests/test_harness_v2_amendment8_usd_cap_mid_episode.py
tests/test_harness_v2_amendment8_wired_integration.py
tests/test_harness_v2_amendment9_final.py
tests/test_harness_v2_amendment9_lastpatch.py
tests/test_harness_v2_amendment9_pilot_label.py
tests/test_harness_v2_amendment9_request_snapshot.py
tests/test_harness_v2_amendment9_round4.py
tests/test_harness_v2_amendment9_round5.py
tests/test_harness_v2_amendment9_run_manifest_shas.py
tests/test_harness_v2_amendment9_smoke_cli.py
tests/test_harness_v2_amendment9_wire_main_local_server.py
tests/test_harness_v2_b3_wrapper.py
tests/test_harness_v2_c2_episode_state.py
tests/test_harness_v2_delivery_amendment5.py
tests/test_harness_v2_exec_success.py
tests/test_harness_v2_exploratory_arms.py
tests/test_harness_v2_finish_reason.py
tests/test_harness_v2_http_preflight.py
tests/test_harness_v2_option_d_runner.py
tests/test_harness_v2_pilot_amendment6.py
tests/test_harness_v2_pilot_preflight_usd_cap_lock.py
tests/test_harness_v2_smoke_scripts_family_kw.py
tests/test_harness_v2_trajectory_request.py
```

## 4. Excluded files and why
- **Template files** (`experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES.json`, 127,242 B, SHA-256 `b9f9994f…`; `…_INDEPENDENT_V2.json`, 136,467 B, SHA-256 `8ae353ca…`): payload-bearing; excluded unless the owner decides otherwise; already retrievable by commit SHA; the SHA-256 values stay in `REPRODUCIBILITY.md`. Two tests read them and would be skipped.
- **Provider key-usage snapshots and preflight files** (`auth_key_snapshot*`, `preflight_auth_key*`): truncated key labels and usage/limit figures.
- **Owner working notes and approval documents** (`AMENDMENT*`, `PREREG_HARNESS_V2_FULL.md`, `PILOT*_CRITERIA*`, `AMENDMENT9_DECISIONS.md`, owner decision packs): they name the owner and record approvals. The runner reads three of them by path (`PREREG_HARNESS_V2_FULL.md`, `PILOT2_CRITERIA_LOCKED.md`, `AMENDMENT9_DECISIONS.md`); the release needs sanitized, clearly marked stand-ins or a runner option that does not require them. Decision for the owner; a sanitized copy must be labelled as such and never presented as the original approval record.
- **`configs/datasets.yaml`** and any file with `/home/<user>/` paths, `/Users/...` or owner names.
- **Unrelated aborted and pilot metadata** (`ABORTED_PILOT2_ATTEMPTS_*`, `HARNESS_V2_A9_LLAMA_SMOKE_*`, `HARNESS_V2_PILOT3_*`, amendment demo directories).
- **Per-episode trajectories, HTTP streams, per-request cost logs, ledgers and `pip_freeze.txt` of the four 2026-09-30 runs**: not part of the code release; they remain in original-history commits. If the owner wants spend to be recomputable, a separately sanitized cost log can be added.
- **Committed virtual environments, benchmark datasets and everything else in the 171 MiB original tree.**

## 5. What the release must not expose (acceptance scan, to be run on the exact release tree)
Truncated provider key labels (`sk-or-v1-...`); `limit_remaining`, `usage`, `usage_daily` fields; owner names and approval notes; `/home/`, `/Users/` paths other than neutral placeholders; agent-tool names and working notes; aborted and pilot run metadata. The patterns used in the 2026-10-03 history audit are the starting set. The release is acceptable only if the scan is clean, all offline tests pass, and the harness-package tree OID of the release equals `2571d14e…`.

## 6. Statements the release would and would not support
Would support: the harness code that produced E3 is public and identical by tree OID to the E3 runner commit; E2 differs by the six listed files; the live runs can be repeated with the user's own provider key (new traces, not the published ones). Would not support: that the cited commits are reachable; that E2 or E3 provider spend is recomputable; that live experiments reproduce bit for bit; any DOI claim before an archive exists.

## 7. Open decisions
Whether to include the templates; how to stand in for the three documents the runner reads; whether to add a sanitized cost log; branch and tag names; archive service. None is decided here.

## 7. Staging tool result (2026-10-04, scratch only; nothing published)
`scripts/e6_stage_harness.py --out DIR --git` stages the §3 closure from `1ae0fb4d` (read with `git show`; history untouched) plus the E6 tooling: 158 files, forbidden-path and text scan (personal paths, owner names, key labels) with **no findings**, a `.gitignore`, a `SANITIZED_MANIFEST.json` (per-file SHA-256, tree hash) and, with `--git`, a local scratch commit that the runner needs to record HEAD. `pyproject.toml` is not staged (it carries the owner's name); `env_loader.py` was reviewed and holds only an `sk-or-` format check, no secret. 20 archived harness tests (+1 that imports one of them) read the payload-bearing E3 template files by fixed path and are **not staged by default**; `--with-templates` stages them with the two template files (owner decision, §4). In the staged tree the remaining suite passes (111 passed, 1 skipped), including the E6 end-to-end test on the real runner with the mock transport. The runner is unmodified; the E6 launcher patches its interfaces at runtime. The tree is still not public: publishing it, a tag and a reachable ref need the owner's approval.
