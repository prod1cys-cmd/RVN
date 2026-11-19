"""Обработка частот кольцевого резонатора и S21 двух купонов."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

C = 299_792_458


def positive(value):
    number = float(value)
    if not np.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("ожидается положительное конечное значение")
    return number


def ring_permittivity(circumference_mm, frequency_ghz, mode):
    circumference_m = circumference_mm * 1e-3
    frequency_hz = frequency_ghz * 1e9
    return (mode * C / (frequency_hz * circumference_m)) ** 2


def read_line_data(path):
    columns = ("frequency_hz", "s21_short_real", "s21_short_imag", "s21_long_real", "s21_long_imag")
    with path.open(encoding="utf-8-sig", newline="") as source:
        data = np.asarray([[float(row[key]) for key in columns] for row in csv.DictReader(source)])
    if len(data) < 3 or not np.all(np.isfinite(data)):
        raise ValueError("Требуются не менее трёх частот и конечные значения CSV")
    frequencies, short_real, short_imag, long_real, long_imag = data.T
    short = short_real + 1j * short_imag
    long = long_real + 1j * long_imag
    if frequencies[0] <= 0 or np.any(np.diff(frequencies) <= 0):
        raise ValueError("Частоты должны быть положительными и строго возрастающими")
    if np.any(short == 0) or np.any(long == 0):
        raise ValueError("Нулевой S21 не позволяет определить фазу")
    return frequencies, short, long


def line_delay(path, length_difference_mm):
    frequencies, short, long = read_line_data(path)
    phase = np.unwrap(np.angle(long / short))
    radian_frequency = 2 * np.pi * (frequencies - frequencies.mean())
    slope, offset = np.polyfit(radian_frequency, phase, 1)
    residual = phase - (slope * radian_frequency + offset)
    delay_s = -float(slope)
    if delay_s <= 0:
        raise ValueError("Отрицательная или нулевая задержка. Проверить порядок линий и развёртку фазы")
    return {
        "sample_count": len(frequencies),
        "f_min_hz": float(frequencies[0]),
        "f_max_hz": float(frequencies[-1]),
        "group_delay_difference_ps": delay_s * 1e12,
        "group_delay_per_mm_ps": delay_s * 1e12 / length_difference_mm,
        "phase_fit_residual_rms_deg": float(np.rad2deg(np.sqrt(np.mean(residual ** 2)))),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="operation", required=True)
    ring = subcommands.add_parser("ring", help="Оценка Dk_eff из моды кольца")
    ring.add_argument("--circumference-mm", required=True, type=positive)
    ring.add_argument("--frequency-ghz", required=True, type=positive)
    ring.add_argument("--mode", required=True, type=int)
    line = subcommands.add_parser("line", help="Групповая задержка между двумя купонами")
    line.add_argument("csv", type=Path)
    line.add_argument("--length-difference-mm", required=True, type=positive)
    args = parser.parse_args()
    if args.operation == "ring":
        if args.mode < 1:
            parser.error("Номер моды должен быть целым и положительным")
        data = {"effective_relative_permittivity": ring_permittivity(
            args.circumference_mm, args.frequency_ghz, args.mode)}
    else:
        data = line_delay(args.csv, args.length_difference_mm)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
