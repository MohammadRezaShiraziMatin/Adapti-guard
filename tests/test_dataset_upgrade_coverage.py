"""Coverage-design and power checks for attack-pack v4 (Stage 2). No dataset examples are generated here."""

import importlib.util
import json
import math
from pathlib import Path
from statistics import NormalDist

import pytest

from adapti_guard.data.attack_schema_v4 import CATEGORY_RULES, CATEGORIES, FAMILY_CATEGORY

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "coverage_matrix", ROOT / "scripts" / "dataset_upgrade" / "coverage_matrix.py"
)
coverage = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(coverage)

COMMITTED_POWER = ROOT / "docs" / "dataset_upgrade" / "generated" / "power_multiturn_v4.json"


# --------------------------------------------------------------------------------------------
# Independent power implementation: log-space binomial terms and a direct z-statistic. It shares
# no code with coverage_matrix.py, so agreement between the two is a real check.
# --------------------------------------------------------------------------------------------

def _log_binom_pmf(n: int, k: int, p: float) -> float:
    log_choose = math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
    return math.exp(log_choose + k * math.log(p) + (n - k) * math.log1p(-p))


def _independent_power(n: int, p1: float, p2: float, alpha: float = 0.05) -> float:
    critical = NormalDist().inv_cdf(1 - alpha / 2)
    total = 0.0
    for x1 in range(n + 1):
        for x2 in range(n + 1):
            pooled = (x1 + x2) / (2 * n)
            spread = math.sqrt(pooled * (1 - pooled) * (2 / n))
            if spread == 0.0:
                continue
            z = (x1 / n - x2 / n) / spread
            if abs(z) > critical:
                total += _log_binom_pmf(n, x1, p1) * _log_binom_pmf(n, x2, p2)
    return total


def _independent_min_n(p1: float, p2: float, target: float = 0.80) -> int:
    for n in range(2, 300):
        if _independent_power(n, p1, p2) >= target:
            return n
    raise AssertionError("no n found")


# --------------------------------------------------------------------------------------------
# Existing design checks (unchanged assertions)
# --------------------------------------------------------------------------------------------

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


def test_totals_match_the_documented_design():
    rows = coverage.build_rows()
    assert len({(r["family"], r["injection_channel"], r["turn_type"]) for r in rows}) == 28
    assert sum(r["attacks_target"] for r in rows) == 396
    assert sum(r["counterparts_target"] for r in rows) == 396
    single = sum(r["attacks_target"] for r in rows if r["turn_type"] == "single")
    multi = sum(r["attacks_target"] for r in rows if r["turn_type"] == "multi")
    assert (single, multi) == (276, 120)


# --------------------------------------------------------------------------------------------
# Finding 5 (registry) and allocation regressions
# --------------------------------------------------------------------------------------------

def test_generator_families_agree_with_schema_registry():
    for family, (category, _cells, _per_cell) in coverage.FAMILIES.items():
        assert FAMILY_CATEGORY[family] == category


def test_generator_rejects_family_category_disagreement(monkeypatch):
    category, cells, per_cell = coverage.FAMILIES["EMAIL_INJECTION"]
    monkeypatch.setitem(coverage.FAMILIES, "EMAIL_INJECTION", ("rag_document_injection", cells, per_cell))
    with pytest.raises(ValueError, match="disagrees with the schema registry"):
        coverage.build_rows()


def test_generator_rejects_per_cell_target_that_does_not_divide_across_styles(monkeypatch):
    category, cells, _ = coverage.FAMILIES["EMAIL_INJECTION"]
    monkeypatch.setitem(coverage.FAMILIES, "EMAIL_INJECTION", (category, cells, 10))
    with pytest.raises(ValueError, match="does not divide"):
        coverage.build_rows()


def test_generator_rejects_channel_not_allowed_for_category(monkeypatch):
    category, _cells, per_cell = coverage.FAMILIES["EMAIL_INJECTION"]
    monkeypatch.setitem(coverage.FAMILIES, "EMAIL_INJECTION", (category, [("user_turn", "single")], per_cell))
    with pytest.raises(ValueError, match="is not allowed"):
        coverage.build_rows()


# --------------------------------------------------------------------------------------------
# Finding 6: power and sample size. The earlier value 58 fails the stated threshold.
# --------------------------------------------------------------------------------------------

def test_exact_power_at_58_is_below_threshold_for_primary_effect():
    # Regression: 58 per arm does not reach 80% power for 0.50 vs 0.25 under the stated test.
    assert _independent_power(58, 0.50, 0.25) < 0.80
    assert coverage.exact_power(58, 0.50, 0.25) < 0.80


def test_exact_minimum_sample_size_for_primary_effect_is_59():
    assert _independent_min_n(0.50, 0.25) == 59
    assert coverage.exact_min_n(0.50, 0.25) == 59


def test_generator_and_independent_implementation_agree_on_power():
    for n, p1, p2 in [(50, 0.50, 0.25), (58, 0.50, 0.25), (59, 0.50, 0.25), (60, 0.50, 0.25), (80, 0.40, 0.20)]:
        generator = coverage.exact_power(n, p1, p2)
        independent = _independent_power(n, p1, p2)
        assert generator == pytest.approx(independent, abs=1e-9), (n, p1, p2)


def test_power_values_match_documented_figures():
    assert round(_independent_power(50, 0.50, 0.25), 3) == 0.745
    assert round(_independent_power(59, 0.50, 0.25), 3) == 0.809
    assert round(_independent_power(60, 0.50, 0.25), 3) == 0.818


def test_floor_of_fifty_does_not_reach_threshold_for_primary_effect():
    assert coverage.FLOOR_PER_MULTI_FAMILY == 50
    assert _independent_power(50, 0.50, 0.25) < 0.80


def test_design_target_of_sixty_reaches_threshold_for_primary_effect():
    assert coverage.DESIGN_TARGET_PER_MULTI_FAMILY == 60
    assert _independent_power(60, 0.50, 0.25) >= 0.80


def test_normal_approximation_is_reference_only_and_not_the_design_basis():
    approx = coverage.normal_approx_n(0.50, 0.25)
    assert approx == pytest.approx(57.673, abs=1e-3)
    assert math.ceil(approx) == 58 and _independent_power(58, 0.50, 0.25) < 0.80


def test_committed_power_artifact_matches_exact_computation():
    table = json.loads(COMMITTED_POWER.read_text(encoding="utf-8"))
    assert table["test"].startswith("two-sided pooled two-proportion z-test")
    assert table["alpha"] == 0.05 and table["power_target"] == 0.80
    primary = next(r for r in table["rows"] if r["p_baseline"] == 0.50 and r["p_treated"] == 0.25)
    assert primary["exact_min_n_power_0.80"] == 59
    assert primary["exact_power_at_min_n"] == pytest.approx(_independent_power(59, 0.50, 0.25), abs=1e-4)
    assert primary["exact_power_at_n_minus_1"] == pytest.approx(_independent_power(58, 0.50, 0.25), abs=1e-4)


def test_committed_power_artifact_documents_assumptions_and_multiplicity():
    table = json.loads(COMMITTED_POWER.read_text(encoding="utf-8"))
    text = " ".join(table["assumptions"]).lower()
    assert "independent" in text
    assert "multiplicity" in text
    assert "does not establish" in text


@pytest.mark.parametrize("p1,p2", [(0.50, 0.30), (0.40, 0.20), (0.30, 0.15)])
def test_secondary_effect_minimum_n_matches_independent_scan(p1, p2):
    assert coverage.exact_min_n(p1, p2) == _independent_min_n(p1, p2)
