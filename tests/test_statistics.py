"""Statistical helper tests."""

from src.adapti_guard.evaluation.statistics import bootstrap_ci, mcnemar_test


def test_bootstrap_ci_bounds():
    values = [0.1, 0.2, 0.3, 0.4, 0.5]
    point, low, high = bootstrap_ci(values, n_bootstrap=500, seed=1)
    assert low <= point <= high


def test_mcnemar_no_difference():
    a = [True, False, True, False]
    b = [True, False, True, False]
    result = mcnemar_test(a, b)
    assert result["p_value"] == 1.0
