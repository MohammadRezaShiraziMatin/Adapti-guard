"""Parse Amendment 9 llama smoke episode list from AMENDMENT9_DECISIONS.md."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_DEFAULT_DECISIONS = (
    Path(__file__).resolve().parents[4] / "experiments/harness_v2/AMENDMENT9_DECISIONS.md"
)

_EPISODE_ID_RE = re.compile(r"`([^`]+/i0/llama/(?:A0|B3))`")


def amendment9_decisions_path(repo_root: Path | None = None) -> Path:
    root = repo_root or Path(__file__).resolve().parents[4]
    return root / "experiments/harness_v2/AMENDMENT9_DECISIONS.md"


def parse_amendment9_llama_smoke_episode_ids(
    decisions_md: Path | None = None,
) -> list[str]:
    """Return ordered episode_id strings from the smoke table (single source of truth)."""
    path = decisions_md or _DEFAULT_DECISIONS
    text = path.read_text(encoding="utf-8")
    start = text.find("### Episode list (20 episodes — exact)")
    if start < 0:
        raise ValueError("smoke episode list section not found in AMENDMENT9_DECISIONS.md")
    section = text[start : start + 4000]
    ids = _EPISODE_ID_RE.findall(section)
    if len(ids) != 20:
        raise ValueError(f"expected 20 smoke episode_ids, found {len(ids)}")
    return ids


def amendment9_llama_smoke_schedule(
    *,
    decisions_md: Path | None = None,
) -> list[dict[str, Any]]:
    """Pilot schedule rows for the 20 llama smoke episodes only."""
    rows: list[dict[str, Any]] = []
    for episode_id in parse_amendment9_llama_smoke_episode_ids(decisions_md):
        scenario_id, inst_part, family, condition = episode_id.split("/")
        if not inst_part.startswith("i") or family != "llama":
            raise ValueError(f"unexpected smoke episode_id shape: {episode_id!r}")
        instance_index = int(inst_part[1:])
        rows.append(
            {
                "scenario_id": scenario_id,
                "instance_index": instance_index,
                "family": family,
                "condition": condition,
            }
        )
    return rows


def amendment9_llama_smoke_episode_ids_ordered(
    *,
    decisions_md: Path | None = None,
) -> list[str]:
    return parse_amendment9_llama_smoke_episode_ids(decisions_md)
