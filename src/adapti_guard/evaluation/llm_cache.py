"""Deterministic LLM request cache."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LLMCache:
    def __init__(self, directory: Path | str = ".llm_cache"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.directory / f"{key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        path = self._path(key)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def set(self, key: str, value: dict[str, Any]) -> None:
        path = self._path(key)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
