"""Post-run reconciliation for cancelled_timeout ledger rows (Amendment 8 §2.5.2)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def _apply_row_update(row: dict[str, Any], led: dict[str, Any]) -> None:
    row["reconciliation_source"] = led["reconciliation_source"]
    row["cost_usd"] = led.get("cost_usd")


def reconcile_cancelled_timeout_rows(
    out_dir: Path,
    *,
    generation_cost_lookup: Callable[[str], float | None],
    attempt_key_windows: dict[str, tuple[float, float]] | None = None,
) -> dict[str, int]:
    """Resolve ``cancelled_timeout`` rows; never guess — leave ``cost_usd`` null if unresolved.

    ``attempt_key_windows`` maps ``request_id`` → ``(usage_before_usd, usage_after_usd)`` for that
    single HTTP attempt only (sequential run). Run-level usage deltas must **not** be passed here.
    """
    ledger_path = out_dir / "ledger_rows.jsonl"
    stream_path = out_dir / "http_stream.jsonl"
    ledger_rows = _load_jsonl(ledger_path)
    stream_rows = _load_jsonl(stream_path)
    windows = attempt_key_windows or {}

    pending_all = [
        r
        for r in ledger_rows
        if r.get("status") == "cancelled_timeout"
        and r.get("reconciliation_source", "pending") == "pending"
    ]

    stats = {"generation_id": 0, "key_delta": 0, "unresolved": 0}

    for led in ledger_rows:
        if led.get("status") != "cancelled_timeout":
            continue
        if led.get("reconciliation_source") not in (None, "pending"):
            continue

        resolved_cost: float | None = None
        source = "unresolved"
        rid = str(led.get("request_id") or "")
        stream_row = next((r for r in stream_rows if str(r.get("request_id")) == rid), {})
        raw = stream_row.get("raw_response") or {}
        gen_id = raw.get("id") if isinstance(raw, dict) else None

        if gen_id:
            resolved_cost = generation_cost_lookup(str(gen_id))
            if resolved_cost is not None:
                source = "generation_id"

        if resolved_cost is None and len(pending_all) == 1 and rid in windows:
            before, after = windows[rid]
            delta = round(after - before, 8)
            pending_same_window = [
                r
                for r in pending_all
                if str(r.get("request_id")) == rid
            ]
            if len(pending_same_window) == 1 and delta > 0.0:
                resolved_cost = delta
                source = "key_delta"

        if resolved_cost is None:
            led["reconciliation_source"] = "unresolved"
            led["cost_usd"] = None
            stats["unresolved"] += 1
        else:
            led["reconciliation_source"] = source
            led["cost_usd"] = resolved_cost
            stats[source] += 1

        for srow in stream_rows:
            if str(srow.get("request_id")) == rid:
                _apply_row_update(srow, led)

    _write_jsonl(ledger_path, ledger_rows)
    _write_jsonl(stream_path, stream_rows)
    return stats
