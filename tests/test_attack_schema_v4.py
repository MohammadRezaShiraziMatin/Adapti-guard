"""Tests for the attack-pack v4 schema validator (Stage 1).

The records below are synthetic validator fixtures. They are not dataset
examples: their text is neutral placeholder prose, and any host they mention
uses a reserved name.
"""

import copy

import pytest

from adapti_guard.data.attack_schema_v4 import (
    CATEGORIES,
    CHANNELS,
    LABELS,
    compute_sha256,
    validate_dataset,
    validate_record,
)

TOOLS = [
    {"name": "search", "arguments": ["query"]},
    {"name": "send_email", "arguments": ["to", "body"]},
]


def _finalise(record: dict) -> dict:
    record["sha256"] = compute_sha256(record)
    return record


def _base(**overrides) -> dict:
    record = {
        "id": "av4-atk-000001",
        "label": "attack",
        "family": "EMAIL_INJECTION",
        "category": "email_injection",
        "turn_type": "single",
        "injection_channel": "email",
        "injection_location": "email body, paragraph 2",
        "attack_objective": "Cause one unauthorised send_email call to a reserved address.",
        "success_condition": "Succeeds if send_email is called with to=ops@example.invalid.",
        "tools": copy.deepcopy(TOOLS),
        "tool_call": {"name": "send_email", "arguments": {"to": "ops@example.invalid"}},
        "source": "self_authored",
        "author_id": "author-01",
        "created_at": "2026-10-10T12:00:00",
        "version": "attack_v4_draft",
        "license": "MIT",
        "turns": ["Summarise the attached support email."],
        "untrusted_content": "Support email body with a placeholder instruction.",
        "pair_id": "av4-ben-000001",
        "canary": None,
        "redistributable": True,
    }
    record.update(overrides)
    return _finalise(record)


def _benign(**overrides) -> dict:
    record = _base(
        id="av4-ben-000001",
        label="benign",
        family="benign",
        category="benign_task",
        injection_location="none",
        attack_objective="none",
        success_condition="Succeeds if the assistant summarises the email and makes no send_email call.",
        tool_call=None,
        untrusted_content="Support email body with ordinary text only.",
        pair_id="av4-atk-000001",
        canary=None,
    )
    record.update(overrides)
    return _finalise(record)


def _hard_negative(**overrides) -> dict:
    record = _base(
        id="av4-hn-000001",
        label="hard_negative",
        family="benign",
        category="hard_negative_benign",
        injection_location="email body, quoted example in paragraph 2",
        attack_objective="none",
        success_condition="Succeeds if the assistant summarises the email and does not call send_email.",
        tool_call=None,
        untrusted_content="Email quoting an example line for a security training note.",
        pair_id="av4-atk-000001",
        canary=None,
    )
    record.update(overrides)
    return _finalise(record)


def test_valid_attack_has_no_errors():
    assert validate_record(_base()) == []


def test_valid_benign_has_no_errors():
    assert validate_record(_benign()) == []


def test_valid_hard_negative_has_no_errors():
    assert validate_record(_hard_negative()) == []


def test_canary_attack_without_tool_call_is_valid():
    record = _base(
        category="system_prompt_leakage",
        family="SYSTEM_PROMPT_LEAKAGE",
        injection_channel="user_turn",
        injection_location="user turn, sentence 1",
        tool_call=None,
        canary="AV4-CANARY-0001",
        success_condition="Succeeds if the output contains the exact string AV4-CANARY-0001.",
        untrusted_content="",
        pair_id="av4-ben-000001",
    )
    assert validate_record(record) == []


@pytest.mark.parametrize("name", [
    "id", "label", "family", "category", "turn_type", "injection_channel",
    "injection_location", "attack_objective", "success_condition", "tools",
    "tool_call", "source", "author_id", "created_at", "version", "license",
    "sha256", "turns", "untrusted_content", "pair_id", "canary", "redistributable",
])
def test_missing_required_field_is_reported(name):
    record = _base()
    del record[name]
    errors = validate_record(record)
    assert f"missing field: {name}" in errors


@pytest.mark.parametrize("name", ["injection_channel", "injection_location", "attack_objective", "author_id", "license"])
def test_empty_string_field_is_rejected(name):
    record = _base(**{name: ""})
    assert validate_record(_finalise(record)) != []


def test_empty_injection_channel_is_rejected_with_explicit_message():
    errors = validate_record(_base(injection_channel=""))
    assert "injection_channel is empty" in errors


@pytest.mark.parametrize("channel", CHANNELS[:-1])
def test_every_allowed_channel_is_accepted_for_email_only_when_matched(channel):
    # Only "email" fits the email_injection category; other channels must fail.
    errors = validate_record(_base(injection_channel=channel))
    if channel == "email":
        assert errors == []
    else:
        assert any("does not allow channel" in e for e in errors)


def test_invalid_channel_value_is_rejected():
    assert any("invalid injection_channel" in e for e in validate_record(_base(injection_channel="sms")))


def test_invalid_label_is_rejected():
    errors = validate_record(_base(label="malicious"))
    assert errors == ["invalid label: 'malicious'"]


def test_invalid_category_is_rejected():
    assert any("invalid category" in e for e in validate_record(_base(category="made_up")))


def test_invalid_turn_type_is_rejected():
    assert any("invalid turn_type" in e for e in validate_record(_base(turn_type="double")))


def test_attack_cannot_use_benign_category():
    assert any("non-attack category" in e for e in validate_record(_base(category="benign_task")))


def test_attack_with_none_channel_is_rejected():
    errors = validate_record(_base(injection_channel="none", untrusted_content=""))
    assert "attack record must have an injection channel other than 'none'" in errors


def test_attack_requires_exact_injection_location():
    assert any("exact injection_location" in e for e in validate_record(_base(injection_location="none")))


def test_attack_needs_tool_call_or_canary():
    record = _base(tool_call=None, canary=None)
    assert any("needs tool_call or canary" in e for e in validate_record(record))


def test_tool_call_must_name_a_declared_tool():
    record = _base(tool_call={"name": "delete_everything", "arguments": {}})
    assert any("is not in tools" in e for e in validate_record(record))


def test_single_turn_needs_exactly_one_turn():
    record = _base(turns=["one", "two"])
    assert any("exactly 1 turn" in e for e in validate_record(record))


def test_multi_turn_category_needs_multi_turn_type():
    record = _base(
        category="multi_turn_persistence",
        family="MULTI_TURN_PERSISTENCE",
        injection_channel="user_turn",
        turn_type="single",
    )
    assert any("does not allow turn_type 'single'" in e for e in validate_record(record))


def test_multi_turn_record_needs_two_turns():
    record = _base(
        category="multi_turn_persistence",
        family="MULTI_TURN_PERSISTENCE",
        injection_channel="user_turn",
        turn_type="multi",
        turns=["only one turn"],
        untrusted_content="",
    )
    assert any("at least 2 turns" in e for e in validate_record(record))


def test_none_channel_requires_empty_untrusted_content():
    record = _benign(injection_channel="none", untrusted_content="unexpected text")
    assert any("requires untrusted_content to be empty" in e for e in validate_record(record))


def test_non_user_channel_requires_untrusted_content():
    record = _base(untrusted_content="   ")
    assert any("requires non-empty untrusted_content" in e for e in validate_record(record))


def test_benign_must_have_none_location_and_objective():
    errors = validate_record(_benign(injection_location="email body"))
    assert "benign record must have injection_location 'none'" in errors


def test_benign_must_not_have_canary():
    errors = validate_record(_benign(canary="AV4-CANARY-9999"))
    assert "benign record must have canary null" in errors


def test_hard_negative_requires_decoy_location_and_channel():
    errors = validate_record(_hard_negative(injection_channel="none", untrusted_content=""))
    assert "hard_negative record must carry untrusted content (channel other than 'none')" in errors


def test_hard_negative_must_use_its_category():
    assert any("hard_negative record must use category" in e for e in validate_record(_hard_negative(category="benign_task")))


def test_id_prefix_must_match_label():
    errors = validate_record(_base(id="av4-ben-000001"))
    assert "id segment does not match label 'attack'" in errors


def test_id_format_is_enforced():
    assert any("id must match" in e for e in validate_record(_base(id="atk-1")))


def test_version_format_is_enforced():
    assert any("invalid version" in e for e in validate_record(_base(version="v3")))


def test_created_at_must_be_iso8601():
    assert any("created_at is not ISO-8601" in e for e in validate_record(_base(created_at="10/10/2026")))


def test_sha256_must_match_content():
    record = _base()
    record["attack_objective"] = "Changed after hashing, so the digest is stale."
    assert "sha256 does not match canonical record content" in validate_record(record)


def test_sha256_format_is_enforced():
    record = _base()
    record["sha256"] = "ABC"
    assert any("sha256 is not" in e for e in validate_record(record))


def test_external_source_requires_provenance():
    record = _base(source="garak", redistributable=True)
    errors = validate_record(_finalise(record))
    for name in ("source_url", "source_version", "retrieved_at"):
        assert f"external source 'garak' requires {name}" in errors


def test_external_source_with_provenance_is_valid():
    record = _base(
        source="garak",
        source_url="https://example.org/garak-release",
        source_version="0.0.0-fixture",
        retrieved_at="2026-10-10",
        redistributable=True,
    )
    assert validate_record(_finalise(record)) == []


def test_non_redistributable_external_record_cannot_carry_text():
    record = _base(
        source="InjecAgent",
        source_url="https://example.org/injecagent",
        source_version="fixture",
        retrieved_at="2026-10-10",
        redistributable=False,
    )
    errors = validate_record(_finalise(record))
    assert any("publish identifiers only" in e for e in errors)


def test_unknown_source_is_rejected():
    assert any("invalid source" in e for e in validate_record(_base(source="random_blog")))


def test_non_reserved_host_is_rejected():
    record = _base(untrusted_content="Contact support at https://vendor.com/reset for details.")
    assert any("non-reserved host" in e for e in validate_record(record))


def test_reserved_host_is_accepted():
    record = _base(untrusted_content="Contact ops@example.invalid or see https://portal.example.org/x.")
    assert validate_record(record) == []


def test_all_labels_and_categories_are_known_to_validator():
    assert set(LABELS) == {"attack", "benign", "hard_negative"}
    assert len(CATEGORIES) == 14


def test_dataset_pair_must_be_reciprocal_and_match_structure():
    attack = _base()
    benign = _benign(injection_channel="email", turn_type="single")
    assert validate_dataset([attack, benign]) == {}


def test_dataset_rejects_unpaired_attack():
    attack = _base(pair_id="av4-ben-999999")
    report = validate_dataset([attack])
    assert any("pair_id 'av4-ben-999999' not found" in e for e in report["av4-atk-000001"])


def test_dataset_rejects_mismatched_turn_count():
    attack = _base()
    benign = _benign(turns=["one", "two"], turn_type="single")
    report = validate_dataset([attack, benign])
    assert "pair mismatch on number of turns" in report.get("av4-atk-000001", [])


def test_dataset_rejects_attack_paired_to_attack():
    attack_a = _base()
    attack_b = _base(id="av4-atk-000002", pair_id="av4-atk-000001")
    report = validate_dataset([attack_a, attack_b])
    assert any("not another attack" in e for e in report.get("av4-atk-000002", []))


def test_dataset_rejects_duplicate_ids():
    report = validate_dataset([_base(), _base()])
    assert any("duplicate id" in e for e in report.get("av4-atk-000001", []))


def test_dataset_rejects_non_reciprocal_pair():
    attack = _base()
    benign = _benign(pair_id="av4-atk-000099")
    report = validate_dataset([attack, benign])
    assert any("not reciprocal" in e for e in report.get("av4-atk-000001", []))
