"""Regenerate confirmatory F3 loss/cost figure from committed results.
Run from repository root: python paper/figures/fig2_confirmatory_tradeoff.py
"""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

OUT = Path("paper/figures/fig2_confirmatory_tradeoff.png")
OUT.parent.mkdir(parents=True, exist_ok=True)

arms = ["Fixed L1", "Fixed L2", "Fixed L3", "Adaptive dev", "Adaptive exp"]
loss = np.array([0.3020, 0.3300, 0.3779, 0.2902, 0.3683])
cost = np.array([0.100, 0.132, 0.186, 0.080, 0.169])
asr = np.array([0.017, 0.012, 0.003, 0.017, 0.008])

fig, ax = plt.subplots(figsize=(7.2, 5.2))
for i, arm in enumerate(arms):
    ax.scatter(cost[i], loss[i], s=70)
    ax.annotate(arm, (cost[i], loss[i]), xytext=(6, 6), textcoords="offset points", fontsize=9)
ax.set_xlabel("Mean defense cost")
ax.set_ylabel("Loss")
ax.set_title("Confirmatory F3: security–cost trade-off")
ax.grid(True, alpha=0.25)
fig.tight_layout()
fig.savefig(OUT, dpi=220, bbox_inches="tight")
print(OUT)
