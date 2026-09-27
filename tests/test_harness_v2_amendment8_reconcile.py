"""Amendment 8 item 5 — cancelled_timeout reconciliation (mock lookups only)."""
from __future__ import annotations

import json
from pathlib import Path

from adapti_guard.evaluation.harness_v2.cancelled_timeout_reconcile import (
    reconcile_cancelled_timeout_rows,
)


def _seed_pack(tmp_path: Path, *, request_id: str, raw_response: dict) -> Path:
    out = tmp_path / "pack"
    out.mkdir()
    row = {
        "request_id": request_id,
        "status": "cancelled_timeout",
        "cost_usd": None,
        "billed_placeholder_usd": 0.01,
        "reconciliation_source": "pending",
        "raw_response": raw_response,
    }
    led = {
        "request_id": request_id,
        "status": "cancelled_timeout",
        "cost_usd": None,
        "billed_placeholder_usd": 0.01,
        "reconciliation_source": "pending",
    }
    (out / "http_stream.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    (out / "ledger_rows.jsonl").write_text(json.dumps(led) + "\n", encoding="utf-8")
    return out


def test_generation_id_path_resolves_cost(tmp_path: Path):
    out = _seed_pack(tmp_path, request_id="r1", raw_response={"id": "gen-abc"})
    stats = reconcile_cancelled_timeout_rows(
        out,
        generation_cost_lookup=lambda gid: 0.0025 if gid == "gen-abc" else None,
        key_usage_before_usd=1.0,
        key_usage_after_usd=1.0,
    )
    led = json.loads((out / "ledger_rows.jsonl").read_text().strip())
    assert stats["generation_id"] == 1
    assert led["reconciliation_source"] == "generation_id"
    assert led["cost_usd"] == 0.0025


def test_single_key_delta_resolves(tmp_path: Path):
    out = _seed_pack(tmp_path, request_id="r2", raw_response={})
    stats = reconcile_cancelled_timeout_rows(
        out,
        generation_cost_lookup=lambda _gid: None,
        key_usage_before_usd=1.0,
        key_usage_after_usd=1.0007,
    )
    led = json.loads((out / "ledger_rows.jsonl").read_text().strip())
    assert stats["key_delta"] == 1
    assert led["reconciliation_source"] == "key_delta"
    assert led["cost_usd"] == 0.0007


def test_ambiguous_delta_stays_unresolved(tmp_path: Path):
    out = tmp_path / "pack"
    out.mkdir()
    rows = [
        {"request_id": "a", "status": "cancelled_timeout", "cost_usd": None, "reconciliation_source": "pending"},
        {"request_id": "b", "status": "cancelled_timeout", "cost_usd": None, "reconciliation_source": "pending"},
    ]
    (out / "ledger_rows.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8"
    )
    (out / "http_stream.jsonl").write_text(
        "\n".join(json.dumps({**r, "raw_response": {}}) for r in rows) + "\n",
        encoding="utf-8",
    )
    stats = reconcile_cancelled_timeout_rows(
        out,
        generation_cost_lookup=lambda _gid: None,
        key_usage_before_usd=1.0,
        key_usage_after_usd=1.01,
    )
    for line in (out / "ledger_rows.jsonl").read_text().splitlines():
        led = json.loads(line)
        assert led["reconciliation_source"] == "unresolved"
        assert led["cost_usd"] is None
    assert stats["unresolved"] == 2
