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
  highlighted: null
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

function renderChart(data, series) {
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

  const barW = 56;
  const gap = 18;

  const padL = 58;   // y-axis labels
  const padR = 18;
  const padT = 18;
  const padB = 92;   // room for rotated x labels + meta

  const innerH = 360;
  const n = series.items.length;

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
  const axisY = document.createElementNS(ns, "line");
  axisY.setAttribute("x1", String(padL));
  axisY.setAttribute("x2", String(padL));
  axisY.setAttribute("y1", String(padT));
  axisY.setAttribute("y2", String(padT + innerH));
  axisY.setAttribute("class", "axisLine");
  svg.appendChild(axisY);

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

    if (dimOthers && d.id !== highlighted) rect.classList.add("dimmed");
    if (highlighted && d.id === highlighted) rect.classList.add("highlighted");

    // rect.addEventListener("click", () => {
    //   state.highlighted = (state.highlighted === d.id) ? null : d.id;
    //   el("highlightModel").value = state.highlighted || "";
    //   refreshChartOnly();
    // });

    // svg.appendChild(rect);

    // outline for highlighted
    if (highlighted && d.id === highlighted) {
      const outline = document.createElementNS(ns, "rect");
      outline.setAttribute("x", String(x - 2));
      outline.setAttribute("y", String(y - 2));
      outline.setAttribute("width", String(barW + 4));
      outline.setAttribute("height", String(h + 4));
      outline.setAttribute("rx", "12");
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

    // model label (rotated)
    const label = document.createElementNS(ns, "text");
    label.setAttribute("class", "modelText");
    label.setAttribute("text-anchor", "end");

    const lx = x + barW / 2 + 18;
    const ly = padT + innerH + 44;
    label.setAttribute("transform", `translate(${lx},${ly}) rotate(-45)`);
    label.textContent = d.name;
    svg.appendChild(label);

    // params meta line
    const meta = document.createElementNS(ns, "text");
    meta.setAttribute("class", "metaText");
    meta.setAttribute("text-anchor", "middle");
    meta.setAttribute("x", String(x + barW / 2));
    meta.setAttribute("y", String(padT + innerH + 76));
    meta.textContent = (d.id === "human") ? "" : `params: ${d.paramsB == null ? "unknown" : `${d.paramsB}B`}`;
    svg.appendChild(meta);
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

  // highlight dropdown remains constant list
  initControls(data);
  refreshChartOnly();
}

function refreshChartOnly() {
  const series = computeSeries(state.data);
  renderChart(state.data, series);
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
