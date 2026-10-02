"""Figure 3: paired change in attack execution, defended arm minus A0, on the independent set. API=0.

Pairs = (family, instance, model) COMPLETE in both the A0 screening and the defended run.
Point = mean paired difference of exec_executed (arm - A0); whiskers = paired bootstrap 95% CI
(5000 resamples, seed 20260930). Grey marker = A0 rate negated, i.e. the largest reduction
possible on that row (what a deterministic argument-level policy would give by construction).
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

import matplotlib

matplotlib.rcParams["svg.hashsalt"] = "adaptiguard"  # byte-reproducible SVG ids

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
A0_RUN = ROOT / "experiments/harness_v2/HARNESS_V2_INDEPENDENT_SCREEN_20260930/episodes.jsonl"
DEF_RUN = ROOT / "experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/episodes.jsonl"
OUT = ROOT / "docs/paper/negative_result/figures"
ARMS = {"B3": ("B3 (adaptive)", "#eb6834"), "CORE": ("PHASE1-CORE", "#1baf7a")}
FAM = {
    "ind_authority_claim_doc_v2i": "Authority claim (doc)",
    "ind_important_instr_doc_v2i": "Important-instructions (doc)",
    "ind_important_instr_weather_v2i": "Important-instructions (weather)",
    "ind_second_doc_v2i": "Updated instruction, 2nd read",
    "ind_unrequested_write_doc_v2i": "Unrequested write",
    "ind_split_address_doc_v2i": "Split e-mail address",
    "ind_workflow_footer_doc_v2i": "Workflow footer",
}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e3e2dd"


def load(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


def ex(r: dict) -> int:
    return int((r["C2"] or {}).get("exec_executed") is True)


def boot(diffs: list[int], rng: random.Random, b: int = 5000) -> tuple[float, float, float]:
    n = len(diffs)
    m = sum(diffs) / n
    ms = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(b))
    return m, ms[int(0.025 * b)], ms[int(0.975 * b) - 1]


def main() -> None:
    a0 = {(r["scenario_id"], r["instance_index"], r["family"]): r for r in load(A0_RUN) if r["condition"] == "A0" and r["status"] == "COMPLETE"}
    de = load(DEF_RUN)
    rng = random.Random(20260930)
    rows = list(FAM) + ["ALL"]
    res: dict = {}
    for arm in ARMS:
        pairs = [(a0[(r["scenario_id"], r["instance_index"], r["family"])], r) for r in de
                 if r["condition"] == arm and r["status"] == "COMPLETE" and (r["scenario_id"], r["instance_index"], r["family"]) in a0]
        for fam in rows:
            sel = [(x, y) for x, y in pairs if fam == "ALL" or x["scenario_id"] == fam]
            d = [ex(y) - ex(x) for x, y in sel]
            m, lo, hi = boot(d, rng)
            res[(arm, fam)] = (m, lo, hi, len(sel), sum(ex(x) for x, _ in sel) / len(sel))
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "fig3_defended_vs_a0.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "row", "pairs", "mean_diff", "ci95_lo", "ci95_hi", "a0_rate"])
        for (arm, fam), (m, lo, hi, n, a0r) in res.items():
            w.writerow([arm, fam, n, f"{m:.4f}", f"{lo:.4f}", f"{hi:.4f}", f"{a0r:.4f}"])

    fig, ax = plt.subplots(figsize=(8.8, 5.1), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ylabels = [FAM.get(r, "All families (pooled)") for r in rows]
    for i, fam in enumerate(rows):
        y0 = i
        ax.axhspan(i - 0.5, i + 0.5, color="#f1f0ec" if fam == "ALL" else SURFACE, zorder=0)
        a0r = res[("B3", fam)][4]
        ax.plot([-a0r], [y0], marker="D", ms=6, mfc="none", mec="#9a9993", mew=1.3, ls="none", zorder=2)
        for k, (arm, (_, col)) in enumerate(ARMS.items()):
            m, lo, hi, n, _ = res[(arm, fam)]
            y = y0 + (-0.14 + 0.28 * k)
            ax.plot([lo, hi], [y, y], color=col, lw=2, solid_capstyle="round", zorder=3)
            ax.plot([m], [y], marker="o", ms=8, mfc=col, mec=SURFACE, mew=2, zorder=4, ls="none")
    ax.axvline(0, color=INK2, lw=1.2, zorder=1)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(ylabels, fontsize=9, color=INK)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xlim(-1.05, 0.45)
    ax.set_xlabel("Change in attack execution rate vs A0 (defended − A0), paired", fontsize=9, color=INK2)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=8.5, labelcolor=INK2)
    ax.tick_params(axis="y", labelcolor=INK)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    handles = [plt.Line2D([], [], marker="o", ms=8, mfc=c, mec=SURFACE, mew=2, lw=2, color=c, label=l) for _, (l, c) in ARMS.items()]
    handles.append(plt.Line2D([], [], marker="D", ms=6, mfc="none", mec="#9a9993", mew=1.3, ls="none", label="A0 rate negated (largest possible reduction)"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.42, -0.14), ncol=3, fontsize=8, frameon=False, labelcolor=INK2, columnspacing=1.6, handletextpad=0.5)
    fig.suptitle("Neither text-level defense moves attack execution on independently authored scenarios", fontsize=11, color=INK, x=0.01, ha="left", y=0.995)
    fig.text(0.01, 0.01, "Points: mean paired difference in exec_executed; whiskers: paired bootstrap 95% CI (5000 resamples). Pairs = same family, instance, model (24 per family, 168 pooled;\n"
             "B3: 167 pooled). PHASE1-CORE vs A0 differs in 8 of 168 pairs although its input is unchanged: run-to-run noise at temperature 0. Exploratory.", fontsize=7.2, color=INK2, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.08, 1, 0.965))
    fig.savefig(OUT / "fig3_defended_vs_a0.png", dpi=200, facecolor=SURFACE)
    fig.savefig(OUT / "fig3_defended_vs_a0.svg", facecolor=SURFACE, metadata={"Date": None})
    for (arm, fam), (m, lo, hi, n, a0r) in res.items():
        if fam == "ALL":
            print(arm, f"n={n} diff={m:+.3f} CI[{lo:+.3f},{hi:+.3f}] a0={a0r:.3f}")


if __name__ == "__main__":
    main()
