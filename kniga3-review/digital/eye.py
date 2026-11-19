"""Parametric NRZ eye through two identical, isolated low-pass poles."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
p = json.loads((HERE / "eye_inputs.json").read_text())
samples = p["samples_per_ui"]
period = p["bits_in_period"]
state = p["initial_register"]
levels = []
states_seen = set()
for _ in range(period):
    assert state and state not in states_seen
    states_seen.add(state)
    levels.append(p["level_high"] if state & 1 else p["level_low"])
    feedback = ((state >> 6) ^ (state >> 5)) & 1
    state = ((state << 1) & 127) | feedback
assert state == p["initial_register"] and len(states_seen) == 127

fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.8), sharey=True, layout="constrained")
rows = []
for rate, ax in zip(p["rate_gbps"], axes, strict=True):
    # Exact piecewise-constant response of y1'=(u-y1)/tau, y2'=(y1-y2)/tau.
    time = np.arange(samples + 1) / samples
    t_tau = time * (2 * np.pi * p["pole_frequency_ghz"] / rate)
    decay = np.exp(-t_tau)
    y1 = y2 = 0.0
    waveform = []
    for level in levels * 4:
        response = level + ((y2 - level) + (y1 - level) * t_tau) * decay
        waveform.extend(response[:-1])
        y1, y2 = level + (y1 - level) * decay[-1], response[-1]
    waveform = np.array(waveform)
    # Remove common propagation delay by referencing time to the median zero crossing.
    crossings = []
    for i, level in enumerate(levels):
        if level == levels[i - 1]:
            continue
        start = (period + i) * samples
        segment = waveform[start:start + samples + 1] * level
        k = np.flatnonzero((segment[:-1] <= 0) & (segment[1:] > 0))[0]
        crossings.append(k - segment[k] / (segment[k + 1] - segment[k]))
    phase = float(np.median(crossings))
    centers = []
    for i, level in enumerate(levels):
        start = (period + i) * samples
        ax.plot(np.arange(2 * samples + 1) / samples,
                np.interp(start + phase + np.arange(2 * samples + 1),
                          np.arange(waveform.size), waveform), color="#184866", lw=0.62)
        centers.append(np.interp(start + phase + samples / 2, np.arange(waveform.size), waveform))
    centers = np.array(centers)
    high = min(centers[np.array(levels) > 0])
    low = max(centers[np.array(levels) < 0])
    height = high - low
    # Worst histories approach a single step between fully settled rails.
    q = (phase / samples + .5) * 2 * np.pi * p["pole_frequency_ghz"] / rate
    expected = 2 - 4 * (1 + q) * np.exp(-q)
    q_next = max(0, q - 2 * np.pi * p["pole_frequency_ghz"] / rate)
    expected -= 4 * (1 - (1 + q_next) * np.exp(-q_next))
    assert abs(expected - height) < 0.0003
    rows.append([rate, 1000 / rate, phase / samples, high, low, height, height / 2])
    ax.axvline(.5, color=".37", ls=":", lw=.8)
    ax.axhline(0, color=".7", lw=.65, zorder=0)
    ax.set(xlim=(0, 2), ylim=(-1.1, 1.1), xticks=[0, .5, 1, 1.5, 2],
           xticklabels=["0", "0,5", "1", "1,5", "2"], xlabel="Время, UI",
           title=f"{rate} Гбит/с  ·  UI = {1000/rate:g} пс")
axes[0].set_ylabel("Нормированное напряжение")
fig.savefig(HERE / "jesd_eye.png", dpi=320)
with (HERE / "eye_results.csv").open("w", newline="") as out:
    writer = csv.writer(out)
    writer.writerow(["rate_Gbps", "UI_ps", "median_crossing_UI", "min_one_0.5UI", "max_zero_0.5UI",
                     "vertical_opening_0.5UI", "fraction_of_full_swing"])
    writer.writerows(rows)
