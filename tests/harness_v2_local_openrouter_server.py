"""Shared local fake OpenRouter HTTP server for harness v2 integration tests."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


class LocalFakeOpenRouterServer:
    def __init__(
        self,
        *,
        auth_limit_remaining: float = 0.8123,
        auth_usage: float = 1.6877,
    ) -> None:
        self.auth_limit_remaining = auth_limit_remaining
        self.auth_usage = auth_usage
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
