import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.colors import to_rgb
import numpy as np
from matplotlib import font_manager as fm, rcParams
import random

def use_iclr_style(preferred_font="Inter"):
    # Choose a geometric sans if available, else fall back.
    installed = {f.name for f in fm.fontManager.ttflist}
    for cand in ["Times New Roman"]:
        if cand in installed:
            base = cand
            break
    rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [base],
        "axes.titlesize": 14,
        "axes.titleweight": 700,
        "axes.labelsize": 14,
        "axes.edgecolor": (0, 0, 0, 0),  # hide default box; we draw arrows ourselves
        "axes.grid": True,
        "grid.color": "#dddddd",
        "grid.linewidth": 1.0,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "figure.dpi": 140,
    })

use_iclr_style()

import matplotlib.pyplot as plt

# Dummy data
categories = [
    "Geology report",
    "Park & trail map",
    "Investment/infrastructure",
    "Disaster/hazard",
    "Planning (city/region)",
    "Environmental review",
]
counts = [166, 22, 27, 83, 112, 100]

col = ["#e45756", "#db9042", "#2fb7a1", "#4f5bd5", "#c27a9e", "#f0c502"]
random.shuffle(col)

# Build labels like "Geology report (10)"
labels = [f"{name}\n({n})" for name, n in zip(categories, counts)]

fig, ax = plt.subplots(figsize=(4, 4))
wedges, texts = ax.pie(
    counts,
    labels=labels,
    startangle=90,
    counterclock=False,
    textprops={"ha": "center", "va": "center"},
    wedgeprops={"width": 0.35, "edgecolor": "white"},
    colors=col
)

# Make it a circle
ax.axis("equal")
ax.set_title("FRIEDA Map Domain Distribution")

plt.tight_layout()
plt.savefig("map-domain.png", dpi=300, bbox_inches="tight")
# plt.show()