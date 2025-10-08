# radar_chart_times.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm, rcParams
import math

# ----------------------------
# 0) Use Times New Roman
# ----------------------------
installed = {f.name for f in fm.fontManager.ttflist}
base_font = "Times New Roman" if "Times New Roman" in installed else rcParams["font.family"]
rcParams.update({
    "font.family": "serif",
    "font.serif": [base_font],
    "figure.dpi": 140
})

# ----------------------------
# 1) Data
# ----------------------------
categories = ["Border", "Distance", "Equal", "Intersect", "Orientation", "Within"]
N = len(categories)

# Example scores (0–100). Add/modify series as needed.
series = {
    "Human":          [89.00, 78.28, 89.10, 85.53, 91.80, 88.08],
    "Gemini-2.5-Pro": [29.58, 25.27, 33.33, 28.75, 71.59, 34.48],
    "Claude-Sonnet 4":   [33.80, 23.08, 37.04, 22.50, 56.82, 21.55],
    "GPT-5-Think":     [25.35, 27.47, 44.44, 31.25, 69.32, 28.45],
}

series = {
    "Human":          [math.log(89.00), math.log(78.28), math.log(89.10), math.log(85.53), math.log(91.80), math.log(88.08)],
    "Gemini-2.5-Pro": [math.log(29.58), math.log(25.27), math.log(33.33), math.log(28.75), math.log(71.59), math.log(34.48)],
    "Claude-Sonnet 4":   [math.log(33.80), math.log(23.08), math.log(37.04), math.log(22.50), math.log(56.82), math.log(21.55)],
    "GPT-5-Think":     [math.log(25.35), math.log(27.47), math.log(44.44), math.log(31.25), math.log(69.32), math.log(28.45)],
}

# Colors (line + fill with alpha)
# palette = [
#     "#9ad4c0",  # teal
#     "#64498d",   # Dark purple clothe
    
#     "#C5BAB6",  # cat
#     # "#DCD6D0",  # cat
#     "#DE4C26", #dark hair
#     "#D180A6",  # clothes
#     "#C5BAB6",  # cat
#     "#D180A6",  # clothes
#     "#64498d",
#     "#CB915B",  # hair
# ]

palette = ["#db9042", "#2fb7a1", "#4f5bd5", "#c27a9e", "#f0c502"]

# ----------------------------
# 2) Geometry
# ----------------------------
angles = np.linspace(0, 2*np.pi, N, endpoint=False)
angles = np.concatenate([angles, angles[:1]])  # close loop

def close(vals):
    return np.concatenate([vals, vals[:1]])

# ----------------------------
# 3) Plot
# ----------------------------
fig, ax = plt.subplots(figsize=(4.3, 4.3), subplot_kw=dict(polar=True))

# Radial ticks/grid
ax.set_rgrids([0,5, 1, 1.5, 2], angle=60, fontsize=11)   # 20/40/60 rings
ax.set_ylim(0, 2.5)                                    # adjust to your scale
ax.set_rticks([0,5, 1, 1.5, 2])
ax.grid(True, linewidth=1.0, color="#d0d0d0")

# Category labels around the circle
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=13)
# ax.set_axisbelow(True)                  # ← grid behind the bars

# Draw each series
for (label, vals), color in zip(series.items(), palette):
    vals = np.array(vals)
    ax.plot(angles, close(vals), linewidth=1.3, color=color, label=label)
    ax.fill(angles, close(vals), color=color, alpha=0.15)

# Legend
leg = ax.legend(loc="center left", bbox_to_anchor=(0.8, 0.3),
                frameon=True, facecolor="white", edgecolor="#444444",
                framealpha=1.0, fontsize=10)

# Title (optional)
# ax.set_title("Example Radar Chart", pad=16, fontsize=14)

plt.tight_layout()
plt.savefig("freida-per-spatial.png", dpi=300, bbox_inches="tight", pad_inches=0.05)