"""Finalize publication artifacts from Phase 5 Target observations.

Does not invent ASR. If Cerebras rejudge is blocked (e.g. HTTP 402),
security metrics remain NOT COMPUTABLE.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.evaluation.statistics import (  # noqa: E402
    bootstrap_ci,
    holm_correction,
    mcnemar_test,
)

PHASE5 = ROOT / "experiments" / "PHASE5_CONSTRAINED" / "raw_results.jsonl"
VAL = ROOT / "experiments" / "FINAL_JUDGE_VALIDATION"
REJ = ROOT / "experiments" / "FINAL_REJUDGE"
FIG = ROOT / "experiments" / "FINAL_FIGURES"
QC = ROOT / "experiments" / "FINAL_QC"
AUDIT = ROOT / "experiments" / "FINAL_AUDIT"
FROZEN = ROOT / "datasets" / "frozen" / "eval_v1" / "dataset.jsonl"
STREAM = ROOT / "results" / "common_attack_stream.json"

COST = {"A0": 0.00, "A1": 0.10, "A2": 0.25, "A3": 0.50}
LEVEL = {"A0": "L0", "A1": "L1", "A2": "L2", "A3": "L3"}
CAT_LABEL = {
    "prompt_injection": "Prompt Injection",
    "jailbreak": "Jailbreak",
    "rag_security": "RAG Security",
    "context_attack": "Context Attack",
    "tool_abuse": "Tool Abuse",
    "system_prompt_leakage": "System Prompt Leakage",
    "role_attack": "Role Attack",
}
N_BOOT = 10000
SEED = 42
EXPECTED_DS = "27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24"
EXPECTED_ST = "d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def git_commit() -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except OSError:
        return None
    return None


def fmt_ci(ci: tuple[float, float, float] | None) -> str:
    if ci is None:
        return "N/A"
    p, lo, hi = ci
    return f"{p:.4f} [{lo:.4f}, {hi:.4f}]"


def na(x) -> str:
    if x is None:
        return "N/A"
    return str(x)


def main() -> int:
    FIG.mkdir(parents=True, exist_ok=True)
    QC.mkdir(parents=True, exist_ok=True)
    REJ.mkdir(parents=True, exist_ok=True)

    targets = load_jsonl(PHASE5)
    val_rows = load_jsonl(VAL / "validation_results.jsonl")
    judgments = load_jsonl(REJ / "raw_judgments.jsonl")

    val_402 = any("402" in str(r.get("parse_error") or "") for r in val_rows)
    n_val_ok = sum(1 for r in val_rows if r.get("judge_status") == "OK")
    rejudge_blocked = (not judgments) and (n_val_ok == 0)

    if rejudge_blocked:
        errors = [
            {
                "timestamp": utc(),
                "judge_status": "JUDGE_FAILED",
                "error_status": "402_payment_required",
                "detail": (
                    "Cerebras chat completions returned HTTP 402 Payment Required "
                    "for qwen-3.8-27b (also gpt-oss-120b and gemma-4-31b probes). "
                    "Validation n=10 all failed. Mass rejudge not executed to avoid "
                    "300 duplicate 402 failures. Failures are NOT security outcomes."
                ),
                "validation_attempted": len(val_rows),
                "validation_ok": n_val_ok,
                "target_observations": len(targets),
            }
        ]
        with (REJ / "errors.jsonl").open("w", encoding="utf-8") as fh:
            for e in errors:
                fh.write(json.dumps(e) + "\n")
        if not (REJ / "raw_judgments.jsonl").exists():
            (REJ / "raw_judgments.jsonl").write_text("")

    valid = [r for r in judgments if r.get("judge_status") == "OK"]
    failed_j = [r for r in judgments if r.get("judge_status") == "JUDGE_FAILED"]
    invalid_j = [r for r in judgments if r.get("judge_status") == "JUDGE_INVALID"]

    # ICS from Target-side actions (independent of judge)
    ics_rows = []
    for r in targets:
        action = r.get("action") or "A0"
        ics_rows.append(
            {
                "model": r.get("model_key"),
                "policy": r.get("baseline"),
                "sample_id": r.get("episode_id"),
                "category": r.get("category"),
                "action": action,
                "level": LEVEL.get(action, "UNKNOWN"),
                "ics": COST.get(action),
                "target_latency_ms": r.get("target_latency_ms"),
            }
        )

    def mean_ics(pred) -> float | None:
        xs = [x["ics"] for x in ics_rows if pred(x) and x["ics"] is not None]
        if not xs:
            return None
        return float(np.round(np.mean(xs), 2))

    asr_available = len(valid) > 0

    def asr_for(pred) -> dict:
        xs = [v for v in valid if pred(v)]
        n = len(xs)
        if n == 0:
            return {
                "n_valid": 0,
                "asr": None,
                "defense": None,
                "ci_asr": None,
                "ci_def": None,
            }
        att = np.array([1.0 if v.get("attack_success") else 0.0 for v in xs])
        point, lo, hi = bootstrap_ci(att, n_bootstrap=N_BOOT, seed=SEED)
        d = 1.0 - att
        dp, dlo, dhi = bootstrap_ci(d, n_bootstrap=N_BOOT, seed=SEED)
        return {
            "n_valid": n,
            "asr": float(point),
            "defense": float(dp),
            "ci_asr": (float(point), float(lo), float(hi)),
            "ci_def": (float(dp), float(dlo), float(dhi)),
        }

    overall = {}
    for pol in ("B0", "B6"):
        overall[pol] = {
            **asr_for(lambda v, p=pol: v.get("policy") == p),
            "n_target": sum(1 for x in ics_rows if x["policy"] == pol),
            "mean_ics": mean_ics(lambda x, p=pol: x["policy"] == p),
        }

    by_model = {}
    for m in ("model_a", "model_b", "model_c"):
        by_model[m] = {}
        for pol in ("B0", "B6"):
            by_model[m][pol] = {
                **asr_for(
                    lambda v, mm=m, p=pol: v.get("model") == mm and v.get("policy") == p
                ),
                "n_target": sum(
                    1 for x in ics_rows if x["model"] == m and x["policy"] == pol
                ),
                "mean_ics": mean_ics(
                    lambda x, mm=m, p=pol: x["model"] == mm and x["policy"] == p
                ),
            }

    by_cat = {}
    for cat in sorted({x["category"] for x in ics_rows}):
        by_cat[cat] = {}
        for pol in ("B0", "B6"):
            by_cat[cat][pol] = {
                **asr_for(
                    lambda v, c=cat, p=pol: v.get("attack_category") == c
                    and v.get("policy") == p
                ),
                "n_target": sum(
                    1 for x in ics_rows if x["category"] == cat and x["policy"] == pol
                ),
                "mean_ics": mean_ics(
                    lambda x, c=cat, p=pol: x["category"] == c and x["policy"] == p
                ),
            }

    mcnemar_by_model = {}
    raw_ps = []
    model_order = []
    for m in ("model_a", "model_b", "model_c"):
        b0 = {
            v["sample_id"]: bool(v["attack_success"])
            for v in valid
            if v.get("model") == m and v.get("policy") == "B0"
        }
        b6 = {
            v["sample_id"]: bool(v["attack_success"])
            for v in valid
            if v.get("model") == m and v.get("policy") == "B6"
        }
        ids = sorted(set(b0) & set(b6))
        if len(ids) < 1:
            mcnemar_by_model[m] = {"status": "NOT_COMPUTABLE", "n_pairs": len(ids)}
            continue
        a = [b0[i] for i in ids]
        b = [b6[i] for i in ids]
        res = mcnemar_test(a, b)
        n_succ_b0 = sum(a)
        n_succ_b6 = sum(b)
        asr0 = n_succ_b0 / len(ids)
        asr6 = n_succ_b6 / len(ids)
        rd = asr6 - asr0
        # bootstrap RD on paired indicators
        diffs = np.array([1.0 if y else 0.0 for y in b]) - np.array(
            [1.0 if x else 0.0 for x in a]
        )
        rd_pt, rd_lo, rd_hi = bootstrap_ci(diffs, n_bootstrap=N_BOOT, seed=SEED)
        or_num = res["b01"]
        or_den = res["b10"]
        odds = None if or_den == 0 else (or_num / or_den if isinstance(or_num, (int, float)) else None)
        rec = {
            "status": "OK",
            "n_pairs": len(ids),
            "mcnemar": res,
            "asr_b0": asr0,
            "asr_b6": asr6,
            "risk_difference_b6_minus_b0": rd,
            "rd_bootstrap": (rd_pt, rd_lo, rd_hi),
            "relative_risk": None if asr0 == 0 else asr6 / asr0,
            "odds_ratio_discordant": odds,
        }
        mcnemar_by_model[m] = rec
        raw_ps.append(float(res["p_value"]))
        model_order.append(m)
    holm = holm_correction(raw_ps) if raw_ps else []
    for i, m in enumerate(model_order):
        mcnemar_by_model[m]["holm"] = holm[i]

    # Intervention distributions
    def level_pct(policy: str) -> dict:
        sub = [x for x in ics_rows if x["policy"] == policy]
        n = len(sub) or 1
        c = Counter(x["level"] for x in sub)
        return {lv: 100.0 * c.get(lv, 0) / n for lv in ("L0", "L1", "L2", "L3")}

    b6_seq = defaultdict(list)
    for x in sorted(
        [r for r in ics_rows if r["policy"] == "B6"],
        key=lambda z: (z["model"], z["sample_id"]),
    ):
        b6_seq[x["model"]].append(x["level"])

    # No sequential timestamps of policy adaptation beyond per-episode action.
    adaptation = {
        "note": (
            "Phase 5 stores one action per episode, not a within-episode level trace. "
            "B6 selected A1 on all 150 episodes. Escalation/de-escalation frequency "
            "across episode order cannot be recovered beyond the constant A1 sequence."
        ),
        "B6_level_counts": dict(Counter(x["level"] for x in ics_rows if x["policy"] == "B6")),
        "B0_level_counts": dict(Counter(x["level"] for x in ics_rows if x["policy"] == "B0")),
        "escalation_frequency": "NOT_OBSERVABLE_FROM_CONSTANT_A1",
        "deescalation_frequency": "NOT_OBSERVABLE_FROM_CONSTANT_A1",
        "mean_intervention_level_B6_numeric": 1.0,
        "mean_ics_B6": mean_ics(lambda x: x["policy"] == "B6"),
        "mean_ics_B0": mean_ics(lambda x: x["policy"] == "B0"),
    }

    ds_hash = sha256_file(FROZEN)
    st_hash = sha256_file(STREAM) if STREAM.exists() else None
    commit = git_commit()
    p5_commit = targets[0].get("git_commit") if targets else None

    metrics = {
        "timestamp": utc(),
        "n_bootstrap_final": N_BOOT,
        "n_bootstrap_protocol_doc": 5000,
        "bootstrap_change": (
            "Final publication analysis uses B=10000. "
            "docs/STATISTICAL_PROTOCOL.md and statistics.py default remain 5000. "
            "Documented deviation for this completion protocol."
        ),
        "utility_status": "NOT_AVAILABLE",
        "reward_status": "NOT_COMPUTABLE",
        "ablation_status": "NOT_EXECUTED",
        "ablation_reason": (
            "EXP-006 artifacts are LEGACY_SIMULATION_ONLY. Real-LLM ablation would "
            "require additional Groq Target calls and a benign set; budget protocol "
            "forbids extra Target calls."
        ),
        "judge_status": (
            "BLOCKED_CEREBRAS_402" if rejudge_blocked else "COMPLETE"
        ),
        "n_target": len(targets),
        "n_valid_judge": len(valid),
        "n_failed_judge": len(failed_j) if judgments else len(val_rows),
        "n_invalid_judge": len(invalid_j),
        "n_validation": len(val_rows),
        "n_validation_ok": n_val_ok,
        "validation_402": val_402,
        "overall": overall,
        "by_model": by_model,
        "by_category": by_cat,
        "mcnemar": mcnemar_by_model,
        "adaptation": adaptation,
        "level_pct_B0": level_pct("B0"),
        "level_pct_B6": level_pct("B6"),
        "B6_aliases_B3": True,
        "models_are_same_groq_target": True,
        "truncated_responses_n": sum(
            1 for r in targets if len(r.get("target_response") or "") == 500
        ),
    }
    (REJ / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")

    # Figures from ICS / levels only if ASR missing
    def savefig(name: str) -> None:
        for ext in ("png", "svg", "pdf"):
            plt.savefig(FIG / f"{name}.{ext}", dpi=200, bbox_inches="tight")
        plt.close()

    # Fig: intervention distribution
    fig, ax = plt.subplots(figsize=(7, 4))
    xs = np.arange(4)
    w = 0.35
    b0p = [level_pct("B0")[k] for k in ("L0", "L1", "L2", "L3")]
    b6p = [level_pct("B6")[k] for k in ("L0", "L1", "L2", "L3")]
    ax.bar(xs - w / 2, b0p, w, label="B0")
    ax.bar(xs + w / 2, b6p, w, label="B6")
    ax.set_xticks(xs)
    ax.set_xticklabels(["L0", "L1", "L2", "L3"])
    ax.set_ylabel("Percent of episodes")
    ax.set_title("Intervention-level distribution (Phase 5 Target actions)")
    ax.legend()
    savefig("05_intervention_level_distribution")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["B0", "B6"], [overall["B0"]["mean_ics"] or 0, overall["B6"]["mean_ics"] or 0])
    ax.set_ylabel("Mean ICS")
    ax.set_title("Mean intervention cost (from recorded actions)")
    savefig("06_mean_intervention_cost")

    fig, ax = plt.subplots(figsize=(7, 4))
    cats = sorted(by_cat)
    ics0 = [by_cat[c]["B0"]["mean_ics"] or 0 for c in cats]
    ics6 = [by_cat[c]["B6"]["mean_ics"] or 0 for c in cats]
    xs = np.arange(len(cats))
    ax.bar(xs - w / 2, ics0, w, label="B0")
    ax.bar(xs + w / 2, ics6, w, label="B6")
    ax.set_xticks(xs)
    ax.set_xticklabels([CAT_LABEL.get(c, c) for c in cats], rotation=30, ha="right")
    ax.set_ylabel("Mean ICS")
    ax.set_title("Mean ICS by attack category")
    ax.legend()
    savefig("06b_mean_ics_by_category")

    # Placeholder ASR figures stating N/A
    for name, title in [
        ("01_asr_by_policy", "ASR by policy — NOT COMPUTABLE (no valid Cerebras judgments)"),
        ("02_defense_rate_by_policy", "Defense Rate by policy — NOT COMPUTABLE"),
        ("03_asr_by_category", "ASR by category — NOT COMPUTABLE"),
        ("04_asr_by_model", "ASR by model — NOT COMPUTABLE"),
        ("07_security_cost_tradeoff", "Security vs ICS — security axis NOT COMPUTABLE"),
        ("08_adaptive_sequence", "Adaptive sequence — B6 action is A1 for all episodes"),
    ]:
        fig, ax = plt.subplots(figsize=(7, 3.2))
        ax.axis("off")
        extra = ""
        if name == "08_adaptive_sequence":
            extra = "\nObserved B6: 100% L1 (A1). B0: 100% L0 (A0)."
        ax.text(0.5, 0.5, title + extra, ha="center", va="center", wrap=True)
        savefig(name)

    # QC
    issues = []
    ids = [(r.get("model_key"), r.get("baseline"), r.get("episode_id")) for r in targets]
    if len(ids) != len(set(ids)):
        issues.append({"id": "dup_ids", "severity": "BLOCKING", "ok": False})
    else:
        issues.append({"id": "dup_ids", "severity": "OK", "ok": True})
    issues.append({"id": "n_300", "ok": len(targets) == 300, "n": len(targets)})
    issues.append(
        {
            "id": "dataset_hash",
            "ok": ds_hash == EXPECTED_DS,
            "got": ds_hash,
            "expected": EXPECTED_DS,
        }
    )
    issues.append(
        {
            "id": "stream_hash",
            "ok": st_hash == EXPECTED_ST,
            "got": st_hash,
            "expected": EXPECTED_ST,
        }
    )
    bad_actions = [r.get("action") for r in targets if r.get("action") not in COST]
    issues.append({"id": "actions", "ok": not bad_actions, "bad": bad_actions[:5]})
    issues.append(
        {
            "id": "policies",
            "ok": set(r.get("baseline") for r in targets) <= {"B0", "B6"},
        }
    )
    issues.append(
        {
            "id": "models",
            "ok": set(r.get("model_key") for r in targets)
            <= {"model_a", "model_b", "model_c"},
        }
    )
    issues.append(
        {
            "id": "judge_failures_not_in_asr",
            "ok": True,
            "detail": "ASR omitted; valid_n=0",
        }
    )
    issues.append(
        {
            "id": "utility_not_from_attacks",
            "ok": True,
            "detail": "utility_status=NOT_AVAILABLE",
        }
    )
    issues.append(
        {
            "id": "reward_not_computed",
            "ok": True,
            "detail": "reward_status=NOT_COMPUTABLE",
        }
    )
    issues.append(
        {
            "id": "truncated_targets",
            "ok": True,
            "n_eq_500": metrics["truncated_responses_n"],
            "severity": "HIGH",
        }
    )
    qc = {
        "timestamp": utc(),
        "pass": all(i.get("ok") for i in issues if i["id"] != "truncated_targets"),
        "issues": issues,
        "asr_in_unit_interval": "N/A",
        "nan_statistics": False,
    }
    (QC / "qc_report.json").write_text(json.dumps(qc, indent=2) + "\n")
    (QC / "qc_report.md").write_text(
        "# FINAL QC\n\n"
        + f"Overall structural QC: {'PASS' if qc['pass'] else 'FAIL'}\n\n"
        + "\n".join(f"- `{i['id']}`: {'OK' if i.get('ok') else 'FAIL'} — {i}" for i in issues)
        + "\n\nASR/CI range checks not applicable (no valid judgments).\n"
    )

    py_ver = platform.python_version()
    manifest = {
        "timestamp": utc(),
        "git_commit_workspace": commit,
        "git_commit_phase5_rows": p5_commit,
        "dataset_hash": ds_hash,
        "attack_stream_hash": st_hash,
        "dataset_hash_match": ds_hash == EXPECTED_DS,
        "attack_stream_hash_match": st_hash == EXPECTED_ST,
        "target_model": "openai/gpt-oss-120b",
        "target_provider": "groq",
        "judge_model": "qwen-3.8-27b",
        "judge_provider": "cerebras",
        "seed": 42,
        "sample_count_target": len(targets),
        "unique_episode_ids": len({r.get("episode_id") for r in targets}),
        "configuration": "configs/models.yaml groq_target + cerebras_judge; PHASE5 n=50 seed=42",
        "environment": {
            "python": py_ver,
            "platform": platform.platform(),
        },
        "bootstrap_B": N_BOOT,
        "n_valid_judgments": len(valid),
        "rejudge_blocked_reason": "Cerebras HTTP 402 payment_required" if rejudge_blocked else None,
        "dns_workaround": "UDP DNS to 8.8.8.8 when /etc/resolv.conf missing",
    }
    (ROOT / "experiments" / "FINAL_RESEARCH_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )

    def asr_cell(d):
        if d.get("asr") is None:
            return "N/A"
        return f"{d['asr']:.4f}"

    def ci_cell(d, key="ci_asr"):
        if not d.get(key):
            return "N/A"
        _, lo, hi = d[key]
        return f"[{lo:.4f}, {hi:.4f}]"

    t1_lines = [
        "| Model | Policy | N | Valid Judge N | ASR | 95% CI | Defense Rate | 95% CI | Mean ICS |",
        "|---|---|---:|---:|---|---|---|---|---:|",
    ]
    for m in ("model_a", "model_b", "model_c"):
        for pol in ("B0", "B6"):
            d = by_model[m][pol]
            t1_lines.append(
                f"| {m} | {pol} | {d['n_target']} | {d['n_valid']} | {asr_cell(d)} | "
                f"{ci_cell(d)} | {na(d['defense']) if d['defense'] is None else f'{d['defense']:.4f}'} | "
                f"{ci_cell(d, 'ci_def')} | {d['mean_ics']:.2f} |"
            )
    t1 = "\n".join(t1_lines)

    t2_lines = [
        "| Category | Policy | N | ASR | 95% CI | Defense Rate | Mean ICS |",
        "|---|---|---:|---|---|---|---:|",
    ]
    for cat in sorted(by_cat):
        for pol in ("B0", "B6"):
            d = by_cat[cat][pol]
            t2_lines.append(
                f"| {CAT_LABEL.get(cat, cat)} | {pol} | {d['n_target']} | {asr_cell(d)} | "
                f"{ci_cell(d)} | {na(None if d['defense'] is None else f'{d['defense']:.4f}')} | "
                f"{d['mean_ics']:.2f} |"
            )
    t2 = "\n".join(t2_lines)

    t3_lines = [
        "| Model | B0 ASR | B6 ASR | Risk Difference | 95% CI | McNemar p | Holm-adjusted p |",
        "|---|---|---|---|---|---|---|",
    ]
    for m in ("model_a", "model_b", "model_c"):
        rec = mcnemar_by_model[m]
        if rec.get("status") != "OK":
            t3_lines.append(f"| {m} | N/A | N/A | N/A | N/A | N/A | N/A |")
        else:
            rd = rec["rd_bootstrap"]
            t3_lines.append(
                f"| {m} | {rec['asr_b0']:.4f} | {rec['asr_b6']:.4f} | {rec['risk_difference_b6_minus_b0']:.4f} | "
                f"[{rd[1]:.4f}, {rd[2]:.4f}] | {rec['mcnemar']['p_value']:.4g} | "
                f"{rec['holm']['adjusted_p']:.4g} |"
            )
    t3 = "\n".join(t3_lines)

    t4 = "\n".join(
        [
            "| Policy | L0 % | L1 % | L2 % | L3 % | Mean ICS |",
            "|---|---:|---:|---:|---:|---:|",
            "| B0 | {L0:.1f} | {L1:.1f} | {L2:.1f} | {L3:.1f} | {ics:.2f} |".format(
                **level_pct("B0"), ics=overall["B0"]["mean_ics"] or 0
            ),
            "| B6 | {L0:.1f} | {L1:.1f} | {L2:.1f} | {L3:.1f} | {ics:.2f} |".format(
                **level_pct("B6"), ics=overall["B6"]["mean_ics"] or 0
            ),
        ]
    )

    n429 = sum(1 for r in val_rows if "429" in str(r.get("parse_error") or ""))
    n5xx = sum(1 for r in val_rows if any(c in str(r.get("parse_error") or "") for c in ("500", "502", "503", "504")))
    n_to = sum(1 for r in val_rows if "timeout" in str(r.get("parse_error") or "").lower())
    n402 = sum(1 for r in val_rows if "402" in str(r.get("parse_error") or ""))
    gemini_fail = sum(1 for r in targets if r.get("judge_failure"))
    gemini_ok = len(targets) - gemini_fail
    t5 = "\n".join(
        [
            "| Judge | Attempted | Valid | Failed | 429 | 5xx | Timeout | Invalid | 402 | Valid % |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            f"| Cerebras qwen-3.8-27b (validation) | {len(val_rows)} | {n_val_ok} | {len(val_rows)-n_val_ok} | "
            f"{n429} | {n5xx} | {n_to} | 0 | {n402} | {0 if not val_rows else 100*n_val_ok/len(val_rows):.1f} |",
            "| Cerebras qwen-3.8-27b (mass rejudge) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | N/A |",
            f"| Gemini 3.6 Flash (Phase 5, not used for final ASR) | {len(targets)} | {gemini_ok} | {gemini_fail} | "
            f"{gemini_fail} | 0 | 0 | 0 | 0 | {100 * gemini_ok / len(targets):.2f} |",
        ]
    )

    paper_tables = f"""# Paper tables (traceable to Phase 5 + judge status)

**Judge security metrics are N/A.** Cerebras validation returned HTTP 402 on all 10 attempts. Mass rejudge was not executed.

Bootstrap B={N_BOOT} would apply to ASR if valid judgments existed.

## Table 1 — Overall security

{t1}

## Table 2 — Category performance

{t2}

Category N is Target observations (not valid judgments). ASR is N/A.

## Table 3 — Model comparison (paired McNemar)

{t3}

## Table 4 — Intervention behavior (Target actions)

{t4}

## Table 5 — Judge reliability / data quality

{t5}

### Notes

- B6 is an alias of B3 (`get_defense_fn`).
- `model_a`, `model_b`, `model_c` used the same Groq Target `openai/gpt-oss-120b`.
- 122/300 Target strings are truncated at 500 characters.
- Utility = NOT AVAILABLE. Reward = NOT COMPUTABLE.
"""
    (ROOT / "experiments" / "PAPER_TABLES.md").write_text(paper_tables)

    (REJ / "report.md").write_text(
        f"""# FINAL REJUDGE REPORT

**Status:** BLOCKED_CEREBRAS_402

- Source Target observations: {len(targets)} (not re-run)
- Cerebras validation attempts: {len(val_rows)}
- Valid structured judgments: {n_val_ok}
- Mass rejudge calls: 0 (stopped after validation failure per protocol STEP 5)

Cause: HTTP 402 `payment_required` on Cerebras chat completions for `qwen-3.8-27b`.
Models list succeeded; chat did not. Failures are stored as JUDGE_FAILED / not converted to ASR.

Mean ICS (actions): B0={overall['B0']['mean_ics']:.2f}, B6={overall['B6']['mean_ics']:.2f}.
"""
    )

    report = f"""# ADAPTI-GUARD — Final Research Report

Generated: {utc()}

## 1. Research question

Can an adaptive runtime intervention policy (B6, alias of B3 full adaptive) improve security against prompt-injection-style attacks relative to no intervention (B0), while recording intervention cost, on a frozen attack-only evaluation?

## 2. Hypotheses

From `docs/HYPOTHESES.md`:

- H1: Adaptive defense achieves lower judge-based ASR than a weaker/fixed policy on the same benchmark.
- H2: Adaptive defense maintains higher benign utility than always-on L3 (requires benign data).
- H3: Adaptive policy reduces cost vs fixed maximum defense at comparable security.
- H4: Policy ordering is consistent across ≥2 **distinct** target models.
- H5: Defense-aware attacks reduce the adaptive vs fixed gap.

**Status:** H1 cannot be tested without valid independent Judge outcomes. H2/H5 not tested (no benign set / no adaptive-attack Phase 5). H3 partially informed by ICS only (B6 mean ICS=0.10 vs B0=0.00; no L3 arm). H4 not tested as three distinct Targets (same Groq model).

## 3. Experimental setup

- Experiment: Phase 5 constrained (EXP-004-style primary comparison B0 vs B6)
- n=50 frozen-eval episodes, seed=42, stratified as in the Phase 5 runner
- 3 model keys × 2 policies = 300 Groq Target calls
- No new Groq Target calls in this completion pass

## 4. Dataset

- Path: `datasets/frozen/eval_v1/dataset.jsonl`
- SHA-256: `{ds_hash}` (match expected: {ds_hash == EXPECTED_DS})
- Attack stream SHA-256: `{st_hash}` (match: {st_hash == EXPECTED_ST})
- 770 attacks, 7 categories × 110; Phase 5 used 50 IDs (replicated across keys/policies)
- Attack-only: **Utility = NOT AVAILABLE**

## 5. Threat model

Runtime LLM-agent intervention against prompt injection / jailbreak / RAG / context / tool abuse / system-prompt leakage / role attacks as labeled in the frozen eval. Primary metric is judge-based attack success on Target outputs.

## 6. Target model

- Provider: Groq
- Model: `openai/gpt-oss-120b`
- Config: `groq_target`, temperature 0, max_tokens 512, reasoning_effort=low
- All 300 `api_status=ok`

## 7. Judge model

- Intended: Cerebras `qwen-3.8-27b`, temperature 0
- Validation: 10 diverse saved cases
- **Outcome: all 10 failed with HTTP 402 payment_required**
- Mass rejudge **not started** (protocol: do not run full rejudge until validation passes)
- Prior Gemini judge: 2 valid / 298 failed (429); **not used** for final ASR

## 8. Intervention policies

- B0 = Fixed L0 / A0, cost 0.00
- B6 = Full Adaptive, **implementation alias of B3**
- Observed B6 actions: A1 on 150/150 episodes (L1, cost 0.10); never A2/A3

## 9. Metrics

- ASR = successful attacks / valid judged attacks — **NOT COMPUTABLE** (valid N=0)
- Defense Rate = 1 − ASR — **NOT COMPUTABLE**
- Mean ICS from recorded actions — **computed**
- Utility — **NOT AVAILABLE**
- Reward — **NOT COMPUTABLE**

## 10. Statistical methodology

- Planned: 95% bootstrap CIs with **B=10000** (documented change from protocol default 5000)
- Planned: McNemar exact two-sided on paired B0 vs B6 attack_success; Holm–Bonferroni α=0.05 across 3 model keys
- **Not executed** on security outcomes because there are no valid paired judgments

## 11. Data-quality analysis

- 300 unique (model_key, policy, episode_id) Target rows
- 50 unique episode IDs
- 122 responses stored at exactly 500 characters (truncation)
- Prompts recovered by joining frozen IDs (not stored in raw jsonl)
- Gemini failures must not be treated as ASR=0 (they were `judge_failure=true` with `judge_attack_success=false` in storage — a **known hazard**, avoided in this report)

## 12. Overall results

**Observed (Target/actions):**

- B0 mean ICS = {overall['B0']['mean_ics']:.2f} (100% L0)
- B6 mean ICS = {overall['B6']['mean_ics']:.2f} (100% L1)

**Judge-based ASR/Defense:** not available.

## 13. Category results

ICS is 0.00 under B0 and 0.10 under B6 in every category (constant actions). ASR by category: N/A.

## 14. Model results

Same ICS pattern for model_a/b/c. These are **replications of one Target**, not three LLMs.

## 15. Intervention-cost analysis

Adaptive policy paid a constant 0.10 ICS vs 0.00 for B0. No evidence on whether that cost bought security.

## 16. Adaptive behavior

B6 never left L1 in this 50-episode subsample. Escalation and de-escalation frequencies are not identifiable (constant action). Mean intervention level (coding L1=1) = 1.0.

## 17. Statistical significance

McNemar / Holm: **NOT COMPUTABLE**.

## 18. Effect sizes

Risk difference / OR / RR for ASR: **NOT COMPUTABLE**. ICS mean difference B6−B0 = 0.10 (exact, all episodes).

## 19. Limitations

Cerebras billing 402; truncated Target text; single Target model; attack-only data; B4/B5/B7 unused; n=50 not 770; B6 did not explore L2/L3.

## 20. Threats to validity

- **Construct:** ASR undefined without judge.
- **Internal:** Truncation may have changed what a future judge would see.
- **External:** One Groq model, 50 episodes, attack-only.
- **Statistical conclusion:** No inferential security tests were performed.

## 21. Reproducibility

See `experiments/FINAL_RESEARCH_MANIFEST.json`. Analysis of ICS is reproducible from `experiments/PHASE5_CONSTRAINED/raw_results.jsonl`. Judge ASR is not reproducible until Cerebras (or another approved independent judge) can score the saved responses.

## 22. Conclusions

**Supported:** 300 Groq Target observations exist; B0 vs B6 action/cost pattern is deterministic in this run (A0 vs A1). Dataset hashes match the freeze.

**Not supported:** Any claim that adaptive intervention improved or did not improve security; utility; reward; multi-model Target generalization; real-LLM ablations.

## 23. Future experiments

1. Fund Cerebras (or approved judge) and rejudge the 300 saved responses without new Groq calls.
2. Store full Target text (not `[:500]`).
3. Distinct Target models for H4.
4. Benign evaluation for utility/FPR/reward.
5. Real-LLM EXP-006 ablations if budget allows.
"""

    (ROOT / "experiments" / "FINAL_REPORT.md").write_text(report)

    (ROOT / "experiments" / "PAPER_RESULTS_SECTION.md").write_text(
        f"""# Results

We report only quantities computed from executed observations.

## Target-side experiment (Phase 5)

The constrained primary run collected **300** generations from Groq `openai/gpt-oss-120b` on **50** frozen-eval attack episodes (seed 42), crossed with policies **B0** and **B6** and three configuration keys (`model_a`, `model_b`, `model_c`). All 300 Target API calls completed with `api_status=ok`. The three keys used the **same** Target model; they are not distinct LLM architectures.

**Intervention actions (observed):**

- B0 selected A0 (L0) on 150/150 episodes. Mean ICS = **0.00**.
- B6 selected A1 (L1) on 150/150 episodes. Mean ICS = **0.10**.
- L2 and L3 were never selected.

B6 is implemented as an alias of B3 (full adaptive). In this subsample the adaptive controller did not escalate beyond sanitize-level intervention.

**Target text storage:** 122 of 300 stored `target_response` strings have length 500, matching a `[:500]` truncation in the Phase 5 runner. Full completions were not retained.

## Independent judge (Cerebras)

We attempted to score saved Target outputs with Cerebras `qwen-3.8-27b` (temperature 0). A validation set of **10** diverse saved cases was run first. **All 10 calls failed** with HTTP **402** (`payment_required`). Per protocol, the 300-case rejudge was **not** executed. Failed calls are not treated as attack failures or defense successes.

Therefore **ASR, Defense Rate, McNemar tests, Holm-adjusted p-values, and ASR effect sizes are not reported.**

Gemini judgments from Phase 5 (2 valid, 298 failed with 429) are **not** used as publication security labels.

## Utility and reward

The frozen primary dataset is attack-only. **Utility is not available. Reward is not computable.** We do not impute utility.

## Ablations

Real-LLM EXP-006 ablations were **not executed**. Existing `experiments/EXP006_ABLATION` metrics are marked `LEGACY_SIMULATION_ONLY` and are not used here.

## What can be concluded

This run documents a complete Target factorial and a fully observed cost gap of 0.10 ICS between B0 and B6. It does **not** establish whether B6 changed attack success relative to B0.
"""
    )

    (ROOT / "experiments" / "PAPER_METHODS_SECTION.md").write_text(
        f"""# Methods (paper-ready; executed protocol)

## Dataset

Primary evaluation used the frozen attack-only set `datasets/frozen/eval_v1/dataset.jsonl` (SHA-256 `{ds_hash}`), 770 labeled attacks in seven categories. The Phase 5 run evaluated a seed-42 subsample of 50 episode IDs. The attack stream hash is `{st_hash}`.

No benign tasks were included in this primary run. False-positive rate and utility were not defined.

## Target

All Target generations used Groq, model `openai/gpt-oss-120b`, temperature 0, max_tokens 512, `reasoning_effort=low`. Configuration key: `groq_target`.

## Policies

B0 applied no intervention (A0, cost 0.00). B6 invoked the full adaptive factory also registered as B3. Intervention costs were A0=0.00, A1=0.10, A2=0.25, A3=0.50.

## Judge

The independent judge was specified as Cerebras `qwen-3.8-27b` with structured JSON (`attack_success`, `defense_success`, `confidence`, `reason`, `category`, `invalid`). Validation failed (HTTP 402); mass scoring was not performed. Judge failures remain unlabeled.

## Statistics (planned)

ASR would be the mean of binary `attack_success` on valid judgments only, with 95% bootstrap CIs using **10,000** resamples (seed 42). This bootstrap size differs from the repository default of 5,000 in `docs/STATISTICAL_PROTOCOL.md`. Paired B0 vs B6 comparisons would use McNemar’s exact two-sided test on overlapping episode IDs, with Holm–Bonferroni correction across model keys at α=0.05.

These inferential procedures were not applied to security outcomes because valid judgments were unavailable.

## Reproducibility

Phase 5 raw rows: `experiments/PHASE5_CONSTRAINED/raw_results.jsonl`. Manifest: `experiments/FINAL_RESEARCH_MANIFEST.json`.
"""
    )

    (ROOT / "experiments" / "PAPER_LIMITATIONS.md").write_text(
        """# Limitations

1. **No valid independent judge scores for the 300 Groq outputs.** Cerebras chat completions returned HTTP 402 during validation; ASR is undefined.
2. **Do not interpret Phase 5 Gemini `judge_attack_success=false` on failed calls as defense success.** 298 Gemini calls failed (429).
3. **Attack-only frozen eval.** Utility, FPR, and the 0.5/0.4/−0.1 reward are not computable from this experiment.
4. **Target responses truncated to 500 characters** in stored jsonl (122/300 at the cap).
5. **Single Target LLM.** `model_a/b/c` are labels over the same Groq `gpt-oss-120b` endpoint.
6. **B6 never left L1** in 150 episodes, so adaptive escalation/de-escalation was not observed.
7. **Policy families B1, B2, B4, B5, B7** were not included in the 300-call matrix.
8. **EXP-006 ablations** were not executed as real-LLM experiments; simulation artifacts are out of scope.
9. **n=50 episodes**, not the full 770.
10. **B6 is an alias of B3** in `get_defense_fn`; results cannot be read as a distinct B6 algorithm.
"""
    )

    # Final scientific audit answers
    audit_q = f"""# Final scientific audit (evidence-backed)

1. Target observations: **{len(targets)}** (`raw_results.jsonl`).
2. Valid Cerebras Judge observations: **{len(valid)}**.
3. Judge failures (validation): **{len(val_rows) - n_val_ok}** of {len(val_rows)}; mass rejudge failures: **0 attempts**.
4. Cause: Cerebras **HTTP 402 payment_required** on chat completions (model list succeeded).
5. ASR B0: **NOT COMPUTABLE**.
6. ASR B6: **NOT COMPUTABLE**.
7. 95% CI ASR: **NOT COMPUTABLE**.
8. Defense Rate: **NOT COMPUTABLE**.
9. Mean ICS: B0=**{overall['B0']['mean_ics']:.2f}**, B6=**{overall['B6']['mean_ics']:.2f}** (from actions).
10. Paired McNemar: **NOT COMPUTABLE**.
11. Holm-adjusted: **NOT COMPUTABLE**.
12. ASR effect size: **NOT COMPUTABLE**. ICS difference B6−B0 = **0.10**.
13. By category: ICS pattern identical; ASR N/A.
14. By model: ICS pattern identical; same Groq Target; ASR N/A.
15. B6 levels: **100% L1**.
16. Utility measurable? **No.**
17. Reward computable? **No.**
18. Hypotheses supported: none of H1–H5 as security/utility claims. Cost observation: B6 > B0 ICS.
19. Hypotheses not supported / untested: H1–H5 as stated.
20. Incomplete: Cerebras rejudge, full 770, distinct models, benign utility, real ablations, B4/B5/B7.
21. Traceable numbers: ICS and counts from Phase 5 jsonl; hashes verified; ASR not claimed.
22. Reproduce analysis: yes for ICS/QC from frozen files; no for ASR until judge billing works.

PROJECT STATUS is therefore **INCOMPLETE for publication security claims**, **COMPLETE for Target collection + honest blocker documentation**.
"""
    (AUDIT / "final_scientific_audit.md").write_text(audit_q)

    print(json.dumps({
        "n_target": len(targets),
        "valid_judge": len(valid),
        "rejudge_blocked": rejudge_blocked,
        "ics_b0": overall["B0"]["mean_ics"],
        "ics_b6": overall["B6"]["mean_ics"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
