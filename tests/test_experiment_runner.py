from adapti_guard.experiments.experiment_runner import (
    ExperimentRunner,
)


def test_single_episode():
    runner = ExperimentRunner()

    result = runner.run_episode(1)

    assert result.episode_id == 1
    assert result.attack_family == "direct_injection"
    assert result.detection_score > 0
    assert result.risk_score > 0
    assert result.defense_action in {
        "A0",
        "A1",
        "A2",
        "A3",
    }


def test_multiple_episodes():
    runner = ExperimentRunner()

    results = runner.run(episodes=5)

    assert len(results) == 5

    assert results[0].episode_id == 1
    assert results[-1].episode_id == 5


def test_results_can_be_saved(tmp_path):
    runner = ExperimentRunner()

    results = runner.run(episodes=3)

    output = tmp_path / "episodes.json"

    runner.save_results(
        results,
        output,
    )

    assert output.exists()
    assert output.stat().st_size > 0
