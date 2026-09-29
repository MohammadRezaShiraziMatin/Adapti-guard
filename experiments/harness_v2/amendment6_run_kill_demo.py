#!/usr/bin/env python3
"""SIGKILL persistence proof supervisor (mock HTTP only)."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
N = 7
TS = "20260927-155900"
DEMO = ROOT / "experiments/harness_v2" / f"AMENDMENT6_DEMO_{TS}"
OUT = DEMO / "pilot_run"
PORT = 18768


def main() -> int:
    DEMO.mkdir(parents=True, exist_ok=True)
    for pat in ("run_harness_v2_pilot.py", "amendment6_mock_openai_server.py"):
        subprocess.run(["pkill", "-9", "-f", pat], check=False)
    time.sleep(0.3)
    lock = ROOT / "experiments/harness_v2/.pilot_live.lock"
    lock.unlink(missing_ok=True)

    mock_log = DEMO / "mock_server_requests.jsonl"
    mock_log.write_text("", encoding="utf-8")
    mock = subprocess.Popen(
        [
            sys.executable,
            str(ROOT / "experiments/harness_v2/amendment6_mock_openai_server.py"),
            "--port",
            str(PORT),
            "--request-log",
            str(mock_log),
        ],
        cwd=str(ROOT),
    )
    time.sleep(0.6)
    env = os.environ.copy()
    env["OPENROUTER_BASE_URL"] = f"http://127.0.0.1:{PORT}/v1"
    env["OPENROUTER_API_KEY"] = "local-mock-amendment6-demo"
    pilot = subprocess.Popen(
        [
            sys.executable,
            str(ROOT / "scripts/run_harness_v2_pilot.py"),
            "--live",
            "--out-dir",
            str(OUT),
        ],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    deadline = time.time() + 30.0
    triggered = False
    while time.time() < deadline:
        stream = OUT / "http_stream.jsonl"
        led_path = OUT / "running_ledger.json"
        if stream.exists() and led_path.exists():
            lines = [ln for ln in stream.read_text(encoding="utf-8").splitlines() if ln.strip()]
            led = json.loads(led_path.read_text(encoding="utf-8"))
            if len(lines) >= N and int(led.get("http_used", 0)) >= N:
                if len(lines) == N and int(led["http_used"]) == N:
                    triggered = True
                    break
        time.sleep(0.005)
    if not triggered:
        pilot.kill()
        mock.kill()
        raise SystemExit("never reached stable N before timeout")
    os.kill(pilot.pid, signal.SIGKILL)
    time.sleep(0.4)
    lines = [
        json.loads(ln)
        for ln in (OUT / "http_stream.jsonl").read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    led = json.loads((OUT / "running_ledger.json").read_text(encoding="utf-8"))
    server_n = sum(
        1 for ln in mock_log.read_text(encoding="utf-8").splitlines() if ln.strip()
    )
    s = sum(float(x.get("cost_usd") or 0) for x in lines)
    report = {
        "N": N,
        "http_stream_lines": len(lines),
        "server_requests": server_n,
        "ledger_http_used": led["http_used"],
        "sum_stream_cost_usd": s,
        "ledger_spent_usd": led["spent_usd"],
    }
    (DEMO / "post_sigkill_report.json").write_text(json.dumps(report, indent=2) + "\n")
    snap = DEMO / "http_stream_at_sigkill.jsonl"
    snap.write_text("\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8")
    (DEMO / "running_ledger_at_sigkill.json").write_text(
        json.dumps(led, indent=2) + "\n", encoding="utf-8"
    )
    mock_snap = DEMO / "mock_server_requests_at_sigkill.jsonl"
    mock_snap.write_text(
        "\n".join(mock_log.read_text(encoding="utf-8").splitlines()[:N]) + "\n", encoding="utf-8"
    )
    assert len(lines) == N == server_n == int(led["http_used"])
    assert abs(s - float(led["spent_usd"])) < 1e-9

    resume_env = env.copy()
    lock.unlink(missing_ok=True)
    resume = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/run_harness_v2_pilot.py"),
            "--live",
            "--out-dir",
            str(OUT),
            "--resume",
        ],
        cwd=str(ROOT),
        env=resume_env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    (DEMO / "pilot_resume_stdout.log").write_text(resume.stdout + resume.stderr)
    progress = (OUT / "progress.log").read_text(encoding="utf-8")
    ids = [
        json.loads(ln)["episode_id"]
        for ln in (OUT / "episodes.jsonl").read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    first = "indirect_retrieved_doc_v1/i0/qwen3/A0"
    skip = {
        "episodes_complete": len(ids),
        "first_in_completed": first in ids,
        "episode_begin_first_count": progress.count(f"episode_begin {first}"),
    }
    (DEMO / "resume_skip_check.json").write_text(json.dumps(skip, indent=2) + "\n")
    mock.kill()
    print(json.dumps({"demo_dir": str(DEMO.relative_to(ROOT)), "report": report, "resume": skip}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
