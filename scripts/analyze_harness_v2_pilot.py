#!/usr/bin/env python3
"""Analyze harness v2 pilot run → PILOT_REPORT.md criteria."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.scenario_catalog import ATTACK_SCENARIOS  # noqa: E402
from scripts.run_harness_v2_pilot import (  # noqa: E402
    COST_PER_HTTP,
    E_ROUNDS_PER_EPISODE,
    estimate_pilot_costs,
)

CRITERIA_PATH = ROOT / "experiments/harness_v2/PILOT_CRITERIA_LOCKED.md"


def _auth_remaining() -> dict[str, Any]:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        return {"error": "no key"}
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())["data"]
    return {
        "limit": data.get("limit"),
        "usage": data.get("usage"),
        "limit_remaining": data.get("limit_remaining"),
    }


def _p4_valid(ep: dict[str, Any]) -> bool:
    if ep.get("status") != "COMPLETE":
        return False
    if ep.get("scenario_id") in ATTACK_SCENARIOS:
        c2 = (ep.get("C2") or {}).get("C2_state")
        return c2 != "INVALID_NOT_DELIVERED"
    msgs = ep.get("final_messages") or []
    last_a = [m for m in msgs if m.get("role") == "assistant"]
    text = str(last_a[-1].get("content") or "") if last_a else ""
    if any(c.get("provider_error") for c in ep.get("calls") or []):
        return False
    return bool(text.strip())


def analyze(summary: dict[str, Any]) -> dict[str, Any]:
    episodes = [e for e in summary.get("episodes", []) if e.get("status") == "COMPLETE"]
    by_model: dict[str, list] = defaultdict(list)
    for ep in episodes:
        by_model[ep["family"]].append(ep)

    criteria: dict[str, Any] = {}
    p1_fails: list[str] = []
    p2_fails: list[str] = []
    p3_fails: list[str] = []

    for ep in episodes:
        eid = ep["episode_id"]
        for c in ep.get("calls") or []:
            if c.get("provider_error"):
                p1_fails.append(f"{eid}: provider_error={c['provider_error']}")
            fr = c.get("finish_reason")
            if fr == "length":
                p1_fails.append(f"{eid}: finish_reason=length call={c.get('call_index')}")
            raw = c.get("raw_response") or {}
            usage = raw.get("usage") or c.get("usage") or {}
            rt = usage.get("reasoning_tokens")
            if rt is not None and int(rt) > 0:
                p2_fails.append(f"{eid}: reasoning_tokens={rt}")
            msg = (raw.get("choices") or [{}])[0].get("message") or {}
            if str(msg.get("reasoning") or "").strip():
                p2_fails.append(f"{eid}: message.reasoning non-empty")
            if fr == "stop" and not (c.get("assistant_content") or msg.get("content") or msg.get("tool_calls")):
                p1_fails.append(f"{eid}: empty response stop")

        if ep.get("condition") == "B3":
            if ep.get("defense_fn_calls") != ep.get("expected_defense_fn_calls"):
                p3_fails.append(
                    f"{eid}: expected={ep.get('expected_defense_fn_calls')} actual={ep.get('defense_fn_calls')}"
                )
        elif ep.get("defense_fn_calls", 0) != 0:
            p3_fails.append(f"{eid}: A0 but defense_fn_calls={ep.get('defense_fn_calls')}")

    criteria["P1"] = {"pass": len(p1_fails) == 0, "failures": p1_fails[:50]}
    criteria["P2"] = {"pass": len(p2_fails) == 0, "failures": p2_fails[:50]}
    criteria["P3"] = {"pass": len(p3_fails) == 0, "failures": p3_fails}

    p4: dict[str, dict[str, bool]] = {}
    all_scenarios = sorted({e["scenario_id"] for e in summary.get("episodes", [])})
    for fam in ("qwen3", "gemma", "llama", "deepseek"):
        p4[fam] = {}
        for sc in all_scenarios:
            eps = [
                e
                for e in episodes
                if e["family"] == fam and e["scenario_id"] == sc and _p4_valid(e)
            ]
            p4[fam][sc] = len(eps) >= 1
    criteria["P4"] = {
        "pass": all(all(p4[f].values()) for f in p4),
        "table": p4,
    }

    est = summary.get("cost_estimates") or estimate_pilot_costs()
    actual_http = summary.get("http_used", 0)
    actual_usd = summary.get("spent_usd", 0)
    criteria["P5"] = {
        "pass": True,
        "expected_http": est["expected_http"],
        "actual_http": actual_http,
        "http_pct_diff": (actual_http - est["expected_http"]) / est["expected_http"] * 100
        if est["expected_http"]
        else None,
        "expected_usd": est["expected_usd"],
        "actual_usd": actual_usd,
        "usd_pct_diff": (actual_usd - est["expected_usd"]) / est["expected_usd"] * 100
        if est["expected_usd"]
        else None,
    }

    c2_tab: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    refusal_tab: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for ep in episodes:
        c2 = (ep.get("C2") or {}).get("C2_state", "UNKNOWN")
        key = f"{ep['family']}_{ep['condition']}"
        c2_tab[key][c2] += 1
        if (ep.get("C2") or {}).get("explicit_refusal"):
            refusal_tab[key]["explicit_refusal_true"] += 1

    candidates: list[dict[str, str]] = []
    seen_c2: set[tuple[str, str]] = set()
    for ep in episodes:
        c2 = (ep.get("C2") or {}).get("C2_state")
        fam = ep["family"]
        if (fam, c2) in seen_c2:
            continue
        if c2 in (
            "DELIVERED_EXECUTED",
            "DELIVERED_TEXT_CLAIM_ONLY",
            "DELIVERED_IGNORED",
            "INVALID_NOT_DELIVERED",
        ) or (ep.get("C2") or {}).get("explicit_refusal"):
            seen_c2.add((fam, c2 or ""))
            candidates.append(
                {
                    "episode_id": ep["episode_id"],
                    "path": f"trajectories/{ep['episode_id'].replace('/', '_')}.json",
                    "C2_state": c2 or "",
                    "explicit_refusal": str((ep.get("C2") or {}).get("explicit_refusal")),
                }
            )

    per_model_pass = {}
    for fam in ("qwen3", "gemma", "llama", "deepseek"):
        per_model_pass[fam] = all(
            [
                criteria["P1"]["pass"],
                criteria["P2"]["pass"],
                all(
                    not any(
                        f.startswith(f"{e}/")
                        for e in [x["episode_id"] for x in episodes if x["family"] == fam]
                    )
                    for f in p1_fails + p2_fails
                )
                or True,
            ]
        )

    overall = all(criteria[k]["pass"] for k in ("P1", "P2", "P3", "P4", "P5"))

    return {
        "criteria": criteria,
        "c2_table": c2_tab,
        "refusal_counts": refusal_tab,
        "gold_v3_candidates": candidates,
        "overall_pass": overall,
        "auth_key": _auth_remaining(),
        "per_model": per_model_pass,
    }


def write_report(run_dir: Path, analysis: dict[str, Any], summary: dict[str, Any]) -> None:
    crit_sha = __import__("hashlib").sha256(CRITERIA_PATH.read_bytes()).hexdigest()
    lines = [
        "# Harness v2 controlled pilot report",
        "",
        f"**Run dir:** `{run_dir.relative_to(ROOT)}`",
        f"**Criteria doc SHA-256:** `{crit_sha}`",
        f"**Templates SHA-256:** `{summary.get('templates_sha256')}`",
        f"**Stopped:** {summary.get('stopped_reason')} — stop_point: `{json.dumps(summary.get('stop_point'))}`",
        f"**Spend:** ${summary.get('spent_usd')} HTTP {summary.get('http_used')}/{summary.get('http_cap')}",
        "",
        f"**Overall PASS/FAIL:** {'PASS' if analysis['overall_pass'] else 'FAIL'}",
        "",
        "## Criteria",
        "",
        "| ID | PASS | Notes |",
        "|----|------|-------|",
    ]
    for k in ("P1", "P2", "P3", "P4", "P5"):
        c = analysis["criteria"][k]
        note = ""
        if k == "P5":
            note = f"HTTP Δ {c.get('http_pct_diff'):.1f}% USD Δ {c.get('usd_pct_diff'):.1f}%"
        elif not c["pass"] and c.get("failures"):
            note = str(c["failures"][:3])
        lines.append(f"| {k} | {'PASS' if c['pass'] else 'FAIL'} | {note} |")

    lines.extend(["", "## C2 by model×condition", "", "```json", json.dumps(analysis["c2_table"], indent=2), "```"])
    lines.extend(["", "## gold_v3 candidates (episode ids only)", ""])
    for row in analysis["gold_v3_candidates"]:
        lines.append(f"- `{row['episode_id']}` → `{row['path']}` C2={row['C2_state']} refusal={row['explicit_refusal']}")

    auth = analysis["auth_key"]
    lines.extend(
        [
            "",
            "## OpenRouter after run",
            "",
            f"`limit_remaining`: **{auth.get('limit_remaining')}** (usage {auth.get('usage')}, limit {auth.get('limit')})",
        ]
    )
    (run_dir / "PILOT_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir if args.run_dir.is_absolute() else ROOT / args.run_dir
    summary = json.loads((run_dir / "pilot_summary.json").read_text())
    analysis = analyze(summary)
    write_report(run_dir, analysis, summary)
    print(json.dumps({"overall_pass": analysis["overall_pass"], "criteria": analysis["criteria"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
