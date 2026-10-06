"""Regenerate the case-study architecture figure from the documented controller design.
Run from repository root: python paper/figures/fig1_architecture.py
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path("paper/figures/fig1_architecture.png")
OUT.parent.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(12, 4.5))
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.5)
ax.axis("off")

boxes = [
    (0.3, 1.6, 2.0, 1.2, "Untrusted\ninput"),
    (2.8, 1.6, 2.0, 1.2, "Detector\nregex + semantic guard"),
    (5.3, 1.6, 2.0, 1.2, "Risk / policy\nL0–L3"),
    (7.8, 1.6, 2.0, 1.2, "Defense action\nA0–A3"),
    (10.3, 1.6, 1.4, 1.2, "LLM\nresponse"),
]
for x, y, w, h, label in boxes:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                                linewidth=1.2, fill=False))
    ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=10)

for x1, x2 in [(2.3, 2.8), (4.8, 5.3), (7.3, 7.8), (9.8, 10.3)]:
    ax.add_patch(FancyArrowPatch((x1, 2.2), (x2, 2.2), arrowstyle="->",
                                 mutation_scale=14, linewidth=1.2))

ax.add_patch(FancyBboxPatch((4.2, 3.35), 3.7, 0.75, boxstyle="round,pad=0.04",
                            linewidth=1.2, fill=False))
ax.text(6.05, 3.72, "Adaptive controller: pressure + dwell + backoff + de-escalation",
        ha="center", va="center", fontsize=10)

ax.add_patch(FancyArrowPatch((6.05, 3.35), (6.05, 2.82), arrowstyle="->",
                             mutation_scale=14, linewidth=1.2))
ax.add_patch(FancyArrowPatch((9.0, 1.55), (6.7, 3.35), arrowstyle="->",
                             mutation_scale=14, linewidth=1.2,
                             connectionstyle="arc3,rad=0.25"))
ax.text(7.9, 3.0, "feedback", fontsize=9, ha="center")

ax.text(6.0, 0.55,
        "Case-study scope: text-only probes; controller is non-learning; detector misses limit adaptation.",
        ha="center", va="center", fontsize=9)

fig.tight_layout()
fig.savefig(OUT, dpi=220, bbox_inches="tight")
print(OUT)
