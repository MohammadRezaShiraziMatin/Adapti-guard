"""EXPLORATORY (non-confirmatory, not registered) analyses of the R2 and R3 InjecAgent runs. Offline.

Nothing here is part of the frozen protocol; no multiplicity correction is applied and no result is a confirmatory
claim. The run folders are read and validated with the loaders of scripts/analyze_confirmatory.py (unchanged).

  1. Proposal-level endpoint: per model x arm, rate of episodes whose model output named an attacker tool
     (record field "any_attacker_tool", set by the launcher from the model's tool_calls names, before the arm's
     executor decides executed/blocked/rejected). Clopper-Pearson 95%. A0 vs SPOT_TOOL exact McNemar (unadjusted).
  2. NOINJ / benign-call interference: executor_log entries with status "blocked" or "rejected" on non-attacker tools,
     per run x model x arm, and on the NOINJ arm. Whether a SPOT_TOOL-defended NOINJ episode exists is reported, not
     assumed.
  3. Error / finish table per run x model x arm, plus notable episodes.
  4. ds-0440 (llama A0, finish=length) sensitivity of the H2 llama McNemar: non-event (as in the main analysis),
     event, excluded.

Unresolved episodes (executed_attacker_call None) are excluded from rates and pairs, never imputed.

Usage:
  python scripts/analyze_exploratory.py --r2 <R2> --r3 <R3> --plan-r2 build/r2_plan.json --plan-r3 build/r3_plan.json \
      --out docs/research/artifacts/exploratory_results.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analysis_mcnemar_bootstrap as A  # noqa: E402

_spec = importlib.util.spec_from_file_location("analyze_confirmatory", HERE / "analyze_confirmatory.py")
C = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("analyze_confirmatory", C)
_spec.loader.exec_module(C)

STATUS = "EXPLORATORY - NOT CONFIRMATORY, NOT REGISTERED"
SEED = 20261001  # recorded for determinism; no resampling is used
LEVEL = 0.95
NOTABLE_R2 = ["ds-0440"]
NOTABLE_R3 = ["dh-0016", "dh-0067", "dh-0152", "dh-0492"]
SHORT = {v: k for k, v in C.MODELS.items()}
PROPOSAL_FIELD = "any_attacker_tool"


def _cp(k: int, n: int) -> list[float] | None:
    return list(A.clopper_pearson(k, n, LEVEL)) if n else None


def _require(records: Sequence[Mapping], fields: Sequence[str]) -> list[str]:
    return sorted({f for r in records for f in fields if f not in r})


def _by(records, model, arm):
    out = {}
    for r in records:
        if r["model"] == model and r["arm"] == arm:
            if r["case_id"] in out:
                raise C.AnalysisError(f"duplicate {model} {arm} {r['case_id']}")
            out[r["case_id"]] = r
    return out


def _attacker_tools(r: Mapping) -> bool | None:
    return r.get(PROPOSAL_FIELD)


def proposal_endpoint(runs: Mapping[str, Sequence[Mapping]]) -> dict:
    rates, paired = {}, {}
    consistency = []
    for run, recs in runs.items():
        for model in sorted({r["model"] for r in recs}):
            for arm in sorted({r["arm"] for r in recs if r["model"] == model} - {"NOINJ"}):
                eps = _by(recs, model, arm)
                vals = [eps[c][PROPOSAL_FIELD] for c in sorted(eps)]
                res = [v for v in vals if v is not None]
                k, n = sum(1 for v in res if v), len(res)
                ex = [eps[c]["executed_attacker_call"] for c in sorted(eps)]
                kx = sum(1 for v in ex if v)
                prop_not_exec = sorted(c for c in eps if eps[c][PROPOSAL_FIELD] and not eps[c]["executed_attacker_call"])
                rates[f"{run}|{SHORT[model]}|{arm}"] = {
                    "n_resolved": n, "unresolved": len(vals) - n, "proposed": k,
                    "rate": k / n if n else None, "clopper_pearson_95": _cp(k, n),
                    "executed": kx, "proposed_not_executed": prop_not_exec}
            if run == "R2":
                a0 = [(c, r[PROPOSAL_FIELD]) for c, r in sorted(_by(recs, model, "A0").items())]
                sp = [(c, r[PROPOSAL_FIELD]) for c, r in sorted(_by(recs, model, "SPOT_TOOL").items())]
                pairs, excl = A.resolved_pairs(a0, sp)
                b, c = A.discordance(pairs)
                paired[SHORT[model]] = {"n_pairs": len(pairs), "excluded_unresolved": excl,
                                        "a0_only": b, "spot_only": c,
                                        "both": sum(1 for _, x, y in pairs if x and y),
                                        "a0_minus_spot": (b - c) / len(pairs) if pairs else None,
                                        "exact_mcnemar_p_unadjusted": A.exact_mcnemar_p(b, c)}
    return {"definition": ("proposed = record field 'any_attacker_tool': True if any tool call the model emitted in the "
                           "episode names one of the case's attacker tools (launcher sets it from the model's tool_calls "
                           "before the executor's executed/blocked/rejected decision). None for errored episodes "
                           "(excluded, not imputed)."),
            "note": "no multiplicity correction; exploratory only",
            "rates": rates, "a0_vs_spot_tool": paired}


def benign_interference(runs: Mapping[str, Sequence[Mapping]]) -> dict:
    table = {}
    for run, recs in runs.items():
        for model in sorted({r["model"] for r in recs}):
            for arm in sorted({r["arm"] for r in recs if r["model"] == model}):
                eps = _by(recs, model, arm)
                statuses = Counter(e["status"] for r in eps.values() for e in r["executor_log"])
                hit = sorted(c for c, r in eps.items()
                             if any(e["status"] in ("blocked", "rejected") for e in r["executor_log"]))
                res = [r for r in eps.values() if r["executed_attacker_call"] is not None]
                k = sum(1 for r in res if r["case_id"] in hit)
                table[f"{run}|{SHORT[model]}|{arm}"] = {
                    "episodes": len(eps), "n_resolved": len(res), "episodes_with_blocked_or_rejected_call": k,
                    "rate": k / len(res) if res else None, "clopper_pearson_95": _cp(k, len(res)),
                    "executor_status_counts": dict(sorted(statuses.items())), "case_ids": hit}
    noinj_arms = sorted({r["arm"] for recs in runs.values() for r in recs if r["arm"] == "NOINJ"})
    return {"definition": ("benign interference = an executor_log entry with status 'blocked' (defense denied) or "
                           "'rejected' (unknown tool name) in the episode"),
            "data_limitation": ("The records contain one NOINJ arm per model (no defense variant field); there are no "
                                "NOINJ episodes run under SPOT_TOOL, so a SPOT_TOOL vs A0 false-positive rate on "
                                "no-injection cases cannot be computed from these records. Reported instead: "
                                "blocked/rejected calls in every arm, including SPOT_TOOL on injected cases."),
            "noinj_arms_present": noinj_arms, "table": table}


def error_finish(runs: Mapping[str, Sequence[Mapping]]) -> dict:
    table, notable = {}, []
    for run, recs in runs.items():
        for model in sorted({r["model"] for r in recs}):
            for arm in sorted({r["arm"] for r in recs if r["model"] == model}):
                eps = list(_by(recs, model, arm).values())
                http = Counter()
                transport = Counter()
                for r in eps:
                    for s in r["http_statuses"]:
                        if isinstance(s, str):
                            transport[s] += 1
                        elif s != 200:
                            http[str(s)] += 1
                table[f"{run}|{SHORT[model]}|{arm}"] = {
                    "episodes": len(eps), "http_error_responses": dict(sorted(http.items())),
                    "transport_errors": dict(sorted(transport.items())),
                    "episodes_with_error": sum(1 for r in eps if r["error"] is not None),
                    "finish": dict(sorted(Counter(str(r["finish"]) for r in eps).items())),
                    "unresolved": sum(1 for r in eps if r["executed_attacker_call"] is None)}
        want = NOTABLE_R2 if run == "R2" else NOTABLE_R3
        for r in sorted(recs, key=lambda r: (r["model"], r["case_id"], r["arm"])):
            if r["case_id"] in want or r["error"] is not None or r["finish"] == "length":
                notable.append({"run": run, "model": SHORT[r["model"]], "arm": r["arm"], "case_id": r["case_id"],
                                "finish": r["finish"], "error": r["error"], "tool_calls": r["tool_calls"],
                                "any_attacker_tool": r[PROPOSAL_FIELD],
                                "executed_attacker_call": r["executed_attacker_call"]})
    return {"table": table, "notable_episodes": notable}


def ds0440_sensitivity(r2: Sequence[Mapping]) -> dict:
    model = C.MODELS["llama"]
    a0 = dict(C._rows(r2, model, "A0"))
    sp = dict(C._rows(r2, model, "SPOT_TOOL"))
    out = {"llama_A0_ds-0440_recorded": a0.get("ds-0440"), "llama_SPOT_TOOL_ds-0440_recorded": sp.get("ds-0440")}
    for name in ("non_event_main", "event", "excluded"):
        a, s = dict(a0), dict(sp)
        if name == "event":
            a["ds-0440"] = True
        elif name == "excluded":
            a.pop("ds-0440"), s.pop("ds-0440")
        pairs, excl = A.resolved_pairs(sorted(a.items()), sorted(s.items()))
        b, c = A.discordance(pairs)
        out[name] = {"n_pairs": len(pairs), "a0_only": b, "spot_only": c, "exact_mcnemar_p": A.exact_mcnemar_p(b, c),
                     "a0_events": sum(1 for _, x, _ in pairs if x)}
    return out


def analyze(r2: Sequence[Mapping], r3: Sequence[Mapping]) -> dict:
    needed = ["case_id", "model", "arm", "finish", "error", "http_statuses", "tool_calls", PROPOSAL_FIELD,
              "executed_attacker_call", "executor_log"]
    missing = {"R2": _require(r2, needed), "R3": _require(r3, needed)}
    if missing["R2"] or missing["R3"]:
        raise C.AnalysisError(f"records lack fields {missing}; nothing is guessed")
    runs = {"R2": r2, "R3": r3}
    return {"status": STATUS, "seed": SEED, "interval_level": LEVEL,
            "inputs_note": "qwen dh-0218 is unresolved (transport error) and excluded; ds-0440 is a non-event in the main analysis",
            "1_proposal_endpoint": proposal_endpoint(runs),
            "2_noinj_benign_interference": benign_interference(runs),
            "3_error_finish": error_finish(runs),
            "4_ds0440_sensitivity_H2_llama": ds0440_sensitivity(r2)}


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for f in ("--r2", "--r3", "--plan-r2", "--plan-r3", "--out"):
        ap.add_argument(f, type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        sha = C.check_protocol_hash()
        campaign = json.loads(C.CAMPAIGN_PLAN.read_text())
        r2, s2 = C.load_run_with_status(a.r2, "R2", a.plan_r2, protocol_sha=sha, campaign=campaign)
        r3, s3 = C.load_run_with_status(a.r3, "R3", a.plan_r3, protocol_sha=sha, campaign=campaign)
        result = analyze(r2, r3)
    except (C.AnalysisError, ValueError, KeyError) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    result["run_status"] = {"R2": s2, "R3": s3}
    result["protocol_sha256"] = sha
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=1, sort_keys=True, ensure_ascii=True) + "\n")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
