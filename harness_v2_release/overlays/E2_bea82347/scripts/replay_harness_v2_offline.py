"""Offline (API=0) replay of harness_v2 scenario text through candidate defenses.

For each scenario instance, feeds the text units the target would receive (user
prompt, tool outputs) through a fresh defense_fn and records whether the
attack-bearing unit was intervened on. Does not call any model. Static tool-deny
is reported analytically (it neutralises every tool call by construction).
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from adapti_guard.experiments.defense_baselines import (
    make_b3_adaptive_v4,
    make_core_defense,
    make_q1_pre_target_adaptive_b3,
)

TEMPLATES = Path("experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES.json")


def units(inst: dict) -> list[tuple[str, str, bool]]:
    """(role, text, carries_attack) in delivery order."""
    marker = inst.get("marker")
    u = [("user", inst["user_prompt"], bool(marker) and marker in inst["user_prompt"])]
    for key in ("injection_doc_body", "injection_doc_body_late"):
        if inst.get(key):
            u.append(("tool", inst[key], True))
    if inst.get("weather_poison_suffix"):
        u.append(("tool", "Seattle: 12C, clear." + inst["weather_poison_suffix"], True))
    return u


ARMS = {
    "B3_orig(harness)": lambda: make_q1_pre_target_adaptive_b3()[0],
    "B3_v4": lambda: make_b3_adaptive_v4()[0],
    "PHASE1-CORE": lambda: make_core_defense()[0],
}


def run(templates: dict) -> dict:
    out: dict = {}
    for arm, factory in ARMS.items():
        per: dict = defaultdict(lambda: {"n": 0, "intervened": 0, "blocked": 0, "marker_survives": 0})
        for scen, v in templates["scenarios"].items():
            for inst in v["instances"]:
                fn = factory()
                atk_seen = atk_hit = atk_blocked = False
                marker_ok = False
                for role, text, carries in units(inst):
                    action, blocked, content = fn(text, None)
                    if carries:
                        atk_seen = True
                        atk_hit |= bool(getattr(fn, "last_detector_hit", False)) or blocked or content != text
                        atk_blocked |= blocked
                        marker_ok |= bool(inst.get("marker")) and inst["marker"] in (content or "")
                    elif not inst.get("marker"):
                        atk_seen = True  # benign: count any intervention as false positive
                        atk_hit |= bool(getattr(fn, "last_detector_hit", False)) or blocked or content != text
                        atk_blocked |= blocked
                p = per[scen]
                p["n"] += 1
                p["intervened"] += atk_hit
                p["blocked"] += atk_blocked
                p["marker_survives"] += marker_ok
        out[arm] = dict(per)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/research/artifacts/harness_v2_offline_replay_20260930.json")
    a = ap.parse_args()
    res = run(json.loads(TEMPLATES.read_text()))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=2))
    scens = list(next(iter(res.values())))
    print(f"{'scenario':30}", *[f"{k[:16]:>18}" for k in res])
    for s in scens:
        print(f"{s:30}", *[f"{v[s]['intervened']:>3}/{v[s]['n']} blk{v[s]['blocked']:>2} mk{v[s]['marker_survives']:>2}".rjust(18) for v in res.values()])


if __name__ == "__main__":
    main()
