# bigcode_style_stacked_bars.py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm, rcParams

# ---------------------------
# 0) Style / font setup
# ---------------------------
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

# ---------------------------
# 1) Example data
# ---------------------------
# Mix of closed (dark) and open (light) models + a small "calibrated" gain.
np.random.seed(1)

mode = 'direct'

if mode == 'direct':
    title = 'FRIEDA-Direct'
    # # Score direct
    # base_score = 
    base_scores = [59.2, 27.0, 26.6, 22.4, 5.6, 5.138339920948616, 8.8, 9.0, 17.4, 11.4, 12.2, 17.8]
    calib_gain = [25.666666666666668, 10.6, 10.6, 9.2, 3.0, 1.1857707509881423, 2.2, 4.0, 8.2, 2.8, 5.6, 8.0]

    labels = [
        "Human", 
        "Gemini-2.5-Pro", "GPT-5-Think", "Claude-4-Sonnet", 
        "LLaVA-NeXT-110B", "GLM-4.5V-108B", 
        "InternVL3-78B", "LLaVA-OneVision-72B", "Qwen2.5-VL-72B",
        "InternVL3.5-38B", "Ovis2-34B",
        "Ovis2.5-9B-Think"
    ]

    # splits = [0, 1, 4, 6, 9, 11, len(labels)]
    # labels_over = ["", "? B", "> 100B", "~70B", "~35B", "<10B"]

else:
    title = 'FRIEDA-Contextual'
    # Score contextual
    base_scores = [0, 24.4, 26.0, 18.0, 3.0, 4.835589941972921, 7.4, 6.2, 18.4, 9.2, 10.8, 17.4]
    calib_gain = [0, 12.0, 11.0, 10.4, 0.8, 1.3539651837524178, 1.8, 3.0, 8.0, 2.8, 5.2, 7.4]

    labels = [
        "",
        "Gemini-2.5-Pro", "GPT-5-Think", "Claude-4-Sonnet", 
        "LLaVA-NeXT-110B", "GLM-4.5V-108B", 
        "InternVL3-78B", "LLaVA-OneVision-72B", "Qwen2.5-VL-72B",
        "InternVL3.5-38B", "Ovis2-34B",
        "Ovis2.5-9B-Think"
    ]
splits = [0, 1, 4, 6, 9, 11, len(labels)]
labels_over = ["", "Proprietary", "> 100B", "~70B", "~35B", "<10B"]
    # splits = [0, 3, 5, 8, 10, len(labels)]
    # labels_over = ["? B", "> 100B", "~70B", "~35B", "<10B"]


open_color  = "#c27a9e"     # light blue
calib_color  = "#6e4559"     # green cap

# colors = np.where(closed_color, open_color)

# ---------------------------
# 2) Plot
# ---------------------------
fig, ax = plt.subplots(figsize=(10, 4))
x = np.arange(len(labels))
bar_w = 0.65

# stacked bars: base + small cap
bars_base = ax.bar(x, base_scores, width=bar_w, color=open_color, edgecolor="none")
bars_cap  = ax.bar(x, calib_gain, bottom=base_scores, width=bar_w,
                   color=calib_color, edgecolor="none")

# Title
ax.set_title(title, pad=20)

# Y settings + reference line at 60
ax.set_ylim(0, 100)
# ax.set_yticks(np.arange(0, 71, 10))
# ax.axhline(60, color="#bdbdbd", linewidth=1.5, linestyle="--", dashes=(4, 4))

# X ticks rotated
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=-60, ha="left")
ax.tick_params(axis="x", length=0)      # ← remove the small black tickmarks at bottom

# Remove spines (we’ll draw arrow axes)
for s in ["top", "right", "left", "bottom"]:
    ax.spines[s].set_visible(False)

# ---------------------------
# 3) Arrow axes + axis labels
# ---------------------------

# ---- Y-axis arrow + label (left) ----
ax.annotate(
    "", xy=(0.0, 1.0), xytext=(0.0, 0.0),
    xycoords=("axes fraction", "axes fraction"),
    arrowprops=dict(arrowstyle="-", lw=1.4, color="black", shrinkA=0, shrinkB=0),
    clip_on=False, zorder=10
)
ax.text(
    -0.06, 0.5, "Accuracy (%)",
    rotation=90, va="center", ha="right",
    transform=ax.transAxes,
    fontsize=14, fontweight=600, color="#6b6b6b"
)

# ---- X-axis arrow + label (bottom) ----
ax.annotate(
    "", xy=(1.0, 0.0), xytext=(0.0, 0.0),
    xycoords=("axes fraction", "axes fraction"),
    arrowprops=dict(arrowstyle="-", lw=1.4, color="black"),
    clip_on=False, zorder=10
)
ax.text(
    1.02, -0.02, "Models",
    va="top", ha="left",
    transform=ax.transAxes,
    fontsize=13, fontweight=600, color="#6b6b6b"
)

ax.grid(False)                          # turn off anything inherited from rcParams
ax.grid(axis="y", which="major", color="#dddddd", linewidth=1.0)  # horizontal only
ax.set_axisbelow(True)                  # ← grid behind the bars

# ---------------------------
# 4) Size separators over the plot
# ---------------------------
# Provide split indices and headings (tune positions to your dat
for i in range(1, len(splits)-1):
    ax.vlines(splits[i]-0.5, 96, 100, colors="black", linewidth=1.2)
for i, txt in enumerate(labels_over):
    xmid = 0.5 * (splits[i] + splits[i+1] - 1)
    ax.text(xmid, 98.0, txt, ha="center", va="center", fontsize=12)

# ---------------------------
# 5) Legend
# ---------------------------
from matplotlib.patches import Patch
handles = [
    Patch(color=open_color,   label="All Agree"),
    Patch(color=calib_color,  label="Partial Agree"),
]
leg = ax.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.98, 0.92), frameon=False, facecolor="white",            # white background
    edgecolor="#444444",framealpha=1.0)

# Tight layout & save
# plt.tight_layout(rect=[0.02, 0.05, 0.98, 0.95])  # leave headroom for top annotations
plt.savefig(f"freida-{mode}-result.png", dpi=300, bbox_inches="tight")

