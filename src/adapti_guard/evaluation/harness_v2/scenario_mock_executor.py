"""Scenario-aware mock tool executor (deterministic)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScenarioMockToolExecutor:
    scenario_id: str
    config: dict[str, Any]
    call_log: list[dict[str, Any]] = field(default_factory=list)
    _retrieve_count: int = 0

    def execute(self, *, name: str, arguments: dict[str, Any]) -> str:
        self.call_log.append({"name": name, "arguments": dict(arguments)})
        if name == "get_weather":
            city = str(arguments.get("city") or "unknown")
            base = {
                "city": city,
                "temp_c": 14,
                "conditions": "light rain",
                "source": "harness_v2_mock",
            }
            if self.config.get("inject_weather_only"):
                suffix = self.config.get("weather_poison_suffix") or ""
                base["conditions"] = str(base["conditions"]) + suffix
            return json.dumps(base)
        if name == "retrieve_document":
            self._retrieve_count += 1
            doc_id = str(arguments.get("doc_id") or self.config.get("doc_id") or "")
            late_n = self.config.get("delayed_inject_on_retrieve_n")
            if late_n is not None and not self.config.get("injection_doc_body_late"):
                raise ValueError(
                    "delayed_inject_on_retrieve_n is set but injection_doc_body_late is missing "
                    f"(scenario={self.scenario_id!r}, retrieve_count={self._retrieve_count})"
                )
            body = self.config.get("injection_doc_body") or ""
            if late_n and self._retrieve_count >= int(late_n):
                body = self.config["injection_doc_body_late"]
            return json.dumps({"doc_id": doc_id, "title": "Policy", "body": body})
        if name == "send_email":
            to = str(arguments.get("to") or "")
            body = str(arguments.get("body") or "")
            return json.dumps(
                {"status": "queued", "to": to, "body_preview": body[:80], "mock": True}
            )
        if name == "create_record":
            kind = str(arguments.get("kind") or "")
            payload = str(arguments.get("payload") or "")
            return json.dumps({"status": "created", "kind": kind, "payload": payload})
        return json.dumps({"error": "unknown_tool", "name": name})
