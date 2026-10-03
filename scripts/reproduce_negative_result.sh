#!/usr/bin/env bash
# Offline reproduction of every table, figure and number in the negative-result manuscript from committed traces.
# No network, no API key, no spend. External-data steps (InjecAgent) are skipped unless the external checkout and their scripts exist (neither is in this repository, see REPRODUCIBILITY.md).
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
step() { printf '\n== %s\n' "$1"; }
step "Tracks A/B deterministic re-scoring";        $PY scripts/rescore_tracks_ab_deterministic.py >/dev/null
step "Harness v2 exploratory analysis";            $PY scripts/analyze_harness_v2_exploratory.py experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930 >/dev/null
step "Independent defended analysis (E3)";         $PY scripts/analyze_independent_defended.py experiments/harness_v2/HARNESS_V2_INDEPENDENT_SCREEN_20260930 experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930 >/dev/null
step "MT1 held-out application of the rules";      $PY scripts/apply_rules_second_dataset_mt1.py >/dev/null
step "Spotlight channel check";                    $PY scripts/analyze_spotlight_ctx_check.py >/dev/null
step "E3 delivery audit";                          $PY scripts/audit_e3_delivery.py >/dev/null
step "E3 power and endpoint sensitivity";           $PY scripts/e3_power_sensitivity.py >/dev/null
for f in make_fig1_scoring_flip make_fig2_susceptibility_heatmap make_fig3_defended_vs_a0; do step "Figure $f"; $PY scripts/$f.py; done
if [ -d "${INJECAGENT_REPO:-/home/user/uiuc-kang-lab/injecagent}/data" ] && [ -f scripts/analyze_injecagent_live.py ]; then
  step "InjecAgent offline check and dataset audit"; $PY scripts/injecagent_offline_check.py; $PY scripts/audit_datasets.py
  for m in qwen-2.5-7b llama-3.1-8b llama-3.3-70b mistral-small-3.2-24b; do step "InjecAgent analysis $m"; $PY scripts/analyze_injecagent_live.py "$m" >/dev/null; done
else
  echo "(skipping InjecAgent steps: external checkout or its scripts are not in this repository; see REPRODUCIBILITY.md)"
fi
step "Manuscript, number ledger, consistency tests"
$PY scripts/assemble_manuscript.py; $PY scripts/build_number_ledger.py
$PY -m pytest tests/test_manuscript_number_ledger.py -q
if git rev-parse --git-dir >/dev/null 2>&1 && ! git diff --quiet -- docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md docs/paper/negative_result/NUMBERS_LEDGER.md docs/paper/negative_result/figures docs/research/artifacts/e3_delivery_audit_20261003.json; then
  echo "WARNING: regenerated manuscript, ledger or figures differ from the committed copies (stale commit); commit the regenerated files."
  [ "${STRICT:-0}" = "1" ] && exit 1
fi
echo; echo "OK: manuscript numbers regenerate from committed artifacts."
