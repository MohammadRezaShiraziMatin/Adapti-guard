"""Campaign plan for protocol §9A items 10–13: runs R1 (pilot), R2 (llama and qwen, confirmatory), R3 (gpt, confirmatory).

Built only from committed records: the retained-set record, the pilot record and the cost rates of §8. It fixes the case
sets, the arms per case (including the NOINJ subset), episode counts, HTTP caps, estimates and per-run soft caps.

Launcher-ready: the launcher sends max_tokens 512 and checks each run with --run. The per-run --plan files come from
scripts/injecagent_case_loader.py, which needs a checkout of the pinned release (f19c9f2) at run time.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETAINED = ROOT / "docs/protocols/injecagent_S-A_retained_20261001.json"
PILOT = ROOT / "docs/protocols/injecagent_S-A_pilot_20261001.json"
OUT = ROOT / "docs/protocols/injecagent_S-A_campaign_plan_20261001.json"

RATE = {"llama": 0.0001777, "qwen": 0.0001772, "gpt": 0.0014775}  # §8, committed per-episode rates
CAMPAIGN_CAP = 0.50
PILOT_SOFT_CAP = 0.02  # author decision (§9A item 2)
NOINJ_N = 40
MODELS = {
    "llama": {"model_id": "meta-llama/llama-4-maverick", "reasoning": None},
    "qwen": {"model_id": "qwen/qwen3.8-flash", "reasoning": {"enabled": False}},
    "gpt": {"model_id": "openai/gpt-5.6-sol", "reasoning": {"enabled": False}},
}


def noinj_subset(retained_ids: list[str]) -> list[str]:
    """First 40 case ids, sorted, of the retained set (author decision, §9A item 10). Same for both targets."""
    return sorted(retained_ids)[:NOINJ_N]


def build_plan() -> dict:
    ret = json.loads(RETAINED.read_text())
    pilot = json.loads(PILOT.read_text())
    retained = sorted(ret["retained_case_ids_n150"])
    gpt_cases = sorted(ret["retained_case_ids_gpt_n72"])
    pilot_cases = sorted(pilot["case_ids"])
    if set(pilot_cases) & set(retained):
        raise ValueError("pilot overlaps the retained confirmatory set")
    if not set(gpt_cases) <= set(retained):
        raise ValueError("gpt cases are not a subset of the retained set")
    if len(retained) != 150 or len(gpt_cases) != 72 or len(pilot_cases) != 30:
        raise ValueError("unexpected case counts")

    noinj = set(noinj_subset(retained))
    r1 = {
        "run": "R1", "purpose": "pilot; excluded from the confirmatory analysis",
        "models": ["llama"],
        "cases": [{"case_id": c, "arms": ["A0", "SPOT_TOOL"]} for c in pilot_cases],
    }
    r2 = {
        "run": "R2", "purpose": "confirmatory, llama and qwen",
        "models": ["llama", "qwen"],
        "cases": [{"case_id": c, "arms": ["A0", "A0_REP", "SPOT_TOOL"] + (["NOINJ"] if c in noinj else [])}
                  for c in retained],
    }
    r3 = {
        "run": "R3", "purpose": "confirmatory, gpt (A0 only)",
        "models": ["gpt"],
        "cases": [{"case_id": c, "arms": ["A0"]} for c in gpt_cases],
    }
    runs = [r1, r2, r3]
    for r in runs:
        episodes = sum(len(c["arms"]) for c in r["cases"]) * len(r["models"])
        est = sum(sum(RATE[m] * len(c["arms"]) for c in r["cases"]) for m in r["models"])
        r["episodes"] = episodes
        r["http_cap"] = episodes  # R-0: one request per episode
        r["estimate_usd"] = round(est, 4)
        r["models_detail"] = [MODELS[m] for m in r["models"]]
    confirm_est = r2["estimate_usd"] + r3["estimate_usd"]
    remaining = CAMPAIGN_CAP - PILOT_SOFT_CAP
    r1["soft_cap_usd"] = PILOT_SOFT_CAP
    r2["soft_cap_usd"] = round(remaining * r2["estimate_usd"] / confirm_est, 4)
    r3["soft_cap_usd"] = round(remaining * r3["estimate_usd"] / confirm_est, 4)
    r1["expected_usage"] = "registration snapshot"
    r2["expected_usage"] = "registration snapshot + reconciled actual cost of R1"
    r3["expected_usage"] = "registration snapshot + reconciled actual costs of R1 and R2"
    return {
        "status": "SIGNED OFF 2026-10-11 (protocol §9A, commit d1538af), FROZEN, NOT REGISTERED",
        "launcher_input_ready": True,
        "launcher_inputs": ("scripts/injecagent_case_loader.py --run R1|R2|R3 --out <plan>, with a checkout of the pinned "
                            "release (f19c9f2). The launcher then refuses any input that differs from this plan (--run)."),
        "campaign_cap_usd": CAMPAIGN_CAP,
        "noinj_rule": f"first {NOINJ_N} retained case ids, sorted; same for both targets",
        "noinj_cases": sorted(noinj),
        "retained_sha256_source": "docs/protocols/injecagent_S-A_retained_20261001.json",
        "runs": runs,
        "confirmatory_episodes": r2["episodes"] + r3["episodes"],
        "confirmatory_estimate_usd": round(confirm_est, 4),
    }


def plan_text(plan: dict) -> str:
    return json.dumps(plan, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    text = plan_text(build_plan())
    if "--write" in argv:
        OUT.write_text(text)
        print(f"wrote {OUT.relative_to(ROOT)}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
