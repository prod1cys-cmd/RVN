"""Оценка покрытия внешних слоёв по положительным Gerber POS26."""
import argparse
import csv
import hashlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import re

import numpy as np
from pygerber.gerberx3.api.v2 import (
    ColorScheme, GerberFile, OnParserErrorEnum,
)
from pygerber.gerberx3.renderer2.raster import RasterRenderer2, RasterRenderer2Hooks


def rectangle(path):
    data = path.read_text()
    if "%FSLAX44Y44*%" not in data or "%MOMM*%" not in data:
        raise ValueError(f"Неожиданный формат GM1: {path}")
    x = y = 0
    segments = set()
    for px, py, op in re.findall(r"X?(-?\d+)?(?:Y(-?\d+))?D0([12])\*", data):
        new_x = int(px) if px else x
        new_y = int(py) if py else y
        if op == "1":
            segments.add(frozenset(((x, y), (new_x, new_y))))
        x, y = new_x, new_y
    points = set().union(*segments)
    left, right = min(x for x, _ in points), max(x for x, _ in points)
    bottom, top = min(y for _, y in points), max(y for _, y in points)
    ordered = [(left, bottom), (right, bottom), (right, top), (left, top)]
    if segments != {frozenset((ordered[i - 1], ordered[i])) for i in range(4)}:
        raise ValueError(f"Нужна явная геометрия непрямоугольного контура: {path}")
    return tuple(val / 10000 for val in (left, bottom, right, top))


def process(job):
    path, dpmm, (left, bottom, right, top) = job
    if "TF.FilePolarity,Positive" not in path.read_text():
        raise ValueError(f"Неподдерживаемая полярность: {path}")
    parsed = GerberFile.from_file(path).parse(on_parser_error=OnParserErrorEnum.Raise)
    bounds = parsed.get_info()
    if (float(bounds.min_x_mm) < left or float(bounds.max_x_mm) > right
            or float(bounds.min_y_mm) < bottom or float(bounds.max_y_mm) > top):
        raise ValueError(f"Медь за контуром: {path}")
    output = RasterRenderer2(RasterRenderer2Hooks(color_scheme=ColorScheme.COPPER, dpmm=dpmm)).render(
        parsed._command_buffer
    )
    # Тёмно-зелёный (40,143,40) – медь, чёрный – фон,
    # светло-зелёный – очищенные участки.
    pixel = np.asarray(output.image.getchannel("G"))
    dark = pixel == 143
    x0 = round((float(bounds.min_x_mm) - left) * dpmm)
    y0 = round((top - float(bounds.max_y_mm)) * dpmm)
    copper_count = int(np.count_nonzero(dark))
    bounds_area = (right - left) * (top - bottom)
    rows = []
    for row in range(4):
        for col in range(4):
            xa = round(col * (right - left) * dpmm / 4)
            xb = round((col + 1) * (right - left) * dpmm / 4)
            ya = round(row * (top - bottom) * dpmm / 4)
            yb = round((row + 1) * (top - bottom) * dpmm / 4)
            sample = dark[max(0, ya - y0):max(0, yb - y0),
                           max(0, xa - x0):max(0, xb - x0)]
            count = int(np.count_nonzero(sample))
            rows.append((row + 1, col + 1, count, 100 * count / ((xb - xa) * (yb - ya))))
    if sum(row[2] for row in rows) != copper_count:
        raise ValueError(f"Проверка сохранения площади не пройдена: {path}")
    return path.name, dpmm, copper_count / dpmm ** 2, 100 * copper_count / (dpmm ** 2 * bounds_area), rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gerbers", type=Path)
    parser.add_argument("--output", type=Path, default=Path("."))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    jobs = []
    sources = []
    for rev in ("12", "13"):
        contour = args.gerbers / f"POS26_{rev}.GM1"
        bounds = rectangle(contour)
        sources.append(contour)
        for extension in ("GTL", "GBL"):
            path = args.gerbers / f"POS26_{rev}.{extension}"
            sources.append(path)
            jobs.extend((path, dpmm, bounds) for dpmm in (30, 60))
    sources.append(args.gerbers / "POS26_stack.csv")
    with (args.output / "input_sha256.txt").open("w", encoding="utf-8") as target:
        for source in sources:
            target.write(f"{hashlib.sha256(source.read_bytes()).hexdigest()}  {source.name}\n")
    with ProcessPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(process, jobs))
    with (args.output / "copper_coverage.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(("filename", "pixels_per_mm", "copper_mm2", "fill_pct"))
        writer.writerows((name, dpmm, f"{area:.4f}", f"{fill:.5f}") for name, dpmm, area, fill, _ in results)
    with (args.output / "copper_tiles.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(("filename", "pixels_per_mm", "row_y_top_to_bottom", "column_x_left_to_right", "fill_pct"))
        writer.writerows((name, dpmm, row, col, f"{fill:.5f}")
                         for name, dpmm, _, _, tiles in results for row, col, _, fill in tiles)


if __name__ == "__main__":
    main()
