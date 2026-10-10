# Legacy claims — not to be used without owner approval

Each item below appears somewhere in the repository (drafts, reports, skeleton, prior conversation summaries). None of them may be cited in the paper unless the owner approves that specific item in writing, after the verification step listed.

| # | claim | where it appears | why it is legacy | verification needed before use |
|---|---|---|---|---|
| L1 | Track A target is `openai/gpt-oss-20b` | `docs/paper/dual_track/PHASE1_SCIENTIFIC_REPORT.md` | conflicts with VNEXT AUDIT (`qwen-2.5-7b`) | owner decision; check the run's `config.json` and `models_observed.json` |
| L2 | Pre-registered before the InjecAgent run | `docs/paper/negative_result/SECTIONS_5_6_EXPERIMENTS_RESULTS.md` (§5.6, §6.6) | no external registration exists | OSF or AsPredicted record with timestamp |
| L3 | Commits `0e64abc`, `14404a2`, `15b4610`, `c462945`, `a2681e9` establish chronology | paper sections; Track B AUDIT | not in the local clone | fetch by full SHA, or owner confirms |
| L4 | InjecAgent backend is OpenRouter | implied by panel config | not recorded in manifests | run `runner` config at the commit that created the folders |
| L5 | Track B result: δ̂=0.4426, p≈1.5e-8 | Phase-1 report; AUDIT | pilot model, single pack, judge-based endpoint | owner decision on scope; judge-to-executor agreement check |
| L6 | CORE 36/72 vs 36/36 under four scoring rules | `figures/fig1_scoring_flip.csv` | depends on a denominator and rule definition that must be re-derived from `scripts/make_fig1_scoring_flip.py` | re-derive from raw episodes |
| L7 | Independent families: 0 of 336 paired episodes blocked | skeleton §6 | the family set has not been checked against `paired_vs_a0_analysis.json` | verify from JSON |
| L8 | Judge vs executor: CORE harm 34/61 vs 6/61 | skeleton §4 | cited to a research note; not checked against the JSON artifact | verify `docs/research/artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| L9 | Hard set has 238 human items and 69 generated items | `attackset_hard_v1/FREEZE_RECORD.json` | MANIFEST and item files are absent | restore the MANIFEST and verify SHA `786505…` |
| L10 | Layer A v4 `B2_L3_V4` reduces ASR (b10=22, p≈4.8e-7) | v4 AUDIT | non-adaptive, high utility cost; not a defense result | owner decision on how to report |
| L11 | Total spend ≈ $0.40 (verified) / $0.47 (with MT1) | conversation summary | MT1 backend not verified; some runs have no recorded cost | per-run cost files |
| L12 | Strong-model results exist | none | no such results exist | — (claim must not be made) |
| L13 | Test suite status: 661 passed / 32 failed | `docs/research/TEST_SUITE_STATUS_20261001.md` | dated 2026-10-01; not re-run | re-run `pytest` and record output |
| L14 | `scripts/replay_harness_v2_offline.py` exists | skeleton §10 | file is missing | restore or remove the reference |
| L15 | Q1 contract panel (`configs/q1_evaluation_contract.yaml`) | `models_panel_external_v2.yaml` header | file is missing | restore or remove the reference |

## Process for approving a legacy claim

1. Owner names the claim (by L-number) and the intended use (which section, which table).
2. The verification step in the table is run and its output is saved under `docs/baseline/verification/`.
3. The claim is then either marked approved, with the approval date and the verification file, or kept out of the paper.
4. Nothing in this file is deleted. Status changes are appended below.

## Status log

- 2026-10-10: all items L1–L15 recorded as legacy. No approvals given.
