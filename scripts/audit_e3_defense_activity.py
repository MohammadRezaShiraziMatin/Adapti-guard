"""Audit what each defense did in the E3 defended run (HARNESS_V2_INDEPENDENT_DEFENDED_20260930).

Offline, no API. Reads the committed episodes of the undefended screening run and of the defended run and reports,
per defense arm: the recorded defense actions, the number of blocks, whether the first user turn the model saw differs
from the undefended run's, and how many stored tool messages are text-identical. Also gives the exact one-sided 95% upper
bound for a per-episode rate with zero events. Output: docs/research/artifacts/e3_defense_activity_20261007.json
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H = ROOT / "experiments/harness_v2"
OUT = ROOT / "docs/research/artifacts/e3_defense_activity_20261007.json"


def load(name: str) -> list[dict]:
    return [json.loads(x) for x in (H / name / "episodes.jsonl").read_text().splitlines() if x.strip()]


def key(e: dict) -> tuple:
    return (e["scenario_id"], e["instance_index"], e["family"])


def main() -> None:
    a0 = {key(e): e for e in load("HARNESS_V2_INDEPENDENT_SCREEN_20260930")}
    res: dict = {}
    for e in load("HARNESS_V2_INDEPENDENT_DEFENDED_20260930"):
        r = res.setdefault(e["condition"], {"episodes": 0, "defense_actions": collections.Counter(), "blocked_messages": 0,
                                            "user_turn": collections.Counter(), "tool_message_pairs_equal": 0, "tool_message_pairs_different": 0,
                                            "episodes_with_different_tool_message_count": 0})
        r["episodes"] += 1
        for x in e.get("b3_log") or []:
            r["defense_actions"][x.get("defense_action")] += 1
            r["blocked_messages"] += bool(x.get("blocked"))
        a = a0[key(e)]
        ua = next(m["content"] for m in a["final_messages"] if m["role"] == "user")
        ud = next(m["content"] for m in e["final_messages"] if m["role"] == "user")
        if ua == ud:
            r["user_turn"]["identical"] += 1
        elif ua.strip().rstrip(".!?") == ud.strip().rstrip(".!?"):
            r["user_turn"]["differs only by trailing punctuation or whitespace"] += 1
        else:
            r["user_turn"]["differs otherwise"] += 1
        ta = [m["content"] for m in a["final_messages"] if m["role"] == "tool"]
        td = [m["content"] for m in e["final_messages"] if m["role"] == "tool"]
        r["episodes_with_different_tool_message_count"] += len(ta) != len(td)
        for x, y in zip(ta, td):
            r["tool_message_pairs_equal" if x == y else "tool_message_pairs_different"] += 1
    for r in res.values():
        r["defense_actions"] = dict(r["defense_actions"])
        r["user_turn"] = dict(r["user_turn"])
        r["exact_95_upper_bound_zero_blocks_per_episode"] = round(1 - 0.05 ** (1 / r["episodes"]), 4)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
