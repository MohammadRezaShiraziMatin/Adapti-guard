"""Shared local fake OpenRouter HTTP server for harness v2 integration tests."""
from __future__ import annotations

import json
import socket
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


def local_loopback_tcp_works() -> bool:
    """False in some unshare -rn network namespaces where lo is not connected."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(1.0)
        client.connect(("127.0.0.1", port))
        client.close()
        return True
    except OSError:
        return False
    finally:
        srv.close()


def require_local_loopback() -> None:
    if not local_loopback_tcp_works():
        raise AssertionError(
            "127.0.0.1 TCP loopback unavailable; use: "
            "env -u OPENROUTER_API_KEY unshare -rn sh -c "
            "'ip link set lo up; python3 -m pytest tests/test_harness_v2_*.py -q -rs'"
        )


class LocalFakeOpenRouterServer:
    def __init__(
        self,
        *,
        auth_limit_remaining: float = 0.8123,
        auth_usage: float = 1.6877,
        post_read_sleep_s: float = 0.0,
        auth_http_status: int = 200,
        tool_then_stop: bool = False,
        close_connection_after_read: bool = False,
    ) -> None:
        self.auth_limit_remaining = auth_limit_remaining
        self.auth_usage = auth_usage
        self.post_read_sleep_s = post_read_sleep_s
        self.auth_http_status = auth_http_status
        self.tool_then_stop = tool_then_stop
        self.close_connection_after_read = close_connection_after_read
        self.server_hits = 0
        self.chat_bodies: list[bytes] = []
        self.auth_hits = 0
        self._httpd: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0

    def start(self) -> None:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
                return

            def do_GET(self) -> None:
                if self.path.endswith("/auth/key") or self.path.endswith("/v1/auth/key"):
                    outer.auth_hits += 1
                    if outer.auth_http_status != 200:
                        self.send_response(outer.auth_http_status)
                        self.end_headers()
                        return
                    payload = {
                        "data": {
                            "limit_remaining": outer.auth_limit_remaining,
                            "usage": outer.auth_usage,
                            "limit": 2.5,
                        }
                    }
                    body = json.dumps(payload).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                self.send_response(404)
                self.end_headers()

            def do_POST(self) -> None:
                if "chat/completions" not in self.path:
                    self.send_response(404)
                    self.end_headers()
                    return
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                outer.chat_bodies.append(body)
                outer.server_hits += 1
                if outer.close_connection_after_read:
                    try:
                        self.connection.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    self.connection.close()
                    return
                if outer.post_read_sleep_s > 0:
                    time.sleep(outer.post_read_sleep_s)
                if outer.tool_then_stop:
                    req = json.loads(body.decode("utf-8"))
                    messages = req.get("messages") or []
                    n_tool_rounds = sum(
                        1 for m in messages if m.get("role") == "assistant" and m.get("tool_calls")
                    )
                    if n_tool_rounds == 0:
                        tc_id = f"call_{uuid.uuid4().hex[:8]}"
                        resp = {
                            "id": "gen-local-tool",
                            "choices": [
                                {
                                    "message": {
                                        "role": "assistant",
                                        "content": "",
                                        "tool_calls": [
                                            {
                                                "id": tc_id,
                                                "type": "function",
                                                "function": {
                                                    "name": "retrieve_document",
                                                    "arguments": '{"doc_id": "hr-vacation-policy-00"}',
                                                },
                                            }
                                        ],
                                    },
                                    "finish_reason": "tool_calls",
                                }
                            ],
                            "usage": {
                                "prompt_tokens": 10,
                                "completion_tokens": 5,
                                "total_tokens": 15,
                                "cost": 0.0,
                            },
                        }
                        raw = json.dumps(resp).encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(raw)))
                        self.end_headers()
                        self.wfile.write(raw)
                        return
                resp = {
                    "id": "gen-local",
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "ok"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                        "cost": 0.0,
                    },
                }
                raw = json.dumps(resp).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        self._httpd = HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd = None
