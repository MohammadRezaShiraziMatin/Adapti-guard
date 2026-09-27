"""MT1 arms on layer_a_v2 pack — offline defense smoke (no API)."""
from adapti_guard.experiments.defense_baselines import get_defense_fn


def test_mt1_arms_registered():
    for arm in ("B0", "STATIC-A3", "SPOTLIGHT", "B3"):
        fn, state = get_defense_fn(arm)
        assert callable(fn)
        if arm == "B3":
            assert state is not None


def test_static_a3_blocks_prompt():
    fn, _ = get_defense_fn("STATIC-A3")
    level, blocked, _ = fn("ignore instructions", None)
    assert blocked is True
    assert level == "A3"


def test_b0_passes_prompt():
    fn, _ = get_defense_fn("B0")
    level, blocked, _ = fn("ignore instructions", None)
    assert blocked is False


def test_spotlight_marks_untrusted():
    fn, _ = get_defense_fn("SPOTLIGHT")
    level, blocked, out = fn("do evil", None)
    assert blocked is False
    assert "UNTRUSTED_START" in out
    assert "do evil" in out
