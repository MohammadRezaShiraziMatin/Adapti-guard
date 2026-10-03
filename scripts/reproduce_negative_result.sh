#!/usr/bin/env bash
# Offline reproduction of the tables, figures and numbers of E1-E3, MT1 and the M6 channel check in the negative-result manuscript, from committed traces.
# No network, no API key, no spend. Manuscript sections 6.6, 6.7 and Appendix A use committed derived artifacts; the scripts that produced them are not in this repository.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
step() { printf '\n== %s\n' "$1"; }
step "Tracks A/B deterministic re-scoring";        $PY scripts/rescore_tracks_ab_deterministic.py >/dev/null
step "Harness v2 exploratory analysis";            $PY scripts/analyze_harness_v2_exploratory.py experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930 >/dev/null
step "Independent defended analysis (E3)";         $PY scripts/analyze_independent_defended.py experiments/harness_v2/HARNESS_V2_INDEPENDENT_SCREEN_20260930 experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930 >/dev/null
step "MT1 held-out application of the rules";      $PY scripts/apply_rules_second_dataset_mt1.py >/dev/null
step "Spotlight channel check";                    $PY scripts/analyze_spotlight_ctx_check.py >/dev/null
for f in make_fig1_scoring_flip make_fig2_susceptibility_heatmap make_fig3_defended_vs_a0; do step "Figure $f"; $PY scripts/$f.py; done
echo "(InjecAgent, calibration and Appendix A numbers are read from committed derived artifacts; their analysis scripts are not in this repository)"
step "Manuscript, number ledger, consistency tests"
$PY scripts/assemble_manuscript.py; $PY scripts/build_number_ledger.py
$PY -m pytest tests/test_manuscript_number_ledger.py -q
if git rev-parse --git-dir >/dev/null 2>&1 && ! git diff --quiet -- docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md docs/paper/negative_result/NUMBERS_LEDGER.md docs/paper/negative_result/figures; then
  echo "WARNING: regenerated manuscript, ledger or figures differ from the committed copies (stale commit); commit the regenerated files."
  [ "${STRICT:-0}" = "1" ] && exit 1
fi
echo; echo "OK: E1-E3, MT1 and M6 numbers regenerate from committed traces."
