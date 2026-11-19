"""Расчёт частот наложения и параметрического бюджета шума платы ПОС."""
import csv
import json
from itertools import combinations, product
from math import ceil, floor, log10, pi, sqrt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "inputs.json").read_text())
fs = data["sampling_mhz"]
lo, hi = data["if_band_mhz"]
limit = data["spectral_search_max_mhz"]
sources = data["sources"]


def alias(frequency):
    return abs((frequency + fs / 2) % fs - fs / 2)


def image_bands(cutoff):
    for order in range(ceil(cutoff / fs) + 1):
        center = order * fs
        for low, high in [(center - hi, center - lo), (center + lo, center + hi)]:
            low = max(0, low)
            high = min(cutoff, high)
            if high > low:
                yield low, high


def write_csv(name, header, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


harmonics = []
for source in sources:
    frequency = source["mhz"]
    last = source.get("max_harmonic", floor(limit / frequency))
    for order in range(1, last + 1):
        original = frequency * order
        folded = alias(original)
        if lo <= folded <= hi:
            harmonics.append((source["name"], order, original, folded, source["status"]))

write_csv("harmonics.csv", ("Источник", "Порядок", "Частота, МГц",
                           "Наложение, МГц", "Условие"), harmonics)
intermod = []
for a, b in combinations(sources, 2):
    for first, second in product(range(1, 3), (-2, -1, 1, 2)):
        if first + abs(second) > 3:
            continue
        frequency = abs(first * a["mhz"] + second * b["mhz"])
        if frequency <= limit and lo <= alias(frequency) <= hi:
            intermod.append((a["name"], b["name"], first, second,
                             round(frequency, 6), round(alias(frequency), 6)))
write_csv("intermodulation.csv", ("Первый источник", "Второй источник", "m", "n",
                                 "|m f1 + n f2|, МГц", "Наложение, МГц"), intermod)

n = data["noise"]
bandwidth = (hi - lo) * 1e6
u_full_scale = n["adc_full_scale_vpp"] / (2 * sqrt(2))
vga_density = sqrt(1.380649e-23 * n["temperature_k"] * n["effective_resistance_ohm"])
vga_density *= 10 ** ((n["vga_nf_db"] + n["vga_gain_db"]) / 20)
adc_snr_min = n["adc_snr_fs_db"][0]
adc_density = u_full_scale * 10 ** (-adc_snr_min / 20) / sqrt(fs * 1e6 / 2)

responses = [("Только рабочая полоса", 1),
             ("Коэффициент исходной оценки Книги 3", 2.5),
             ("Идеально плоская АЧХ до 500 МГц", sum(
                 high - low for low, high in image_bands(n["vga_idealized_cutoff_mhz"])
             ) / (hi - lo))]
noise_rows = []
for scenario, multiplier in responses:
    total = sqrt(bandwidth * (multiplier * vga_density ** 2 + adc_density ** 2))
    noise_rows.append((scenario, multiplier, round(1e9 * vga_density, 3),
                       round(1e9 * adc_density, 3), round(total * 1e3, 4),
                       round(20 * log10(u_full_scale / total), 3)))
write_csv("noise_budget.csv", ("Условие", "Kн", "eш, нВ/√Гц", "eАЦП, нВ/√Гц",
                               "Uш, мВ СКЗ", "D, дБ"), noise_rows)

jitter_rows = []
for freq, adc_snr in product([lo, data["if_center_mhz"], hi], n["adc_snr_fs_db"]):
    freq_hz = freq * 1e6
    sigma = n["clock_jitter_fs"] * 1e-15
    noise_ratio = (2 * pi * freq_hz * sigma) ** 2
    adc_noise_ratio = 10 ** (-adc_snr / 10)
    loss = 10 * log10(1 + noise_ratio / adc_noise_ratio)
    max_sigma = sqrt(adc_noise_ratio * (10 ** (n["jitter_budget_db"] / 10) - 1))
    max_sigma /= 2 * pi * freq_hz
    sampled_snr = adc_snr - loss + 10 * log10(fs * 1e6 / 2 / bandwidth)
    jitter_rows.append((freq, adc_snr, round(loss, 4), round(max_sigma * 1e15, 2),
                        round(sampled_snr, 3)))
write_csv("jitter_budget.csv", ("Частота ПЧ, МГц", "Опорное SNR АЦП, дБ",
                               "Потеря при 330 фс, дБ", "σ для потери 0,1 дБ, фс",
                               "SNR в полосе, дБ"), jitter_rows)

assert list(image_bands(500)) == [(50, 70), (330, 350), (450, 470)]
assert alias(340) == alias(460) == alias(60) == 60
assert alias(60) == 12 * 5
assert abs(noise_rows[2][-1] - 51.4) < 0.2

fig, (top, bottom) = plt.subplots(2, 1, figsize=(9.5, 5), layout="constrained")
x = list(range(limit + 1))
top.plot(x, [alias(f) for f in x], color="#235384", linewidth=1.8)
top.axhspan(lo, hi, color="#93ca99", alpha=0.5, label="Полоса обработки")
for low, high in image_bands(limit):
    top.axvspan(low, high, color="#dca446", alpha=0.32)
top.axvline(n["vga_idealized_cutoff_mhz"], color="0.35", linestyle="--",
            label="Условная граница спектра шума")
top.set(xlim=(0, limit), ylim=(0, fs / 2), xlabel="Аналоговая частота, МГц",
        ylabel="После дискретизации, МГц")
top.legend(loc="upper right", fontsize=8)
groups = ("12 МГц", "10 МГц", "25 МГц", "50 МГц", "RGMII")
labels = ("USB", "Опора", "STM32 / PHY", "PS", "RGMII")
match = (1, 0, 2, 4, 7)
for row, (label, index) in enumerate(zip(labels, match)):
    label_freqs = sorted({h[3] for h in harmonics if h[0] == sources[index]["name"]})
    if label_freqs:
        bottom.scatter(label_freqs, [row] * len(label_freqs), s=35, color="#235384")
bottom.axvline(data["if_center_mhz"], color="0.3", linestyle="--", linewidth=1)
bottom.set(xlim=(lo - 1, hi + 1), yticks=range(len(groups)), yticklabels=labels,
           xlabel="Частота наложения в полосе обработки, МГц")
bottom.grid(axis="x", alpha=0.3)
fig.savefig(HERE / "frequency_plan.png", dpi=180)
