# fixed_sunburst.py
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.colors import to_rgb
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
        "axes.edgecolor": (0, 0, 0, 0),  # hide default box; we draw arrows ourselves
        "axes.grid": True,
        "grid.color": "#dddddd",
        "grid.linewidth": 1.0,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "figure.dpi": 140,
    })

use_iclr_style()
# -----------------------------
# 1) Hierarchy (edit as needed)
# -----------------------------
data = {
    "Border\n(71)": {
        "Single\n(41)": 41,
        "Multi\n(30)": 30
    },
    "Distance\n(91)": {
        "Single\n(42)": 42,
        "Multi\n(49)": 49
    },
    "Equal\n(54)": {
        "Multi\n(54)": 54
    },
    "Intersect\n(80)": {
        "Single\n(38)": 38,
        "Multi\n(42)": 42
    },
    "Orientation\n(89)": {
        "Single\n(32)": 32,
        "Multi\n(57)": 57
    },
    "Within\n(114)": {
        "Single\n(49)": 49,
        "Multi\n(65)": 65
    }







    # "property": {
    #     "attribute": 18,
    #     "number": 8,
    #     "color": 5,
    #     "mass": 3,
    # },
    # "scene": {
    #     "light": 16,
    #     "viewpoint": 14,
    #     "occlusion/visibility": 1,
    #     "weather": 1,
    # },
    # "dynamics": {
    #     "throwing": 6,
    #     "fluid": 8,
    #     "collision": 10,
    #     "manipulation": 7,
    #     "others": 2,
    # },
    # "relationships": {
    #     "depth": 5,
    #     "location": 7,
    #     "motion": 18,
    #     "distance": 1,
    # },
}

# -----------------------------
# 2) Helpers
# -----------------------------
def lighten(color, amount=0.55):
    r, g, b = to_rgb(color)
    return (1 - amount) + amount * r, (1 - amount) + amount * g, (1 - amount) + amount * b

def wedge_text(ax, r, th1, th2, txt, fs=12, w=700, c="black"):
    """Place rotated text at the wedge mid-angle."""
    ang = 0.5 * (th1 + th2)
    ar = np.deg2rad(ang)
    x, y = r * np.cos(ar), r * np.sin(ar)
    rot = ang if -90 <= ang <= 90 else ang + 180
    ax.text(x, y, txt, rotation=rot, rotation_mode="anchor",
            ha="center", va="center", fontsize=fs, fontweight=w, color=c)

# -----------------------------
# 3) Geometry + drawing
# -----------------------------
parents = list(data.keys())
p_vals = [sum(ch.values()) for ch in data.values()]
total = sum(p_vals)

# pleasant distinct parent colors
# parent_colors = ["#c27a9e", "#db9042", "#91c6b2", "#f0c502", "#1d5dcd", "#f2b134"]
parent_colors = ["#e45756", "#db9042", "#2fb7a1", "#4f5bd5", "#c27a9e", "#f0c502"]

# radii for rings
R1_in, R1_out = 0.28, 1.00   # parent ring
R2_in, R2_out = 1.00, 1.55   # child ring

fig, ax = plt.subplots(figsize=(4.5, 4.5))
ax.set_aspect("equal", "box")
ax.axis("off")

# >>> KEY: ensure the full circle is in view (fixes your clipping/quadrant issue)
Rmax = R2_out + 0.08
ax.set_xlim(-Rmax, Rmax)
ax.set_ylim(-Rmax, Rmax)

start = 90.0          # start at top
gap = 0.0             # degrees gap between parent wedges
parent_arcs = []

# ---- parents
for p, v, col in zip(parents, p_vals, parent_colors):
    sweep = 360.0 * v / total
    th1 = start
    th2 = start - (sweep - gap)   # clockwise
    wedge = Wedge((0, 0), r=R1_out, theta1=th2, theta2=th1,
                  width=R1_out - R1_in, facecolor=col, edgecolor="white", linewidth=1)
    ax.add_patch(wedge)
    wedge_text(ax, (R1_in + R1_out)/2, th2, th1, p, fs=14, w=800)
    parent_arcs.append((th2, th1, p, col))
    start = th2

# ---- children
for th2, th1, p, p_col in parent_arcs:
    children = data[p]
    s = sum(children.values())
    span = th1 - th2  # positive degrees
    c_start = th1
    for idx, a in enumerate(children.items()):
        ch, v = a
        frac = v / s
        c_sweep = span * frac
        c_th1 = c_start
        c_th2 = c_start - c_sweep
        c_col = lighten(p_col, 0.24 * (idx + 1))
        w2 = Wedge((0, 0), r=R2_out, theta1=c_th2, theta2=c_th1,
                   width=R2_out - R2_in, facecolor=c_col, edgecolor="white", linewidth=1)
        ax.add_patch(w2)
        wedge_text(ax, (R2_in + R2_out)/2, c_th2, c_th1, ch, fs=12, w=800)
        c_start = c_th2

# optional: clean inner hole
ax.add_artist(plt.Circle((0, 0), R1_in - 0.02, color="white", zorder=10))

plt.tight_layout()
plt.savefig("benchmark_stat.png", dpi=300, bbox_inches="tight", pad_inches=0.05)
# plt.show()
