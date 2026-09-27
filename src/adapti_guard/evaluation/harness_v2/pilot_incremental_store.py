"""Incremental on-disk pilot persistence (Amendment 6)."""
from __future__ import annotations

import json
import os
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
        self.ledger_path = self.out_dir / "running_ledger.json"
        self.progress_path = self.out_dir / "progress.log"
        self.episodes_jsonl = self.out_dir / "episodes.jsonl"
        if not self.ledger_path.exists():
            self._write_ledger({"http_used": 0, "spent_usd": 0.0, "episodes_complete": 0})

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

    def append_http_call(
        self,
        *,
        episode_id: str,
        record: Any,
        serialized: dict[str, Any],
    ) -> dict[str, Any]:
        row = {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "episode_id": episode_id,
            **serialized,
        }
        line = json.dumps(row, ensure_ascii=False) + "\n"
        with open(self.http_stream_path, "a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())
        cost = float(serialized.get("cost_usd") or 0.0)
        led = self.ledger()
        led["http_used"] = int(led.get("http_used", 0)) + 1
        led["spent_usd"] = round(float(led.get("spent_usd", 0.0)) + cost, 8)
        led["last_episode_id"] = episode_id
        led["last_call_index"] = serialized.get("call_index")
        led["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        self._write_ledger(led)
        return led

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
