# Release: re-analysis of released AgentDojo/AgentDyn runs (M1, M3, judge vs checker, drift)

No API keys, tokens or credentials are included. The only paid component, the judge pilot, reads `OPENROUTER_API_KEY` from the environment; its outputs are included, so no rerun is needed. Everything else is offline (Python 3, numpy).

**Layout.** The scripts expect the original working layout `pivot-checks/{rankflip,review,clustered,lodo,stage,drift,judge_pilot,docs}`. To reproduce:
1. Copy `scripts/<dir>/*` into `<dir>/`.
2. Copy `inputs/` files to their paths in `MANIFEST.sha256`, `prereg/*` to `docs/` or `review/`, and `results/` likewise.

Absolute paths `/workspace/pivot-checks` and `/workspace/rf_split` in some scripts refer to that working directory. Adjust them if you use another root. The released benchmark runs themselves (AgentDojo `runs/`, AgentDyn `runs/` at commit 5353cf7) are public and not included.

| Table / result | Command (from the pivot-checks root) | Output |
|---|---|---|
| Inventory and per-episode scoring | `python3 rankflip/inventory.py && python3 rankflip/score_all.py` (needs the public runs) | `rankflip/inventory.csv`, `rankflip/episodes.jsonl` (included in inputs/) |
| Ranking flips, full data (Table: Robustness, row 1, full) | `python3 rankflip/analyze.py` | `rankflip/results.json` |
| Ranking flips, confirmatory subset (row 1, subset) | `python3 review/run.py conf` | `/workspace/rf_split/results_conf.json` (= `review/results_conf.json`) |
| Drop-errors (row 2) | `python3 review/run_droperr.py conf && python3 review/run_droperr.py all` | `review/results_droperr_{conf,all}.json` |
| Task-clustered + Holm (row 3) | `python3 clustered/clustered.py` (and `clustered/diag.py`) | `clustered/clustered_results.json`, `clustered/diag_results.json` |
| LODO without progent (row 4) | `python3 lodo/lodo.py` | `lodo/lodo_results.json` |
| Stage gaps | `python3 stage/stage_gap.py` | `stage/stage_gap_results.json` |
| AgentDyn ground-truth audit (§5.1) | `python3 drift/gt_audit.py`; minimal: `python3 repro_agentdyn_ground_truth.py` | `drift/gt_audit_agentdyn_v1.json`; prints "21 of 55" |
| Drift replay (§5.4) | `python3 drift/replay_current.py && python3 drift/analyze_drift.py && python3 drift/classify_changes.py` | `drift/drift_results.json` |
| Judge pilot (§5.3; paid, $0.3787) | `python3 judge_pilot/make_sample.py && python3 judge_pilot/run_pilot.py && python3 judge_pilot/analyze.py` | `judge_pilot/judgments.jsonl`, `RESULTS.md` |
| Recall review | `python3 review/recall_analysis.py` | `review/recall_analysis.json` |
| Owner agreement (when labels exist) | `python3 review/owner_agreement.py` | `review/owner_agreement.json` |
| Number check | `python3 review/verify_numbers.py MANUSCRIPT_SUBMISSION_INTERNAL.md` | mismatch list |
| Prereg hash | `sha256sum docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md` | must equal `prereg/PREREG_RANKFLIP.sha256` |

**Withheld until the owner's blind labels are collected** (to keep the owner blind): `review/reviewer_labels.jsonl`, `review/unblinded.json`, `review/KEY_DO_NOT_OPEN.json`, `review/RECALL_KEY_DO_NOT_OPEN.json`. Their frozen hashes are in `prereg/LABELS_FROZEN.sha256` and `prereg/RECALL_LABELS_FROZEN.sha256`. `review/unblind.py` needs them; until they are added, run it in the original workspace.

**Removed for privacy:** `rankflip/upstream/cmp.json` (GitHub API commit metadata with contributor e-mail addresses). It can be re-fetched from the public GitHub compare API.

**Third-party content.** The `inputs/*PACKET*.md` files and the replay files quote trajectories from public benchmark releases. The e-mail addresses in them are benchmark fixtures.
