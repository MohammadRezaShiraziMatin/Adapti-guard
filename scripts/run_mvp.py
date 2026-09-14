from src.adapti_guard.experiments.experiment_runner import ExperimentRunner


def main():
    runner = ExperimentRunner()

    results = runner.run(episodes=100)

    runner.save_results(
        results,
        "results/mvp_100_episodes.json",
    )

    print("=" * 70)
    print("ADAPTI-GUARD MVP EXPERIMENT")
    print("=" * 70)

    for r in results:
        print(
            f"Episode {r.episode_id:02d} | "
            f"Attack={r.attack_family:22s} | "
            f"Risk={r.risk_score:.3f} | "
            f"Level={r.risk_level:6s} | "
            f"Action={r.defense_action} | "
            f"Success={r.attack_success} | "
            f"DefenseLevel={r.defense_level}"
        )

    print("=" * 70)

    n = len(results)

    legit_results = [r for r in results if r.attack_family == "legitimate"]
    attack_results = [r for r in results if r.attack_family != "legitimate"]

    attack_success_rate = sum(
        r.attack_success for r in attack_results
    ) / len(attack_results)

    security_score = sum(
        r.security_score for r in results
    ) / n

    utility_score = sum(
        r.utility_score for r in legit_results
    ) / len(legit_results)

    average_cost = sum(
        r.defense_cost for r in results
    ) / n

    print(f"Episodes:             {n}")
    print(f"Attack Success Rate:  {attack_success_rate:.3f}")
    print(f"Security Score:       {security_score:.3f}")
    print(f"Utility Score:        {utility_score:.3f}")
    print(f"Average Cost:         {average_cost:.3f}")

    print("=" * 70)
    print("RESULT SAVED:")
    print("results/mvp_100_episodes.json")


if __name__ == "__main__":
    main()
