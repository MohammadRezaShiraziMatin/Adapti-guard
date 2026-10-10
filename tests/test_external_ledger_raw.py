"""Every §6.6 and §6.7 ledger number must match the raw committed records.

Each value is recomputed here from the per-episode JSON files. This test does not import scripts/recompute_external_test.py,
so a bug in that script cannot make the test pass. The one exception is the cluster-bootstrap intervals of §6.6: their
producer is not in the tree, so they are checked against experiments/external/injecagent_registered_20261001/ANALYSIS.json only.
"""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/paper/negative_result/NUMBERS_LEDGER.md"
SOURCE = re.compile(r"^(experiments/external/\S+) · key (\S+)$")
REG_DIR = "experiments/external/injecagent_registered_20261001/"
ANALYSIS = REG_DIR + "ANALYSIS.json"
PHASE2 = "experiments/external/phase2_calibration_20261001/calibration.json"


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def ledger_rows():
    rows = []
    for ln in LEDGER.read_text(encoding="utf-8").splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) < 3:
            continue
        src = cells[2].strip("`")
        if src.startswith("experiments/external/"):
            rows.append((cells[0], cells[1].strip("`"), src))
    return rows


def wilson_pct(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{100 * (c - h):.1f} to {100 * (c + h):.1f}"


def cp_upper_zero_pct(n):
    return f"{100 * (1 - 0.025 ** (1 / n)):.1f}%"


def arm_rows(eps, arm):
    return {e["case_id"]: e for e in eps if e["arm"] == arm}


def recompute(path, key):
    """Value for (raw file, key), from the raw records only."""
    if path == ANALYSIS:
        model = next(m for m in ("meta-llama/llama-4-maverick", "qwen/qwen3.8-flash") if key.startswith(m + "."))
        metric, stat = key[len(model) + 1:].split(".", 1)
        lo, hi = load(path)[model][metric][stat]
        return f"[{lo:.3f}, {hi:.3f}]"
    if path.startswith(REG_DIR) and path.endswith(".json"):
        eps = load(path)["episodes"]
        arm, _, stat = key.partition(".")
        rows = arm_rows(eps, arm)
        if stat == "hits/n":
            return f"{sum(1 for e in rows.values() if e['first_attacker_tool'])}/{len(rows)}"
        if stat == "wilson95":
            k = sum(1 for e in rows.values() if e["first_attacker_tool"])
            return wilson_pct(k, len(rows))
        if stat == "mean":
            other, ref = arm.split("-")
            a, b = arm_rows(eps, ref), arm_rows(eps, other)
            d = [int(b[c]["first_attacker_tool"]) - int(a[c]["first_attacker_tool"]) for c in a]
            return f"{sum(d) / len(d):.3f}"
    if path.startswith("experiments/external/injecagent_panel_calib_20261001/"):
        eps = [e for e in load(path)["episodes"] if e["kind"] in ("dh", "ds")]
        arm, stat = key.split(".")[1], key.split(".")[2]
        scored = [e for e in eps if e["arm"] == arm and e["http"] == 200]
        if stat == "scored":
            return cp_upper_zero_pct(len(scored))
        hits = sum(1 for e in scored if e["first_attacker_tool"])
        return f"{hits}/{len(scored)}"
    if path == PHASE2:
        model = key.split(".Hard.")[0]
        rest = key.split(".Hard.")[1]
        res = next(r for r in load(path)["results"] if r["model"] == model)
        scored = [e for e in res["episodes"] if e["origin"] == "human" and e["arm"] == "A0" and e["http"] == 200]
        if rest == "A0.scored":
            return cp_upper_zero_pct(len(scored))
        return f"{sum(1 for e in scored if e.get('goal_met') is True)}/{len(scored)}"
    raise AssertionError(f"no recomputation rule for {path} · {key}")


def test_external_ledger_rows_match_raw_records():
    rows = ledger_rows()
    assert len(rows) >= 30, "ledger lost its §6.6/§6.7 rows"
    bad = []
    for quantity, value, source in rows:
        m = SOURCE.match(source)
        assert m, f"{quantity}: source must be 'path · key name', got {source!r}"
        got = recompute(*m.groups())
        if got != value:
            bad.append(f"{quantity}: ledger {value!r} != raw {got!r} ({source})")
    assert not bad, "\n".join(bad)
