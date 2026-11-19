"""Сравнение однородных TEM-линий одинакового поперечного сечения."""
import argparse
import csv
from math import e, log10, pi, sqrt
from pathlib import Path

LIGHT_SPEED = 299_792_458


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length-mm", type=float, default=100.0)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("laminate_inputs.csv"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.length_mm <= 0:
        parser.error("Длина должна быть положительной")
    length_m = args.length_mm / 1000
    with args.input.open(encoding="utf-8", newline="") as source:
        materials = list(csv.DictReader(source))
    if not materials:
        raise ValueError("Таблица материалов пуста")
    reference_dk = float(materials[0]["dk"])
    reference_frequency = float(materials[0]["frequency_ghz"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.writer(destination)
        writer.writerow(["material", "frequency_ghz", "length_mm", "dielectric_loss_db",
                         "delay_ns", "z_ratio_to_first_material"])
        for row in materials:
            dk, df, frequency_ghz = map(float, (row["dk"], row["df"], row["frequency_ghz"]))
            if frequency_ghz != reference_frequency or dk < 1 or not 0 <= df < 0.1:
                raise ValueError(f"Вне области сравнения: {row}")
            attenuation_nepers_per_m = pi * frequency_ghz * 1e9 * sqrt(dk) * df / LIGHT_SPEED
            loss_db = 20 * log10(e) * attenuation_nepers_per_m * length_m
            delay_ns = length_m * sqrt(dk) / LIGHT_SPEED * 1e9
            impedance_ratio = sqrt(reference_dk / dk)
            writer.writerow([row["material"], frequency_ghz, args.length_mm, f"{loss_db:.4f}",
                             f"{delay_ns:.4f}", f"{impedance_ratio:.4f}"])


if __name__ == "__main__":
    main()
