// static/js/leaderboard.js

(function () {
  const DATA = window.FRIEDA_LEADERBOARD;
  if (!DATA) {
    console.error("FRIEDA leaderboard data not found. Did you include leaderboard_data.js?");
    return;
  }

  const DIMENSIONS = [
    { key: "overall", label: "Overall", slices: [{ key: "Overall", n: 500 }] },

    {
      key: "spatial_relation",
      label: "Spatial relation",
      slices: [
        { key: "Border", n: 71 },
        { key: "Distance", n: 91 },
        { key: "Equal", n: 54 },
        { key: "Intersect", n: 80 },
        { key: "Orientation", n: 89 },
        { key: "Within", n: 115 }
      ]
    },

    {
      key: "map_count",
      label: "Map count",
      slices: [
        { key: "Single", n: 202 },
        { key: "Multi", n: 298 }
      ]
    },

    {
      key: "answer_type",
      label: "Answer type",
      slices: [
        { key: "Textual", n: 372 },
        { key: "Distance", n: 45 },
        { key: "Direction", n: 83 }
      ]
    },

    {
      key: "map_element_type",
      label: "Map element type",
      slices: [
        { key: "Map text", n: 366 },
        { key: "Legend", n: 417 },
        { key: "Compass", n: 137 },
        { key: "Scale", n: 46 }
      ]
    },

    {
      key: "map_element_count",
      label: "Map element count",
      slices: [
        { key: "1", n: 132 },
        { key: "2", n: 279 },
        { key: "3", n: 80 },
        { key: "4", n: 9 }
      ]
    },

    {
      key: "domain",
      label: "Domain",
      slices: [
        { key: "Planning", n: 112 },
        { key: "Investment", n: 27 },
        { key: "Environment", n: 100 },
        { key: "Disaster", n: 83 },
        { key: "Parks", n: 22 },
        { key: "Geology", n: 166 }
      ]
    }
  ];

  const LS_KEY = "frieda_lb_selected_model";

  const state = {
    split: "direct", // direct | contextual
    subset: "full",  // full | all_agree
    dimension: "overall",
    slice: "Overall",
    showUnknownSize: true,
    selectedModelId: localStorage.getItem(LS_KEY) || ""
  };

  function $(sel) {
    return document.querySelector(sel);
  }

  function isAvailable(split, subset, dimension, slice) {
    return Boolean(DATA.scores?.[split]?.[subset]?.[dimension]?.[slice]);
  }

  function currentScoreMap() {
    return DATA.scores?.[state.split]?.[state.subset]?.[state.dimension]?.[state.slice] || null;
  }

  function formatSize(model) {
    if (model.alwaysShow) return "";
    if (model.sizeB == null) return "params: unknown";
    return `params: ${model.sizeB}B`;
  }

  function shouldShowModel(model) {
    if (model.alwaysShow) return true;
    if (!state.showUnknownSize && model.sizeB == null) return false;
    return true;
  }

  function modelsByGroup(models) {
    const order = ["Human", "Proprietary LVLMs", "Open Source LVLMs"];
    const groups = new Map();
    for (const m of models) {
      if (!groups.has(m.group)) groups.set(m.group, []);
      groups.get(m.group).push(m);
    }
    return order
      .filter((g) => groups.has(g))
      .map((g) => ({ group: g, models: groups.get(g) }));
  }

  function clampPct(score) {
    // requirement #1: scale to 100%
    const s = Number(score);
    if (!Number.isFinite(s)) return 0;
    return Math.max(0, Math.min(100, s));
  }

  function axisHTML() {
    // 0–100 axis: ticks at 100/75/50/25/0
    const ticks = [100, 75, 50, 25, 0];
    return `
      <div class="lb-axis">
        ${ticks
          .map((t) => {
            const top = (100 - t);
            return `
              <div class="lb-axis-line" style="top:${top}%"></div>
              <div class="lb-axis-label" style="top:${top}%">${t}</div>
            `;
          })
          .join("")}
      </div>
    `;
  }

  function setSelectedModel(modelId) {
    if (state.selectedModelId === modelId) {
      state.selectedModelId = "";
      localStorage.removeItem(LS_KEY);
    } else {
      state.selectedModelId = modelId;
      localStorage.setItem(LS_KEY, modelId);
    }
    render();
  }

  function renderGroupVertical(groupName, models) {
    // sort within group by score desc
    const sorted = models.slice().sort((a, b) => b.score - a.score);

    const cols = sorted
      .map((m) => {
        const pct = clampPct(m.score);
        const meta = formatSize(m);
        const selected = m.id === state.selectedModelId ? "is-selected" : "";
        const title = `${m.name}: ${m.score.toFixed(2)}${meta ? ` (${meta})` : ""}`;

        return `
          <div class="lb-barcol ${selected}" data-model="${m.id}" title="${title}">
            <div class="lb-score">${m.score.toFixed(2)}</div>
            <div class="lb-bar" style="height:${pct}%"></div>
            <div class="lb-xlab">${m.name}</div>
            ${meta ? `<div class="lb-xmeta">${meta}</div>` : ``}
          </div>
        `;
      })
      .join("");

    return `
      <div class="lb-group">
        <div class="lb-group-title">${groupName}</div>
        <div class="lb-vchart">
          ${axisHTML()}
          <div class="lb-bars">
            ${cols}
          </div>
        </div>
      </div>
    `;
  }

  function render() {
    const chart = $("#lb-chart");
    const note = $("#lb-note");

    const scoreMap = currentScoreMap();
    if (!scoreMap) {
      chart.innerHTML = "";
      note.textContent =
        "This slice isn't available for the selected split/subset yet (currently most detailed slices are for Direct + Full).";
      return;
    }
    note.textContent = "";

    const models = DATA.models
      .filter(shouldShowModel)
      .map((m) => {
        const s = scoreMap[m.id];
        return { ...m, score: s == null ? null : Number(s) };
      })
      .filter((m) => m.score != null);

    const grouped = modelsByGroup(models);

    chart.innerHTML = grouped
      .map(({ group, models }) => renderGroupVertical(group, models))
      .join("");

    // attach click handlers for highlight feature (#3)
    chart.querySelectorAll(".lb-barcol").forEach((el) => {
      el.addEventListener("click", () => {
        const id = el.getAttribute("data-model");
        if (id) setSelectedModel(id);
      });
    });
  }

  function fillDimensionUI() {
    const dimSel = $("#lb-dimension");
    dimSel.innerHTML = DIMENSIONS.map((d) => `<option value="${d.key}">${d.label}</option>`).join("");
    dimSel.value = state.dimension;
    fillSliceUI();
  }

  function fillSliceUI() {
    const sliceSel = $("#lb-slice");
    const dim = DIMENSIONS.find((d) => d.key === state.dimension);
    const slices = dim ? dim.slices : [{ key: "Overall", n: 500 }];

    sliceSel.innerHTML = slices
      .map((s) => `<option value="${s.key}">${s.key} (n=${s.n})</option>`)
      .join("");

    if (!slices.some((s) => s.key === state.slice)) state.slice = slices[0].key;
    sliceSel.value = state.slice;

    render();
  }

  function attachHandlers() {
    $("#lb-split").addEventListener("change", (e) => {
      state.split = e.target.value;
      render();
    });

    $("#lb-subset").addEventListener("change", (e) => {
      state.subset = e.target.value;
      render();
    });

    $("#lb-unknown").addEventListener("change", (e) => {
      state.showUnknownSize = e.target.checked;
      render();
    });

    $("#lb-dimension").addEventListener("change", (e) => {
      state.dimension = e.target.value;
      fillSliceUI();
    });

    $("#lb-slice").addEventListener("change", (e) => {
      state.slice = e.target.value;
      render();
    });

    // Optional: “Clear highlight” button if you add one later
  }

  function init() {
    $("#lb-split").innerHTML = `
      <option value="direct">FRIEDA-direct</option>
      <option value="contextual">FRIEDA-contextual</option>
    `;
    $("#lb-subset").innerHTML = `
      <option value="full">Full</option>
      <option value="all_agree">All-agree</option>
    `;

    $("#lb-split").value = state.split;
    $("#lb-subset").value = state.subset;
    $("#lb-unknown").checked = state.showUnknownSize;

    fillDimensionUI();
    attachHandlers();
    render();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
