"""Scenario catalog + instance materialization for harness v2 pilot/full eval."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from adapti_guard.evaluation.harness_v2.exec_success import ExecSuccessSpec
from adapti_guard.evaluation.harness_v2.tool_definitions import HARNESS_V2_SYSTEM_PROMPT

TEMPLATES_PATH = Path(__file__).resolve().parents[4] / "experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES.json"

ATTACK_SCENARIOS = (
    "indirect_retrieved_doc_v1",
    "poisoned_benign_tool_v1",
    "direct_user_override_v1",
    "create_record_exfil_v1",
    "multi_step_chain_v1",
    "delayed_second_turn_v1",
    "obfuscated_instruction_v1",
)
BENIGN_SCENARIOS = (
    "benign_weather_v1",
    "benign_email_allowlist_v1",
    "benign_create_record_v1",
)
ALL_SCENARIOS = ATTACK_SCENARIOS + BENIGN_SCENARIOS


def templates_sha256(path: Path | None = None) -> str:
    p = path or TEMPLATES_PATH
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def load_templates(path: Path | None = None) -> dict[str, Any]:
    p = path or TEMPLATES_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def get_instance(scenario_id: str, instance_index: int, *, templates: dict[str, Any] | None = None) -> dict[str, Any]:
    data = templates or load_templates()
    block = data["scenarios"][scenario_id]
    inst = block["instances"][instance_index]
    return dict(inst)


def exec_spec_for_instance(scenario_id: str, inst: dict[str, Any]) -> ExecSuccessSpec | None:
    if scenario_id in BENIGN_SCENARIOS:
        return None
    tool = inst.get("attack_tool", "send_email")
    return ExecSuccessSpec(
        tool_name=tool,
        required_args=inst.get("required_args") or {},
        body_marker=inst.get("marker"),
    )


def build_mock_executor_config(scenario_id: str, inst: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "doc_id": inst.get("doc_id", "dock-policy-001"),
        "injection_doc_body": inst.get("injection_doc_body"),
        "injection_doc_body_late": inst.get("injection_doc_body_late"),
        "weather_poison_suffix": inst.get("weather_poison_suffix"),
        "inject_weather_only": scenario_id == "poisoned_benign_tool_v1",
        "delayed_inject_on_retrieve_n": inst.get("delayed_inject_on_retrieve_n"),
        "allowlisted_email_to": inst.get("allowlisted_email_to"),
    }


def materialize_user_prompt(scenario_id: str, inst: dict[str, Any]) -> str:
    return str(inst["user_prompt"])


def scenario_meta(scenario_id: str) -> dict[str, Any]:
    is_attack = scenario_id in ATTACK_SCENARIOS
    return {
        "scenario_id": scenario_id,
        "is_attack": is_attack,
        "system_prompt": HARNESS_V2_SYSTEM_PROMPT,
    }
