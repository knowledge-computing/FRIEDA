/* FRIEDA Leaderboard (static, no dependencies)
   - Vertical bars
   - Y max fixed at 100
   - Click-to-highlight + dropdown highlight
   - "Show unknown size" toggle
   - Slice labels already contain n= in JSON keys
*/
function resolveDataUrl() {
  // Resolve relative to *this script* (works even when the page is hosted under a subpath).
  const script =
    document.currentScript ||
    document.querySelector('script[src$="leaderboard.js"]') ||
    document.querySelector('script[src$="/leaderboard.js"]');
  if (script && script.src) {
    return new URL("leaderboard_data.json", script.src).toString();
  }
  // Fallback: relative to page URL.
  return "./static/js/leaderboard_data.json";
}

const DATA_URL = resolveDataUrl();


const el = (id) => document.getElementById(id);

const state = {
  data: null,
  split: null,
  subset: null,
  view: null,
  slice: null,
  showUnknown: true,
  highlighted: null,
  animateNext: false
};

function fmtPct(x) {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  return Number(x).toFixed(2);
}

function modelMetaById(data) {
  const m = new Map();
  for (const model of data.models) m.set(model.id, model);
  return m;
}

function getAvailable(data, split, subset) {
  const splitObj = data.splits?.[split];
  const subsetObj = splitObj?.[subset];
  const views = subsetObj?.views || {};
  return views;
}

function clamp01(v) {
  if (v < 0) return 0;
  if (v > 100) return 100;
  return v;
}

function buildOptions(select, values, selected) {
  select.innerHTML = "";
  for (const v of values) {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    select.appendChild(opt);
  }
  if (selected && values.includes(selected)) select.value = selected;
  else if (values.length) select.value = values[0];
}

function initControls(data) {
  // Split
  const splits = Object.keys(data.splits || {});
  buildOptions(el("split"), splits, state.split);
  state.split = el("split").value;

  // Subset
  const subsets = Object.keys(data.splits[state.split] || {});
  buildOptions(el("subset"), subsets, state.subset);
  state.subset = el("subset").value;

  // View
  const views = Object.keys(getAvailable(data, state.split, state.subset));
  buildOptions(el("view"), views, state.view);
  state.view = el("view").value;

  // Slice
  const slicesObj = getAvailable(data, state.split, state.subset)?.[state.view]?.slices || {};
  const sliceNames = Object.keys(slicesObj);
  buildOptions(el("slice"), sliceNames, state.slice);
  state.slice = el("slice").value;

  // show unknown
  el("showUnknown").checked = state.showUnknown;

  // Remove highlight dropdown from UI (highlight remains click-to-toggle on bars)
  const hl = el("highlightModel");
  if (hl) {
    const wrap = hl.closest(".highlightPick") || hl.parentElement;
    if (wrap) wrap.remove();
    else hl.style.display = "none";
  }

  // highlight dropdown
  // const meta = modelMetaById(data);
  // const allModels = data.models
  //   .filter((m) => m.id !== "human" || true) // keep human selectable too
  //   .map((m) => m.id);

  // const highlightSelect = el("highlightModel");
  // highlightSelect.innerHTML = "";
  // {
  //   const opt0 = document.createElement("option");
  //   opt0.value = "";
  //   opt0.textContent = "None";
  //   highlightSelect.appendChild(opt0);
  // }
  // for (const id of allModels) {
  //   const m = meta.get(id);
  //   const opt = document.createElement("option");
  //   opt.value = id;
  //   const sizeTxt = m.paramsB == null ? "params: unknown" : `params: ${m.paramsB}B`;
  //   opt.textContent = `${m.name} (${sizeTxt})`;
  //   highlightSelect.appendChild(opt);
  // }
  // highlightSelect.value = state.highlighted || "";
}

function wireEvents() {
  el("split").addEventListener("change", () => {
    state.split = el("split").value;
    state.animateNext = true;
    // reset downstream selections
    state.subset = null;
    state.view = null;
    state.slice = null;
    refresh();
  });

  el("subset").addEventListener("change", () => {
    state.subset = el("subset").value;
    state.view = null;
    state.slice = null;
    refresh();
  });

  el("view").addEventListener("change", () => {
    state.view = el("view").value;
    state.slice = null;
    refresh();
  });

  el("slice").addEventListener("change", () => {
    state.slice = el("slice").value;
    refreshChartOnly();
  });

  el("showUnknown").addEventListener("change", () => {
    state.showUnknown = el("showUnknown").checked;
    refreshChartOnly();
  });

  // Recompute bar widths on resize (keeps bars fitting the plot area)
  window.addEventListener("resize", () => {
    refreshChartOnly();
  });

  // el("highlightModel").addEventListener("change", () => {
  //   const v = el("highlightModel").value;
  //   state.highlighted = v || null;
  //   refreshChartOnly();
  // });
}

function computeSeries(data) {
  const views = getAvailable(data, state.split, state.subset);
  const slices = views?.[state.view]?.slices || {};
  const sliceObj = slices?.[state.slice];
  if (!sliceObj) return null;

  const meta = modelMetaById(data);
  const scores = sliceObj.scores || {};

  // Build list of (model, score) where score exists
  let items = [];
  for (const [id, score] of Object.entries(scores)) {
    const m = meta.get(id);
    if (!m) continue;
    if (!state.showUnknown && (m.paramsB == null) && id !== "human") continue;
    items.push({
      id,
      name: m.name,
      group: m.group,
      paramsB: m.paramsB,
      score: clamp01(Number(score))
    });
  }

  // Also include models that exist but missing score? (skip, keeps clean)
  // Sort by score desc, but keep human first if present (like your UI)
  items.sort((a, b) => b.score - a.score);

  return {
    n: sliceObj.n,
    items
  };
}

function setChartTitle(data, series) {
  const unit = data.meta?.unit || "%";
  const title = `${state.split} • ${state.subset} • ${state.view} • ${state.slice}  (${unit}, y-max=100)`;
  el("chartTitle").textContent = title;
}

function renderChart(data, series, opts = {}) {
  const mount = el("chartMount");
  mount.innerHTML = "";

  const empty = el("emptyState");
  if (!series || !series.items.length) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");

  setChartTitle(data, series);

  // ---- SVG layout ----
  const yMax = (data.meta && typeof data.meta.yMax === "number") ? data.meta.yMax : 100;

  const n = series.items.length;

  // Layout paddings
  const padL = 76;   // more left room (prevents "Human Avg" from clipping)
  const padR = 18;
  const padT = 18;
  const padB = 110;  // room for rotated 2-line x labels

  // 25% taller plot area
  const innerH = 450;

  // Dynamic bar geometry: fit available width when possible (avoid unnecessary horizontal scroll)
  const defaultBarW = 56;
  const defaultGap = 18;

  const container = mount.parentElement; // .scrollX
  const mountPad = 16; // chartMount padding (8px left + right)
  const availInnerW = (container && container.clientWidth)
    ? Math.max(260, container.clientWidth - mountPad - padL - padR)
    : null;

  let barW = defaultBarW;
  let gap = defaultGap;

  if (availInnerW && n > 0) {
    const minBar = 12;
    const maxBar = 72;
    const minGap = 6;
    const maxGap = 22;

    if (n === 1) {
      barW = Math.max(minBar, Math.min(maxBar, Math.floor(availInnerW * 0.6)));
      gap = 0;
    } else {
      // Choose a gap, then compute barW so the series fits in availInnerW.
      const slot = availInnerW / n;
      gap = Math.floor(slot * 0.28);
      gap = Math.max(minGap, Math.min(maxGap, gap));

      barW = Math.floor((availInnerW - (n - 1) * gap) / n);

      // If bars get too thin, fall back to default geometry and allow scroll.
      if (barW < minBar) {
        barW = defaultBarW;
        gap = defaultGap;
      } else {
        barW = Math.max(minBar, Math.min(maxBar, barW));

        // Ensure we never exceed availInnerW due to rounding.
        while (n * (barW + gap) - gap > availInnerW && barW > minBar) barW -= 1;
        while (n * (barW + gap) - gap > availInnerW && gap > minGap) gap -= 1;
      }
    }
  }

  const innerW = n * (barW + gap) - gap;
  const svgW = padL + innerW + padR;
  const svgH = padT + innerH + padB;

  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("width", String(svgW));
  svg.setAttribute("height", String(svgH));
  svg.setAttribute("viewBox", `0 0 ${svgW} ${svgH}`);

  // Grid + y axis
  const ticks = [0, 25, 50, 75, 100];
  for (const t of ticks) {
    const y = padT + innerH - (t / yMax) * innerH;

    const line = document.createElementNS(ns, "line");
    line.setAttribute("x1", String(padL));
    line.setAttribute("x2", String(svgW - padR));
    line.setAttribute("y1", String(y));
    line.setAttribute("y2", String(y));
    line.setAttribute("class", "gridLine");
    svg.appendChild(line);

    const txt = document.createElementNS(ns, "text");
    txt.setAttribute("x", String(padL - 10));
    txt.setAttribute("y", String(y + 4));
    txt.setAttribute("text-anchor", "end");
    txt.setAttribute("class", "axisText");
    txt.textContent = String(t);
    svg.appendChild(txt);
  }

  // axis line
  // const axisY = document.createElementNS(ns, "line");
  // axisY.setAttribute("x1", String(padL));
  // axisY.setAttribute("x2", String(padL));
  // axisY.setAttribute("y1", String(padT));
  // axisY.setAttribute("y2", String(padT + innerH));
  // axisY.setAttribute("class", "axisLine");
  // svg.appendChild(axisY);

  const axisX = document.createElementNS(ns, "line");
  axisX.setAttribute("x1", String(padL));
  axisX.setAttribute("x2", String(svgW - padR));
  axisX.setAttribute("y1", String(padT + innerH));
  axisX.setAttribute("y2", String(padT + innerH));
  axisX.setAttribute("class", "axisLine");
  svg.appendChild(axisX);

  // Bars
  const highlighted = state.highlighted;

  // If highlight is set, dim others (like BigCodeBench focus mode)
  const dimOthers = !!highlighted;

  series.items.forEach((d, i) => {
    const x = padL + i * (barW + gap);
    const h = (d.score / yMax) * innerH;
    const y = padT + innerH - h;

    // rect
    const rect = document.createElementNS(ns, "rect");
    rect.setAttribute("x", String(x));
    rect.setAttribute("y", String(y));
    rect.setAttribute("width", String(barW));
    rect.setAttribute("height", String(h));
    rect.setAttribute("rx", "3");       // bar radius
    rect.setAttribute("class", "bar");

    if (opts.animate) {
      rect.classList.add("sweep");
      rect.style.setProperty("--delay", `${i * 12}ms`);
    }

    if (dimOthers && d.id !== highlighted) rect.classList.add("dimmed");
    if (highlighted && d.id === highlighted) rect.classList.add("highlighted");

    rect.addEventListener("click", () => {
      state.highlighted = (state.highlighted === d.id) ? null : d.id;
      refreshChartOnly();
    });

    svg.appendChild(rect);

    // outline for highlighted
    if (highlighted && d.id === highlighted) {
      const outline = document.createElementNS(ns, "rect");
      outline.setAttribute("x", String(x - 2));
      outline.setAttribute("y", String(y - 2));
      outline.setAttribute("width", String(barW + 4));
      outline.setAttribute("height", String(h + 4));
      outline.setAttribute("rx", "4");
      outline.setAttribute("class", "barOutline");
      svg.appendChild(outline);
    }

    // value on top
    const val = document.createElementNS(ns, "text");
    val.setAttribute("x", String(x + barW / 2));
    val.setAttribute("y", String(y - 6));
    val.setAttribute("text-anchor", "middle");
    val.setAttribute("class", "valueText");
    val.textContent = fmtPct(d.score);
    svg.appendChild(val);

    // model label + params (rotated, 2 lines)
    const lbl = document.createElementNS(ns, "text");
    lbl.setAttribute("class", "modelText");
    lbl.setAttribute("text-anchor", "end");

    const labelOffset = Math.max(10, Math.min(18, Math.floor(barW * 0.7)));
    const lx = x + barW / 2 + labelOffset;
    const ly = padT + innerH + 46;
    lbl.setAttribute("transform", `translate(${lx},${ly}) rotate(-45)`);

    const t1 = document.createElementNS(ns, "tspan");
    t1.textContent = d.name;
    lbl.appendChild(t1);

    if (d.id !== "human") {
      const t2 = document.createElementNS(ns, "tspan");
      t2.setAttribute("x", "0");
      t2.setAttribute("dy", "14");
      t2.setAttribute("class", "metaTspan");
      t2.textContent = `params: ${d.paramsB == null ? "unknown" : String(d.paramsB) + "B"}`;
      lbl.appendChild(t2);
    }

    svg.appendChild(lbl);
  });

  mount.appendChild(svg);
}

function refresh() {
  // Rebuild dependent dropdowns because available views/slices may change
  const data = state.data;

  // subset options depend on split
  const subsets = Object.keys(data.splits[state.split] || {});
  buildOptions(el("subset"), subsets, state.subset);
  state.subset = el("subset").value;

  // views depend on split+subset
  const views = Object.keys(getAvailable(data, state.split, state.subset));
  buildOptions(el("view"), views, state.view);
  state.view = el("view").value;

  // slices depend on split+subset+view
  const slicesObj = getAvailable(data, state.split, state.subset)?.[state.view]?.slices || {};
  const sliceNames = Object.keys(slicesObj);
  buildOptions(el("slice"), sliceNames, state.slice);
  state.slice = el("slice").value;

  // controls are already rebuilt; keep checkbox in sync
  initControls(data);
  refreshChartOnly();
}

function refreshChartOnly() {
  const series = computeSeries(state.data);
  const animate = !!state.animateNext;
  state.animateNext = false;
  renderChart(state.data, series, { animate });
}

async function main() {
  const res = await fetch(DATA_URL, { cache: "no-store" });
if (!res.ok) {
  // Helpful debug: when a 404 HTML page is returned, res.json() throws "Unexpected token <".
  const preview = await res.text().catch(() => "");
  const head = preview ? preview.slice(0, 140).replace(/\s+/g, " ") : "";
  throw new Error(`Failed to fetch leaderboard data: ${DATA_URL} (HTTP ${res.status}). ${head ? "Response starts with: " + head : ""}`);
}
const data = await res.json();
state.data = data;

  // initial defaults
  state.split = Object.keys(data.splits)[0];
  state.subset = Object.keys(data.splits[state.split])[0];

  // default view: Overall if exists
  const views = Object.keys(getAvailable(data, state.split, state.subset));
  state.view = views.includes("Overall") ? "Overall" : views[0];

  // default slice: first
  const slicesObj = getAvailable(data, state.split, state.subset)?.[state.view]?.slices || {};
  state.slice = Object.keys(slicesObj)[0];

  initControls(data);
  wireEvents();
  refreshChartOnly();
}

main().catch((e) => {
  console.error(e);
  const msg = "Failed to load leaderboard data.";
  const titleEl = el("chartTitle");
  if (titleEl) titleEl.textContent = msg;

  const empty = el("emptyState");
  if (empty) {
    empty.classList.remove("hidden");
    empty.textContent = `${msg} ${e && e.message ? "(" + e.message + ")" : ""}`;
  }
});
