"""Second-dataset (MT1 r1) rule application reproduces the numbers quoted in the docs."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_mt1_second_dataset_numbers(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("apply_rules_second_dataset_mt1", ROOT / "scripts/apply_rules_second_dataset_mt1.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    monkeypatch.setattr(m, "OUT", tmp_path / "o.json")
    m.main()
    r = json.loads((tmp_path / "o.json").read_text())
    a = r["agreement"]
    assert (a["B0"]["judge"], a["B0"]["canary"], a["B0"]["n"]) == (76, 70, 114)
    assert (a["SPOTLIGHT"]["judge"], a["SPOTLIGHT"]["canary"]) == (43, 48)
    assert 0.8 < a["B0"]["kappa"] < 0.82
    sp = r["paired"]["SPOTLIGHT"]["pooled"]
    assert (sp["judge"]["b10"], sp["judge"]["b01"]) == (39, 6) and (sp["canary"]["b10"], sp["canary"]["b01"]) == (31, 9)
    b3 = r["paired"]["B3"]["pooled"]
    assert (b3["judge"]["b10"], b3["judge"]["b01"]) == (11, 7)
    ch = r["by_channel"]
    assert (ch["SPOTLIGHT|direct (user prompt)"]["b0_judge"], ch["SPOTLIGHT|direct (user prompt)"]["arm_judge"]) == (46, 22)
    assert (ch["SPOTLIGHT|indirect (context)"]["b0_judge"], ch["SPOTLIGHT|indirect (context)"]["arm_judge"]) == (21, 21)
