"""Независимая проверка оценки площади через Gerbonara и CairoSVG."""
import argparse
import csv
from io import BytesIO
from pathlib import Path

import cairosvg
from gerbonara import GerberFile
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gerbers", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Контрольный контур POS26_13.GM1 в миллиметрах.
    width, height = 160, 233.35
    dpmm = 40
    rows = []
    for extension in ("GTL", "GBL"):
        path = args.gerbers / f"POS26_13.{extension}"
        svg = GerberFile.open(path).to_svg(force_bounds=((0, 0), (width, height)))
        png = cairosvg.svg2png(bytestring=str(svg).encode(), output_width=round(width * dpmm),
                               output_height=round(height * dpmm), background_color="white")
        channel = Image.open(BytesIO(png)).convert("L")
        counts = channel.histogram()
        # Взвешивание полутонов по доле покрытия по краям штрихов.
        area = sum((1 - level / 255) * count for level, count in enumerate(counts)) / dpmm ** 2
        rows.append((path.name, dpmm, f"{area:.4f}", f"{100 * area / (width * height):.5f}"))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("filename", "pixels_per_mm", "copper_mm2", "fill_pct"))
        writer.writerows(rows)


if __name__ == "__main__":
    main()
