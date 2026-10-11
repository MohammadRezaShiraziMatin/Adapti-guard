"""The ledger reads the confirmatory results JSON when it exists, and formats each value as the manuscript states it.
Offline: a synthetic results file in a temp directory, and the check that nothing is added while no file exists."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location("ledger", ROOT / "scripts" / "build_number_ledger.py")
L = importlib.util.module_from_spec(_spec)
sys.modules["ledger"] = L
_spec.loader.exec_module(L)

RESULTS = {
    "H1": {"targets": {"gpt": {"events": 0, "n_cases": 72, "binomial_p": 0.024936, "clopper_pearson_95": [0.0, 0.0499]}}},
    "H2": {"targets": {"llama": {"a0_only": 10, "spot_only": 0, "mcnemar_p": 0.001953125,
                                 "cluster_bootstrap_a0_minus_spot": {"point": 0.0667, "lower": 0.0123, "upper": 0.1}}}},
    "H3": {"targets": {"llama": {"cluster_bootstrap_a0_minus_rep": {"point": 0.0, "lower": -0.02, "upper": 0.02}}}},
}


def test_nothing_is_added_while_the_results_file_does_not_exist(tmp_path):
    assert L.confirmatory_entries(tmp_path / "absent.json") == []


def test_each_value_is_a_ledger_row_with_the_manuscript_format(tmp_path):
    path = tmp_path / "confirmatory_results.json"
    path.write_text(json.dumps(RESULTS))
    rows = {label: value for label, value, _ in L.confirmatory_entries(path)}
    assert rows["confirmatory H1 gpt events"] == "0/72"
    assert rows["confirmatory H1 gpt binomial p"] == "0.0249"
    assert rows["confirmatory H1 gpt Clopper–Pearson"] == "[0.00%, 4.99%]"
    assert rows["confirmatory H2 llama b/c"] == "10/0"
    assert rows["confirmatory H2 llama McNemar p"] == "0.0020"
    assert rows["confirmatory H2 llama interval"] == "[+0.012, +0.100]"
    assert rows["confirmatory H3 llama interval"] == "[−0.020, +0.020]"


def test_the_current_ledger_has_no_confirmatory_rows():
    assert not [e for e in L.entries() if e[0].startswith("confirmatory")]
