"""Coverage-design checks for attack-pack v4 (Stage 2). No dataset examples are generated here."""

import importlib.util
from pathlib import Path

from adapti_guard.data.attack_schema_v4 import CATEGORY_RULES, CATEGORIES

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "coverage_matrix", ROOT / "scripts" / "dataset_upgrade" / "coverage_matrix.py"
)
coverage = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(coverage)


def test_every_family_uses_a_known_category():
    for family, (category, _cells, _per_cell) in coverage.FAMILIES.items():
        assert category in CATEGORIES, family


def test_every_primary_cell_is_allowed_by_the_validator():
    for family, (category, cells, _per_cell) in coverage.FAMILIES.items():
        channels, turns = CATEGORY_RULES[category]
        for channel, turn in cells:
            assert channel in channels, (family, channel)
            assert turn in turns, (family, turn)


def test_single_cells_meet_minimum_of_ten_attacks():
    rows = coverage.build_rows()
    per_cell: dict[tuple, int] = {}
    for r in rows:
        key = (r["family"], r["injection_channel"], r["turn_type"])
        per_cell[key] = per_cell.get(key, 0) + r["attacks_target"]
    for key, count in per_cell.items():
        if key[2] == "single":
            assert count >= 10, key


def test_multi_turn_families_meet_floor_of_fifty():
    totals = coverage.totals(coverage.build_rows())
    for family in ("MULTI_TURN_PERSISTENCE", "MULTI_TURN_INJECTION"):
        assert totals[family]["attacks"] >= 50, family


def test_attack_and_counterpart_targets_are_one_to_one():
    rows = coverage.build_rows()
    assert sum(r["attacks_target"] for r in rows) == sum(r["counterparts_target"] for r in rows)


def test_each_style_is_represented_in_every_family():
    rows = coverage.build_rows()
    for family in coverage.FAMILIES:
        styles = {r["style"] for r in rows if r["family"] == family}
        assert styles == set(coverage.STYLES), family


def test_power_floor_is_below_design_target_and_documented():
    table = coverage.power_table()
    assert table["floor_per_multi_family"] == 50
    assert table["design_target_per_multi_family"] == 60
    assert coverage.n_per_arm(0.5, 0.25) == 58
