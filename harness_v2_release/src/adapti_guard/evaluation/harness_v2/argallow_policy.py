"""Static argument-level tool policy (exploratory ARGALLOW arm). Deployer-declared, no model calls.

send_email: recipient domain must be in ``allowed_email_domains``.
create_record: kind must be in ``allowed_record_kinds``.
Other tools are not constrained. The default lists come from the *benign* workflow
definitions, i.e. what a deployer would declare for legitimate tasks; they are not
derived from attack instances. Because the benign and attack scenarios were authored
together, utility measured against the same benign set is optimistic by construction.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ARGALLOW_OBSERVATION = '{"error": "tool_denied_by_argument_policy"}'
_TEMPLATES = Path(__file__).resolve().parents[4] / "experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES.json"


@dataclass(frozen=True)
class ArgAllowPolicy:
    allowed_email_domains: frozenset[str]
    allowed_record_kinds: frozenset[str]

    def denies(self, tool_name: str, arguments: dict[str, Any] | None) -> bool:
        args = arguments or {}
        if tool_name == "send_email":
            to = str(args.get("to", "")).strip().lower()
            domain = to.rsplit("@", 1)[-1] if "@" in to else ""
            return domain not in self.allowed_email_domains
        if tool_name == "create_record":
            return str(args.get("kind", "")) not in self.allowed_record_kinds
        return False


def default_policy(templates_path: Path | None = None) -> ArgAllowPolicy:
    scen = json.loads((templates_path or _TEMPLATES).read_text())["scenarios"]
    domains = {
        i["allowlisted_email_to"].rsplit("@", 1)[-1].lower()
        for i in scen["benign_email_allowlist_v1"]["instances"]
    }
    kinds = {i["expected_create_kind"] for i in scen["benign_create_record_v1"]["instances"]}
    return ArgAllowPolicy(frozenset(domains), frozenset(kinds))
