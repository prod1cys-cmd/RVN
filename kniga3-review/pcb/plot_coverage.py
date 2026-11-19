"""Карта локального заполнения медью по результатам copper_coverage.py."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np


def main():
    outputs = Path(__file__).with_name("outputs")
    maps = {extension: np.full((4, 4), np.nan) for extension in ("GTL", "GBL")}
    with (outputs / "copper_tiles.csv").open(encoding="utf-8", newline="") as source:
        for line in csv.DictReader(source):
            if line["filename"].startswith("POS26_13.") and line["pixels_per_mm"] == "60":
                layer = line["filename"].split(".")[1]
                i = int(line["row_y_top_to_bottom"]) - 1
                j = int(line["column_x_left_to_right"]) - 1
                maps[layer][i, j] = float(line["fill_pct"])
    if any(np.isnan(data).any() for data in maps.values()):
        raise ValueError("Требуются данные по всем ячейкам L1 и L8")
    top, bottom = maps.values()
    fig, axes = plt.subplots(1, 3, figsize=(10.7, 4.2), layout="constrained")
    for i, (axis, values, title) in enumerate(zip(
        axes, (top, bottom, top - bottom),
        ("L1 · медь, %", "L8 · медь, %", "L1 − L8 · п. п.")
    )):
        lower, upper, cmap = (-100, 100, "coolwarm") if i == 2 else (0, 100, "viridis")
        rendered = axis.imshow(values, vmin=lower, vmax=upper, cmap=cmap,
                              extent=(0, 160, 0, 233.35), origin="upper")
        axis.set_title(title)
        axis.set_xlabel("X, мм")
        axis.set_xticks([0, 40, 80, 120, 160])
        axis.set_yticks([0, 58.3375, 116.675, 175.0125, 233.35], ["0", "58", "117", "175", "233"])
        axis.set_ylabel("Y, мм")
        for row in range(4):
            for col in range(4):
                value = values[row, col]
                rgba = rendered.cmap(rendered.norm(value))
                gray = rgba[0] * 0.2126 + rgba[1] * 0.7152 + rgba[2] * 0.0722
                axis.text((col + 0.5) * 40, 233.35 - (row + 0.5) * 233.35 / 4,
                          f"{value:.1f}".replace(".", ","), ha="center", va="center",
                          fontsize=9, color="black" if gray > 0.52 else "white")
    fig.suptitle("Распределение меди наружных слоёв по Gerber POS26_13", fontsize=13)
    fig.savefig(outputs / "copper_coverage_POS26_13.png", dpi=210, facecolor="white")


if __name__ == "__main__":
    main()
