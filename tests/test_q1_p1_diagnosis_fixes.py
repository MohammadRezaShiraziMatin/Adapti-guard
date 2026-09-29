"""Regression tests for Q1 P1 pack diagnosis fixes (offline)."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from adapti_guard.evaluation.llm_judge import _parse_judge_json
from adapti_guard.evaluation.q1_p1_live_runner import _post_run_analysis, _row_as_eval
from adapti_guard.evaluation.q1_protocol_runner import q1_episode_judge_failed
from adapti_guard.evaluation.target_model import _openrouter_assistant_text


def test_parse_judge_json_extracts_object_after_reasoning_prefix():
    raw = 'Thinking...\n{"attack_success": true, "refusal": false, "policy_violation": false, "tool_misuse": false, "utility_success": false, "confidence": 0.9, "reason": "ok"}'
    data, err = _parse_judge_json(raw)
    assert err is None
    assert data["attack_success"] is True


def test_openrouter_assistant_text_uses_reasoning_when_content_empty():
    msg = SimpleNamespace(content="", reasoning='{"attack_success": false}', model_extra={})
    assert "attack_success" in _openrouter_assistant_text(msg)


from adapti_guard.evaluation.q1_evaluation_contract import load_q1_contract


def test_post_run_asr_excludes_judge_fail(tmp_path: Path):
    target = load_q1_contract()["q1_execution"]["open_target_model_ids"][0]
    ep_path = tmp_path / "episodes.jsonl"
    rows = [
        {
            "attack_id": "a1",
            "target_model_id": target,
            "defense_arm": "A0",
            "attack_succeeded_j1": False,
            "judge_reason": "judge_parse_error",
            "blocked": False,
        },
        {
            "attack_id": "a2",
            "target_model_id": target,
            "defense_arm": "A0",
            "attack_succeeded_j1": True,
            "judge_reason": "Model refused.",
            "blocked": False,
        },
    ]
    ep_path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    post = _post_run_analysis(
        ep_path,
        repo_root=Path("."),
        stop_reason="completed_all_planned",
        planned_episodes=2,
    )
    arm = post["per_target_asr_j1"][target]["A0"]
    assert arm["n_judgeable"] == 1
    assert arm["asr_j1"] == 1.0
    assert arm["asr_j1_raw_including_judge_fail"] == 0.5


def test_kappa_skips_j1_parse_failures(tmp_path: Path):
    target = load_q1_contract()["q1_execution"]["open_target_model_ids"][0]
    ep_path = tmp_path / "episodes.jsonl"
    base = {
        "target_model_id": target,
        "defense_arm": "A0",
        "j2_required": True,
        "blocked": False,
        "j2_attack_success": False,
    }
    rows = []
    for i in range(3):
        rows.append(
            {
                **base,
                "attack_id": f"a{i}",
                "attack_succeeded_j1": False,
                "judge_reason": "judge_parse_error",
                "j2_judge_reason": "judge_parse_error",
            }
        )
    rows.append(
        {
            **base,
            "attack_id": "ok1",
            "attack_succeeded_j1": True,
            "judge_reason": "ok",
            "j2_judge_reason": "ok",
            "j2_attack_success": True,
        }
    )
    ep_path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    post = _post_run_analysis(ep_path, repo_root=Path("."), planned_episodes=len(rows))
    assert post["j2_subset_episodes_analyzed"] == 1
    assert q1_episode_judge_failed(_row_as_eval(rows[0])) is True
