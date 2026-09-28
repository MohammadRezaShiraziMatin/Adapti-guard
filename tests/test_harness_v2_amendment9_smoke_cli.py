"""Amendment 9 — llama smoke schedule from AMENDMENT9_DECISIONS.md."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.amendment9_smoke_schedule import (  # noqa: E402
    amendment9_llama_smoke_schedule,
    parse_amendment9_llama_smoke_episode_ids,
)
from scripts.run_harness_v2_pilot import (  # noqa: E402
    _episode_id,
    pilot_episode_schedule,
    pilot_schedule_for_run,
)


def _expected_ids_from_decisions() -> list[str]:
    decisions = ROOT / "experiments/harness_v2/AMENDMENT9_DECISIONS.md"
    return parse_amendment9_llama_smoke_episode_ids(decisions)


def test_smoke_parser_returns_exactly_twenty_ordered_episode_ids():
    ids = _expected_ids_from_decisions()
    assert len(ids) == 20
    assert ids[0] == "indirect_retrieved_doc_v1/i0/llama/A0"
    assert ids[1] == "indirect_retrieved_doc_v1/i0/llama/B3"
    assert ids[-1] == "benign_create_record_v1/i0/llama/B3"


def test_amendment9_llama_smoke_schedule_matches_decisions_table():
    expected_ids = _expected_ids_from_decisions()
    schedule = amendment9_llama_smoke_schedule(
        decisions_md=ROOT / "experiments/harness_v2/AMENDMENT9_DECISIONS.md"
    )
    assert len(schedule) == 20
    got_ids = [_episode_id(row) for row in schedule]
    assert got_ids == expected_ids
    for row in schedule:
        assert row["family"] == "llama"
        assert row["instance_index"] == 0
        assert row["condition"] in ("A0", "B3")


def test_pilot_schedule_for_run_smoke_flag_selects_only_smoke_episodes():
    full = pilot_episode_schedule()
    smoke = pilot_schedule_for_run(amendment9_llama_smoke=True)
    assert len(full) > len(smoke)
    assert len(smoke) == 20
    smoke_ids = {_episode_id(r) for r in smoke}
    expected = set(_expected_ids_from_decisions())
    assert smoke_ids == expected
    assert [_episode_id(r) for r in smoke] == _expected_ids_from_decisions()


def test_cli_amendment9_llama_smoke_flag_exists():
    parser = argparse.ArgumentParser()
    parser.add_argument("--amendment9-llama-smoke", action="store_true")
    ns = parser.parse_args(["--amendment9-llama-smoke"])
    assert ns.amendment9_llama_smoke is True
