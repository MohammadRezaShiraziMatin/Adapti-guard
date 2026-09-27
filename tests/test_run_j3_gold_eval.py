"""Offline tests for J3 gold eval script."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from run_j3_gold_eval import collect_facts, fleiss_kappa_binary  # noqa: E402


def test_fleiss_kappa_perfect_agreement():
    triplets = [(True, True, True)] * 10 + [(False, False, False)] * 10
    k = fleiss_kappa_binary(triplets)
    assert k is not None
    assert k > 0.99


def test_collect_facts_j1_present_j2_missing():
    facts = collect_facts(
        gold_path=ROOT / "experiments/judge_gold/GOLD_SET_v2.jsonl",
        j1_pack=ROOT
        / "experiments/judge_gold/J1_V2_ABLATION_20260927-070101/per_item.jsonl",
        j2_pack=None,
    )
    assert facts["gold_v3_exists"] is False
    assert facts["j1_labels_on_all_40"]["present"] is True
    assert facts["j1_labels_on_all_40"]["p0_parse_ok_n"] == 39
    assert facts["j2_labels_on_all_40"]["present"] is False


def test_run_j3_prepare_only_cli():
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_j3_gold_eval.py"), "--facts-only"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["mode"] == "facts"
    assert data["facts"]["locked_gold_set"]["n_items"] == 40
