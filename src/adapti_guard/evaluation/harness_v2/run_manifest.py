"""Run pack manifest helpers (Amendment 8)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def write_run_manifest(out_dir: Path, **fields: Any) -> Path:
    manifest = {
        "python_version": sys.version,
        "python_version_info": list(sys.version_info[:3]),
        **fields,
    }
    path = out_dir / "run_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def write_pip_freeze(out_dir: Path) -> Path:
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True,
        text=True,
        check=True,
    )
    path = out_dir / "pip_freeze.txt"
    path.write_text(proc.stdout, encoding="utf-8")
    return path
