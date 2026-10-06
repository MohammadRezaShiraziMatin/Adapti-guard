# Reproducibility

This file describes what the repository regenerates offline, what it does not, and where the provenance records live.

## Offline reproduction (no network, no API key, no spend)

```bash
pip install -r requirements-core.txt          # pins matplotlib==3.11.2 (figure bytes depend on it)
STRICT=1 bash scripts/reproduce_negative_result.sh
```

The script regenerates every analysis artifact, the three figures, `NUMBERS_LEDGER.md` and `MANUSCRIPT_DRAFT_v1.md` from committed traces, runs the ledger consistency test, and with `STRICT=1` fails if any regenerated manuscript, ledger or figure file differs from the committed copy.

| Experiment | Raw input (committed) | Analysis script | Derived artifact |
|---|---|---|---|
| E1 Tracks A/B | `experiments/real_llm_eval/{VNEXT,PHASE1}_CONFIRM/**/*_predictions.jsonl`, frozen packs | `scripts/rescore_tracks_ab_deterministic.py` | `docs/research/artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| E2 exploratory | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/episodes.jsonl` | `scripts/analyze_harness_v2_exploratory.py`, `scripts/make_fig1_scoring_flip.py` | `exploratory_analysis.json`, `figures/fig1_*` |
| E3 independent set | `HARNESS_V2_INDEPENDENT_{SCREEN,DEFENDED}_20260930/episodes.jsonl` | `scripts/analyze_independent_defended.py`, `scripts/make_fig{2,3}_*.py` | `paired_vs_a0_analysis.json` (Appendix D source), `figures/fig{2,3}_*` |
| MT1 held-out rules | `experiments/real_llm_eval/MT1/r1/*/*/*_predictions.jsonl`, `datasets/frozen/layer_a_v2` | `scripts/apply_rules_second_dataset_mt1.py` | `docs/research/artifacts/mt1_second_dataset_rules_20260930.json` |
| M6 channel check | `experiments/real_llm_eval/MT1/spotlight_ctx_check_20260930/*/*/*_predictions.jsonl` + MT1 r1 | `scripts/analyze_spotlight_ctx_check.py` | `docs/research/artifacts/spotlight_ctx_check_20260930.json` |

Tests: `tests/test_manuscript_number_ledger.py`, `tests/test_rescore_tracks_ab.py`, `tests/test_second_dataset_mt1_rules.py`.

## Not regenerated offline

- **E2/E3 live runs.** The harness, run scripts and templates are released as an offline snapshot in `harness_v2_release/` (see below). Re-executing E2/E3 needs `OPENROUTER_API_KEY`, paid calls and the same providers; it was not attempted and no claim rests on it.
- **InjecAgent and calibration (§6.6, §6.7).** The scripts for these steps (`injecagent_offline_check.py`, `audit_datasets.py`, `analyze_injecagent_live.py`, the §6.6 runner and analysis, `run_phase2_calibration.py`, `run_injecagent_panel.py`) are not in the tree, and the external InjecAgent checkout (`INJECAGENT_REPO`) is not part of this repository; the reproduction script skips these steps. The committed per-episode records (`experiments/external/`) and derived `docs/research/artifacts/injecagent_live_analysis_20260930*.json` files are read by the ledger builder, but the §6.6 and §6.7 numbers cannot be regenerated from this repository.
- **E3 delivery audit.** `scripts/audit_e3_delivery.py` is offline and is run by the reproduction script; it writes `docs/research/artifacts/e3_delivery_audit_20261003.json`.
- **Live runs.** Hosted models change and temperature 0 is not deterministic (§6.3). Re-running a live experiment produces new traces, not the published ones; the published traces are the committed ones.

## Spend sources

| Claim | Source |
|---|---|
| E2 smoke $0.0104 | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_SMOKE_20260930/cost_summary.json` |
| E2 run | `HARNESS_V2_EXPLORATORY_20260930/cost_summary.json` |
| E3 screen $0.0469, defended $0.0944 | `HARNESS_V2_INDEPENDENT_{SCREEN,DEFENDED}_20260930/cost_summary.json` |
| E2 + E3 about $0.23 | sum of the four files above (0.2307) |
| M6 re-run $0.0669 | `experiments/real_llm_eval/MT1/spotlight_ctx_check_20260930/LEDGER.json` |

## Provenance

Each harness run directory keeps its `run_manifest.json` (runner commit, repository and docs SHAs at launch, Python version).

**Commit identifiers.** The manuscript and the run manifests cite commits from the original research history (for example runner commit `bea82347`). That history was later rewritten with identical file trees and changed author metadata. Status checked on 2026-10-03 against the public remote:

- No tag `case-study-v1` exists on the remote (its only tag is `historical-packages-recovery-20260920`). The commit that earlier versions of this file named as the tip of that tag, `dfbea801e01051974f51efcc9b7aea179b32d42a`, is not reachable from any branch, tag or pull-request ref.
- It, and every commit in the table below (both columns), can nevertheless be fetched by full SHA (`git fetch origin <full SHA>`). The tip of the original history, `1ae0fb4dd96129dcbf21ce0bad8646f5411b75b7`, can be fetched the same way. This is not a published archive: unreachable commits are not guaranteed to remain retrievable, and the Git bundle of the original history is held by the authors and is not published.
- The cited identifiers are kept unchanged.

| Cited (original history) | Rewritten equivalent (same tree) |
|---|---|
| `bea82347460f6dfa9cbac81ab1b14d50e0a39f29` | `eeeb391315da501f79d8f63e60880c3598a0a951` |
| `e5135a61cc6a5b254f9d91184aebf22963ab8ff4` | `cd65cdf7c31670a4c2d5616c92cb8aa9e228543f` |
| `7b0e053d9da8ed913257ecb725362d1907d0e6d4` | `e08a6527ac365c9391af5644f2c0dac33aef8eb6` |
| `44830fa23dce2d38f129a89a149af2f4deefb72c` | `65660215fe7345dfcd663a90854d38f1d8a8884d` |
| `caa7ad893c87eb82eb26689dd3970e5075d7bfa7` | `3edbe95550c2793ac7e8aa41508f3e20bbc4b632` |
| `d369edf2a7f438f982dc7c64b10400b1a0a5b703` | `6c4ef915c6bacb6c7f275c3cb14cede59272fb0a` |
| `a58be9be164ec8022e7ba8c78f886c1767620eaa` | `cfa11cca6cbfedc49f19044bdaf2fd85ffcac18e` |

Of the pairs checked on 2026-10-03, `d369edf2` is on a public branch (`cursor/q1-p1-diagnosis-1282`); the others are not reachable from any ref. The Phase-1 detector commit `c462945a0c0a29ab9a9593e33a73983e4e42a1ab` (2026-09-14 19:09 UTC) is reachable from public pull-request refs; its rewritten equivalent `12414c8f` (identical tree) is in the history of `main`.

**Attack templates (in `harness_v2_release/`; also retrievable by SHA).** The template files are in the tree only inside the offline snapshot (`harness_v2_release/experiments/harness_v2/`), and are also retrievable from the public remote by commit SHA. Regeneration does not read them: the analyses produce identical output without them. Files read from the cited commits on 2026-10-03 match the recorded hashes and sizes:

| File | SHA-256 | Size | Retrievable at |
|---|---|---|---|
| `experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES.json` | `b9f9994fcbae9af42810d2d9e3ff31bd64825cc5005a8fa2523abec91d7bdb9d` | 127,242 B | `bea82347…`, `eeeb3913…` |
| `experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES_INDEPENDENT_V2.json` | `8ae353ca21fc5aa1966292c52c2f887ddef369cc296fd77afa283c5fe9149de8` | 136,467 B | `e5135a61…`, `cd65cdf7…`, `7b0e053d…`, `44830fa2…` |

The E2 and E3 runs recorded `templates_sha256 = b9f9994f…` (the runner hashes the base template file only) in `pilot_summary.json`, which is archive-only; the in-tree `run_manifest.json` files record commit SHAs and no file hashes. The independent file's hash `8ae353ca…` is attested by the commit message of `e5135a6` ("Frozen file SHA-256 8ae353ca…") and by its content at the E3 launch commits (`e5135a6`, `7b0e053`, `44830fa`), where it is unchanged. Whether to remove these commits from the remote is an open decision for the authors; this document does not describe a staged release.

## Harness snapshot (offline)

`harness_v2_release/` holds a verbatim copy of the E2/E3 runner code, execution scripts, harness test and scenario templates, taken from commits that exist on the public remote (`44830fa2…` E3 defended and base tree; overlays for `7b0e053d…` E3 screen and `bea82347…` E2). Nothing was edited or regenerated; every file is listed with its SHA-256 in `harness_v2_release/MANIFEST.sha256`. Its `README.md` states what can be checked offline (the harness test and two replays that are byte-identical to the replay outputs committed at `dfbea801…`) and what is not covered (live re-execution, the amendment test suite, provider-side behaviour). It is self-contained and must not be mixed with `src/`.

## Archived only (not in the tree of any branch or tag)

These are not read by any analysis, figure or ledger script and back no quoted number; they are present in the unreachable archive commit `dfbea801…` (checked 2026-10-03), not in a published tag: per-episode `trajectories/`, `http_stream.jsonl`, `ledger_rows.jsonl`, `cost_log.jsonl`, `running_ledger.json`, `pip_freeze.txt` and `pilot_summary.json` of each harness run (the last also records `templates_sha256`); the smoke run's episode data; MT1 `r1/episodes.jsonl` (incomplete, see `r1_AUDIT_OFFLINE.md` in the archive); per-arm `*_metrics.json`.

**Historical harness test.** `tests/test_harness_v2_exploratory_arms.py` tests the live multi-turn harness (mock mode; two of its tests read the scenario templates). It is not in the root `tests/` because it needs the harness import tree, which does not belong in `src/`; it is carried, with that tree, in `harness_v2_release/tests/` and runs from there (command in the snapshot README). The offline reproduction above does not depend on it: every regenerated artifact, figure, the ledger and the manuscript are byte-identical to the committed copies, and the tests listed above pass.
