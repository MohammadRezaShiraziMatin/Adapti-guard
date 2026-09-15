"""Offline tests for P1 mechanism candidate pack.

No LLM/API. Does not modify frozen packs.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from adapti_guard.core.episode import ContextBuilder, EpisodeInput

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "datasets" / "candidates" / "p1_mechanism_v1"
BUILDER = ROOT / "scripts" / "build_p1_mechanism_v1_pack.py"
VALIDATOR = ROOT / "scripts" / "validate_p1_mechanism_pack.py"

FROZEN_HASHES = {
    ROOT
    / "datasets/frozen/eval_v1/dataset.jsonl": "27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24",
    ROOT
    / "results/common_attack_stream.json": "d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47",
    ROOT
    / "datasets/frozen/vnext_confirm_v1/dataset.jsonl": "523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518",
    ROOT
    / "datasets/frozen/phase1_confirm_v1/dataset.jsonl": "c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01",
}


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_p1_mechanism_v1_pack", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _rows() -> list[dict]:
    return [
        json.loads(line)
        for line in (PACK / "dataset.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_pack_artifacts_exist():
    for name in (
        "dataset.jsonl",
        "manifest.json",
        "hashes.sha256",
        "DATASET_CARD.md",
        "README.md",
    ):
        assert (PACK / name).is_file(), name


def test_counts_and_family_coverage():
    rows = _rows()
    assert len(rows) == 96
    attacks = [r for r in rows if r["label"] == "attack"]
    benigns = [r for r in rows if r["label"] == "benign"]
    assert len(attacks) == 44
    assert len(benigns) == 52
    counts = Counter(r["metadata"]["family"] for r in attacks)
    assert counts["C4"] == 0 if "C4" in counts else True
    for fam in _load_builder().IN_SCOPE_FAMILIES:
        assert counts[fam] == 2, fam
    assert sum(1 for r in benigns if r["metadata"].get("hard_negative")) == 8


def test_benign_twins_bidirectional():
    rows = _rows()
    by_id = {r["id"]: r for r in rows}
    for r in rows:
        if r["label"] != "attack":
            continue
        twin = r["metadata"]["benign_twin"]
        assert by_id[twin]["metadata"]["attack_twin"] == r["id"]


def test_manifest_candidate_not_live():
    man = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
    assert man["status"] == "CANDIDATE"
    assert man["live_evaluated"] is False
    assert man["out_of_scope_families"] == ["C4"]
    digest = hashlib.sha256((PACK / "dataset.jsonl").read_bytes()).hexdigest()
    assert man["dataset_sha256"] == digest
    listed = (PACK / "hashes.sha256").read_text(encoding="utf-8").split()[0]
    assert listed == digest


def test_builder_is_deterministic():
    mod = _load_builder()
    rows1 = mod.assemble()
    rows2 = mod.assemble()
    assert json.dumps(rows1, sort_keys=True) == json.dumps(rows2, sort_keys=True)


def test_validator_script_ok():
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_episode_input_accepts_runtime_fields_only():
    rows = _rows()
    atk = next(r for r in rows if r["label"] == "attack" and r.get("tool_call"))
    builder = ContextBuilder()
    # Gold keys must not enter EpisodeInput; pass runtime fields only.
    runtime = {
        "prompt": atk["prompt"],
        "context": atk.get("context") or "",
        "tool_call": atk.get("tool_call"),
    }
    ctx = builder.build(runtime)
    assert ctx.prompt == atk["prompt"]
    assert ctx.privileged_tool is True
    # Dataclass form also works when privilege is inferred from tool_name.
    tc = atk["tool_call"]
    inp = EpisodeInput(
        prompt=atk["prompt"],
        context=atk.get("context") or "",
        tool_name=tc["name"],
        tool_arguments=dict(tc.get("arguments") or {}),
    )
    assert builder.build(inp).privileged_tool is True


def test_no_dan_surface_in_pack():
    for r in _rows():
        blob = f"{r.get('prompt', '')} {r.get('context', '')}".lower()
        assert "you are now dan" not in blob
        assert "do anything now" not in blob


def test_sequential_families_marked_frozen_context():
    for r in _rows():
        if r["label"] != "attack":
            continue
        if r["metadata"]["family"] in {"C1", "C2", "C3"}:
            assert r["metadata"]["sequential_representation"] == "frozen_context"
            assert (r.get("context") or "").strip()


def test_frozen_artifacts_unchanged():
    for path, expected in FROZEN_HASHES.items():
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        assert got == expected, path


def test_candidate_not_under_frozen_tree():
    assert "datasets/candidates/" in str(PACK)
    assert "datasets/frozen/" not in str(PACK.resolve())
