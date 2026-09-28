"""Amendment 9 round 4 — shared HTTP client, wire capture, manifest, smoke guards."""
from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.amendment9_smoke_controls import SMOKE_USD_CAP  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_v2_http_client import (  # noqa: E402
    close_pilot_http_client,
    create_pilot_http_client,
)
from adapti_guard.evaluation.harness_v2.run_manifest import (  # noqa: E402
    is_worktree_dirty,
    resolve_repo_head_sha,
    resolve_runner_code_sha,
    write_run_manifest,
)
from adapti_guard.evaluation.harness_v2.wire_request_body import remove_top_level_json_field  # noqa: E402
from scripts.run_harness_v2_pilot import (  # noqa: E402
    pilot_schedule_for_run,
)
from tests.harness_v2_local_openrouter_server import (  # noqa: E402
    LocalFakeOpenRouterServer,
    require_local_loopback,
)
from tests.test_harness_v2_amendment9_smoke_cli import AMENDMENT9_SMOKE_EPISODE_IDS  # noqa: E402


def _load_pilot_module():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        ROOT / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _wire_main_schedule():
    return [
        {
            "scenario_id": "benign_weather_v1",
            "instance_index": 0,
            "family": "llama",
            "condition": "A0",
        }
    ]


def _patch_pilot_for_local_main(monkeypatch, mod, out: Path):
    monkeypatch.setattr(mod, "is_worktree_dirty", lambda _root: False)
    monkeypatch.setattr(
        mod.PilotRunLock,
        "try_acquire",
        lambda **kwargs: type("L", (), {"release": lambda self: None})(),
    )
    real_sched = mod.pilot_schedule_for_run

    def _sched(**kw):
        if kw.get("amendment9_llama_smoke"):
            return real_sched(**kw)
        return _wire_main_schedule()

    monkeypatch.setattr(mod, "pilot_schedule_for_run", _sched)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_harness_v2_pilot.py",
            "--live",
            "--pilot-label",
            "harness_v2_pilot_0",
            "--out-dir",
            str(out),
        ],
    )


class _ForwardHttpProxy:
    """Minimal HTTP proxy recording forwarded POST bodies (plain http targets)."""

    def __init__(self) -> None:
        self.forwarded_bodies: list[bytes] = []
        self._httpd: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0

    def start(self) -> None:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args) -> None:  # noqa: A003
                return

            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                outer.forwarded_bodies.append(body)
                target = self.path
                if not target.startswith("http"):
                    self.send_response(400)
                    self.end_headers()
                    return
                parsed = urllib.parse.urlparse(target)
                host = parsed.hostname or "127.0.0.1"
                port = parsed.port or 80
                path = parsed.path or "/"
                if parsed.query:
                    path = f"{path}?{parsed.query}"
                sock = socket.create_connection((host, port), timeout=30)
                try:
                    req_lines = [
                        f"POST {path} HTTP/1.1",
                        f"Host: {host}:{port}",
                        "Content-Type: application/json",
                        f"Content-Length: {len(body)}",
                        "Connection: close",
                        "",
                        "",
                    ]
                    header_block = "\r\n".join(req_lines[:-2]).encode("ascii") + b"\r\n\r\n"
                    sock.sendall(header_block + body)
                    resp = b""
                    while True:
                        chunk = sock.recv(4096)
                        if not chunk:
                            break
                        resp += chunk
                finally:
                    sock.close()
                header_end = resp.find(b"\r\n\r\n")
                if header_end < 0:
                    self.send_response(502)
                    self.end_headers()
                    return
                header_text = resp[:header_end].decode("iso-8859-1", errors="replace")
                status_line = header_text.split("\r\n", 1)[0]
                status_code = int(status_line.split()[1])
                resp_body = resp[header_end + 4 :]
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)

        self._httpd = HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd = None


def test_shared_http_client_honours_proxy_and_closes_after_main(monkeypatch, tmp_path):
    require_local_loopback()
    server = LocalFakeOpenRouterServer()
    server.start()
    proxy = _ForwardHttpProxy()
    proxy.start()
    try:
        target = f"http://127.0.0.1:{server.port}/v1"
        monkeypatch.setenv("HTTP_PROXY", f"http://127.0.0.1:{proxy.port}")
        monkeypatch.setenv("http_proxy", f"http://127.0.0.1:{proxy.port}")
        monkeypatch.setenv("NO_PROXY", "")
        monkeypatch.setenv("no_proxy", "")
        monkeypatch.setenv("OPENROUTER_BASE_URL", target)
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        mod = _load_pilot_module()
        created_clients: list[httpx.AsyncClient] = []
        real_create = mod.create_pilot_http_client

        def _capture_create(**kwargs):
            client = real_create(**kwargs)
            created_clients.append(client)
            return client

        monkeypatch.setattr(mod, "create_pilot_http_client", _capture_create)
        out = tmp_path / "proxy_run"
        _patch_pilot_for_local_main(monkeypatch, mod, out)
        assert mod.main() == 0
        assert server.chat_bodies
        assert proxy.forwarded_bodies
        assert proxy.forwarded_bodies[0] == server.chat_bodies[0]
        assert created_clients and created_clients[0].is_closed
    finally:
        proxy.stop()
        server.stop()
        monkeypatch.delenv("HTTP_PROXY", raising=False)
        monkeypatch.delenv("http_proxy", raising=False)


def test_removed_harness_v2_env_vars_have_no_effect(monkeypatch, tmp_path):
    monkeypatch.setenv("HARNESS_V2_WIRE_MAIN_TEST", "1")
    monkeypatch.setenv("HARNESS_V2_ALLOW_DIRTY_LIVE", "1")
    smoke = pilot_schedule_for_run(amendment9_llama_smoke=True)
    assert len(smoke) == 20
    assert [f"{r['scenario_id']}/i{r['instance_index']}/{r['family']}/{r['condition']}" for r in smoke] == (
        AMENDMENT9_SMOKE_EPISODE_IDS
    )
    mod = _load_pilot_module()
    monkeypatch.setattr(mod, "is_worktree_dirty", lambda _root: True)
    out = tmp_path / "dirty"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_harness_v2_pilot.py",
            "--live",
            "--pilot-label",
            "harness_v2_pilot_0",
            "--out-dir",
            str(out),
            "--amendment9-llama-smoke",
        ],
    )
    assert mod.main() == 3


def test_smoke_with_non_default_usd_cap_refuses_before_http(monkeypatch, tmp_path):
    require_local_loopback()
    server = LocalFakeOpenRouterServer()
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        mod = _load_pilot_module()
        out = tmp_path / "bad_cap"
        monkeypatch.setattr(mod, "is_worktree_dirty", lambda _root: False)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "run_harness_v2_pilot.py",
                "--live",
                "--pilot-label",
                "harness_v2_pilot_0",
                "--out-dir",
                str(out),
                "--amendment9-llama-smoke",
                "--usd-cap",
                "0.05",
            ],
        )
        assert mod.main() != 0
        assert server.server_hits == 0
        assert server.auth_hits == 0
    finally:
        server.stop()


def test_timeout_keeps_wire_bytes_with_sent_unconfirmed_label(monkeypatch, tmp_path):
    require_local_loopback()
    server = LocalFakeOpenRouterServer(post_read_sleep_s=2.0)
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        mod = _load_pilot_module()
        out = tmp_path / "slow"
        _patch_pilot_for_local_main(monkeypatch, mod, out)

        async def _run_with_short_wall():
            return await mod.run_pilot_async(
                out,
                pilot_label="harness_v2_pilot_0",
                schedule_override=_wire_main_schedule(),
                wall_timeout_s=0.25,
                skip_preflight=True,
                reconcile_at_end=False,
            )

        summary = run_harness_event_loop(_run_with_short_wall)
        assert summary["http_used"] == 1
        assert len(server.chat_bodies) == 1
        row = json.loads((out / "http_stream.jsonl").read_text(encoding="utf-8").splitlines()[0])
        assert row["status"] == "cancelled_timeout"
        assert row.get("wire_sent_unconfirmed") is True
        stored = __import__("base64").standard_b64decode(row["request_wire_body_base64"])
        assert stored == server.chat_bodies[0]
    finally:
        server.stop()


def test_auth_preflight_http_error_persists_abort_reason(monkeypatch, tmp_path):
    require_local_loopback()
    server = LocalFakeOpenRouterServer(auth_http_status=503)
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        mod = _load_pilot_module()
        out = tmp_path / "auth_err"
        summary = run_harness_event_loop(
            lambda: mod.run_pilot_async(
                out,
                pilot_label="harness_v2_pilot_0",
                amendment9_llama_smoke=True,
                skip_preflight=False,
                reconcile_at_end=False,
            )
        )
        assert summary["stopped_reason"] == "auth_preflight_abort"
        record = json.loads((out / "preflight_auth_key_launch.json").read_text(encoding="utf-8"))
        assert record.get("abort_reason") == "auth_key_http_error"
    finally:
        server.stop()


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "test"
    env["GIT_AUTHOR_EMAIL"] = "test@example.com"
    env["GIT_COMMITTER_NAME"] = "test"
    env["GIT_COMMITTER_EMAIL"] = "test@example.com"
    return env


def _run_git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        env=_git_env(),
    )
    return proc.stdout.strip()


def test_manifest_runner_code_sha_vs_repo_head_and_dirty(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init")
    (repo / "experiments" / "harness_v2").mkdir(parents=True)
    (repo / "experiments" / "harness_v2" / "README.md").write_text("docs\n", encoding="utf-8")
    (repo / "src").mkdir()
    _run_git(repo, "add", ".")
    _run_git(repo, "commit", "-m", "bootstrap")
    (repo / "src" / "runner.py").write_text("print('run')\n", encoding="utf-8")
    _run_git(repo, "add", ".")
    _run_git(repo, "commit", "-m", "runner code")
    code_sha = _run_git(repo, "log", "-1", "--format=%H", "--", "src", "scripts")
    (repo / "notes.md").write_text("docs only\n", encoding="utf-8")
    _run_git(repo, "add", "notes.md")
    _run_git(repo, "commit", "-m", "docs only head")
    head_sha = _run_git(repo, "rev-parse", "HEAD")
    assert head_sha != code_sha
    assert resolve_runner_code_sha(repo) == code_sha
    assert resolve_repo_head_sha(repo) == head_sha
    out = tmp_path / "manifest_out"
    path = write_run_manifest(out, repo_root=repo, pilot="harness_v2_pilot_0")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["runner_code_sha"] == code_sha
    assert manifest["repo_head_sha"] == head_sha
    assert manifest["runner_worktree_dirty"] is False
    (repo / "notes.md").write_text("dirty\n", encoding="utf-8")
    assert is_worktree_dirty(repo) is True


@pytest.mark.parametrize("field", ["model", "tools", "max_tokens", "provider"])
@pytest.mark.parametrize("position", ["first", "middle", "last"])
def test_remove_top_level_json_field_positions_and_message_noise(field: str, position: str):
    msg_content = "text with ,, model tools max_tokens provider names unchanged"
    messages_json = json.dumps([{"role": "user", "content": msg_content}], separators=(",", ":"))
    if position == "first":
        original_text = f'{{"{field}":"v","messages":{messages_json},"tail":true}}'
    elif position == "middle":
        original_text = f'{{"head":true,"messages":{messages_json},"{field}":"v","tail":true}}'
    else:
        original_text = f'{{"head":true,"messages":{messages_json},"{field}":"v"}}'
    original = original_text.encode("utf-8")
    tampered = remove_top_level_json_field(original, field)
    parsed = json.loads(tampered.decode("utf-8"))
    assert field not in parsed
    assert msg_content in json.dumps(parsed)
    start, end = _deleted_span(original_text, field)
    assert original_text[:start] + original_text[end:] == tampered.decode("utf-8")


def _deleted_span(text: str, field: str) -> tuple[int, int]:
    from adapti_guard.evaluation.harness_v2.wire_request_body import _find_top_level_key_span

    return _find_top_level_key_span(text, field)


def test_trust_env_client_uses_proxy_for_local_target():
    require_local_loopback()
    server = LocalFakeOpenRouterServer()
    server.start()
    proxy = _ForwardHttpProxy()
    proxy.start()
    try:
        os.environ["HTTP_PROXY"] = f"http://127.0.0.1:{proxy.port}"
        os.environ["NO_PROXY"] = ""
        os.environ["no_proxy"] = ""
        client = create_pilot_http_client(trust_env=True)

        async def _post():
            try:
                resp = await client.post(
                    f"http://127.0.0.1:{server.port}/v1/chat/completions",
                    json={"model": "m", "messages": [{"role": "user", "content": "hi"}]},
                    headers={"Authorization": "Bearer x"},
                )
                resp.raise_for_status()
            finally:
                await close_pilot_http_client(client)

        run_harness_event_loop(_post)
        assert server.chat_bodies
        assert proxy.forwarded_bodies[0] == server.chat_bodies[0]
    finally:
        os.environ.pop("HTTP_PROXY", None)
        proxy.stop()
        server.stop()
