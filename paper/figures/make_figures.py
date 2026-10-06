"""Regenerate manuscript figures (SVG, stdlib only) from results/f3_confirmatory/RESULTS.md.

Usage: python paper/figures/make_figures.py   (writes fig1_paired_diff.svg, fig2_loss_cost.svg here)
No new data: every plotted value is parsed from RESULTS.md.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "results" / "f3_confirmatory" / "RESULTS.md"
txt = SRC.read_text()

arms = {}
for m in re.finditer(r"^\| (\w+_sem) \| ([\d.]+) \[([\d.]+),([\d.]+)\] \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|", txt, re.M):
    arms[m[1]] = dict(loss=float(m[2]), lo=float(m[3]), hi=float(m[4]), asr=float(m[5]), util=float(m[6]), cost=float(m[7]))

diffs = []
for m in re.finditer(r"^\| (\w+_sem) vs (\w+_sem) \| (pooled[^|]*|uniform25[^|]*|burst[^|]*) \| ([+-][\d.]+) \| \[([+-][\d.]+), ([+-][\d.]+)\] \|", txt, re.M):
    diffs.append((m[1], m[2], m[3].strip(), float(m[4]), float(m[5]), float(m[6])))

NAME = {"fixed_l1_sem": "fixed L1", "fixed_l2_sem": "fixed L2", "fixed_l3_sem": "fixed L3",
        "adaptive_dev_sem": "adaptive_dev", "adaptive_exp_sem": "adaptive_exp"}
FONT = 'font-family="sans-serif" font-size="12" fill="#222"'


def fig1():
    rows = [d for d in diffs if d[2].startswith("pooled")]
    w, h, left, right, top = 640, 60 + 34 * len(rows), 250, 30, 40
    xmin, xmax = -0.10, 0.09
    sx = lambda v: left + (v - xmin) / (xmax - xmin) * (w - left - right)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="10" y="22" {FONT} font-weight="bold">Paired loss difference (adaptive - fixed), pooled, 95% bootstrap CI</text>']
    for v in (-0.04, 0.0, 0.04, 0.08):
        s.append(f'<line x1="{sx(v)}" y1="{top}" x2="{sx(v)}" y2="{h-20}" stroke="{"#222" if v == 0 else "#ddd"}"/>')
        s.append(f'<text x="{sx(v)-12}" y="{h-5}" {FONT}>{v:+.2f}</text>')
    s.append(f'<rect x="{sx(-0.02)}" y="{top}" width="{sx(0.02)-sx(-0.02)}" height="{h-20-top}" fill="#9cf" fill-opacity="0.2"/>')
    for i, (a, f, _, mean, lo, hi) in enumerate(rows):
        y = top + 20 + 34 * i
        col = "#c33" if lo > 0 else ("#2a7" if hi < 0 else "#777")
        s.append(f'<text x="8" y="{y+4}" {FONT}>{NAME[a]} vs {NAME[f]}{"  (PRIMARY)" if (a, f) == ("adaptive_dev_sem", "fixed_l1_sem") else ""}</text>')
        s.append(f'<line x1="{sx(lo)}" y1="{y}" x2="{sx(hi)}" y2="{y}" stroke="{col}" stroke-width="2"/>')
        s.append(f'<circle cx="{sx(mean)}" cy="{y}" r="4" fill="{col}"/>')
    s.append("</svg>")
    (HERE / "fig1_paired_diff.svg").write_text("\n".join(s))


def fig2():
    w, h, l, b, t = 520, 380, 60, 50, 40
    xs = [a["cost"] for a in arms.values()]
    ys = [a["asr"] for a in arms.values()]
    x0, x1, y0, y1 = 0.06, 0.20, -0.002, 0.022
    sx = lambda v: l + (v - x0) / (x1 - x0) * (w - l - 20)
    sy = lambda v: h - b - (v - y0) / (y1 - y0) * (h - b - t)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="10" y="22" {FONT} font-weight="bold">ASR vs mean cost per arm (confirmatory F3, llama-3.1-8b)</text>',
         f'<line x1="{l}" y1="{h-b}" x2="{w-20}" y2="{h-b}" stroke="#222"/><line x1="{l}" y1="{t}" x2="{l}" y2="{h-b}" stroke="#222"/>',
         f'<text x="{w//2-30}" y="{h-12}" {FONT}>mean cost</text>',
         f'<text x="8" y="{t+4}" {FONT}>ASR</text>']
    for v in (0.08, 0.12, 0.16, 0.20):
        s.append(f'<text x="{sx(v)-12}" y="{h-b+16}" {FONT}>{v:.2f}</text>')
    for v in (0.0, 0.01, 0.02):
        s.append(f'<text x="{l-38}" y="{sy(v)+4}" {FONT}>{v:.2f}</text>')
    for k, a in arms.items():
        col = "#c60" if k.startswith("adaptive") else "#357"
        s.append(f'<circle cx="{sx(a["cost"])}" cy="{sy(a["asr"])}" r="5" fill="{col}"/>')
        s.append(f'<text x="{sx(a["cost"])+8}" y="{sy(a["asr"])-6}" {FONT}>{NAME[k]} (loss {a["loss"]:.3f})</text>')
    s.append("</svg>")
    (HERE / "fig2_loss_cost.svg").write_text("\n".join(s))


assert len(arms) == 5 and len(diffs) == 18, (len(arms), len(diffs))
fig1()
fig2()
print("wrote", [p.name for p in HERE.glob("*.svg")])
