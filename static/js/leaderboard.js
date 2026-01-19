// static/js/leaderboard.js

(function () {
    const DATA = window.FRIEDA_LEADERBOARD;
    if (!DATA) {
      console.error("FRIEDA leaderboard data not found. Did you include leaderboard_data.js?");
      return;
    }
  
    const DIMENSIONS = [
      { key: "overall", label: "Overall", slices: ["Overall"] },
      { key: "spatial_relation", label: "Spatial relation", slices: ["Border", "Distance", "Equal", "Intersect", "Orientation", "Within"] },
      { key: "map_count", label: "Map count", slices: ["Single", "Multi"] },
      { key: "answer_type", label: "Answer type", slices: ["Textual", "Distance", "Direction"] },
      { key: "map_element_type", label: "Map element type", slices: ["Map text", "Legend", "Compass", "Scale"] },
      { key: "map_element_count", label: "Map element count", slices: ["1", "2", "3", "4"] },
      { key: "domain", label: "Domain", slices: ["Planning", "Investment", "Environment", "Disaster", "Parks", "Geology"] }
    ];
  
    const state = {
      split: "direct",        // direct | contextual
      subset: "full",         // full | all_agree
      dimension: "overall",
      slice: "Overall",
      showUnknownSize: true
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
  
      // build visible model list with scores
      const models = DATA.models
        .filter(shouldShowModel)
        .map((m) => {
          const s = scoreMap[m.id];
          return { ...m, score: (s == null ? null : Number(s)) };
        })
        .filter((m) => m.score != null); // drop missing scores
  
      // per-group sorting (desc by score)
      const grouped = modelsByGroup(models).map(({ group, models }) => ({
        group,
        models: models.slice().sort((a, b) => b.score - a.score)
      }));
  
      const max = Math.max(...models.map((m) => m.score), 1);
  
      // render
      chart.innerHTML = grouped
        .map(({ group, models }) => {
          const rows = models
            .map((m) => {
              const pct = (m.score / max) * 100;
              const meta = formatSize(m);
              return `
                <div class="lb-row">
                  <div class="lb-model">
                    <div class="name">${m.name}</div>
                    ${meta ? `<div class="meta">${meta}</div>` : ``}
                  </div>
                  <div class="lb-bar-wrap" title="${m.score.toFixed(2)}">
                    <div class="lb-bar" style="width:${pct}%;"></div>
                  </div>
                  <div class="lb-score">${m.score.toFixed(2)}</div>
                </div>
              `;
            })
            .join("");
  
          return `
            <div class="lb-group">
              <div class="lb-group-title">${group}</div>
              ${rows}
            </div>
          `;
        })
        .join("");
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
      const slices = dim ? dim.slices : ["Overall"];
  
      sliceSel.innerHTML = slices.map((s) => `<option value="${s}">${s}</option>`).join("");
  
      // Keep current slice if it exists, otherwise default to first
      if (!slices.includes(state.slice)) state.slice = slices[0];
      sliceSel.value = state.slice;
  
      // If the selected combination isn't available, we still render a message in render()
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
    }
  
    function init() {
      // populate split/subset selectors
      $("#lb-split").innerHTML = `
        <option value="direct">FRIEDA-direct</option>
        <option value="contextual">FRIEDA-contextual</option>
      `;
      $("#lb-subset").innerHTML = `
        <option value="full">Full</option>
        <option value="all_agree">All-agree</option>
      `;
  
      $("#lb-unknown").checked = state.showUnknownSize;
  
      fillDimensionUI();
      attachHandlers();
      render();
    }
  
    // wait for DOM
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  })();
  