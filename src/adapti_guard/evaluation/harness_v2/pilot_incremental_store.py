"""Incremental on-disk pilot persistence (Amendment 6 + 7a ledger rows + 7c resume)."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapti_guard.evaluation.harness_v2.trajectory_store import serialize_trajectory_call


def _fsync_path(path: Path) -> None:
    with open(path, "rb") as fh:
        os.fsync(fh.fileno())


class PilotIncrementalStore:
    def __init__(self, out_dir: Path, *, usd_cap: float, http_cap: int) -> None:
        self.out_dir = out_dir
        self.usd_cap = usd_cap
        self.http_cap = http_cap
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "trajectories").mkdir(exist_ok=True)
        self.http_stream_path = self.out_dir / "http_stream.jsonl"
        self.ledger_rows_path = self.out_dir / "ledger_rows.jsonl"
        self.ledger_path = self.out_dir / "running_ledger.json"
        self.progress_path = self.out_dir / "progress.log"
        self.episodes_jsonl = self.out_dir / "episodes.jsonl"
        self._seen_request_ids: set[str] = self._load_seen_request_ids()
        if not self.ledger_path.exists():
            self._write_ledger({"http_used": 0, "spent_usd": 0.0, "episodes_complete": 0})

    def _load_seen_request_ids(self) -> set[str]:
        ids: set[str] = set()
        if not self.ledger_rows_path.exists():
            return ids
        for line in self.ledger_rows_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rid = json.loads(line).get("request_id")
            if rid:
                ids.add(str(rid))
        return ids

    def log_progress(self, line: str) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        with open(self.progress_path, "a", encoding="utf-8") as fh:
            fh.write(f"{ts} {line}\n")
            fh.flush()
            os.fsync(fh.fileno())

    def ledger(self) -> dict[str, Any]:
        return json.loads(self.ledger_path.read_text(encoding="utf-8"))

    def spent_usd(self) -> float:
        return float(self.ledger().get("spent_usd", 0.0))

    def http_used(self) -> int:
        return int(self.ledger().get("http_used", 0))

    def usd_budget_exhausted(self) -> bool:
        return self.spent_usd() >= self.usd_cap

    def http_budget_exhausted(self) -> bool:
        return self.http_used() >= self.http_cap

    def append_ledger_row(self, row: dict[str, Any]) -> None:
        line = json.dumps(row, ensure_ascii=False) + "\n"
        with open(self.ledger_rows_path, "a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())

    def append_http_call(
        self,
        *,
        episode_id: str,
        record: Any,
        serialized: dict[str, Any],
        episode_attempt_id: str | None = None,
    ) -> dict[str, Any]:
        recorded_at = datetime.now(timezone.utc).isoformat()
        cost = float(serialized.get("cost_usd") or 0.0)
        request_id = serialized.get("request_id") or getattr(record, "request_id", None)
        if request_id and str(request_id) in self._seen_request_ids:
            self.log_progress(
                f"skip_duplicate_http_record request_id={request_id} episode={episode_id}"
            )
            return self.ledger()
        if request_id:
            self._seen_request_ids.add(str(request_id))
        attempt = episode_attempt_id or str(uuid.uuid4())
        ledger_row = {
            "request_id": request_id,
            "episode_id": episode_id,
            "call_index": serialized.get("call_index"),
            "cost_usd": cost,
            "recorded_at_utc": recorded_at,
            "episode_attempt_id": attempt,
            "superseded_by_resume": False,
        }
        row = {
            "recorded_at_utc": recorded_at,
            "episode_id": episode_id,
            "episode_attempt_id": attempt,
            "superseded_by_resume": False,
            **serialized,
        }
        line = json.dumps(row, ensure_ascii=False) + "\n"
        with open(self.http_stream_path, "a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())
        self.append_ledger_row(ledger_row)
        led = self.ledger()
        led["http_used"] = int(led.get("http_used", 0)) + 1
        led["spent_usd"] = round(float(led.get("spent_usd", 0.0)) + cost, 8)
        led["last_episode_id"] = episode_id
        led["last_call_index"] = serialized.get("call_index")
        led["last_request_id"] = request_id
        led["updated_at_utc"] = recorded_at
        self._refresh_billed_analysis_totals(led)
        self._write_ledger(led)
        return led

    def _refresh_billed_analysis_totals(self, led: dict[str, Any]) -> None:
        billed_usd, billed_http = 0.0, 0
        analysis_usd, analysis_http = 0.0, 0
        if self.ledger_rows_path.exists():
            for line in self.ledger_rows_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                cost = float(row.get("cost_usd") or 0.0)
                billed_usd += cost
                billed_http += 1
                if not row.get("superseded_by_resume"):
                    analysis_usd += cost
                    analysis_http += 1
        led["billed_spent_usd"] = round(billed_usd, 8)
        led["analysis_spent_usd"] = round(analysis_usd, 8)
        led["billed_http_used"] = billed_http
        led["analysis_http_used"] = analysis_http
        led["http_used"] = billed_http
        led["spent_usd"] = round(billed_usd, 8)

    def mark_episode_rows_superseded(
        self, episode_id: str, *, superseded_by_attempt_id: str
    ) -> int:
        """Amendment 7c: flag partial-attempt rows (same out_dir resume; rows retained)."""
        marked = 0

        def rewrite(path: Path, *, count_marked: bool) -> None:
            nonlocal marked
            if not path.exists():
                return
            out_lines: list[str] = []
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                if row.get("episode_id") == episode_id and not row.get("superseded_by_resume"):
                    row["superseded_by_resume"] = True
                    row["superseded_by_attempt_id"] = superseded_by_attempt_id
                    if count_marked:
                        marked += 1
                out_lines.append(json.dumps(row, ensure_ascii=False))
            text = "\n".join(out_lines) + ("\n" if out_lines else "")
            path.write_text(text, encoding="utf-8")
            _fsync_path(path)

        rewrite(self.http_stream_path, count_marked=False)
        rewrite(self.ledger_rows_path, count_marked=True)
        if marked:
            led = self.ledger()
            self._refresh_billed_analysis_totals(led)
            led["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
            self._write_ledger(led)
            self.log_progress(
                f"superseded_by_resume episode={episode_id} rows={marked} "
                f"new_attempt={superseded_by_attempt_id}"
            )
        return marked

    def episode_has_active_http_rows(self, episode_id: str) -> bool:
        if not self.http_stream_path.exists():
            return False
        for line in self.http_stream_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("episode_id") == episode_id and not row.get("superseded_by_resume"):
                return True
        return False

    def reconcile_http_stream_from_ledger(self) -> int:
        """Backfill http_stream rows for ledger request_ids missing from stream (crash mid-append)."""
        if not self.ledger_rows_path.exists():
            return 0
        stream_ids: set[str] = set()
        if self.http_stream_path.exists():
            for line in self.http_stream_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                rid = json.loads(line).get("request_id")
                if rid:
                    stream_ids.add(str(rid))
        added = 0
        for line in self.ledger_rows_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            led = json.loads(line)
            rid = led.get("request_id")
            if not rid or str(rid) in stream_ids:
                continue
            stub = {
                "recorded_at_utc": led.get("recorded_at_utc"),
                "episode_id": led.get("episode_id"),
                "episode_attempt_id": led.get("episode_attempt_id"),
                "superseded_by_resume": led.get("superseded_by_resume", False),
                "superseded_by_attempt_id": led.get("superseded_by_attempt_id"),
                "request_id": rid,
                "call_index": led.get("call_index"),
                "cost_usd": led.get("cost_usd"),
                "reconciled_from_ledger": True,
            }
            with open(self.http_stream_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(stub, ensure_ascii=False) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            stream_ids.add(str(rid))
            added += 1
        if added:
            led = self.ledger()
            self._refresh_billed_analysis_totals(led)
            self._write_ledger(led)
            self.log_progress(f"reconcile_http_stream_from_ledger added={added}")
        return added

    def write_episode_complete(self, episode: dict[str, Any]) -> None:
        eid = episode["episode_id"]
        safe = eid.replace("/", "_")
        traj_path = self.out_dir / "trajectories" / f"{safe}.json"
        traj_path.write_text(
            json.dumps(
                {"calls": episode.get("calls", []), "final_messages": episode.get("final_messages")},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        _fsync_path(traj_path)
        slim = {k: v for k, v in episode.items() if k != "calls"}
        with open(self.episodes_jsonl, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(slim, ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        led = self.ledger()
        led["episodes_complete"] = int(led.get("episodes_complete", 0)) + 1
        led["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        self._write_ledger(led)
        self.log_progress(f"episode_complete {eid} spent_usd={led['spent_usd']}")

    def completed_episode_ids(self) -> set[str]:
        if not self.episodes_jsonl.exists():
            return set()
        ids: set[str] = set()
        for line in self.episodes_jsonl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            ids.add(json.loads(line)["episode_id"])
        return ids

    def restore_http_budget_counter(self) -> int:
        return self.http_used()

    def _write_ledger(self, data: dict[str, Any]) -> None:
        data.setdefault("usd_cap", self.usd_cap)
        data.setdefault("http_cap", self.http_cap)
        self.ledger_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        _fsync_path(self.ledger_path)


def serialize_call_for_stream(record: Any, *, http_index: int | None = None) -> dict[str, Any]:
    return serialize_trajectory_call(record, http_index=http_index or record.call_index)
