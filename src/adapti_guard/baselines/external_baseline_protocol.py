from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class ExternalBaselineSpec:
    name: str
    version: str
    source: str
    configuration: dict[str, Any] = field(default_factory=dict)
    assumptions: str = ""
    status: str = "DESIGN ONLY"

class ExternalBaselineRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, ExternalBaselineSpec] = {}

    def register(self, spec: ExternalBaselineSpec) -> None:
        self._entries[spec.name] = spec

    def list(self) -> list[ExternalBaselineSpec]:
        return list(self._entries.values())
