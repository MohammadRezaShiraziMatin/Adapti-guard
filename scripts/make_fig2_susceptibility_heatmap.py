"""Figure 2: A0 susceptibility of the independent attack families, by target model. API=0.

Source: the A0 screening run (168 episodes, 7 families x 8 instances x 3 models).
Cell value = share of the 8 episodes in which the attacker-specified call reached the executor
(exec_executed). A dagger marks cells containing INVALID_NOT_DELIVERED episodes (harness/provider
causes); those episodes stay in the denominator of 8, so the cell is a lower bound.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.rcParams["svg.hashsalt"] = "adaptiguard"  # byte-reproducible SVG ids

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments/harness_v2/HARNESS_V2_INDEPENDENT_SCREEN_20260930/episodes.jsonl"
OUT = ROOT / "docs/paper/negative_result/figures"
MODELS = ["qwen3", "gemma", "deepseek"]
FAMILY_LABEL = {
    "ind_authority_claim_doc_v2i": "Authority claim (doc)",
    "ind_important_instr_doc_v2i": "Important-instructions block (doc)",
    "ind_important_instr_weather_v2i": "Important-instructions block (weather tool)",
    "ind_second_doc_v2i": "Updated instruction on 2nd read (doc)",
    "ind_unrequested_write_doc_v2i": "Unrequested write (doc)",
    "ind_split_address_doc_v2i": "Split e-mail address (doc)",
    "ind_workflow_footer_doc_v2i": "Workflow footer (doc)",
}
# sequential blue, steps 100 -> 700 of the reference palette (light -> dark)
BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"


def main() -> None:
    rows = [json.loads(x) for x in RUN.read_text().splitlines() if x.strip()]
    cell = defaultdict(lambda: [0, 0, 0])  # executed, n, invalid
    for r in rows:
        c = cell[(r["scenario_id"], r["family"])]
        c[1] += 1
        c[0] += (r["C2"] or {}).get("exec_executed") is True
        c[2] += (r["C2"] or {}).get("C2_state") == "INVALID_NOT_DELIVERED"
    fams = sorted(FAMILY_LABEL, key=lambda s: -sum(cell[(s, m)][0] for m in MODELS))
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "fig2_susceptibility.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["family", "model", "executed", "n", "rate", "invalid_not_delivered"])
        for s in fams:
            for m in MODELS:
                k, n, inv = cell[(s, m)]
                w.writerow([s, m, k, n, f"{k / n:.4f}", inv])
            k = sum(cell[(s, m)][0] for m in MODELS)
            n = sum(cell[(s, m)][1] for m in MODELS)
            w.writerow([s, "pooled", k, n, f"{k / n:.4f}", sum(cell[(s, m)][2] for m in MODELS)])
        for m in MODELS:
            k = sum(cell[(s, m)][0] for s in fams)
            n = sum(cell[(s, m)][1] for s in fams)
            w.writerow(["ALL_FAMILIES", m, k, n, f"{k / n:.4f}", sum(cell[(s, m)][2] for s in fams)])

    cmap = LinearSegmentedColormap.from_list("blue_seq", BLUE)
    cols = MODELS + ["pooled"]
    fig, ax = plt.subplots(figsize=(8.6, 4.3), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    gap = 0.06
    for i, s in enumerate(fams):
        for j, col in enumerate(cols):
            if col == "pooled":
                k = sum(cell[(s, m)][0] for m in MODELS)
                n = sum(cell[(s, m)][1] for m in MODELS)
                inv = 0
            else:
                k, n, inv = cell[(s, col)]
            p = k / n
            x = j + (0.22 if col == "pooled" else 0)  # separate the pooled column
            ax.add_patch(plt.Rectangle((x + gap / 2, i + gap / 2), 1 - gap, 1 - gap, facecolor=cmap(p), edgecolor="none"))
            txt_color = "#ffffff" if p >= 0.5 else INK
            label = f"{k}/{n}" + ("†" if inv else "")
            ax.text(x + 0.5, i + 0.5, label, ha="center", va="center", fontsize=9, color=txt_color)
    ax.set_xlim(0, len(cols) + 0.22)
    ax.set_ylim(len(fams), 0)
    ax.set_xticks([j + 0.5 + (0.22 if c == "pooled" else 0) for j, c in enumerate(cols)])
    ax.set_xticklabels(["qwen3", "gemma", "deepseek", "all 3 models"], fontsize=9, color=INK)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.5 for i in range(len(fams))])
    ax.set_yticklabels([FAMILY_LABEL[s] for s in fams], fontsize=9, color=INK)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, ticks=[0, 0.5, 1])
    cb.set_label("Attack execution rate (A0, no defense)", fontsize=8, color=INK2)
    cb.ax.tick_params(labelsize=8, colors=INK2, length=0)
    cb.outline.set_visible(False)
    fig.suptitle("Susceptibility to tool-channel injection depends on the model and the framing", fontsize=11, color=INK, x=0.01, ha="left", y=0.995)
    fig.text(0.01, 0.01, "Cells: executed/8 episodes (attacker-specified call reached the executor). † = includes INVALID_NOT_DELIVERED episodes (harness/provider causes), so the\n"
             "cell is a lower bound. Rows ordered by pooled rate. Exploratory A0 screening, frozen templates SHA 8ae353ca…9de8; K = 8 per cell.", fontsize=7.3, color=INK2, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    fig.savefig(OUT / "fig2_susceptibility.png", dpi=200, facecolor=SURFACE)
    fig.savefig(OUT / "fig2_susceptibility.svg", facecolor=SURFACE, metadata={"Date": None})
    for s in fams:
        print(f"{FAMILY_LABEL[s]:46}", *[f"{cell[(s, m)][0]}/{cell[(s, m)][1]}" + ("+" if cell[(s, m)][2] else "") for m in MODELS])


if __name__ == "__main__":
    main()
