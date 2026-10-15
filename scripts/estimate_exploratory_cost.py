"""EXPLORATORY cost estimate for the model-extension plans (outside the frozen protocol). Offline, no network.

Episode records carry cost but no token counts, so the per-episode token basis is reconstructed:
  prompt tokens     = characters of the request (messages + tools JSON) / CHARS_PER_TOKEN
  completion tokens = (recorded cost - prompt tokens * input price) / output price, floored at 0
using the price snapshot of the model that produced the record. Estimates use the mean over R2 (llama, qwen) per arm;
gpt SPOT_TOOL uses the R3 gpt A0 records with the SPOT_TOOL prompt length. Upper bound: prompt tokens x1.3
(tokenizer variance) and completion at max_tokens (512).
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R2_DIR = ROOT / "experiments/external/20261014T142921Z"
R3_DIR = ROOT / "experiments/external/20261014T181606Z"
CHARS_PER_TOKEN = 4.0
MAX_TOKENS = 512
PROMPT_UPPER = 1.3
# USD per token, public https://openrouter.ai/api/v1/models snapshot 2026-10-15 (no auth)
PRICES = {
    "meta-llama/llama-4-maverick": (0.0000001875, 0.0000006525),
    "qwen/qwen3.8-flash": (0.00000015, 0.00000047),
    "openai/gpt-5.6-sol": (0.000004, 0.00002),
    "anthropic/claude-haiku-5.5": (0.0000001, 0.0000005),
    "google/gemini-3.1-flash-lite": (0.00000025, 0.0000015),
    "deepseek/deepseek-v4-flash": (0.000000091, 0.000000182),
}
SPENT_USD = 0.313657207
CAP_USD = 0.50


def prompt_chars(case: dict, arm: str) -> int:
    return len(json.dumps(case["arms"][arm]["messages"])) + len(json.dumps(case["tools"]))


def token_basis(records, plan_cases) -> dict:
    by_arm: dict[str, dict[str, list]] = {}
    for r in records:
        if r.get("cost") is None:
            continue
        pin, pout = PRICES[r["model"]]
        tp = prompt_chars(plan_cases[r["case_id"]], r["arm"]) / CHARS_PER_TOKEN
        tc = max(0.0, (float(r["cost"]) - tp * pin) / pout)
        d = by_arm.setdefault(r["arm"], {"p": [], "c": []})
        d["p"].append(tp)
        d["c"].append(tc)
    return {a: {"prompt": statistics.mean(d["p"]), "completion": statistics.mean(d["c"]), "n": len(d["p"])}
            for a, d in sorted(by_arm.items())}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def estimate(plan: dict, basis: dict, model_id: str) -> tuple[float, float]:
    pin, pout = PRICES[model_id]
    est = upper = 0.0
    for c in plan["cases"]:
        for a in c["arms"]:
            b = basis[a]
            est += b["prompt"] * pin + b["completion"] * pout
            upper += b["prompt"] * PROMPT_UPPER * pin + MAX_TOKENS * pout
    return est, upper


def main(argv: list[str]) -> int:
    build = ROOT / "build"
    r2 = json.loads((build / "r2_plan.json").read_text())
    cases = {c["case_id"]: c for c in r2["cases"]}
    basis = token_basis(read_jsonl(R2_DIR / "episodes.jsonl"), cases)
    gpt_a0 = token_basis(read_jsonl(R3_DIR / "episodes.jsonl"), cases)["A0"]
    spot_p = statistics.mean(prompt_chars(cases[c["case_id"]], "SPOT_TOOL") / CHARS_PER_TOKEN
                             for c in json.loads((build / "r3_plan.json").read_text())["cases"])
    gpt_basis = {"SPOT_TOOL": {"prompt": spot_p, "completion": gpt_a0["completion"], "n": gpt_a0["n"]}}
    rows = {}
    for fname in ("expl_haiku.json", "expl_gemini.json", "expl_deepseek.json", "expl_gpt_spot_tool.json"):
        plan = json.loads((build / fname).read_text())
        mid = plan["models"][0]["model_id"]
        b = gpt_basis if "gpt" in fname else basis
        est, up = estimate(plan, b, mid)
        rows[fname] = {"model": mid, "price_in_per_M": PRICES[mid][0] * 1e6, "price_out_per_M": PRICES[mid][1] * 1e6,
                       "estimate_usd": round(est, 6), "upper_usd": round(up, 6)}
    out = {"label": "EXPLORATORY - outside the frozen protocol", "token_basis_r2_per_arm": basis,
           "token_basis_gpt_spot_tool": gpt_basis, "rows": rows, "remaining_usd": round(CAP_USD - SPENT_USD, 9)}
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
