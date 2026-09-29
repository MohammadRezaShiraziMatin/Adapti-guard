"""Single-flight lock for harness v2 live pilot (Amendment 6)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOCK_PATH = Path(__file__).resolve().parents[4] / "experiments/harness_v2/.pilot_live.lock"


@dataclass
class PilotRunLock:
    path: Path
    payload: dict

    @classmethod
    def try_acquire(
        cls,
        *,
        out_dir: Path,
        path: Path | None = None,
        pilot_label: str = "harness_v2_pilot",
    ) -> PilotRunLock:
        lock_path = path or DEFAULT_LOCK_PATH
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        if lock_path.exists():
            existing = json.loads(lock_path.read_text(encoding="utf-8"))
            pid = int(existing.get("pid", 0))
            if pid and _pid_alive(pid):
                raise RuntimeError(
                    f"pilot_run_lock_held: pid={pid} out_dir={existing.get('out_dir')}"
                )
        payload = {
            "pid": os.getpid(),
            "out_dir": str(out_dir),
            "pilot_label": pilot_label,
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        lock_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return cls(path=lock_path, payload=payload)

    def release(self) -> None:
        if not self.path.exists():
            return
        try:
            on_disk = json.loads(self.path.read_text(encoding="utf-8"))
            if int(on_disk.get("pid", -1)) != os.getpid():
                return
        except (json.JSONDecodeError, OSError):
            pass
        self.path.unlink(missing_ok=True)


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True
