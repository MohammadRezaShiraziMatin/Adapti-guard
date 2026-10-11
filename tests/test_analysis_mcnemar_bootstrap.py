"""Checks for scripts/analysis_mcnemar_bootstrap.py. The McNemar expected values come from SciPy's binomtest, an independent
route. The bootstrap checks use fixed seeds and cases whose answer is known in advance."""
import importlib.util
import random
import sys
from pathlib import Path

import pytest
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("analysis", ROOT / "scripts" / "analysis_mcnemar_bootstrap.py")
A = importlib.util.module_from_spec(_spec)
sys.modules["analysis"] = A
_spec.loader.exec_module(A)


# ---------- exact McNemar ----------

@pytest.mark.parametrize("b,c", [(b, c) for b in range(0, 13) for c in range(0, 13)])
def test_exact_mcnemar_matches_scipy_binomtest(b, c):
    expected = binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
    assert abs(A.exact_mcnemar_p(b, c) - expected) < 1e-12


def test_exact_mcnemar_hand_values():
    assert A.exact_mcnemar_p(0, 0) == 1.0
    assert A.exact_mcnemar_p(5, 5) == 1.0
    assert A.exact_mcnemar_p(0, 10) == pytest.approx(2 / 1024)
    assert A.exact_mcnemar_p(10, 0) == pytest.approx(2 / 1024)


def test_exact_mcnemar_is_symmetric_and_bounded():
    for b, c in [(3, 9), (21, 3), (22, 3)]:
        p = A.exact_mcnemar_p(b, c)
        assert p == A.exact_mcnemar_p(c, b)
        assert 0 < p <= 1


def test_exact_mcnemar_refuses_negative_counts():
    with pytest.raises(ValueError):
        A.exact_mcnemar_p(-1, 2)


def test_discordance_counts_the_two_directions():
    triples = [("c1", True, False), ("c2", True, False), ("c3", False, True), ("c4", True, True), ("c5", False, False)]
    assert A.discordance(triples) == (2, 1)


@pytest.mark.parametrize("bad", [None, 0, 1])
def test_discordance_refuses_non_bool_outcomes(bad):
    with pytest.raises(ValueError, match="must be a bool"):
        A.discordance([("c1", bad, True)])
    with pytest.raises(ValueError, match="must be a bool"):
        A.discordance([("c1", True, bad)])


def test_discordance_refuses_pairs_without_case_id():
    with pytest.raises(ValueError, match="triples"):
        A.discordance([(True, False)])


def test_end_to_end_pairing_discordance_and_mcnemar_with_hand_derived_values():
    # 15 cases. Hand count: cases 0-1 are A0 only (b = 2); cases 2-11 are SPOT only (c = 10); cases 12-14 are concordant.
    # Exact two-sided McNemar with n = b + c = 12 and k = min(b, c) = 2:
    #   tail = (C(12,0) + C(12,1) + C(12,2)) / 2^12 = (1 + 12 + 66) / 4096 = 79 / 4096
    #   p = 2 * tail = 158 / 4096 = 0.03857421875
    a0 = [(f"c{i:02d}", i < 2) for i in range(15)]
    spot = [(f"c{i:02d}", 2 <= i < 12) for i in range(15)]
    pairs = A.pair_by_case_id(a0, spot)
    assert A.discordance(pairs) == (2, 10)
    assert A.exact_mcnemar_p(*A.discordance(pairs)) == pytest.approx(158 / 4096, abs=1e-15)


def test_end_to_end_result_does_not_depend_on_input_order():
    a0 = [(f"c{i:02d}", i < 2) for i in range(15)]
    spot = [(f"c{i:02d}", 2 <= i < 12) for i in range(15)]
    shuffled_spot = list(reversed(spot))
    assert A.discordance(A.pair_by_case_id(a0, shuffled_spot)) == A.discordance(A.pair_by_case_id(a0, spot))


def test_end_to_end_pipeline_refuses_an_errored_episode():
    a0 = [("c1", True), ("c2", None)]  # c2 errored
    spot = [("c1", False), ("c2", False)]
    with pytest.raises(ValueError, match="must be a bool"):
        A.discordance(A.pair_by_case_id(a0, spot))


@pytest.mark.parametrize("bad", [None, 0, 1])
def test_bootstrap_refuses_non_bool_outcomes(bad):
    clusters = [[(True, bad)], [(False, False)]]
    with pytest.raises(ValueError, match="must be a bool"):
        A.cluster_bootstrap_interval(clusters, resamples=10, seed=1, level=0.95)
    clusters = [[(bad, False)], [(False, False)]]
    with pytest.raises(ValueError, match="must be a bool"):
        A.cluster_bootstrap_interval(clusters, resamples=10, seed=1, level=0.95)


# ---------- cluster bootstrap ----------

def _clusters():
    # cluster 1: 10 cases, A0 event in 8, SPOT event in 3 -> diff sum 5
    c1 = [(i < 8, i < 3) for i in range(10)]
    # cluster 2: 1 case, no difference
    c2 = [(False, False)]
    return [c1, c2]


def test_point_estimate_pools_cases_not_clusters():
    point, lower, upper = A.cluster_bootstrap_interval(_clusters(), resamples=200, seed=1, level=0.95)
    assert point == pytest.approx(5 / 11)
    assert lower <= point <= upper


def test_same_seed_gives_the_same_interval():
    a = A.cluster_bootstrap_interval(_clusters(), resamples=500, seed=7, level=0.95)
    b = A.cluster_bootstrap_interval(_clusters(), resamples=500, seed=7, level=0.95)
    assert a == b


def test_seed_changes_the_resamples_not_the_point_estimate():
    # The endpoints of a percentile interval are discrete here, so two seeds may give equal bounds; the point must not change.
    a = A.cluster_bootstrap_interval(_clusters(), resamples=500, seed=7, level=0.95)
    c = A.cluster_bootstrap_interval(_clusters(), resamples=500, seed=8, level=0.95)
    assert a[0] == c[0]


def test_all_concordant_gives_zero_interval():
    clusters = [[(True, True)] * 4, [(False, False)] * 2]
    assert A.cluster_bootstrap_interval(clusters, resamples=50, seed=3, level=0.95) == (0.0, 0.0, 0.0)


def test_every_case_a0_event_and_no_spot_event_gives_one():
    clusters = [[(True, False)] * 3, [(True, False)] * 5]
    assert A.cluster_bootstrap_interval(clusters, resamples=50, seed=3, level=0.95) == (1.0, 1.0, 1.0)


def test_interval_excludes_zero_when_the_reduction_is_clear():
    clusters = [[(True, False)] * 6 + [(False, False)] * 2 for _ in range(10)]
    point, lower, upper = A.cluster_bootstrap_interval(clusters, resamples=1000, seed=11, level=0.95)
    assert point == pytest.approx(0.75)  # 6 of 8 A0 events, no SPOT events, in every cluster
    assert lower > 0


def test_global_random_state_is_not_touched():
    random.seed(12345)
    before = random.random()
    random.seed(12345)
    A.cluster_bootstrap_interval(_clusters(), resamples=100, seed=99, level=0.95)
    assert random.random() == before


@pytest.mark.parametrize("kwargs", [
    {"resamples": 0, "seed": 1, "level": 0.95},
    {"resamples": 10, "seed": 1.5, "level": 0.95},
    {"resamples": 10, "seed": 1, "level": 1.0},
    {"resamples": 10, "seed": 1, "level": 0.0},
])
def test_invalid_bootstrap_settings_are_refused(kwargs):
    with pytest.raises(ValueError):
        A.cluster_bootstrap_interval(_clusters(), **kwargs)


@pytest.mark.parametrize("missing", ["resamples", "seed", "level"])
def test_bootstrap_parameters_have_no_defaults(missing):
    # The protocol fixes these in advance; the function must not choose them.
    kwargs = {"resamples": 10, "seed": 1, "level": 0.95}
    del kwargs[missing]
    with pytest.raises(TypeError):
        A.cluster_bootstrap_interval(_clusters(), **kwargs)


def test_empty_cluster_is_refused():
    with pytest.raises(ValueError):
        A.cluster_bootstrap_interval([[(True, False)], []], resamples=10, seed=1, level=0.95)


def test_resampling_is_by_cluster_not_by_case():
    # Two clusters, each internally identical: all +1 and all -1. Point estimate 0.
    # Drawing whole clusters gives pooled statistics -1 (both clusters are the -1 kind), 0 (one of each) and +1 (both
    # the +1 kind), with probabilities 1/4, 1/2, 1/4, so the 95% percentile interval is (-1, +1). Resampling individual
    # cases would give a much narrower interval (about +/-0.1).
    clusters = [[(True, False)] * 10, [(False, True)] * 10]
    point, lower, upper = A.cluster_bootstrap_interval(clusters, resamples=2000, seed=5, level=0.95)
    assert point == pytest.approx(0.0)
    assert lower == pytest.approx(-1.0)
    assert upper == pytest.approx(1.0)


# ---------- pairing by case_id ----------

def test_pairing_is_by_case_id_not_by_position():
    a0 = [("c2", True), ("c1", False)]
    spot = [("c1", True), ("c2", False)]  # same ids, opposite order
    assert A.pair_by_case_id(a0, spot) == [("c1", False, True), ("c2", True, False)]


@pytest.mark.parametrize("a0,spot,message", [
    ([("c1", True), ("c2", False)], [("c1", True)], "different case_id sets"),
    ([("c1", True)], [("c1", True), ("c2", False)], "different case_id sets"),
    ([("c1", True), ("c1", False)], [("c1", True)], "duplicate case_id"),
    ([("c1", True)], [("c1", True), ("c1", True)], "duplicate case_id"),
    ([("c1", None)], [("c1", True)], "must be a bool"),
    ([("c1", True)], [("c1", None)], "must be a bool"),
    ([("c1", 0)], [("c1", True)], "must be a bool"),
    ([("c1", 1)], [("c1", True)], "must be a bool"),
    ([("", True)], [("", True)], "non-empty string"),
])
def test_pairing_refuses_missing_duplicate_and_non_bool_outcomes(a0, spot, message):
    with pytest.raises(ValueError, match=message):
        A.pair_by_case_id(a0, spot)


# ---------- clusters by attacker instruction ----------

def test_clusters_group_cases_by_attacker_instruction_in_sorted_order():
    pairs = [("c1", True, False), ("c2", False, False), ("c3", True, True)]
    instruction_of = {"c1": "instr-b", "c2": "instr-a", "c3": "instr-b"}
    clusters = A.attacker_instruction_clusters(pairs, instruction_of)
    assert clusters == [[(False, False)], [(True, False), (True, True)]]  # instr-a first, then instr-b


def test_clusters_refuse_a_case_without_an_instruction():
    with pytest.raises(ValueError, match="no attacker instruction"):
        A.attacker_instruction_clusters([("c1", True, False)], {})


# ---------- Holm ----------

@pytest.mark.parametrize("pvals,expected", [
    ([0.01, 0.03], [True, True]),      # 0.01 <= 0.025, then 0.03 <= 0.05
    ([0.03, 0.04], [False, False]),    # smallest already above 0.025: nothing rejected
    ([0.02, 0.06], [True, False]),     # second is above 0.05
    ([0.5, 0.01], [False, True]),      # order of the input does not matter
    ([0.025, 0.5], [True, False]),     # boundary is inclusive
    ([0.0251, 0.04], [False, False]),  # step 1 fails, so step 2 is not tested even though 0.04 <= 0.05
])
def test_holm_two_targets_hand_values(pvals, expected):
    assert A.holm(pvals, 0.05) == expected


@pytest.mark.parametrize("pvals,alpha", [([], 0.05), ([0.1], 0.0), ([0.1], 1.0), ([1.5], 0.05), ([-0.1], 0.05)])
def test_holm_refuses_bad_inputs(pvals, alpha):
    with pytest.raises(ValueError):
        A.holm(pvals, alpha)


# ---------- settings: bool and cluster count ----------

@pytest.mark.parametrize("kwargs", [
    {"resamples": True, "seed": 1, "level": 0.95},
    {"resamples": 10, "seed": True, "level": 0.95},
    {"resamples": 10, "seed": 1, "level": True},
])
def test_bool_is_not_accepted_as_an_integer_or_level(kwargs):
    with pytest.raises(ValueError):
        A.cluster_bootstrap_interval(_clusters(), **kwargs)


def test_one_cluster_is_refused():
    with pytest.raises(ValueError, match="at least two clusters"):
        A.cluster_bootstrap_interval([[(True, False), (False, False)]], resamples=10, seed=1, level=0.95)


# ---------- quantile rule ----------

def test_percentile_bounds_are_order_statistics_at_the_documented_indices():
    stats = list(range(1000))  # already sorted; value equals 0-based index
    assert A._order_statistic_bounds(stats, 0.95) == (25, 974)  # 26th and 975th smallest
    assert A._order_statistic_bounds(list(range(20)), 0.90) == (1, 18)  # floor(0.05*20)=1, ceil(0.95*20)-1=18


def test_percentile_bounds_use_sorted_input():
    assert A._order_statistic_bounds([9, 3, 7, 1, 5] * 200, 0.95) == (1, 9)


# ---------- unresolved episodes (errored: None) are excluded explicitly and counted ----------

def test_a_none_in_either_arm_excludes_the_case_from_both_arms_and_reports_it():
    a0 = [("c1", True), ("c2", None), ("c3", False)]
    spot = [("c1", False), ("c2", True), ("c3", False)]
    pairs, excluded = A.resolved_pairs(a0, spot)
    assert pairs == [("c1", True, False), ("c3", False, False)]
    assert excluded == ["c2"]


def test_none_in_the_spot_arm_is_excluded_too():
    pairs, excluded = A.resolved_pairs([("c1", True)], [("c1", None)])
    assert pairs == [] and excluded == ["c1"]


def test_other_non_bool_outcomes_are_still_refused():
    for bad in (0, 1, "True", 1.0):
        with pytest.raises(ValueError, match="must be a bool"):
            A.resolved_pairs([("c1", bad)], [("c1", True)])


def test_resolved_pairs_still_refuses_mismatched_case_sets():
    with pytest.raises(ValueError, match="different case_id sets"):
        A.resolved_pairs([("c1", True)], [("c2", True)])


def test_the_strict_pairing_still_refuses_none():
    with pytest.raises(ValueError, match="must be a bool"):
        A.pair_by_case_id([("c1", None)], [("c1", True)])


@pytest.mark.parametrize("unresolved,total,exceeds", [(0, 150, False), (7, 150, False), (8, 150, True),
                                                       (1, 20, False), (2, 20, True), (2, 19, True)])
def test_error_rate_is_checked_strictly_above_the_five_percent_limit(unresolved, total, exceeds):
    # 1/20 = 0.05 is at the limit and does not exceed it; 2/20 = 0.10 does
    assert A.unresolved_rate_exceeds(unresolved, total, limit=0.05) is exceeds


def test_the_limit_is_an_explicit_argument_with_no_default():
    with pytest.raises(TypeError):
        A.unresolved_rate_exceeds(1, 20)


def test_a_launcher_style_503_episode_is_excluded_not_counted_as_no_attack():
    # the launcher writes None for an errored episode; a false would wrongly read as "no attack"
    episodes_a0 = [{"case_id": "c1", "arm": "A0", "executed_attacker_call": True, "error": None},
                   {"case_id": "c2", "arm": "A0", "executed_attacker_call": None, "error": "http 503"}]
    episodes_spot = [{"case_id": "c1", "arm": "SPOT_TOOL", "executed_attacker_call": False, "error": None},
                     {"case_id": "c2", "arm": "SPOT_TOOL", "executed_attacker_call": False, "error": None}]
    a0 = [(e["case_id"], e["executed_attacker_call"]) for e in episodes_a0]
    spot = [(e["case_id"], e["executed_attacker_call"]) for e in episodes_spot]
    pairs, excluded = A.resolved_pairs(a0, spot)
    assert pairs == [("c1", True, False)]
    assert excluded == ["c2"]
    assert A.unresolved_rate_exceeds(len(excluded), len(a0), limit=0.05) is True
