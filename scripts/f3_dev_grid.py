"""F3 dev-phase grid over adaptive-controller settings (offline replay, dev seeds 0-19).

See docs/F3_CONFIRMATORY_CONTRACT.md. Needs results/f3_confirmatory/dev_guard_cache.json
(built by ``scripts/f3_dev_replay.py --build-guard-cache``).
"""

import importlib.util
import itertools
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("d", ROOT / "scripts" / "f3_dev_replay.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
from adapti_guard.adaptation.policy_update_engine import PolicyUpdateEngine  # noqa: E402
d.f3._GUARD_CACHE.update(json.loads((ROOT / "results" / "f3_confirmatory" / "dev_guard_cache.json").read_text()))
SEEDS = range(20)  # dev seeds, disjoint from any confirmatory seeds


def mean_metrics(res, kind=None):
    xs = [v for (k, _), v in res.items() if kind in (None, k)]
    return [round(statistics.mean(x[i] for x in xs), 3) for i in range(4)]  # loss, asr, util, cost


def main():
    for arm in ("fixed_l1", "fixed_l2", "fixed_l3"):
        r = d.evaluate(arm, SEEDS)
        print(arm, mean_metrics(r), "uniform", mean_metrics(r, "uniform25")[0], "burst", mean_metrics(r, "burst")[0])
    rows = []
    for at, dw, bc, dec in itertools.product([2, 3], [3, 5], [0, 4], [0, 1]):
        kw = dict(attack_threshold=at, legitimate_threshold=2, pressure_decay=dec,
                  benign_streak_threshold=10, min_dwell=dw, backoff_cap=bc)
        r = d.evaluate("adaptive_proxy_sem", SEEDS, lambda kw=kw: PolicyUpdateEngine(**kw))
        rows.append((mean_metrics(r)[0], kw, mean_metrics(r)))
    for row in sorted(rows, key=lambda x: x[0])[:8]:
        print(row)
    print("experiment-scale default:", mean_metrics(d.evaluate("adaptive_proxy_sem", SEEDS)))


if __name__ == "__main__":
    main()
