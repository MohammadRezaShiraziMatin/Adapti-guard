from __future__ import annotations

import pytest

from adapti_guard.evaluation.mt2_panel import (
    MT2PanelConfigError,
    resolve_mt2_judges_for_target,
    validate_mt2_panel,
)
from adapti_guard.evaluation.live_model_resolver import model_id_for_config_key


def test_mt2_panel_has_six_distinct_targets():
    report = validate_mt2_panel()
    assert report["n_targets"] == 6
    families = {t["vendor_family"] for t in report["targets"]}
    assert len(families) == 6


def test_mt2_openai_target_uses_substitute_judges():
    j = resolve_mt2_judges_for_target("mt2_target_openai_gpt_4o")
    assert j["rule"] == "openai_target_vendor_substitute"
    assert j["primary_config_key"] == "mt2_judge_primary_openai_target_substitute"
    assert j["secondary_config_key"] == "mt2_judge_secondary_openai_target_substitute"
    from adapti_guard.evaluation.mt2_panel import DEFAULT_MODELS_PATH

    assert (
        model_id_for_config_key(j["primary_config_key"], DEFAULT_MODELS_PATH)
        == "deepseek/deepseek-chat-v3-0324"
    )
    assert model_id_for_config_key(j["secondary_config_key"], DEFAULT_MODELS_PATH) == "amazon/nova-lite-v1"


def test_mt2_default_judges_for_non_openai_target():
    j = resolve_mt2_judges_for_target("mt2_target_qwen3_30b_a3b")
    assert j["rule"] == "default"
    from adapti_guard.evaluation.mt2_panel import DEFAULT_MODELS_PATH

    assert model_id_for_config_key(j["primary_config_key"], DEFAULT_MODELS_PATH) == "openai/gpt-oss-120b"
    assert (
        model_id_for_config_key(j["secondary_config_key"], DEFAULT_MODELS_PATH)
        == "deepseek/deepseek-chat-v3-0324"
    )


def test_mt2_historical_keys_unchanged():
    assert model_id_for_config_key("target_2") == "qwen/qwen-2.5-7b-instruct"
    assert model_id_for_config_key("judge_fallback") == "qwen/qwen-2.5-72b-instruct"
    assert model_id_for_config_key("model_a") == "google/gemma-4-31b-it"


def test_mt2_validate_rejects_family_collision(tmp_path):
    import yaml
    from pathlib import Path

    models = yaml.safe_load(Path("configs/models_mt2.yaml").read_text())
    panel = yaml.safe_load(Path("configs/mt2_panel.yaml").read_text())
    bad_models = dict(models)
    bad_models["models"]["mt2_judge_primary"]["vendor_family"] = "qwen"
    bad_models["models"]["mt2_judge_primary"]["model"] = "qwen/qwen3-30b-a3b"
    mp = tmp_path / "models_mt2.yaml"
    pp = tmp_path / "panel.yaml"
    mp.write_text(yaml.dump(bad_models))
    pp.write_text(yaml.dump(panel))
    with pytest.raises(MT2PanelConfigError):
        validate_mt2_panel(models_path=mp, panel_path=pp)
