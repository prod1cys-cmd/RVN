"""Условные бюджеты разрядности, двухканального диапазона и развязки."""
import csv
import json
from itertools import product
from math import log10, pi, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
inputs = json.loads((HERE / "architecture_inputs.json").read_text())
headroom = inputs["headroom_db"]
noise_gain = 10 * log10(inputs["sampling_mhz"] / (2 * inputs["bandwidth_mhz"]))
jitter_s = inputs["jitter_fs"] * 1e-15
phase_error = 2 * pi * inputs["tone_mhz"] * 1e6 * jitter_s
reference_snr = inputs["adc_reference_snr_dbfs"]


def combined_snr(baseline, jitter_weight):
    return -10 * log10(10 ** (-(baseline + noise_gain) / 10) + jitter_weight * phase_error ** 2)


def write_csv(name, columns, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)


quantization_rows = []
for bits in inputs["nominal_bits"]:
    ideal = 6.02 * bits + 1.76
    quantization_rows.append((bits, round(ideal, 2), round(ideal + noise_gain, 2),
                              round(ideal + noise_gain - headroom, 2),
                              round(combined_snr(ideal, 10 ** (-noise_gain / 10)), 3),
                              round(combined_snr(ideal, 1), 3)))
write_csv("quantization.csv", ("Разрядов", "Идеал, полоса Найквиста, дБ",
                               "Идеал в 20 МГц, дБ", "Идеал при запасе 6 дБ, дБ",
                               "Идеальный АЦП и распределённый джиттер, дБ",
                               "Идеальный АЦП и вся мощность джиттера в полосе, дБ"),
          quantization_rows)

isolation_rows = []
for dynamic, margin in product(inputs["target_dynamics_db"], inputs["isolation_margin_db"]):
    required = dynamic + margin
    isolation_rows.append((dynamic, margin, required, inputs["test_isolation_db"] - required))
write_csv("isolation.csv", ("Разность входных уровней, дБ", "Иллюстративный запас, дБ",
                            "Требуемая развязка при равных иных коэффициентах, дБ",
                            "Запас П-06 относительно сценария, дБ"), isolation_rows)

# D is referenced to usable maximum. The input limit of the lower gain path
# moves up by gain_difference, while the high gain path sets the low endpoint.
single_usable = inputs["mockup_noise_ratio_dbfs"] - headroom
dual_rows = []
for dynamic, overlap in product(inputs["target_dynamics_db"], inputs["candidate_overlap_db"]):
    gain_difference = max(0, dynamic - single_usable)
    max_gain_difference = single_usable - overlap
    dual_rows.append((dynamic, overlap, round(single_usable, 3), round(gain_difference, 3),
                      round(max_gain_difference, 3), round(2 * single_usable - overlap, 3),
                      gain_difference <= max_gain_difference))
write_csv("dual_paths.csv", ("Сценарий, дБ", "Перекрытие, дБ", "Диапазон ветви, дБ",
                             "Минимальная разность усилений, дБ",
                             "Максимальная разность усилений, дБ",
                             "Максимальный диапазон пары, дБ", "Выполнимо математически"),
          dual_rows)

write_csv("pulse_duty.csv", ("Режим", "Длительность, мкс", "Частота повторения, Гц",
                             "Коэффициент заполнения", "Средняя к импульсной мощности, дБ"),
          [(label, pulse, prf, round(pulse * 1e-6 * prf, 8),
            round(10 * log10(pulse * 1e-6 * prf), 3)) for label, pulse, prf in inputs["timings"]])

frontend = inputs["analog_input"]
z_ref = frontend["sma_reference_ohm"]
series = frontend["input_series_ohm"]
shunt = frontend["input_shunt_ohm"]
gain = 10 ** (frontend["vga_nominal_gain_db"] / 20)
g_min_vrms = frontend["vga_target_vrms"] / gain
g_max_vrms = frontend["vga_max_input_vpp"] / (2 * sqrt(2))


def dbm(voltage, resistance):
    return 10 * log10(voltage ** 2 / resistance / 0.001)


signal_path_rows = []
for vga_r in sorted([frontend["vga_input_nominal_ohm"], *frontend["vga_input_range_ohm"]]):
    z_sma = (series + vga_r) * shunt / (series + vga_r + shunt)
    divider = vga_r / (series + vga_r)
    transducer_voltage_ratio = 2 * z_sma / (z_ref + z_sma) * divider
    minimum = dbm(g_min_vrms / transducer_voltage_ratio, z_ref)
    maximum = dbm(g_max_vrms / transducer_voltage_ratio, z_ref)
    signal_path_rows.append((vga_r, round(z_sma, 3), round(divider, 5),
                             round(20 * log10(transducer_voltage_ratio) + 10 * log10(z_ref / vga_r), 3),
                             round(minimum, 3), round(maximum, 3)))
write_csv("connector_reference.csv", ("Rвх AD8367, Ом", "Расчётное Rвх SMA, Ом",
                                     "U_INPT/U_SMA", "P_INPT/Pдост. 50 Ом, дБ",
                                     "При 2,65 мВ на INPT, дБм", "При 0,7 В двойного размаха, дБм"),
          signal_path_rows)

ref_split = inputs["reference_split"]
z = ref_split["impedance_ohm"]
z_double = z / 2
split_voltage_ratio = (z_double / (z + z_double)) / (z / (z + z))
single_ref = ref_split["low_source_dbm"] - ref_split["pad_db"]
split_ref = single_ref + 20 * log10(split_voltage_ratio)
print(f"Power-reference shift to AD8367 input, nominal: {signal_path_rows[1][3]:.3f} dB")
print(f"10 MHz X12 floor scenario, direct / with 50 Ω tee: {single_ref:.2f} / {split_ref:.2f} dBm")
assert abs(signal_path_rows[1][2] - 0.535) < 0.001
assert abs(split_ref + 5.52) < 0.01

assert quantization_rows[1][3] == 102.08
assert dual_rows[3][-1] and not dual_rows[4][-1]
assert isolation_rows[2][2] == 80
print(f"ADC-only at 60 MHz, distributed jitter: {combined_snr(reference_snr, 10 ** (-noise_gain / 10)):.3f} dB")
print(f"ADC-only if all jitter power is in band: {combined_snr(reference_snr, 1):.3f} dB")
