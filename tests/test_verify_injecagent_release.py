"""Checks for scripts/verify_injecagent_release.py. Offline: synthetic release files in tmp_path, and the committed map.
The real checkout is not needed; the verifier's comparison and write gate are tested on their own."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("verify_release", ROOT / "scripts" / "verify_injecagent_release.py")
V = importlib.util.module_from_spec(_spec)
sys.modules["verify_release"] = V
_spec.loader.exec_module(V)


def _rec(user_tool, attacker_tools, attacker_text, user_text):
    return {"User Tool": user_tool, "Attacker Tools": attacker_tools,
            "Attacker Instruction": attacker_text, "User Instruction": user_text}


def _release(tmp_path):
    rel = tmp_path / "rel"
    (rel / "data").mkdir(parents=True)
    dh = [_rec("UT0", ["AT0"], "steal the key", "read my mail"), _rec("UT1", ["AT1"], "unlock door", "fetch price")]
    ds = [_rec("UT2", ["AT2"], "send data out", "summarise notes")]
    (rel / "data/test_cases_dh_base.json").write_text(json.dumps(dh))
    (rel / "data/test_cases_ds_base.json").write_text(json.dumps(ds))
    (rel / "data/tools.json").write_text(json.dumps([{"name": "x"}]))
    return rel


def _pins(rel):
    return {name: hashlib.sha256((rel / p).read_bytes()).hexdigest() for name, p in V.PIN_FILES.items()}


def _episodes(ids_tools):
    return [{"case_id": cid, "arm": "A0", "user_tool": ut, "attacker_tools": at} for cid, ut, at in ids_tools]


# ---------- pins ----------

def test_pins_match_when_the_files_are_the_pinned_ones(tmp_path):
    rel = _release(tmp_path)
    rows = V.check_pins(rel, _pins(rel))
    assert [r["match"] for r in rows] == [True, True, True]


def test_a_changed_file_is_a_pin_mismatch(tmp_path):
    rel = _release(tmp_path)
    pins = _pins(rel)
    (rel / "data/tools.json").write_text(json.dumps([{"name": "changed"}]))
    rows = {r["pin"]: r["match"] for r in V.check_pins(rel, pins)}
    assert rows == {"dh": True, "ds": True, "tools": False}


# ---------- mapping and identifier ----------

def test_mapping_uses_the_zero_based_index_and_the_attacker_text_hash(tmp_path):
    rel = _release(tmp_path)
    eps = _episodes([("dh-0000", "UT0", ["AT0"]), ("dh-0001", "UT1", ["AT1"]), ("ds-0000", "UT2", ["AT2"])])
    rows, problems = V.map_cases(rel, ["dh-0000", "dh-0001", "ds-0000"], eps)
    assert problems == [] and len(rows) == 3
    first = rows[0]
    assert first["release_index"] == 0
    assert first["attacker_instruction_sha256"] == hashlib.sha256("steal the key".encode()).hexdigest()
    assert first["user_instruction_sha256"] == hashlib.sha256("read my mail".encode()).hexdigest()
    assert first["attacker_instruction_sha256"] != first["user_instruction_sha256"]


def test_a_tool_mismatch_is_a_problem(tmp_path):
    rel = _release(tmp_path)
    eps = _episodes([("dh-0000", "WRONG", ["AT0"])])
    rows, problems = V.map_cases(rel, ["dh-0000"], eps)
    assert rows == [] and len(problems) == 1 and "does not match" in problems[0]


def test_an_index_outside_the_file_is_a_problem(tmp_path):
    rel = _release(tmp_path)
    rows, problems = V.map_cases(rel, ["dh-0099"], _episodes([("dh-0099", "UT0", ["AT0"])]))
    assert rows == [] and "outside" in problems[0]


def test_a_case_without_an_a0_episode_is_a_problem(tmp_path):
    rel = _release(tmp_path)
    rows, problems = V.map_cases(rel, ["dh-0000"], [])
    assert rows == [] and "no A0 episode" in problems[0]


# ---------- comparison with the committed map ----------

def _doc(hashes):
    return {"status": "DRAFT, NOT FROZEN", "pins": [], "n_cases": len(hashes),
            "cases": [{"case_id": f"c{i}", "attacker_instruction_sha256": h} for i, h in enumerate(hashes)]}


def test_identical_maps_have_no_differences():
    d = _doc(["aa", "bb"])
    assert V.diff_maps(d, json.loads(json.dumps(d))) == []


def test_one_changed_hash_is_named_with_its_case_and_field():
    diffs = V.diff_maps(_doc(["aa", "bb"]), _doc(["aa", "XX"]))
    assert diffs == ["c1: differs in attacker_instruction_sha256"]


def test_a_missing_or_extra_case_is_reported_both_ways():
    short = _doc(["aa"])
    long = _doc(["aa", "bb"])
    assert any("in the committed map, not produced" in d for d in V.diff_maps(long, short))
    assert any("produced by the release, not in the committed map" in d for d in V.diff_maps(short, long))


def test_a_top_level_change_is_reported():
    a = _doc(["aa"])
    b = dict(a, status="FROZEN")
    assert V.diff_maps(a, b) == ["top-level 'status' differs"]


def test_the_committed_map_is_internally_consistent_and_complete():
    committed = json.loads(V.OUT.read_text())
    assert V.diff_maps(committed, committed) == []
    assert committed["n_cases"] == 186 and len(committed["cases"]) == 186
    assert all(p["match"] for p in committed["pins"])


# ---------- write gate ----------

def test_without_write_the_committed_file_is_never_touched(tmp_path, monkeypatch):
    rel = _release(tmp_path)
    committed = tmp_path / "map.json"
    fresh = _doc(["aa"])
    committed.write_text(json.dumps(_doc(["zz"])))  # differs from the fresh map
    monkeypatch.setattr(V, "build_map", lambda *a, **k: (fresh, []))
    before = committed.read_text()
    assert V.run(rel, write=False, committed_path=committed) == 1
    assert committed.read_text() == before


def test_with_write_the_map_is_written_only_when_all_checks_pass(tmp_path, monkeypatch):
    rel = _release(tmp_path)
    committed = tmp_path / "map.json"
    fresh = _doc(["aa"])
    committed.write_text(json.dumps(_doc(["zz"])))
    monkeypatch.setattr(V, "build_map", lambda *a, **k: (fresh, []))
    assert V.run(rel, write=True, committed_path=committed) == 1  # differs: refuse even with --write
    assert json.loads(committed.read_text()) == _doc(["zz"])
    committed.write_text(json.dumps(fresh))
    assert V.run(rel, write=True, committed_path=committed) == 0  # identical: writes


def test_a_failed_check_writes_nothing_even_with_write(tmp_path, monkeypatch):
    rel = _release(tmp_path)
    committed = tmp_path / "map.json"
    committed.write_text(json.dumps(_doc(["aa"])))
    monkeypatch.setattr(V, "build_map", lambda *a, **k: (_doc(["aa"]), ["pin dh: differs"]))
    before = committed.read_text()
    assert V.run(rel, write=True, committed_path=committed) == 1
    assert committed.read_text() == before


def test_without_write_an_identical_map_is_not_rewritten_either(tmp_path, monkeypatch):
    # Same content, different bytes (no indentation): a rewrite would change the file, so this catches an always-write.
    rel = _release(tmp_path)
    committed = tmp_path / "map.json"
    fresh = _doc(["aa"])
    committed.write_text(json.dumps(fresh))
    monkeypatch.setattr(V, "build_map", lambda *a, **k: (fresh, []))
    before = committed.read_text()
    assert V.run(rel, write=False, committed_path=committed) == 0
    assert committed.read_text() == before
