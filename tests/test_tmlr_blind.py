"""The double-blind manuscript differs from the public one only by anonymization and carries no identity-bearing text."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_tmlr_blind as bb  # noqa: E402

PUBLIC = ROOT / "docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md"
BLIND = ROOT / "docs/paper/negative_result/tmlr_blind/MANUSCRIPT_TMLR_BLIND.md"
STRIP = lambda s: re.sub(r"\[commit C\d+\]|`[0-9a-f]{7,40}`|\[tag withheld\]|`?case-study-v1`?", "X", s)


def test_blind_file_is_current_clean_and_changes_only_names_and_hashes():
    pub, blind = PUBLIC.read_text(), BLIND.read_text()
    assert bb.blind(pub)[0] == blind  # regenerate with scripts/build_tmlr_blind.py after editing the public manuscript
    assert bb.audit(blind) == {}
    a, b = pub.splitlines(), blind.splitlines()
    assert len(a) == len(b) and a[0] == b[0]  # same title line
    digits = lambda lines: re.findall(r"\d+(?:\.\d+)?", "\n".join(STRIP(x) for x in lines))
    note = [i for i, y in enumerate(b) if "double-blind version" in y][0]  # the one paragraph that gains the disclosure note
    assert digits(a[:note] + a[note + 1:]) == digits(b[:note] + b[note + 1:])  # every number elsewhere is identical
    for x, y in zip(a, b):
        if STRIP(x) != STRIP(y):  # the only other differences: project and package names, tag name, the disclosure note
            assert re.search(r"AdaptiGuard|ADAPTI-GUARD|adapti_guard|case-study-v1|Unless a row says otherwise", x)


def test_e6_stays_unrun_future_work_in_the_blind_version():
    t = BLIND.read_text()
    assert "not frozen, not approved, not registered and not run" in t and "future work" in t and "E6 would not validate M6" in t


def test_hash_labels_are_stable_and_file_hashes_survive():
    out, labels = bb.blind("Unless a row says otherwise the artifact is in the repository. See `abcdef1` and `abcdef123456` and `1234567`; file `8ae353ca…9de8`")
    body = out.split("generic wording.")[1]
    assert body.count("[commit C1]") == 2 and "[commit C2]" in body and "`8ae353ca…9de8`" in out and len(labels) == 2
