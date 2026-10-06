"""Regenerate the primary paired-seed F3 comparison from committed runs_v3.json.
Run from repository root: python paper/figures/fig3_primary_paired_difference.py
"""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(".")
DATA = ROOT / "results/f3_confirmatory/runs_v3.json"
OUT = ROOT / "paper/figures/fig3_primary_paired_difference.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

rows = json.loads(DATA.read_text())
by_seed = {}
for row in rows:
    if row["arm"] in {"adaptive_dev_sem", "fixed_l1_sem"}:
        by_seed.setdefault(row["seed"], {})[row["arm"]] = float(row["loss"])

seeds = sorted(s for s, d in by_seed.items()
               if "adaptive_dev_sem" in d and "fixed_l1_sem" in d)
diff = np.array([by_seed[s]["adaptive_dev_sem"] - by_seed[s]["fixed_l1_sem"] for s in seeds])

fig, ax = plt.subplots(figsize=(8.0, 4.8))
ax.axhline(0.0, linewidth=1.0)
ax.plot(range(1, len(diff) + 1), diff, marker="o", linewidth=1.2)
ax.axhline(-0.02, linestyle="--", linewidth=1.0)
ax.axhline(0.02, linestyle="--", linewidth=1.0)
ax.set_xlabel("Confirmatory seed index")
ax.set_ylabel("Adaptive dev − fixed L1 loss")
ax.set_title("Primary paired-seed F3 comparison")
ax.set_xticks(range(1, len(diff) + 1))
ax.set_xticklabels([str(s) for s in seeds], rotation=60, fontsize=7)
ax.grid(True, axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT, dpi=220, bbox_inches="tight")
print(OUT)
