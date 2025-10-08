
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
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

# -----------------------------
# 1) Your data (country -> count)
# -----------------------------
raw_counts = {
    "United States": 251,
    "Canada": 82,
    "South Africa": 32,
    "Peru": 9,
    "Burkina Faso": 1,
    "Guyana": 2,
    "Mexico": 18,
    "Portugal": 2,
    "New Zealand": 1,
    "Chile": 4,
    "Brazil": 2,
    "Guinea": 3,
    "Colombia": 2,
    "Ecuador": 1,
    "Cuba": 1,
    "Argentina": 3,
    "Bolivia": 2,
    "Spain": 1,
    "Sweden": 1,
    "Australia": 1,
    "Namibia": 2,
    "Nicaragua": 1,
    "Ghana": 1,
    "United Arab Emirates": 3,
    "Kazakhstan": 6,
    "Cambodia": 5,
    "India": 7,
    "Bangladesh": 6,
    "Sri Lanka": 3,
    "Ireland": 24,
    "Seychelles": 14,
    "Singapore": 9,
}

df = pd.DataFrame(
    [{"country": k, "count": v} for k, v in raw_counts.items()]
).sort_values("count", ascending=False)

N_countries = df.shape[0]
N_total = int(df["count"].sum())

# -----------------------------
# 2) World polygons (Natural Earth low-res)
# -----------------------------
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

english_primary = {
    # Core Anglosphere
    "United States of America", "United Kingdom", "Ireland",
    "Canada", "Australia", "New Zealand",

    # Caribbean / Americas
    "Jamaica", "Trinidad and Tobago", "Barbados", "The Bahamas",
    "Belize", "Guyana", "Antigua and Barbuda", "Dominica",
    "Saint Lucia", "Saint Vincent and the Grenadines", "Grenada",
    "Saint Kitts and Nevis",

    # Africa
    "South Africa", "Nigeria", "Ghana", "Kenya", "Uganda",
    "Tanzania", "Zambia", "Zimbabwe", "Botswana", "Namibia",
    "Sierra Leone", "Liberia", "The Gambia", "Malawi", "Lesotho",
    "Eswatini", "Rwanda", "Cameroon", "Mauritius", "Seychelles",

    # Asia
    "India", "Pakistan", "Bangladesh", "Singapore", "Philippines",
    "Malaysia", "Sri Lanka",

    # Europe
    "Malta", "Cyprus",

    # Oceania / Pacific
    "Papua New Guinea", "Fiji", "Solomon Islands", "Vanuatu",
    "Samoa", "Kiribati", "Tonga", "Tuvalu", "Nauru"
}

# Flag countries in the world layer
world["is_english_primary"] = world["name"].isin(english_primary)

# Clean (drop Antarctica, invalid rows)
world = world[(world.name != "Antarctica") & (world.pop_est > 0)].copy()

# Name harmonization (Natural Earth uses "United States of America")
name_fix = {
    "United States": "United States of America",
}
df["country_ne"] = df["country"].replace(name_fix)

# Merge on country name
world = world.merge(df[["country_ne", "count"]], left_on="name", right_on="country_ne", how="left")
world["count_f"] = world["count"].fillna(0)

# -----------------------------
# 3) Handle tiny/missing countries as point markers
# -----------------------------
# Some microstates or very small countries may be missing in low-res polygons (e.g., Singapore).
# Provide fallback lat/lon (approx city/centroid) for any countries that didn't merge.
merged_names = set(world["name"].unique())
missing = sorted(set(df["country_ne"]) - merged_names)

# Manual coordinates (lon, lat)
fallback_coords = {
    "Singapore": (103.8198, 1.3521),
    # Add any additional tiny countries here if they show up in `missing`
    # "Seychelles": (55.4920, -4.6796),  # Only use if Seychelles is missing in your environment
}

fallback_rows = []
for c in missing:
    if c in fallback_coords:
        lon, lat = fallback_coords[c]
        count_val = int(df.loc[df["country_ne"] == c, "count"].iloc[0])
        fallback_rows.append({"country_ne": c, "count": count_val, "geometry": Point(lon, lat)})

fallback_gdf = gpd.GeoDataFrame(fallback_rows, geometry="geometry", crs="EPSG:4326") if fallback_rows else None

# -----------------------------
# 4) Panel A: Coverage (binary)
# -----------------------------
figA, axA = plt.subplots(figsize=(10, 5))
world.plot(ax=axA, color="#ffffff", edgecolor="#e6e6e6", linewidth=0.3)
world.loc[world["is_english_primary"]].plot(
    ax=axA, color="#e6e6e6", edgecolor="#bdbdbd", linewidth=0.3
)

main_color = '#6e4559'
# highlight polygons with ≥1
world.loc[world["count_f"] > 0].plot(ax=axA, color=main_color, edgecolor="#bdbdbd", linewidth=0.3)

# plot fallback points (if any)
if fallback_gdf is not None and not fallback_gdf.empty:
    fallback_gdf.plot(ax=axA, markersize=20, color=main_color, edgecolor="white", linewidth=0.3)

axA.set_axis_off()
axA.set_title(f"FRIEDA Coverage: {N_countries} Countries", pad=8)
plt.tight_layout()
figA.savefig("frieda_coverage_binary.png", bbox_inches="tight")

# -----------------------------
# 5) Panel B: Intensity map (quantile bins)
# -----------------------------
# build quantile bins only on positive counts
pos = world.loc[world["count_f"] > 0, "count_f"]
# Guard: if very few positives, just use unique sorted values
if pos.size > 0:
    q = np.unique(np.quantile(pos, [0, 0.2, 0.4, 0.6, 0.8, 1.0])).tolist()
    # ensure strictly increasing bins (fallback to sorted uniques)
    bins = q if len(q) > 2 else sorted(pos.unique().tolist())
else:
    bins = [0, 1]

figB, axB = plt.subplots(figsize=(10, 5))
world.plot(ax=axB, color="#e6e6e6", edgecolor="#bdbdbd", linewidth=0.3)
if pos.size > 0:
    world.loc[world["count_f"] > 0].plot(
        ax=axB,
        column="count_f",
        cmap="Blues",
        scheme="User_Defined",
        classification_kwds={"bins": bins},
        edgecolor="#bdbdbd",
        linewidth=0.3,
        legend=True,
        legend_kwds={"title": "Questions"},
    )

# plot fallback points with a simple size scale
if fallback_gdf is not None and not fallback_gdf.empty:
    sizes = 10 + 2 * fallback_gdf["count"]  # simple marker sizing
    fallback_gdf.plot(ax=axB, markersize=sizes, color="#08519c", alpha=0.9, edgecolor="white", linewidth=0.3)

axB.set_axis_off()
axB.set_title("FRIEDA Questions per Country", pad=8)
plt.tight_layout()
figB.savefig("frieda_coverage_intensity.png", bbox_inches="tight")

# -----------------------------
# 6) Panel C: Top-10 bar chart (precise comparisons)
# -----------------------------
top10 = df.nlargest(10, "count").copy()
figC, axC = plt.subplots(figsize=(6, 5))
axC.barh(top10["country"][::-1], top10["count"][::-1], color="#c27a9e")
axC.set_xlabel("Questions")
axC.set_ylabel("Country")
axC.set_title("Top-10 Countries by Question Count")
axC.set_axisbelow(True)   
for i, v in enumerate(top10["count"][::-1].values):
    axC.text(v + max(top10["count"])*0.01, i, str(v), va="center")
plt.tight_layout()
figC.savefig("frieda_top10_bars.png", bbox_inches="tight")

# -----------------------------
# 7) (Optional) Composite figure in LaTeX
# Use the three PDFs:
# - frieda_coverage_binary.png
# - frieda_coverage_intensity.png
# - frieda_top10_bars.png
# -----------------------------
print(f"Done. Countries: {N_countries}, Total questions: {N_total}. "
      "Saved: frieda_coverage_binary.png, frieda_coverage_intensity.png, frieda_top10_bars.png")