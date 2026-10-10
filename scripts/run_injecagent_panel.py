#!/usr/bin/env python3
"""InjecAgent floor calibration on the final panel (4 open + 1 closed targets). Exploratory screening, NOT the confirmatory test.

Cases are drawn OUTSIDE the frozen phase-2 test sample (datasets/external_samples/injecagent_phase2_sample.json), seed 20261002.
Arms: A0 (attack in the tool output) and NOINJ (neutral text, validity control). Provider/transport errors are recorded as failures,
never as safe. Per-model results are written as they finish. Dry run by default; live needs --live --cap (<= 0.40) and a clean worktree.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from adapti_guard.evaluation import panel_registry as reg  # noqa: E402
from adapti_guard.evaluation.external import injecagent as ia  # noqa: E402

OUT = ROOT / "experiments/external/injecagent_panel_calib_20261001"
SEED = 20261002
MAX_CAP = 0.40
_REG = reg.load_panel()
PANEL = [(m.model, m.reasoning_request) for m in _REG if m.is_target]
PRICES = {m.model: (m.price_in, m.price_out) for m in _REG}
EST_TOK = (900, 120)


def http(body, key):
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {"error": "unreadable error body"}
    except Exception as e:
        return 0, {"error": f"{type(e).__name__}: {e}"[:140]}


def draw(n_per_kind):
    frozen = set(json.load(open(ROOT / "datasets/external_samples/injecagent_phase2_sample.json"))["case_ids"])
    pool = [c for c in ia.load_cases() if c["case_id"] not in frozen]
    return ia.sample_cases(pool, n_per_kind, SEED)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-per-kind", type=int, default=25)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--cap", type=float, default=None)
    a = ap.parse_args()
    cases = draw(a.n_per_kind)
    est = sum(2 * len(cases) * (EST_TOK[0] * PRICES[m][0] + EST_TOK[1] * PRICES[m][1]) for m, _ in PANEL)
    print(json.dumps({"cases": len(cases), "models": [m for m, _ in PANEL], "calls": 2 * len(cases) * len(PANEL), "est_usd": round(est, 4)}))
    if not a.live:
        return 0
    if a.cap is None or not (0 < a.cap <= MAX_CAP) or est > a.cap:
        print("refused: need 0 < --cap <= 0.40 and estimate within cap", file=sys.stderr)
        return 1
    if subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip():
        print("refused: worktree is dirty", file=sys.stderr)
        return 3
    key = os.environ["OPENROUTER_API_KEY"].strip()
    specs = ia.load_tool_specs()
    spent = {"usd": 0.0}
    OUT.mkdir(parents=True, exist_ok=True)

    def run(mid, rs):
        log = []
        for arm in ("A0", "NOINJ"):
            for c in cases:
                if spent["usd"] >= a.cap:
                    log.append({"arm": arm, "case_id": c["case_id"], "error": "cap"})
                    continue
                msgs = ia.build_messages(c, injected=(arm == "A0"), call_id="call00001")
                body = {"model": mid, "messages": msgs, "tools": ia.request_tools(c, specs), "temperature": 0.0, "max_tokens": 512}
                if rs is not None:
                    body["reasoning"] = rs
                for _ in (0, 1):
                    code, r = http(body, key)
                    if code == 200 and "choices" in r:
                        break
                    time.sleep(3)
                rec = {"arm": arm, "case_id": c["case_id"], "kind": c["kind"], "user_tool": c["User Tool"], "http": code}
                if code == 200 and "choices" in r:
                    m, u = r["choices"][0]["message"], r.get("usage") or {}
                    cost = (u.get("prompt_tokens") or 0) * PRICES[mid][0] + (u.get("completion_tokens") or 0) * PRICES[mid][1]
                    spent["usd"] += cost
                    rec.update({"cost": cost, "finish": r["choices"][0].get("finish_reason"), **ia.score_response(c, m.get("tool_calls") or [])})
                else:
                    rec["error"] = json.dumps(r.get("error", ""))[:140]
                log.append(rec)
        out = {"model": mid, "reasoning": rs, "episodes": log}
        (OUT / f"{mid.replace('/', '__')}.json").write_text(json.dumps(out, indent=1) + "\n")
        return out

    with ThreadPoolExecutor(max_workers=5) as ex:
        list(ex.map(lambda m: run(*m), PANEL))
    print("spent", round(spent["usd"], 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
