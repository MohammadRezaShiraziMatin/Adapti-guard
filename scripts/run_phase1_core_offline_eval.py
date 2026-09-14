#!/usr/bin/env python3
"""Read-only Phase 1 architectural checks on frozen JSONL.

Does not modify packs. Does not call LLM APIs. Does not retune VNEXT.
Prints action/tool-enforcement counts as architecture diagnostics, not ASR claims.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.core.core_pipeline import CoreDefensePipeline
from src.adapti_guard.core.episode import EpisodeInput
from src.adapti_guard.defense.tool_loop import MockToolRegistry

PACK = ROOT / "datasets/frozen/vnext_confirm_v1/dataset.jsonl"
EXPECTED = "523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518"


def main() -> int:
    digest = hashlib.sha256(PACK.read_bytes()).hexdigest()
    if digest != EXPECTED:
        print(f"FAIL: pack hash {digest} != {EXPECTED}")
        return 1
    pipe = CoreDefensePipeline()
    actions: Counter[str] = Counter()
    tool_denied = 0
    tool_ran = 0
    traces_complete = 0
    n = 0
    attack_hit = 0
    attack_n = 0
    benign_intervene = 0
    required = (
        "policy_action",
        "policy_reason",
        "risk_level",
        "detector_hit",
        "tool_executed",
    )
    for line in PACK.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        blob = row.get("tool_call") or (row.get("metadata") or {}).get("tool_call")
        name = blob.get("name") if isinstance(blob, dict) else None
        args = (blob.get("arguments") or {}) if isinstance(blob, dict) else {}
        if not isinstance(args, dict):
            args = {}
        inp = EpisodeInput(
            prompt=str(row.get("prompt") or ""),
            context=str(row.get("context") or ""),
            tool_name=name,
            tool_arguments=dict(args),
        )
        registry = MockToolRegistry()
        trace = pipe.run(inp, registry=registry)
        n += 1
        actions[trace.policy_action] += 1
        if trace.tool_requested and not trace.tool_executed:
            tool_denied += 1
        if trace.tool_executed:
            tool_ran += 1
        d = trace.to_dict()
        if all(d.get(k) is not None or k == "tool_executed" for k in required) and d.get(
            "policy_reason"
        ):
            traces_complete += 1
        # Gold label used only for diagnostic counters in this offline script.
        if row.get("label") == "attack":
            attack_n += 1
            if trace.detector_probability > 0:
                attack_hit += 1
        elif trace.policy_action in {"A2", "A3"}:
            benign_intervene += 1
    print("PHASE1_CORE_OFFLINE architectural diagnostics (NOT a security performance claim)")
    print(f"pack_sha={digest}")
    print(f"n={n}")
    print(f"actions={dict(actions)}")
    print(f"attack_detector_hits={attack_hit}/{attack_n}")
    print(f"benign_false_interventions={benign_intervene}")
    print(f"tool_denied={tool_denied} tool_executed={tool_ran}")
    print(f"traces_complete={traces_complete}/{n}")
    print("llm_api_calls=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
