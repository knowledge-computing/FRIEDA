import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm, rcParams

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
        # "axes.edgecolor": (0, 0, 0, 0),  # hide default box; we draw arrows ourselves
        "axes.grid": True,
        "grid.color": "#dddddd",
        "grid.linewidth": 1.0,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "figure.dpi": 140,
    })

use_iclr_style()

# Data
sizes = np.array([1, 2, 4, 8, 14, 30, 38, 241], dtype=float)   # (B parameters)
acc   = np.array([9.40, 12.80, 20.00, 23.20, 23.00, 24.20, 14.20, 11.40])

fig, ax = plt.subplots(figsize=(5, 3))
# ax.plot(sizes, acc, marker='o', color="#6e4559")
ax.plot(sizes, acc, marker='o', color="#c27a9e")

ax.set_title("InternVL3.5 Overall Accuracy vs. Model Size")
ax.set_xlabel("Parameters (B)")
ax.set_ylabel("Overall Accuracy (%)")
ax.set_xticks(sizes)

# Add a little headroom/footroom so labels don't clip the box
ymin, ymax = acc.min(), acc.max()
ax.set_ylim(ymin - 2, ymax + 2)

# Place labels with smart vertical offsets
for i, (x, y) in enumerate(zip(sizes, acc)):
    prev_y = acc[i-1] if i > 0 else y
    next_y = acc[i+1] if i < len(acc)-1 else y

    # If this point is a local max → put label above; else below
    is_local_max = (y >= prev_y) and (y >= next_y)
    dy = 7 if is_local_max else -9   # vertical offset in points
    va = 'bottom' if is_local_max else 'top'

    ax.annotate(f"{y:.1f}",
                xy=(x, y),
                xytext=(0, dy),
                textcoords='offset points',
                ha='center', va=va,
                fontsize=9,
                clip_on=True)  # keep text inside axes

ax.grid(True, linestyle='--', linewidth=0.6, alpha=0.6)
ax.margins(x=0.02)
fig.tight_layout()
plt.savefig('internvl35perf.png')
