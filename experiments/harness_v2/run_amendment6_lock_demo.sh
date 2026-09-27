#!/usr/bin/env bash
set -euo pipefail
cd /workspace
TS=$(date -u +%Y%m%d-%H%M%S)
LOG="experiments/harness_v2/AMENDMENT6_DEMO_${TS}/lock_demo.log"
mkdir -p "$(dirname "$LOG")"
exec > >(tee "$LOG") 2>&1

kill $(pgrep -f 'amendment6_mock_openai_server.py --port 18765' 2>/dev/null) 2>/dev/null || true
sleep 0.2
rm -f experiments/harness_v2/.pilot_live.lock

python3 experiments/harness_v2/amendment6_mock_openai_server.py \
  --port 18765 \
  --request-log /tmp/amend6_lock_mock.jsonl >>/tmp/amend6_lock_mock_server.log 2>&1 &
MOCK=$!
sleep 0.5
export OPENROUTER_BASE_URL=http://127.0.0.1:18765/v1
export OPENROUTER_API_KEY=local-mock-amendment6-demo

OUT1="experiments/harness_v2/AMENDMENT6_LOCK_HOLD_${TS}"
python3 scripts/run_harness_v2_pilot.py --live --out-dir "$OUT1" >/tmp/pilot_hold.log 2>&1 &
HOLD=$!
sleep 1.2
echo "=== lock file while first pilot running (pid $HOLD) ==="
cat experiments/harness_v2/.pilot_live.lock

echo "=== second concurrent pilot ==="
set +e
python3 scripts/run_harness_v2_pilot.py --live --out-dir "experiments/harness_v2/AMENDMENT6_LOCK_BLOCK_${TS}" >/tmp/pilot_block.log 2>&1
EC=$?
set -e
echo "exit_code=$EC"
echo "stderr/stdout:"
cat /tmp/pilot_block.log

kill -9 "$HOLD" 2>/dev/null || true
sleep 0.3
rm -f experiments/harness_v2/.pilot_live.lock

echo "=== stale lock (dead pid 999999999) ==="
printf '%s\n' '{"pid": 999999999, "out_dir": "/tmp/stale", "pilot_label": "x"}' > experiments/harness_v2/.pilot_live.lock
cat experiments/harness_v2/.pilot_live.lock
python3 - <<'PY'
import json
from pathlib import Path
import sys
sys.path.insert(0, "src")
from adapti_guard.evaluation.harness_v2.pilot_run_lock import PilotRunLock
lock = PilotRunLock.try_acquire(out_dir=Path("experiments/harness_v2/AMENDMENT6_STALE_OK"))
print("acquired_pid", lock.payload["pid"])
lock.release()
print("lock_after_release_exists", Path("experiments/harness_v2/.pilot_live.lock").exists())
PY

kill "$MOCK" 2>/dev/null || true
echo "LOG=$LOG"
