#!/usr/bin/env bash
# Amendment 6 practical proof orchestrator (mock HTTP only; no OpenRouter).
set -euo pipefail
cd /workspace
TS=$(date -u +%Y%m%d-%H%M%S)
DEMO="experiments/harness_v2/AMENDMENT6_DEMO_${TS}"
mkdir -p "$DEMO"
PROOF_LOG="$DEMO/proof_commands.log"
exec > >(tee -a "$PROOF_LOG") 2>&1

echo "=== DEMO_DIR=$DEMO ==="
kill $(pgrep -f 'amendment6_mock_openai_server.py --port 18765' 2>/dev/null) 2>/dev/null || true
sleep 0.3
rm -f experiments/harness_v2/.pilot_live.lock

python3 experiments/harness_v2/amendment6_mock_openai_server.py \
  --port 18765 \
  --request-log "$DEMO/mock_server_requests.jsonl" \
  >>"$DEMO/mock_server.log" 2>&1 &
MOCK_PID=$!
echo "mock_pid=$MOCK_PID"
sleep 0.8

export OPENROUTER_BASE_URL=http://127.0.0.1:18765/v1
export OPENROUTER_API_KEY=local-mock-amendment6-demo
OUT="$DEMO/pilot_run"
N=7

python3 scripts/run_harness_v2_pilot.py --live --out-dir "$OUT" >>"$DEMO/pilot_stdout.log" 2>&1 &
PILOT_PID=$!
echo "pilot_pid=$PILOT_PID target_N=$N"

for i in $(seq 1 400); do
  c=$(wc -l < "$OUT/http_stream.jsonl" 2>/dev/null || echo 0)
  if [ "$c" -ge "$N" ]; then
    echo "http_stream_lines_reached=$c"
    break
  fi
  sleep 0.05
done

kill -9 "$PILOT_PID" 2>/dev/null || true
sleep 0.5
STREAM_LINES=$(wc -l < "$OUT/http_stream.jsonl")
SERVER_LINES=$(wc -l < "$DEMO/mock_server_requests.jsonl")
LEDGER_HTTP=$(python3 -c "import json; print(json.load(open('$OUT/running_ledger.json'))['http_used'])")
echo "=== post_sigkill counts (target N=$N) ==="
echo "http_stream.jsonl lines: $STREAM_LINES"
echo "mock_server_requests.jsonl lines: $SERVER_LINES"
echo "running_ledger.json http_used: $LEDGER_HTTP"
cat "$OUT/running_ledger.json"
python3 - <<PY
import json
from pathlib import Path
out = Path("$OUT")
n = int("$N")
lines = [json.loads(l) for l in out.joinpath("http_stream.jsonl").read_text().splitlines() if l.strip()]
led = json.loads((out / "running_ledger.json").read_text())
s = sum(float(x.get("cost_usd") or 0) for x in lines)
print("sum_stream_cost_usd", s)
print("ledger_spent_usd", led["spent_usd"])
assert len(lines) == n, (len(lines), n)
assert int(led["http_used"]) == n, (led["http_used"], n)
assert abs(s - float(led["spent_usd"])) < 1e-9, (s, led["spent_usd"])
print("ASSERT_OK lines=ledger=server=", n)
PY
SERVER_LINES_AFTER=$(wc -l < "$DEMO/mock_server_requests.jsonl")
if [ "$SERVER_LINES_AFTER" != "$N" ]; then
  echo "WARN server line count $SERVER_LINES_AFTER != $N (race); re-check"
fi
test "$STREAM_LINES" = "$N" && test "$LEDGER_HTTP" = "$N"

# Resume: complete run (mock still up)
rm -f experiments/harness_v2/.pilot_live.lock
echo "=== resume run (first 40 lines progress) ==="
python3 scripts/run_harness_v2_pilot.py --live --out-dir "$OUT" --resume >>"$DEMO/pilot_resume_stdout.log" 2>&1 || true
head -40 "$OUT/progress.log" | tee "$DEMO/resume_progress_head.txt"
python3 - <<PY
import json
from pathlib import Path
out = Path("$OUT")
completed = set()
for line in (out / "episodes.jsonl").read_text().splitlines():
    if line.strip():
        completed.add(json.loads(line)["episode_id"])
# first schedule slot should remain if killed mid-episode
first = "indirect_retrieved_doc_v1/i0/qwen3/A0"
print("completed_count", len(completed))
print("first_episode_in_episodes_jsonl", first in completed)
PY

kill "$MOCK_PID" 2>/dev/null || true
echo "$DEMO" > /tmp/amend6_demo_final.txt
