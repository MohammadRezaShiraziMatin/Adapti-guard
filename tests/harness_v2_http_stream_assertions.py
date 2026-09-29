"""Helpers for Amendment 9 http_stream.jsonl wire-byte assertions."""
from __future__ import annotations

import base64
import json
from pathlib import Path


def load_http_stream_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def assert_all_stream_rows_have_wire_bytes(
    path: Path,
    *,
    expected_bodies: list[bytes] | None = None,
) -> list[dict]:
    rows = load_http_stream_rows(path)
    assert rows, "http_stream.jsonl must contain at least one row"
    with_wire = [r for r in rows if r.get("request_wire_body_base64")]
    assert len(with_wire) == len(rows), (
        f"every row must have request_wire_body_base64 (rows={len(rows)} with_wire={len(with_wire)})"
    )
    if expected_bodies is not None:
        assert len(rows) == len(expected_bodies)
        for row, expected in zip(rows, expected_bodies, strict=True):
            stored = base64.standard_b64decode(row["request_wire_body_base64"])
            assert stored == expected
    return rows
