#!/usr/bin/env python3
"""Reproduce analytical scenarios and normalized finite-DFT clutter model."""
import cmath
import csv
import json
import math
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parent
C = 299_792_458
DATA = json.loads((DIRECTORY / "inputs.json").read_text(encoding="utf-8"))


def write_rows(name, columns, rows):
    with (DIRECTORY / name).open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows(rows)


def jesd_rows():
    settings = DATA["jesd"]
    for converters, decimation in [(2, 1), (4, 1), (8, 2), (8, 4)]:
        line_rate = (
            converters * settings["transmitted_sample_bits"]
            * settings["sample_rate_hz"] / decimation
            * settings["coding_numerator"] / settings["coding_denominator"]
            / settings["physical_lanes"]
        )
        yield converters, decimation, line_rate, 1e12 / line_rate


def flash_rows():
    settings = DATA["flash"]
    clock = settings["qspi_scenario_clock_hz"]
    for mib in settings["image_sizes_mib"]:
        size = mib * 2**20
        pages = math.ceil(size / settings["page_size_bytes"])
        sectors = math.ceil(size / settings["sector_size_bytes"])
        program_bus = (
            size * 8 / settings["program_payload_bits_per_clock"]
            + pages * settings["conservative_transaction_overhead_clocks_per_page"]
        ) / clock
        verification = size * 8 / settings["verification_payload_bits_per_clock"] / clock
        yield (
            mib, size * 8 / (4 * settings["qspi_quad_max_clock_hz"]),
            size * 8 / settings["jtag_scenario_clock_hz"],
            size * 8 / (4 * settings["sd_scenario_clock_hz"]),
            sectors * settings["typical_sector_erase_s"],
            sectors * settings["maximum_sector_erase_s"],
            program_bus, pages * settings["typical_page_program_us"] / 1e6,
            pages * settings["maximum_page_program_us"] / 1e6,
            verification,
            sectors * settings["typical_sector_erase_s"] + program_bus
            + pages * settings["typical_page_program_us"] / 1e6 + verification,
            sectors * settings["maximum_sector_erase_s"] + program_bus
            + pages * settings["maximum_page_program_us"] / 1e6 + verification,
        )


def signal_rows():
    settings = DATA["signal_integrity"]
    modes = [
        ("JESD204B 4", 4e9), ("JESD204B 8", 8e9),
        *[(f"DDR3 {rate / 1e6:g}", rate) for rate in settings["ddr_transfers_hz"]],
        ("RGMII", settings["rgmii_transfers_hz"]),
        ("1000BASE-T MDI", settings["mdi_baud"]),
    ]
    for mode, rate in modes:
        for epsilon in settings["effective_permittivity_scenarios"]:
            propagation_speed = C / math.sqrt(epsilon)
            delay_ps_per_mm = 1e9 / propagation_speed
            nyquist = rate / 2
            explicit_loss_db_m = (
                20 / math.log(10) * math.pi * nyquist
                * settings["loss_tangent_scenario"] / propagation_speed
            )
            for length in settings["length_mm_scenarios"]:
                yield (
                    mode, rate, 1e12 / rate, nyquist, epsilon, length,
                    delay_ps_per_mm * length,
                    settings["skew_scenario_mm"] * delay_ps_per_mm * rate / 1e10,
                    explicit_loss_db_m * length / 1e3,
                    propagation_speed / (4 * settings["via_stub_scenario_mm"] / 1e3),
                )


def instrument_rows():
    settings = DATA["metrology"]
    sample_interval_ns = 1e9 / settings["sample_rate_hz"]
    for delta in settings["nominal_delta_ns"]:
        timebase_ns = settings["time_delta_limit_ppm"] * delta / 1e6
        yield (delta,
               sample_interval_ns + timebase_ns + settings["single_capture_floor_ns"],
               sample_interval_ns + timebase_ns + settings["averaged_capture_floor_ns"])


def clutter_rows():
    settings = DATA["clutter"]
    for pulses in settings["pulses"]:
        weights = [
            0.54 - 0.46 * math.cos(2 * math.pi * n / (pulses - 1))
            for n in range(pulses)
        ]
        transform_size = 2 * pulses
        for offset in settings["fractional_bin_offsets"]:
            spectrum = [
                abs(sum(
                    weight * cmath.exp(2j * math.pi * (offset - channel) * n
                                       / transform_size)
                    for n, weight in enumerate(weights)
                ) / sum(weights)) ** 2
                for channel in range(transform_size)
            ]
            for halfwidth in settings["mask_halfwidth_bins"]:
                unmasked = [
                    power for channel, power in enumerate(spectrum)
                    if min(channel, transform_size - channel) > halfwidth
                ]
                yield (
                    pulses, transform_size, offset, halfwidth,
                    10 * math.log10(max(spectrum) / max(unmasked)),
                )


def main():
    write_rows("jesd.csv", ["M", "decimation", "lane_bps", "UI_ps"], jesd_rows())
    write_rows("flash.csv", [
        "image_MiB", "ideal_quad_wire_s", "ideal_jtag_10MHz_s",
        "ideal_sd_25MHz_s", "typ_erase_s", "max_erase_s",
        "program_transfer_model_s", "typ_internal_program_s",
        "max_internal_program_s", "ideal_qspi_verify_s",
        "typ_total_without_host_overhead_s", "max_device_time_scenario_without_host_overhead_s",
    ], flash_rows())
    write_rows("signal_integrity.csv", [
        "mode", "rate_per_s", "UI_ps", "nyquist_hz", "effective_permittivity",
        "length_mm", "delay_ps", "one_mm_skew_pct_UI",
        "dielectric_loss_at_nyquist_db", "one_mm_stub_quarterwave_hz",
    ], signal_rows())
    write_rows("timing_accuracy.csv", [
        "delta_ns", "single_capture_abs_ns", "averaged_capture_abs_ns",
    ], instrument_rows())
    load = DATA["metrology"]["pat_trig_nominal_load_ohm"]
    outputs = DATA["metrology"]["parallel_outputs"]
    write_rows("trigger_load.csv", [
        "load_voltage_v", "total_current_ma", "balanced_branch_current_ma",
    ], ((level, level * 1e3 / load, level * 1e3 / load / outputs)
        for level in DATA["metrology"]["load_level_scenarios_v"]))
    write_rows("clutter.csv", [
        "pulses", "DFT_length", "fractional_bin_offset", "mask_halfwidth_bins",
        "peak_to_peak_clutter_suppression_db",
    ], clutter_rows())


if __name__ == "__main__":
    main()
