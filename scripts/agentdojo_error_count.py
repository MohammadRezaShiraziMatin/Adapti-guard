"""Re-derive the AgentDojo targeted ASR for one model and attack from the public run files.

Input: a checkout of https://github.com/ethz-spylab/agentdojo at the pinned commit (see verify/agentdojo/PIN.md).
Reads only runs/<model>/<suite>/user_task_*/<attack>/... JSON files. No network, no model calls.

Two readings of the same files:
- published rule: security = True means the injection succeeded. An errored episode has security = True, so it counts as an attack success;
- unresolved rule: an errored episode is None and is excluded from numerator and denominator.

Usage: python scripts/agentdojo_error_count.py <agentdojo_checkout> <model_dir> <attack> [--csv out.csv]
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
from pathlib import Path


def episodes(root: Path, model: str, attack: str) -> list[dict]:
    files = sorted(glob.glob(str(root / "runs" / model / "*" / "user_task_*" / attack / "*.json")))
    files += sorted(glob.glob(str(root / "runs" / model / "*" / "user_task_*" / attack / "*" / "*.json")))
    seen: dict[tuple[str, str, str], dict] = {}
    for f in files:
        d = json.load(open(f))
        key = (d["suite_name"], d["user_task_id"], d["injection_task_id"])
        if key in seen:
            continue
        err = d.get("error") not in (None, "None", "")
        seen[key] = {
            "suite": key[0], "user_task": key[1], "injection_task": key[2],
            "errored": err, "security": d.get("security") in (True, "True"), "file": str(Path(f).relative_to(root)),
        }
    return sorted(seen.values(), key=lambda e: (e["suite"], e["user_task"], e["injection_task"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("model")
    ap.add_argument("attack")
    ap.add_argument("--csv", type=Path)
    a = ap.parse_args()
    eps = episodes(a.root, a.model, a.attack)
    n = len(eps)
    err = sum(e["errored"] for e in eps)
    sec = sum(e["security"] for e in eps)
    ok = [e for e in eps if not e["errored"]]
    sec_ok = sum(e["security"] for e in ok)
    print(f"{a.model} {a.attack}: pairs={n} errored={err}")
    print(f"published rule (errored = attack success): {sec}/{n} = {100 * sec / n:.2f}%")
    print(f"unresolved rule (errored = None): {sec_ok}/{len(ok)} = {100 * sec_ok / len(ok):.2f}%")
    if a.csv:
        with a.csv.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(eps[0].keys()))
            w.writeheader()
            w.writerows(eps)


if __name__ == "__main__":
    main()
