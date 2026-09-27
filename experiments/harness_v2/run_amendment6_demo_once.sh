#!/usr/bin/env bash
set -euo pipefail
cd /workspace
TS=20260927-155700
DEMO=experiments/harness_v2/AMENDMENT6_DEMO_${TS}
mkdir -p "$DEMO"
pkill -9 -f run_harness_v2_pilot.py 2>/dev/null || true
pkill -9 -f amendment6_mock_openai_server.py 2>/dev/null || true
sleep 0.3
rm -f experiments/harness_v2/.pilot_live.lock
PORT=18766
python3 experiments/harness_v2/amendment6_mock_openai_server.py --port "$PORT" --request-log "$DEMO/mock_server_requests.jsonl" &
MOCK=$!
sleep 0.8
export OPENROUTER_BASE_URL=http://127.0.0.1:${PORT}/v1
export OPENROUTER_API_KEY=local-mock-amendment6-demo
OUT="$DEMO/pilot_run"
N=7
python3 scripts/run_harness_v2_pilot.py --live --out-dir "$OUT" &
PILOT=$!
for i in $(seq 1 500); do
  if [ -f "$OUT/running_ledger.json" ] && [ -f "$OUT/http_stream.jsonl" ]; then
    c=$(wc -l < "$OUT/http_stream.jsonl")
    h=$(python3 -c "import json; print(json.load(open('$OUT/running_ledger.json'))['http_used'])")
    if [ "$c" -eq "$N" ] && [ "$h" -eq "$N" ]; then
      echo "http_stream=$c ledger_http_used=$h"
      break
    fi
  fi
  sleep 0.02
done
sleep 0.05
kill -9 "$PILOT" 2>/dev/null || true
sleep 0.6
{
  echo "N=$N"
  echo -n "wc -l http_stream.jsonl: "
  wc -l "$OUT/http_stream.jsonl"
  echo -n "wc -l mock_server_requests.jsonl: "
  wc -l "$DEMO/mock_server_requests.jsonl"
  echo "running_ledger.json:"
  cat "$OUT/running_ledger.json"
} | tee "$DEMO/post_sigkill_counts.txt"

python3 - "$OUT" "$N" <<'PY' | tee "$DEMO/post_sigkill_assert.txt"
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
n = int(sys.argv[2])
lines = [json.loads(l) for l in out.joinpath("http_stream.jsonl").read_text().splitlines() if l.strip()]
led = json.loads((out / "running_ledger.json").read_text())
s = sum(float(x.get("cost_usd") or 0) for x in lines)
server_n = sum(1 for _ in Path(out.parent).joinpath("mock_server_requests.jsonl").read_text().splitlines() if _.strip())
print("sum_stream_cost_usd", s)
print("ledger_spent_usd", led["spent_usd"])
print("server_requests", server_n)
assert len(lines) == n
assert int(led["http_used"]) == n
assert server_n == n
assert abs(s - float(led["spent_usd"])) < 1e-9
print("ASSERT_OK all_counts=", n)
PY

rm -f experiments/harness_v2/.pilot_live.lock
python3 scripts/run_harness_v2_pilot.py --live --out-dir "$OUT" --resume > "$DEMO/pilot_resume_stdout.log" 2>&1
grep episode_begin "$OUT/progress.log" | head -5 | tee "$DEMO/resume_progress_sample.txt"
python3 - <<PY | tee "$DEMO/resume_skip_check.txt"
import json
from pathlib import Path
out = Path("$OUT")
ids = [json.loads(l)["episode_id"] for l in out.joinpath("episodes.jsonl").read_text().splitlines() if l.strip()]
print("episodes_complete", len(ids))
print("skipped_first", "indirect_retrieved_doc_v1/i0/qwen3/A0" in ids)
begins = open(out/"progress.log").read().count("episode_begin indirect_retrieved_doc_v1/i0/qwen3/A0")
print("episode_begin_count_first", begins)
PY

kill "$MOCK" 2>/dev/null || true
echo "DONE $DEMO"
