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

---
## Round-10 additions (2026-10-16, Tehran), in `round10/`
- `attarg/`: ATT-ARG argument-constant attempt scorer. The procedure and constant table were hash-locked before scoring (`PROCEDURE_ATTARG.sha256`). `score_attarg.py` needs the public runs; analyses run via `analyses.py`. `validation/` holds the AI-label validation (labels hash-locked before comparison).
- `ext/`: extended reference-solution audit of AgentDojo (089ed468), AgentDyn (5353cf76), AutoDojo (xhOwenMa/AutoDojo aa458794) and uber/ADR (a6076aa3, not runnable as-is). Clones are NOT included; fetch them at those commits. Run `python audit_suites.py <path-to-src> out.json`.
- `exposure/`: downstream-exposure table and procedure. `c_items/`, `bitems/`: earlier executed checks.
- `human_packet/`: 40-episode blind packet and instructions. The answer key is **withheld**; its hash is in `KEY_SEPARATE.sha256`.
- `ISSUE_AgentDyn_FINAL_round10.md`: issue draft (not filed). `RELATED_WORK_ROUND10.md`: related-work notes.
- Not included: third-party paper texts and benchmark run files.

## Secret scan
A regex scan for API keys, tokens, private keys and e-mail addresses was run on 2026-10-16. Hits are only fictitious fixture data from the benchmarks: e-mail addresses such as trustme@gmail.com, and an "OPENSSH PRIVATE KEY" string that is part of an AgentDyn dailylife injection-task GOAL. No credentials were found. The scan script is reproduced in `round10/SECRET_SCAN.txt`.

## License
Our code and derived data: [PLACEHOLDER: license chosen by the owner, e.g. MIT / CC-BY-4.0]. Third-party benchmark code and runs keep their own licenses (AgentDojo MIT [verify], AgentDyn MIT, AutoDojo MIT, ADR Apache-2.0).
