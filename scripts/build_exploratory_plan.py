"""EXPLORATORY model-extension plans for the InjecAgent case study. OUTSIDE the frozen confirmatory protocol.

Nothing here is part of CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md. Results from these plans must be reported as exploratory.

The plans are derived, without any network call, from the launcher plans of the frozen runs, which
scripts/injecagent_case_loader.py built from the pinned release:
  build/r2_plan.json (sha256 must equal the R2 run manifest plan_sha256)
  build/r3_plan.json (sha256 must equal the R3 run manifest plan_sha256)
Case sampling, arm messages, tools, temperature and max_tokens are copied unchanged; only the model list (and, for
the gpt SPOT_TOOL plan, the arm set) changes. Usage:
  python scripts/build_exploratory_plan.py --write   # writes build/expl_*.json and prints hashes
  python scripts/build_exploratory_plan.py --topup deepseek [--write]   # build/expl_deepseek_topup.json

Top-up plans (PROPOSED) contain exactly the episodes of a stopped EXPL- run that were never sent, read from the
committed episodes.jsonl of the parent run. Episodes that were sent and errored are NOT included (R-0: no retries).
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
R2_PLAN = BUILD / "r2_plan.json"
R3_PLAN = BUILD / "r3_plan.json"
R2_PLAN_SHA = "d522b21bfb35c3c80d763742aee449dda1ce35442cca73bb2bd9d0bc99d6c5df"  # 20261014T142921Z manifest
R3_PLAN_SHA = "30d8bc2890d27ec40fe458873bb461476f24fb2fe2011c5171be2ba9328f5c8f"  # 20261014T181606Z manifest
LABEL = "EXPLORATORY - outside the frozen confirmatory protocol (CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md)"
NO_REASONING = {"enabled": False}  # same request setting as the registered qwen and gpt targets
EXT_MODELS = {
    "haiku": "anthropic/claude-haiku-5.5",
    "gemini": "google/gemini-3.1-flash-lite",
    "deepseek": "deepseek/deepseek-v4-flash",
}
GPT_MODEL = "openai/gpt-5.6-sol"
R2_ARMS = ("A0", "A0_REP", "SPOT_TOOL", "NOINJ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan_text(plan: dict) -> str:
    return json.dumps(plan, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def episodes(plan: dict) -> dict:
    per_arm: dict[str, int] = {}
    for c in plan["cases"]:
        for a in c["arms"]:
            per_arm[a] = per_arm.get(a, 0) + 1
    n = sum(per_arm.values())
    return {"per_model": n, "per_model_per_arm": dict(sorted(per_arm.items())), "total": n * len(plan["models"])}


def model_extension(base: dict, name: str, model_id: str, base_sha: str) -> dict:
    """R2 design (same cases, arms, messages, request) for one new model."""
    if base.get("run") != "R2":
        raise ValueError("model extension must derive from the R2 launcher plan")
    plan = copy.deepcopy(base)
    plan["run"] = f"EXPL-{name}"
    plan["models"] = [{"model_id": model_id, "route": "openrouter", "reasoning": dict(NO_REASONING)}]
    plan["exploratory"] = True
    plan["label"] = LABEL
    plan["derived_from"] = {"plan": "build/r2_plan.json", "sha256": base_sha, "design": "R2 arms per case, unchanged"}
    return plan


def gpt_spot_tool(r2: dict, r3: dict, r2_sha: str, r3_sha: str) -> dict:
    """SPOT_TOOL for the R3 gpt cases (R3 ran A0 only). SPOT_TOOL messages are taken from the R2 plan for the same ids."""
    if r3.get("run") != "R3" or [m["model_id"] for m in r3["models"]] != [GPT_MODEL]:
        raise ValueError("unexpected R3 plan")
    r2_cases = {c["case_id"]: c for c in r2["cases"]}
    cases = []
    for c in r3["cases"]:
        src = r2_cases.get(c["case_id"])
        if src is None or "SPOT_TOOL" not in src["arms"]:
            raise ValueError(f"{c['case_id']}: no SPOT_TOOL arm in the R2 plan")
        if src["tools"] != c["tools"] or src["arms"]["A0"] != c["arms"]["A0"]:
            raise ValueError(f"{c['case_id']}: R2 and R3 inputs differ")
        nc = copy.deepcopy(c)
        nc["arms"] = {"SPOT_TOOL": copy.deepcopy(src["arms"]["SPOT_TOOL"])}
        nc["messages"] = []
        cases.append(nc)
    plan = {"run": "EXPL-gpt-SPOT_TOOL", "request": copy.deepcopy(r3["request"]), "models": copy.deepcopy(r3["models"]),
            "cases": cases, "exploratory": True, "label": LABEL,
            "derived_from": {"plan": "build/r3_plan.json", "sha256": r3_sha, "spot_tool_messages_from": "build/r2_plan.json",
                             "spot_tool_sha256": r2_sha}}
    return plan


TOPUP_PARENTS = {  # name -> (parent run dir, parent plan file, parent plan sha256 from its run_manifest.json)
    "deepseek": ("experiments/external/20261015T005504Z", "expl_deepseek.json",
                 "a0db0645da619e2026e3a7f777f2423be5f1904f4ec23b532b7e008cc86bd296"),
}


def topup(parent: dict, sent_episodes: list[dict], parent_sha: str, parent_run_dir: str) -> dict:
    """Plan with only the (case, arm) pairs of `parent` that have no record in the parent's episodes.jsonl.

    Errored episodes have a record and are therefore excluded (no retries). Order follows the parent plan."""
    if parent.get("exploratory") is not True or not str(parent.get("run", "")).startswith("EXPL-"):
        raise ValueError("top-up parent must be an EXPL- plan")
    model_ids = {m["model_id"] for m in parent["models"]}
    planned = {(c["case_id"], a) for c in parent["cases"] for a in c["arms"]}
    sent: set[tuple[str, str]] = set()
    for e in sent_episodes:
        key = (e["case_id"], e["arm"])
        if e.get("model") not in model_ids or key not in planned:
            raise ValueError(f"episode {key} / {e.get('model')} is not in the parent plan")
        if key in sent:
            raise ValueError(f"duplicate episode record {key}")
        sent.add(key)
    cases = []
    for c in parent["cases"]:
        arms = {a: copy.deepcopy(v) for a, v in c["arms"].items() if (c["case_id"], a) not in sent}
        if arms:
            nc = copy.deepcopy(c)
            nc["arms"] = arms
            cases.append(nc)
    if not cases:
        raise ValueError("nothing left to top up")
    plan = copy.deepcopy({k: v for k, v in parent.items() if k not in ("cases", "derived_from")})
    plan["run"] = parent["run"] + "-topup"
    plan["cases"] = cases
    plan["exploratory"] = True
    plan["label"] = LABEL
    plan["derived_from"] = {"plan": f"build/{parent['run'].lower().replace('-', '_')}.json", "sha256": parent_sha,
                            "parent_run": parent["run"], "parent_run_dir": parent_run_dir,
                            "design": "unsent (case, arm) pairs of the parent run only; errored episodes excluded (no retries)"}
    return plan


def build_topup(name: str) -> dict:
    run_dir, fname, sha = TOPUP_PARENTS[name]
    if sha256_file(BUILD / fname) != sha:
        raise ValueError(f"build/{fname} differs from the plan the parent run used")
    eps = [json.loads(l) for l in (ROOT / run_dir / "episodes.jsonl").read_text().splitlines() if l.strip()]
    return topup(json.loads((BUILD / fname).read_text()), eps, sha, run_dir)


def build_all(r2: dict, r3: dict, r2_sha: str, r3_sha: str) -> dict[str, dict]:
    out = {f"expl_{n}.json": model_extension(r2, n, mid, r2_sha) for n, mid in EXT_MODELS.items()}
    out["expl_gpt_spot_tool.json"] = gpt_spot_tool(r2, r3, r2_sha, r3_sha)
    return out


def load_bases() -> tuple[dict, dict, str, str]:
    r2_sha, r3_sha = sha256_file(R2_PLAN), sha256_file(R3_PLAN)
    if r2_sha != R2_PLAN_SHA or r3_sha != R3_PLAN_SHA:
        raise ValueError("build/r2_plan.json or build/r3_plan.json differs from the plans the frozen runs used")
    return json.loads(R2_PLAN.read_text()), json.loads(R3_PLAN.read_text()), r2_sha, r3_sha


def main(argv: list[str]) -> int:
    if "--topup" in argv:
        name = argv[argv.index("--topup") + 1]
        plans = {f"expl_{name}_topup.json": build_topup(name)}
    else:
        plans = build_all(*load_bases())
    summary = {"label": LABEL, "plans": {}}
    for fname, plan in plans.items():
        text = plan_text(plan)
        if "--write" in argv:
            (BUILD / fname).write_text(text)
        summary["plans"][fname] = {"models": [m["model_id"] for m in plan["models"]],
                                   "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), **episodes(plan)}
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
