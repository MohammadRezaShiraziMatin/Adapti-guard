from pathlib import Path

import pytest

from adapti_guard.evaluation.q1_evaluation_contract import (
    Q1ContractError,
    validate_q1_evaluation_contract,
)


def test_validator_fails_when_pack_manifest_sha_missing(tmp_path):
    pack = Path("docs/Q1_OWNER_DECISION_PACK.md").read_text(encoding="utf-8")
    bad = tmp_path / "bad_pack.md"
    bad.write_text(pack.replace("1ccf9fe1c632909adc131c7d776749361d13bbcb3ec8e4c0806abfbd887863b0", "deadbeef"), encoding="utf-8")
    with pytest.raises(Q1ContractError, match="owner pack missing manifest sha256"):
        validate_q1_evaluation_contract(repo_root=".", owner_pack_path=bad)
