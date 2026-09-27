#!/usr/bin/env python3
"""Amendment 7a mock resume proof (no OpenRouter)."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
DEMO = ROOT / "experiments/harness_v2" / f"AMENDMENT7A_DEMO_{TS}"
OUT = DEMO / "pilot_run"
PORT = 18790
TARGET_EP = "indirect_retrieved_doc_v1/i0/gemma/A0"
REPORT = DEMO / "raw_proof.txt"


def mock_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k != "OPENROUTER_API_KEY"}
    env["OPENROUTER_BASE_URL"] = f"http://127.0.0.1:{PORT}/v1"
    return env


def wc_lines(path: Path) -> str:
    if not path.exists():
        return f"0 (missing {path.name})"
    n = sum(1 for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip())
    return str(n)


def snapshot(label: str, mock_log: Path) -> str:
    lines = [
        f"=== {label} ===",
        f"OPENROUTER_API_KEY in env: {repr(os.environ.get('OPENROUTER_API_KEY'))}",
        f"OPENROUTER_BASE_URL: {os.environ.get('OPENROUTER_BASE_URL')}",
        f"wc http_stream.jsonl: {wc_lines(OUT / 'http_stream.jsonl')}",
        f"wc ledger_rows.jsonl: {wc_lines(OUT / 'ledger_rows.jsonl')}",
        f"wc mock_server_requests.jsonl: {wc_lines(mock_log)}",
    ]
    return "\n".join(lines) + "\n"


def load_request_ids(*paths: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for p in paths:
        ids: set[str] = set()
        if p.exists():
            for ln in p.read_text(encoding="utf-8").splitlines():
                if not ln.strip():
                    continue
                o = json.loads(ln)
                rid = o.get("request_id")
                if rid:
                    ids.add(str(rid))
        out[p.name] = ids
    return out


def mock_rows_for_episode(mock_log: Path, http_stream: Path, episode_id: str) -> list[dict]:
    """Join mock log request_ids to http_stream episode rows."""
    stream_rows = []
    for ln in http_stream.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        o = json.loads(ln)
        if o.get("episode_id") == episode_id:
            stream_rows.append(o)
    return stream_rows


def main() -> int:
    DEMO.mkdir(parents=True, exist_ok=True)
    mock_log = DEMO / "mock_server_requests.jsonl"
    chunks: list[str] = []

    subprocess.run(["pkill", "-9", "-f", "run_harness_v2_pilot.py"], check=False)
    subprocess.run(["pkill", "-9", "-f", "amendment6_mock_openai_server.py"], check=False)
    time.sleep(0.3)
    lock = ROOT / "experiments/harness_v2/.pilot_live.lock"
    lock.unlink(missing_ok=True)

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
    env = mock_env()
    chunks.append(f"subprocess env OPENROUTER_API_KEY present: {'OPENROUTER_API_KEY' in env}\n")
    chunks.append(f"subprocess OPENROUTER_BASE_URL={env.get('OPENROUTER_BASE_URL')}\n")

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
    )
    deadline = time.time() + 45.0
    while time.time() < deadline:
        lr = OUT / "ledger_rows.jsonl"
        if lr.exists():
            rows = [json.loads(l) for l in lr.read_text(encoding="utf-8").splitlines() if l.strip()]
            if rows:
                last = rows[-1]
                if last.get("episode_id") == TARGET_EP and int(last.get("call_index") or 0) == 1:
                    break
        time.sleep(0.005)
    os.environ.update(env)
    chunks.append(snapshot("(i) just before SIGKILL", mock_log))
    os.kill(pilot.pid, signal.SIGKILL)
    time.sleep(0.5)
    chunks.append(snapshot("(ii) immediately after SIGKILL", mock_log))

    pre_stream = OUT / "http_stream.jsonl"
    pre_rows = mock_rows_for_episode(mock_log, pre_stream, TARGET_EP) if pre_stream.exists() else []
    chunks.append("TARGET_EP rows in http_stream before resume:\n")
    for r in pre_rows:
        chunks.append(json.dumps({"episode_id": r.get("episode_id"), "call_index": r.get("call_index"), "request_id": r.get("request_id")}) + "\n")

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
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    chunks.append(f"resume exit_code={resume.returncode}\n")
    chunks.append(snapshot("(iii) after --resume completes", mock_log))

    post_rows = mock_rows_for_episode(mock_log, pre_stream, TARGET_EP)
    chunks.append("TARGET_EP rows in http_stream after resume (all calls for episode):\n")
    for r in post_rows:
        chunks.append(json.dumps({"episode_id": r.get("episode_id"), "call_index": r.get("call_index"), "request_id": r.get("request_id")}) + "\n")

    ids_map = load_request_ids(
        OUT / "http_stream.jsonl",
        OUT / "ledger_rows.jsonl",
        mock_log,
    )
    all_three = set.intersection(*ids_map.values()) if len(ids_map) == 3 else set()
    mism = []
    for name, s in ids_map.items():
        mism.append(f"{name} only: {sorted(s - all_three)}")
    chunks.append("request_id set-compare at (iii):\n")
    chunks.append(json.dumps({k: sorted(v) for k, v in ids_map.items()}, indent=2) + "\n")
    chunks.append("\n".join(mism) + "\n")

    # Re-send finding
    by_ci: dict[int, list[str]] = {}
    for r in post_rows:
        by_ci.setdefault(int(r["call_index"]), []).append(str(r["request_id"]))
    chunks.append(f"call_index request_ids for {TARGET_EP}: {json.dumps(by_ci, indent=2)}\n")
    if len(by_ci.get(1, [])) > 1:
        chunks.append(
            "FINDING: call_index 1 was RE-SENT after resume (duplicate request_id for same episode_id+call_index).\n"
        )
    elif 1 in by_ci and len(pre_rows) == 1 and len(post_rows) > len(pre_rows):
        chunks.append("FINDING: episode restarted; new request_id(s) for continued indices.\n")

    mock.kill()
    REPORT.write_text("".join(chunks), encoding="utf-8")
    print(REPORT.read_text(encoding="utf-8"))
    print(f"DEMO_DIR={DEMO.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
