#!/usr/bin/env bash
# Regenerate experiments/harness_v2/AMENDMENT9_WIRE_MAIN_PRE23125d7_PYTEST.txt
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORKTREE="${WORKTREE:-/tmp/adapti-guard-pre23125d7}"
EVIDENCE="${REPO_ROOT}/experiments/harness_v2/AMENDMENT9_WIRE_MAIN_PRE23125d7_PYTEST.txt"
git -C "$REPO_ROOT" worktree remove -f "$WORKTREE" 2>/dev/null || true
git -C "$REPO_ROOT" worktree add -f "$WORKTREE" 23125d7
cp "${REPO_ROOT}/tests/harness_v2_local_openrouter_server.py" "${WORKTREE}/tests/"
(
  cd "$WORKTREE"
  ADAPTI_GUARD_WORKTREE_ROOT="$WORKTREE" PYTHONPATH=src python3 -m pytest \
    "${REPO_ROOT}/tests/prefix_evidence/test_pre23125d7_zero_server_hits.py" \
    -q --tb=short 2>&1 || true
) | tee "$EVIDENCE"
