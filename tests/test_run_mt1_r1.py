"""MT1 r1 runner — offline preflight and CMH helper."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("mt1", ROOT / "scripts/run_mt1_r1.py")
_mt1 = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_mt1)


def test_preflight_under_two_dollar_cap():
    ok, worst, n = _mt1.preflight_worst_usd()
    assert n == 6 * 4 * 40
    assert ok
    assert worst <= 2.0


def test_cmh_discordant_smoke():
    p = _mt1.cmh_discordant_p([2, 1], [0, 1])
    assert 0 <= p <= 1
