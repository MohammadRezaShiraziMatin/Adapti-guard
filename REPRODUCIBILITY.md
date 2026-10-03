# Reproducibility

This file describes what the repository regenerates offline, what it does not, and where the provenance records live.

## Offline reproduction (no network, no API key, no spend)

```bash
pip install -r requirements-core.txt          # pins matplotlib==3.11.2 (figure bytes depend on it)
STRICT=1 bash scripts/reproduce_negative_result.sh
```

The script regenerates the analysis artifacts of E1 to E3, MT1 and the M6 channel check, the three figures, `NUMBERS_LEDGER.md` and `MANUSCRIPT_DRAFT_v1.md` from committed traces, runs the ledger consistency test, and with `STRICT=1` fails if any regenerated manuscript, ledger or figure file differs from the committed copy.

| Experiment | Raw input (committed) | Analysis script | Derived artifact |
|---|---|---|---|
| E1 Tracks A/B | `experiments/real_llm_eval/{VNEXT,PHASE1}_CONFIRM/**/*_predictions.jsonl`, frozen packs | `scripts/rescore_tracks_ab_deterministic.py` | `docs/research/artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| E2 exploratory | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/episodes.jsonl` | `scripts/analyze_harness_v2_exploratory.py`, `scripts/make_fig1_scoring_flip.py` | `exploratory_analysis.json`, `figures/fig1_*` |
| E3 independent set | `HARNESS_V2_INDEPENDENT_{SCREEN,DEFENDED}_20260930/episodes.jsonl` | `scripts/analyze_independent_defended.py`, `scripts/make_fig{2,3}_*.py` | `paired_vs_a0_analysis.json` (Appendix D source), `figures/fig{2,3}_*` |
| MT1 held-out rules | `experiments/real_llm_eval/MT1/r1/*/*/*_predictions.jsonl`, `datasets/frozen/layer_a_v2` | `scripts/apply_rules_second_dataset_mt1.py` | `docs/research/artifacts/mt1_second_dataset_rules_20260930.json` |
| M6 channel check | `experiments/real_llm_eval/MT1/spotlight_ctx_check_20260930/*/*/*_predictions.jsonl` + MT1 r1 | `scripts/analyze_spotlight_ctx_check.py` | `docs/research/artifacts/spotlight_ctx_check_20260930.json` |

Tests: `tests/test_manuscript_number_ledger.py`, `tests/test_rescore_tracks_ab.py`, `tests/test_second_dataset_mt1_rules.py`.

## Not regenerated offline

- **§6.6, §6.7 and Appendix A (InjecAgent, calibration, pilot).** These use committed derived artifacts only: `experiments/external/**` (raw episodes, `ANALYSIS.json`, `calibration.json`) and `docs/research/artifacts/injecagent_live_analysis_20260930*.json` (read by the ledger builder). The scripts that produced them (for example `analyze_injecagent_live.py`, `run_injecagent_live.py`, `injecagent_offline_check.py`, `audit_datasets.py`, `run_phase2_calibration.py`, `run_injecagent_panel.py`) and the external InjecAgent checkout are not in this repository, and `reproduce_negative_result.sh` does not run them.
- **The multi-turn harness and runner** (`scripts/run_harness_v2_pilot.py`, `src/adapti_guard/evaluation/harness_v2/`) and the attack-template files and generator are not in this repository (staged release).
- **Live runs.** Hosted models change and temperature 0 is not deterministic (§6.3). Re-running a live experiment produces new traces, not the published ones; the published traces are the committed ones.

## Spend sources

| Claim | Source |
|---|---|
| E2 smoke $0.0104 | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_SMOKE_20260930/cost_summary.json` |
| E2 run | `HARNESS_V2_EXPLORATORY_20260930/cost_summary.json` |
| E3 screen $0.0469, defended $0.0944 | `HARNESS_V2_INDEPENDENT_{SCREEN,DEFENDED}_20260930/cost_summary.json` |
| E2 + E3 about $0.23 | sum of the four files above: 0.2307 including the smoke run, 0.2203 without it |
| M6 re-run $0.0669 | `experiments/real_llm_eval/MT1/spotlight_ctx_check_20260930/LEDGER.json` |

## Provenance

Each harness run directory keeps its `run_manifest.json` (runner commit, repository and docs SHAs at launch, Python version).

**Commit identifiers (unpublished historical state).** The manuscript and the run manifests cite commits from the original research history (for example runner commit `bea82347`). Those commits are not reachable from any branch, tag or pull-request ref of the public repository, and the chronology they would document (runner state, template freeze, run order) is not publicly verifiable. The authors report that the history was later rewritten with identical file trees and changed author metadata and archived in an annotated tag `case-study-v1` (commit `dfbea801e01051974f51efcc9b7aea179b32d42a`); **that tag is not published** (the remote has no tag of that name) and no tag or ref was created to stand in for it. The cited identifiers are kept unchanged. The table records the authors' mapping and cannot be checked from this repository; the only cited identifier that is public is `d369edf2` (branch `cursor/q1-p1-diagnosis-1282`, pull request #80):

| Cited (original history) | Equivalent in `case-study-v1` (unpublished tag; authors' mapping) |
|---|---|
| `bea82347460f6dfa9cbac81ab1b14d50e0a39f29` | `eeeb391315da501f79d8f63e60880c3598a0a951` |
| `e5135a61cc6a5b254f9d91184aebf22963ab8ff4` | `cd65cdf7c31670a4c2d5616c92cb8aa9e228543f` |
| `7b0e053d9da8ed913257ecb725362d1907d0e6d4` | `e08a6527ac365c9391af5644f2c0dac33aef8eb6` |
| `44830fa23dce2d38f129a89a149af2f4deefb72c` | `65660215fe7345dfcd663a90854d38f1d8a8884d` |
| `caa7ad893c87eb82eb26689dd3970e5075d7bfa7` | `3edbe95550c2793ac7e8aa41508f3e20bbc4b632` |
| `d369edf2a7f438f982dc7c64b10400b1a0a5b703` | `6c4ef915c6bacb6c7f275c3cb14cede59272fb0a` |
| `a58be9be164ec8022e7ba8c78f886c1767620eaa` | `cfa11cca6cbfedc49f19044bdaf2fd85ffcac18e` |

The original history (tip `1ae0fb4dd96129dcbf21ce0bad8646f5411b75b7`) is preserved as a Git bundle held by the authors.

**Attack templates (withheld).** Released in stages (§10); not in this repository. Regeneration does not read them: the analyses produce identical output without them.

| File | SHA-256 | Size |
|---|---|---|
| `experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES.json` | `b9f9994fcbae9af42810d2d9e3ff31bd64825cc5005a8fa2523abec91d7bdb9d` | 127,242 B |
| `experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES_INDEPENDENT_V2.json` | `8ae353ca21fc5aa1966292c52c2f887ddef369cc296fd77afa283c5fe9149de8` | 136,467 B |

The run manifests committed here (`run_manifest.json`) contain code and docs commit SHAs only and no template hash. The authors report that the archived `pilot_summary.json` of each run stores `templates_sha256 = b9f9994f…` (the runner hashes the base template file only); that file is not published. The independent file's hash `8ae353ca…` is attested only by its content at the E3 launch commits (`e5135a6`, `7b0e053`, `44830fa`), which are unpublished historical commits, so the template freeze is not publicly verifiable from this repository.

**Key reconciliation and approval.** No provider-key usage snapshots, `progress.log`, reconciliation records or per-request cost records are in the repository, and no record of the owner's approval of the four harness runs is preserved here (manuscript §8.5).

**Observed-consequence rule.** The counting rule used in E2 episode scoring was introduced in `dc3e175` (public branch `counting-rule-frozen-observed-consequence`, committed 2026-10-02 23:43 UTC) and enforced on `main` in `974b391` (2026-10-03), after the 2026-09-30 executions; it is not pre-registered and does not change the E3 pairing (manuscript §4.2).

## Archived only (not in this repository)

These are not read by any analysis, figure or ledger script and back no quoted number; they are held by the authors in the unpublished archive: per-episode `trajectories/`, `http_stream.jsonl`, `ledger_rows.jsonl`, `cost_log.jsonl`, `running_ledger.json`, `pip_freeze.txt` and `pilot_summary.json` of each harness run (the last also records `templates_sha256`); the smoke run's episode data; MT1 `r1/episodes.jsonl` (incomplete, see `r1_AUDIT_OFFLINE.md` in the archive); per-arm `*_metrics.json`.

**Historical harness test (archive-only, scope limitation).** `tests/test_harness_v2_exploratory_arms.py` tests the live multi-turn harness. It imports the harness package (`src/adapti_guard/evaluation/harness_v2/`), drives the live runner `scripts/run_harness_v2_pilot.py` in mock mode, and two of its tests read the withheld template files. That dependency tree is intentionally not part of this selective release, so the test is kept in the unpublished archive only. The offline reproduction above does not depend on it: `STRICT=1 bash scripts/reproduce_negative_result.sh` regenerates the artifacts, figures, ledger and manuscript byte-identically to the committed copies, and the tests listed above pass. (A comparison with the unpublished archive, reported by the authors, cannot be checked here.) Its absence is a scope limitation of the release, not a failed scientific reproduction.
