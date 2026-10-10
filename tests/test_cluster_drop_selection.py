"""Checks for scripts/cluster_drop_selection.py (protocol §3, S-A). Offline. Reads only committed files."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("cds", ROOT / "scripts" / "cluster_drop_selection.py")
C = importlib.util.module_from_spec(_spec)
sys.modules["cds"] = C
_spec.loader.exec_module(C)

KEYS = [f"k{i:02d}" for i in range(62)]


def _synthetic_map():
    return {f"case-{k}-{j}": k for k in KEYS for j in range(3)}


# ---------- selection ----------

def test_selection_is_deterministic_and_depends_on_the_seed():
    a = C.select_whole_clusters(KEYS, keep=50, seed=C.SEED)
    b = C.select_whole_clusters(KEYS, keep=50, seed=C.SEED)
    c = C.select_whole_clusters(KEYS, keep=50, seed=C.SEED + 1)
    assert a == b
    assert a != c
    assert len(a) == 50 and set(a) <= set(KEYS)


def test_selection_is_independent_of_input_order():
    shuffled = list(reversed(KEYS))
    assert C.select_whole_clusters(shuffled, keep=24, seed=C.SEED) == C.select_whole_clusters(KEYS, keep=24, seed=C.SEED)


def test_only_whole_clusters_are_retained():
    case_map = _synthetic_map()
    kept = C.select_whole_clusters(KEYS, keep=50, seed=C.SEED)
    retained = set(C.retained_case_ids(case_map, kept))
    assert len(retained) == 150
    for k in KEYS:
        members = {cid for cid, key in case_map.items() if key == k}
        inside = members & retained
        assert inside in (set(), members), f"cluster {k} is partly retained"


# ---------- same case set for every target and arm ----------

def test_cluster_keys_are_identical_for_llama_and_qwen():
    paths = [ROOT / "experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json",
             ROOT / "experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json"]
    maps = [C.clusters_from_episodes(json.loads(p.read_text())["episodes"]) for p in paths]
    assert maps[0] == maps[1]
    assert len(set(maps[0].values())) == 62


def test_same_retained_set_for_every_arm_and_target_order():
    ep = [{"case_id": f"c{i}", "arm": arm, "attacker_tools": [f"T{i % 4}"]}
          for i in range(8) for arm in ("A0", "SPOT_TOOL", "A0_REP")]
    forward = C.clusters_from_episodes(ep)
    backward = C.clusters_from_episodes(list(reversed(ep)))
    assert forward == backward


def test_a_case_with_different_attacker_tools_in_different_episodes_is_refused():
    ep = [{"case_id": "c1", "arm": "A0", "attacker_tools": ["X"]},
          {"case_id": "c1", "arm": "SPOT_TOOL", "attacker_tools": ["Y"]}]
    with pytest.raises(ValueError, match="different attacker tools"):
        C.clusters_from_episodes(ep)


def test_a_case_without_attacker_tools_is_refused():
    with pytest.raises(ValueError, match="no attacker tools"):
        C.clusters_from_episodes([{"case_id": "c1", "arm": "A0", "attacker_tools": []}])


# ---------- refusals ----------

@pytest.mark.parametrize("kwargs", [
    {"keep": True, "seed": 1},
    {"keep": 10, "seed": True},
    {"keep": 0, "seed": 1},
    {"keep": 63, "seed": 1},
])
def test_bad_keep_or_seed_is_refused(kwargs):
    with pytest.raises(ValueError):
        C.select_whole_clusters(KEYS, **kwargs)


def test_duplicate_or_empty_cluster_keys_are_refused():
    with pytest.raises(ValueError, match="unique"):
        C.select_whole_clusters(["a", "a"], keep=1, seed=1)
    with pytest.raises(ValueError, match="non-empty"):
        C.select_whole_clusters(["a", ""], keep=1, seed=1)


@pytest.mark.parametrize("missing", ["keep", "seed"])
def test_keep_and_seed_have_no_defaults(missing):
    kwargs = {"keep": 10, "seed": 1}
    del kwargs[missing]
    with pytest.raises(TypeError):
        C.select_whole_clusters(KEYS, **kwargs)


# ---------- committed record ----------

def test_counts_in_the_committed_record():
    rec = json.loads(C.RECORD.read_text())
    assert rec["seed"] == 20261001
    assert rec["n_clusters"] == 62 and rec["n_cases"] == 186
    assert len(rec["kept_clusters_n150"]) == 50 and len(rec["dropped_clusters_n150"]) == 12
    assert len(rec["retained_case_ids_n150"]) == 150
    assert len(rec["kept_clusters_gpt_n72"]) == 24 and len(rec["retained_case_ids_gpt_n72"]) == 72
    assert set(rec["retained_case_ids_gpt_n72"]) <= set(rec["retained_case_ids_n150"])


def test_committed_record_is_exactly_what_the_rule_produces():
    assert C.record_text(C.build_record()) == C.RECORD.read_text()


def test_record_sha256_is_the_value_written_in_the_protocol():
    sha = hashlib.sha256(C.RECORD.read_bytes()).hexdigest()
    protocol = (ROOT / "docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md").read_text()
    assert sha in protocol
