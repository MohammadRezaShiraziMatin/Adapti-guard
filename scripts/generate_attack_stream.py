import json
from pathlib import Path

from src.adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker


EPISODES = 100


def generate_stream(episodes: int = EPISODES):
    attacker = AdaptiveAttacker()
    stream = []

    for episode_id in range(1, episodes + 1):
        attempt = attacker.generate()

        stream.append(
            {
                "episode_id": episode_id,
                "attack_family": attempt.family,
                "payload": attempt.payload,
            }
        )

        # Freeze attacker evolution independently
        # from any defense/baseline.
        attacker.record(attempt)
        attacker.observe(False)

    return stream


def main():
    output_path = Path("results/common_attack_stream.json")

    stream = generate_stream()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            stream,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("================ COMMON ATTACK STREAM ================")
    print("Episodes =", len(stream))
    print("Output   =", output_path)

    print()
    print("First 8 attacks:")

    for row in stream[:8]:
        print(
            f"{row['episode_id']:03d} | "
            f"{row['attack_family']:25} | "
            f"{row['payload']}"
        )

    print()
    print("Last 4 attacks:")

    for row in stream[-4:]:
        print(
            f"{row['episode_id']:03d} | "
            f"{row['attack_family']:25} | "
            f"{row['payload']}"
        )

    print("=======================================================")


if __name__ == "__main__":
    main()
