"""Figures for the printed frequency plan, from the same inputs as frequency_noise.py."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

here = Path(__file__).resolve().parent
data = json.loads((here / "inputs.json").read_text())
lo, hi = data["if_band_mhz"]
fs = data["sampling_mhz"]
ink, amber = "#244f67", "#92531c"
plt.rcParams.update({"font.size": 10, "axes.spines.right": False, "axes.spines.top": False})

bands = [(lo, hi), (fs - hi, fs - lo), (fs + lo, fs + hi)]
fig, ax = plt.subplots(figsize=(6.55, 2.85))
fig.subplots_adjust(left=.07, right=.97, bottom=.30, top=.86)
ax.set(xlim=(0, 500), ylim=(0, 1), yticks=[], xlabel="Частота на аналоговом входе АЦП, МГц")
ax.spines["left"].set_visible(False)
for i, (a, b) in enumerate(bands):
    color = ink if i == 0 else amber
    ax.axvspan(a, b, color=color, alpha=.16)
    ax.hlines(.42, a, b, color=color, lw=4)
    # Text alignment staggers the two nearest image bands.
    ax.text((a+b)/2, .68, f"{a}–{b}", ha="center", color=color, weight="bold")
    left, right = ((hi, lo) if i == 1 else (lo, hi))
    ax.text((a+b)/2, .17, f"{left} → {right}", ha="center", fontsize=9)
for x, label in [(fs / 2, "граница Найквиста"), (fs, "частота выборок")]:
    ax.axvline(x, color=".53", ls=":", lw=.9)
    ax.text(x, .99, label, ha="center", va="bottom", fontsize=9, color=".26")
ax.set_xticks([0, 100, 200, 300, 400, 500])
fig.text(.52,.035,"Стрелки показывают ход частоты после дискретизации, МГц.", ha="center", fontsize=10)
fig.savefig(here / "sampling_bands.png", dpi=320)
plt.close(fig)

with (here / "harmonics.csv").open() as f:
    harmonics = list(csv.DictReader(f))
with (here / "intermodulation.csv").open() as f:
    mixed = list(csv.DictReader(f))
groups = [
    ("Опора 10 МГц", 0), ("USB 12 МГц", 1), ("STM32 / PHY 25 МГц", 2),
    ("PS 50 МГц", 4), ("RGMII 125 МГц", 7), ("Суммы и разности", None)
]
fig, ax = plt.subplots(figsize=(6.55, 3.45))
fig.subplots_adjust(left=.29, right=.96, top=.94, bottom=.30)
for i, (name, index) in enumerate(groups):
    row = len(groups) - i
    ax.hlines(row, lo, hi, color=".87", lw=.65)
    if index is None:
        peaks = {(float(r["|m f1 + n f2|, МГц"]), float(r["Наложение, МГц"])) for r in mixed}
    else:
        peaks = {(float(r["Частота, МГц"]), float(r["Наложение, МГц"])) for r in harmonics
                 if r["Источник"] == data["sources"][index]["name"]}
    for direct, yoffset, marker, color in [(True,.13,"o",ink), (False,-.13,"D",amber)]:
        folded = {y for x,y in peaks if (lo <= x <= hi) == direct}
        if folded:
            ax.scatter(sorted(folded), [row+yoffset]*len(folded), s=35, marker=marker,
                       edgecolor=color, facecolor=color if direct else "white", lw=1.1)
ax.set(xticks=range(lo,hi+1,2), xlim=(lo-.5,hi+.5), ylim=(.5,6.55),
       yticks=list(reversed(range(1,7))), yticklabels=[g[0] for g in groups],
       xlabel="Частота после дискретизации, МГц")
ax.grid(axis="x", lw=.45, color=".82")
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y",length=0)
fig.legend(handles=[Line2D([],[],color=ink,marker="o",linestyle="none",label="В рабочей полосе"),
                    Line2D([],[],color=amber,marker="D",markerfacecolor="white",linestyle="none",
                           label="Наложение из другой полосы")],
           loc="lower center",frameon=False, ncol=2, columnspacing=.85, handletextpad=.3)
fig.savefig(here / "spur_map.png", dpi=320)

# I2, table 9. Branch labels describe modes rather than measured outputs.
outputs = [
    (6, "400 МГц", "DCLK_ADC, GLBLCLK_0"),
    (48, "50 МГц", "X21; отключён в П-03"),
    (240, "10 МГц", "X20; только в РМ"),
    (768, "3,125 МГц", "SYSREF АЦП и ПЛИС"),
]
vco = 2400
fig, ax = plt.subplots(figsize=(6.55, 2.65))
fig.subplots_adjust(left=.03, right=.97, top=.94, bottom=.04)
ax.set(xlim=(0, 1), ylim=(0, 1))
ax.axis("off")
ys = [.82, .60, .38, .16]
ax.plot([.30,.38], [.49,.49], lw=1.15, color=ink)
ax.plot([.38,.38], [ys[-1],ys[0]], lw=1.15, color=ink)
ax.text(.15,.49,"HMC7044\nГУН 2400 МГц", ha="center", va="center", weight="bold",
        bbox={"facecolor":"#e8eff3","edgecolor":ink,"boxstyle":"round,pad=0.65"})
for (divider, freq, label), y in zip(outputs, ys):
    assert vco / divider == float(freq.split()[0].replace(",","."))
    ax.annotate("", xy=(.51,y), xytext=(.38,y), arrowprops={"arrowstyle":"->","color":ink})
    ax.text(.443,y+.017,f"÷{divider}", ha="center", va="bottom", fontsize=9)
    ax.text(.53,y+.018,freq, va="center", weight="bold")
    ax.text(.53,y-.067,label, va="center", fontsize=9.5)
fig.savefig(here / "clock_distribution.png", dpi=320)
