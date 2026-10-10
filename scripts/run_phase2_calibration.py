#!/usr/bin/env python3
"""Phase 2b/2c: floor calibration on the CALIBRATION split of the Hard set (the test split is never touched here).

Items: 68 human-written (LLMail-Inject) + 22 model-generated calibration items, reported separately. Arms: A0 (attack in the retrieved content) and NOINJ (benign twin).
Open targets run A0 and NOINJ on all calibration items; closed targets run A0 only on the first N_CLOSED items per origin (budget). Provider errors are retried once, then recorded
as failures (never scored as safe, never charged to the science). Default is a dry run with a cost estimate; live needs --live --cap and a clean worktree.
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
from adapti_guard.evaluation.external import hardset as hs  # noqa: E402
from adapti_guard.evaluation.external import llmail  # noqa: E402

OUT = ROOT / "experiments/external/phase2_calibration_20261001"
from adapti_guard.evaluation import panel_registry as reg  # noqa: E402

_REG = reg.load_panel()  # single source of truth: configs/models_panel_external_v2.yaml (validated)
PANEL = [(m.model, "open" if m.role.startswith("open") else "closed", m.reasoning_request) for m in _REG if m.is_target]
PRICES = {m.model: (m.price_in, m.price_out) for m in _REG}
N_CLOSED = 20  # per origin, A0 only (40 items in total per closed model)
DATA = Path("/tmp/llmail")
EST_TOK = {"human": (1500, 130), "generated": (800, 110)}  # prompt and completion tokens per episode (measured in smoke runs)


def load_items():
    system = json.load(open(DATA / "system_prompt.json"))["email_client"]
    human = [dict(json.loads(l), origin="human") for l in open(DATA / "hardset_items.jsonl", encoding="utf-8")]
    gen = [dict(json.loads(l), origin="generated") for l in open(DATA / "xchannel_items_final.jsonl", encoding="utf-8")]
    return system, [i for i in human if i["split"] == "calibration"], [i for i in gen if i["split"] == "calibration"]


def episode(item, arm, system):
    if item["origin"] == "human":
        msgs = llmail.build_messages(system, item["benign_twin"], item["injection"] if arm == "A0" else None)
        return msgs, [llmail.RETRIEVE_TOOL, llmail.SEND_EMAIL_TOOL], lambda tc: llmail.score_response(tc)["attack_goal_met"]
    return hs.build_messages(item, arm == "A0"), hs.tools_for(item), lambda tc: hs.score(item, tc)["attack_goal_met"]


def plan(prices, human, gen):
    rows = []
    for mid, kind, _ in PANEL:
        eps = []
        for origin, items in (("human", human), ("generated", gen)):
            n = len(items) if kind == "open" else min(N_CLOSED, len(items))
            arms = 2 if kind == "open" else 1
            eps.append((origin, n * arms))
        cost = sum(n * (EST_TOK[o][0] * prices[mid][0] + EST_TOK[o][1] * prices[mid][1]) for o, n in eps)
        rows.append({"model": mid, "kind": kind, "episodes": dict(eps), "est_usd": round(cost, 4)})
    return rows


def http(body, key):
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {"error": "unreadable error body"}
    except Exception as e:  # incomplete read, timeout, reset: a failure, never scored as safe
        return 0, {"error": f"{type(e).__name__}: {e}"[:140]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--cap", type=float, default=None, help="total hard cap in USD")
    ap.add_argument("--models", nargs="*", default=None)
    a = ap.parse_args()
    prices = PRICES  # pinned prices from the registry
    system, human, gen = load_items()
    models = [m for m in PANEL if a.models is None or m[0] in a.models]
    rows = [r for r in plan(prices, human, gen) if r["model"] in {m[0] for m in models}]
    print(json.dumps({"calibration_items": {"human": len(human), "generated": len(gen)}, "plan": rows, "est_total_usd": round(sum(r["est_usd"] for r in rows), 3)}, indent=1))
    if not a.live:
        return 0
    if a.cap is None or not 0 < a.cap <= 0.50:
        print("refused: --live needs --cap in (0, 0.50]", file=sys.stderr)
        return 1
    if subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip():
        print("refused: worktree is dirty", file=sys.stderr)
        return 3
    key = os.environ["OPENROUTER_API_KEY"].strip()
    spent = {"usd": 0.0}

    def run(mid, kind, rs):
        log, mspent = [], 0.0
        cap_m = a.cap * next(r["est_usd"] for r in rows if r["model"] == mid) / sum(r["est_usd"] for r in rows) * 1.5
        for origin, items in (("human", human), ("generated", gen)):
            use = items if kind == "open" else items[:N_CLOSED]
            for arm in ("A0", "NOINJ") if kind == "open" else ("A0",):
                for it in use:
                    if spent["usd"] >= a.cap or mspent >= cap_m:
                        log.append({"origin": origin, "arm": arm, "id": it["id"], "error": "cap"})
                        continue
                    msgs, tools, ok = episode(it, arm, system)
                    body = {"model": mid, "messages": msgs, "tools": tools, "temperature": 0.0, "max_tokens": 512}
                    if rs is not None:
                        body["reasoning"] = rs
                    for attempt in (0, 1):
                        code, r = http(body, key)
                        if code == 200 and "choices" in r:
                            break
                        time.sleep(3)
                    rec = {"origin": origin, "arm": arm, "id": it["id"], "http": code}
                    if code == 200 and "choices" in r:
                        m, u = r["choices"][0]["message"], r.get("usage") or {}
                        c = (u.get("prompt_tokens") or 0) * prices[mid][0] + (u.get("completion_tokens") or 0) * prices[mid][1]
                        mspent += c
                        spent["usd"] += c
                        rec.update({"finish": r["choices"][0].get("finish_reason"), "goal_met": bool(ok(m.get("tool_calls"))), "cost": c})
                    else:
                        rec["error"] = json.dumps(r.get("error", ""))[:140]
                    log.append(rec)
        out = {"model": mid, "kind": kind, "reasoning": rs, "spent": round(mspent, 5), "episodes": log}
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"partial_{mid.split('/')[-1]}.json").write_text(json.dumps(out, indent=1) + "\n")
        return out

    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as ex:
        res = [f.result() for f in [ex.submit(run, *m) for m in models]]
    tag = "" if a.models is None else "_" + "_".join(m.split("/")[-1] for m in a.models)
    (OUT / f"calibration{tag}.json").write_text(json.dumps({"cap": a.cap, "spent": round(spent["usd"], 5), "prices": {m[0]: prices[m[0]] for m in models}, "results": res}, indent=1) + "\n")
    print("spent", round(spent["usd"], 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
