from adapti_guard.evaluation.execution_metadata import metadata_from_config

def test_metadata_roles():
    t = metadata_from_config("model_a", role="target", seed=42)
    j = metadata_from_config("judge_primary", role="judge", seed=42)
    assert t.role == "target" and j.role == "judge"
    assert t.model_id and j.model_id
