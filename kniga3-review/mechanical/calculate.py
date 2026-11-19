"""Воспроизводимая проверка расчётов разделов 4.4 и 9 Книги 3."""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUTS = json.loads((ROOT / "inputs.json").read_text(encoding="utf-8"))


def write_csv(name, header, rows):
    with (ROOT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def effective_acceleration(frequency, model):
    if frequency < model["frequency_break_hz"]:
        displacement = model["displacement_peak_m"]
        return displacement * (2 * math.pi * frequency) ** 2 / model["standard_gravity_m_s2"]
    return model["fixed_acceleration_peak_g"]


def phase_difference_peak(frequency, acceleration, sensitivity, carrier, delay, period):
    modulation_index = sensitivity * acceleration * carrier / frequency
    return abs(4 * modulation_index * math.sin(math.pi * frequency * delay)
               * math.sin(math.pi * frequency * period))


def two_pulse_improvement_db(phase_peak):
    return 10 * math.log10(4 / phase_peak ** 2)


def calculate_vibration(model):
    step = model["frequency_grid_step_hz"]
    low = model["frequency_low_hz"]
    high = model["frequency_high_hz"]
    frequencies = [low + i * step for i in range(round((high - low) / step) + 1)]
    rows = []
    for band, carrier in model["carrier_hz"].items():
        for delay in model["delay_s"]:
            for period in model["pulse_period_s"]:
                def phase_at(frequency):
                    return phase_difference_peak(
                        frequency, effective_acceleration(frequency, model),
                        model["sensitivity_per_g"], carrier, delay, period,
                    )
                worst_frequency = max(frequencies, key=phase_at)
                phase_peak = phase_at(worst_frequency)
                assert phase_peak < 0.1, "Недопустимо приближение малой фазы"
                improvement = two_pulse_improvement_db(phase_peak)
                sensitivity_limit = model["sensitivity_per_g"] * 10 ** (
                    (improvement - model["proof_threshold_db"]) / 20
                )
                rows.append([band, carrier, delay, period, f"{worst_frequency:.1f}",
                             f"{phase_peak:.9g}", f"{improvement:.3f}", f"{sensitivity_limit:.6g}"])
    write_csv("vibration.csv", [
        "band", "frequency_carrier_hz", "delay_s", "period_s", "peak_grid_frequency_hz",
        "phase_difference_peak_rad", "improvement_cycle_average_db",
        "scenario_sensitivity_for_47_db_per_g",
    ], rows)


def calculate_thermal(model):
    rows = []
    total_converter = 0.0
    total_ldo = 0.0
    for rail, voltage, current, fed_by_ldo in model["converter_rails"]:
        power = voltage * current
        loss = (model["ldo_nominal_input_v"] - voltage) * current if fed_by_ldo else 0.0
        total_converter += power
        total_ldo += loss
        rows.append([rail, f"{power:.6f}", f"{loss:.6f}"])
    rows.append(["Сумма произведений независимых максимумов", f"{total_converter:.6f}", f"{total_ldo:.6f}"])
    write_csv("thermal_converter_rails.csv", ["rail", "load_w", "series_regulator_loss_w"], rows)
    amplifier_supply = model["if_amplifier_count"] * model["if_amplifier_scenario_v"]
    write_csv("thermal_reference_points.csv", ["case", "value", "unit"], [
        ["К5119ПВ1Я, типовая паспортная конфигурация по Книге 3", model["converter_catalog_typical_w"], "Вт"],
        ["К5119ПВ1Я, максимальное значение по Книге 3", model["converter_catalog_max_w"], "Вт"],
        ["HMC7044, профиль 1, потребление с учётом терминации", model["clock_v"] * model["clock_current_profile_1_a"], "Вт"],
        ["Четыре AD8367, типовой ток при максимальном усилении", amplifier_supply * model["if_amplifier_current_typ_a"], "Вт"],
        ["Четыре AD8367, максимум тока при максимальном усилении", amplifier_supply * model["if_amplifier_current_max_a"], "Вт"],
        ["XC7Z030, температурный перепад до паспортного предела",
         model["junction_limit_c"] - model["case_air_scenario_c"], "К"],
    ])


if __name__ == "__main__":
    calculate_vibration(INPUTS["vibration"])
    calculate_thermal(INPUTS["thermal"])
