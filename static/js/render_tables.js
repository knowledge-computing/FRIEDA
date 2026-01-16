// Function to render the 4D Object Captioning Results table
function renderCaptioningTable() {
    const tableContainer = document.getElementById('captioning-table-container');
    if (!tableContainer) return;
  
    let tableHTML = `
      <table class="results-table">
        <thead>
          <tr>
            <th class="row-number">#</th>
            <th style="text-align: left; padding-left: 15px;"><strong>Model</strong></th>
            <th><strong>CIDEr</strong></th>
            <th><strong>BLEU@4</strong></th>
            <th><strong>METEOR</strong></th>
            <th><strong>ROUGE</strong></th>
            <th><strong>BERT</strong></th>
            <th><strong>SBERT</strong></th>
            <th class="green-text"><strong>GPT-Appearance</strong></th>
            <th class="green-text"><strong>GPT-Action</strong></th>
            <th class="green-text"><strong>GPT-Eval</strong></th>
          </tr>
        </thead>
        <tbody>
    `;
  
    // 使用LaTeX表格中的数据，并按GPT-Eval从大到小排序
    const captioningData = [
      { model: "GPT-5-Think", affiliation: "OpenAI", cider: 69.0, bleu4: 6.4, meteor: 35.9, rouge: 32.1, bert: 64.1, sbert: 66.4, gptAppearance: "3.507/5", gptAction: "3.258/5", gptEval: "3.382/5", gptEvalValue: 3.382, isBest: ["gptAppearance", "gptAction", "gptEval"], isGray: true },
      { model: "Gemini 2.5 Pro", affiliation: "Google", cider: 94.8, bleu4: 11.2, meteor: 38.7, rouge: 39.0, bert: 68.5, sbert: 68.8, gptAppearance: "3.311/5", gptAction: "2.983/5", gptEval: "3.147/5", gptEvalValue: 3.147, isBest: ["bert"], isGray: false },
      { model: "Claude Sonnet 4", affiliation: "Anthropic", cider: 84.3, bleu4: 7.3, meteor: 36.5, rouge: 32.9, bert: 65.3, sbert: 68.9, gptAppearance: "3.246/5", gptAction: "2.931/5", gptEval: "3.088/5", gptEvalValue: 3.088, isBest: ["sbert"], isGray: false },
      { model: "Qwen2.5-VL 72B", affiliation: "Alibaba", cider: 95.1, bleu4: 12.4, meteor: 40.3, rouge: 38.0, bert: 66.8, sbert: 67.5, gptAppearance: "3.324/5", gptAction: "2.791/5", gptEval: "3.057/5", gptEvalValue: 3.057, isBest: [], isGray: false },
      { model: "InternVL3 78B", affiliation: "OpenGV Lab", cider: 72.0, bleu4: 5.5, meteor: 34.2, rouge: 27.1, bert: 60.9, sbert: 65.3, gptAppearance: "3.099/5", gptAction: "2.637/5", gptEval: "2.868/5", gptEvalValue: 2.868, isBest: [], isGray: false },
      { model: "InternVL3.5 38B", affiliation: "OpenGV Lab", cider: 72.0, bleu4: 5.5, meteor: 34.2, rouge: 27.1, bert: 60.9, sbert: 65.3, gptAppearance: "3.099/5", gptAction: "2.637/5", gptEval: "2.868/5", gptEvalValue: 2.868, isBest: [], isGray: false },
      { model: "LLaVA-OneVison 72B", affiliation: "Bytedance & NTU S-Lab", cider: 86.4, bleu4: 10.0, meteor: 39.2, rouge: 32.7, bert: 63.2, sbert: 65.6, gptAppearance: "3.166/5", gptAction: "2.479/5", gptEval: "2.823/5", gptEvalValue: 2.823, isBest: [], isGray: false },
      { model: "LLaVA-NeXT 110B", affiliation: "Bytedance & NTU S-Lab", cider: 107.4, bleu4: 16.1, meteor: 41.1, rouge: 41.5, bert: 68.5, sbert: 68.0, gptAppearance: "3.180/5", gptAction: "2.268/5", gptEval: "2.724/5", gptEvalValue: 2.724, isBest: ["cider", "bleu4", "rouge", "bert"], isGray: false },
      { model: "Ovis2 34B", affiliation: "Alibaba", cider: 79.0, bleu4: 6.9, meteor: 33.5, rouge: 33.5, bert: 65.4, sbert: 59.7, gptAppearance: "2.578/5", gptAction: "1.912/5", gptEval: "2.245/5", gptEvalValue: 2.245, isBest: [], isGray: false },
      { model: "Ovis2.5 9B-Think", affiliation: "Alibaba", cider: 48.4, bleu4: 2.5, meteor: 27.9, rouge: 22.6, bert: 58.2, sbert: 60.3, gptAppearance: "2.531/5", gptAction: "1.877/5", gptEval: "2.204/5", gptEvalValue: 2.204, isBest: [], isGray: false },
    ];
  
    captioningData.forEach((result, index) => {
      const rowClass = '';
      
      tableHTML += `<tr class="${rowClass}">`;
      tableHTML += `<td class="row-number">${index + 1}</td>`;
      
      // Model name with affiliation if available
      if (result.affiliation) {
        tableHTML += `<td><span class="model-name">${result.model}</span><span class="model-affiliation">${result.affiliation}</span></td>`;
      } else {
        tableHTML += `<td><span class="model-name">${result.model}</span></td>`;
      }
      
      // CIDEr
      tableHTML += `<td class="${result.isBest.includes('cider') ? 'highlight' : ''}">${result.cider}</td>`;
      
      // BLEU@4
      tableHTML += `<td class="${result.isBest.includes('bleu4') ? 'highlight' : ''}">${result.bleu4}</td>`;
      
      // METEOR
      tableHTML += `<td class="${result.isBest.includes('meteor') ? 'highlight' : ''}">${result.meteor}</td>`;
      
      // ROUGE
      tableHTML += `<td class="${result.isBest.includes('rouge') ? 'highlight' : ''}">${result.rouge}</td>`;
      
      // BERT
      tableHTML += `<td class="${result.isBest.includes('bert') ? 'highlight' : ''}">${result.bert}</td>`;
      
      // SBERT
      tableHTML += `<td class="${result.isBest.includes('sbert') ? 'highlight' : ''}">${result.sbert}</td>`;
      
      // GPT-Appearance
      const gptAppearanceClass = result.isGray ? 'gray-text' : '';
      const gptAppearanceHighlight = result.isBest.includes('gptAppearance') ? 'highlight' : '';
      tableHTML += `<td class="${gptAppearanceClass} ${gptAppearanceHighlight}">${result.gptAppearance}</td>`;
      
      // GPT-Action
      const gptActionClass = result.isGray ? 'gray-text' : '';
      const gptActionHighlight = result.isBest.includes('gptAction') ? 'highlight' : '';
      tableHTML += `<td class="${gptActionClass} ${gptActionHighlight}">${result.gptAction}</td>`;
      
      // GPT-Eval
      const gptEvalClass = result.isGray ? 'gray-text' : '';
      const gptEvalHighlight = result.isBest.includes('gptEval') ? 'highlight' : '';
      tableHTML += `<td class="${gptEvalClass} ${gptEvalHighlight}">${result.gptEval}</td>`;
      
      tableHTML += `</tr>`;
    });
    
    // Add Average row
    // tableHTML += `<tr>`;
    // tableHTML += `<td class="row-number"></td>`;
    // tableHTML += `<td><span class="model-name">Average</span></td>`;
    // tableHTML += `<td>-</td>`;
    // tableHTML += `<td>-</td>`;
    // tableHTML += `<td>-</td>`;
    // tableHTML += `<td>-</td>`;
    // tableHTML += `<td>-</td>`;
    // tableHTML += `<td>-</td>`;
    // tableHTML += `<td>3.038/5</td>`;
    // tableHTML += `<td>2.522/5</td>`;
    // tableHTML += `<td>2.780/5</td>`;
    // tableHTML += `</tr>`;
    
    // Add Human row
    tableHTML += `<tr class="gray-row">`;
    tableHTML += `<td class="row-number"></td>`;
    tableHTML += `<td><span class="model-name">Human</span></td>`;
    tableHTML += `<td>126.6</td>`;
    tableHTML += `<td>14.12</td>`;
    tableHTML += `<td>45.01</td>`;
    tableHTML += `<td>43.48</td>`;
    tableHTML += `<td>71.69</td>`;
    tableHTML += `<td>76.30</td>`;
    tableHTML += `<td>3.772/5</td>`;
    tableHTML += `<td>3.879/5</td>`;
    tableHTML += `<td>3.826/5</td>`;
    tableHTML += `</tr>`;
  
    tableHTML += `
        </tbody>
      </table>
    `;
  
    tableContainer.innerHTML = tableHTML;
    
    // Add caption
    const captionContainer = document.getElementById('captioning-caption-container');
    if (captionContainer) {
      captionContainer.innerHTML = `<p></p>`;
    }
  }
  
  // Function to render the 4D Object QA Results table
  function renderQATable() {
    const tableContainer = document.getElementById('qa-table-container');
    if (!tableContainer) return;
  
    // 添加qa-table-container类
    tableContainer.classList.add('qa-table-container');
  
    let tableHTML = `
      <table class="results-table qa-table">
        <thead>
          <tr>
            <th class="row-number">#</th>
            <th style="text-align: left; padding-left: 15px;"><strong>Model</strong></th>
            <th><strong>Object Counting (%)</strong></th>
            <th><strong>Temporal Relationship (%)</strong></th>
            <th><strong>Action (%)</strong></th>
            <th><strong>Spatial Relationship (%)</strong></th>
            <th><strong>Appearance (%)</strong></th>
            <th><strong>Overall (%)</strong></th>
          </tr>
        </thead>
        <tbody>
    `;
  
    // 使用LaTeX表格中的数据，并按Overall从大到小排序
    const qaData = [
      { model: "GPT-4o", affiliation: "OpenAI", objectCounting: 44.09, temporalRelationship: 59.29, action: 63.55, spatialRelationship: 69.40, appearance: 77.21, overall: 62.98, overallValue: 62.98, isBest: ["temporalRelationship", "action", "spatialRelationship", "overall"] },
      { model: "LLaVA-Video 72B", affiliation: "Bytedance & NTU S-Lab", objectCounting: 54.33, temporalRelationship: 58.57, action: 57.48, spatialRelationship: 66.42, appearance: 77.21, overall: 62.32, overallValue: 62.32, isBest: ["objectCounting"] },
      { model: "LLaVA-OneVision 72B", affiliation: "Bytedance & NTU S-Lab", objectCounting: 49.61, temporalRelationship: 58.57, action: 60.75, spatialRelationship: 61.19, appearance: 76.47, overall: 61.38, overallValue: 61.38, isBest: [] },
      { model: "Gemini 1.5 Pro", affiliation: "Google", objectCounting: 46.46, temporalRelationship: 58.57, action: 59.35, spatialRelationship: 64.18, appearance: 68.38, overall: 59.52, overallValue: 59.52, isBest: [] },
      { model: "Qwen2-VL 72B", affiliation: "Alibaba", objectCounting: 45.67, temporalRelationship: 55.71, action: 58.41, spatialRelationship: 61.19, appearance: 72.06, overall: 58.72, overallValue: 58.72, isBest: [] },
      { model: "Qwen2-VL 7B", affiliation: "Alibaba", objectCounting: 38.58, temporalRelationship: 56.43, action: 57.94, spatialRelationship: 58.96, appearance: 71.32, overall: 56.99, overallValue: 56.99, isBest: [] },
      { model: "LLaVA-Video 7B", affiliation: "Bytedance & NTU S-Lab", objectCounting: 42.52, temporalRelationship: 55.00, action: 52.80, spatialRelationship: 56.72, appearance: 78.68, overall: 56.86, overallValue: 56.86, isBest: ["appearance"] },
      { model: "GPT-4o mini", affiliation: "OpenAI", objectCounting: 40.16, temporalRelationship: 50.71, action: 50.00, spatialRelationship: 61.94, appearance: 72.06, overall: 54.59, overallValue: 54.59, isBest: [] },
      { model: "LLaVA-OneVision 7B", affiliation: "Bytedance & NTU S-Lab", objectCounting: 42.52, temporalRelationship: 52.86, action: 42.99, spatialRelationship: 57.46, appearance: 74.26, overall: 53.00, overallValue: 53.00, isBest: [] },
      { model: "Gemini 1.5 Flash", affiliation: "Google", objectCounting: 26.77, temporalRelationship: 50.00, action: 53.27, spatialRelationship: 60.45, appearance: 66.18, overall: 51.80, overallValue: 51.80, isBest: [] },
      { model: "InternVL2 76B", affiliation: "OpenGV Lab", objectCounting: 28.35, temporalRelationship: 45.00, action: 42.52, spatialRelationship: 38.81, appearance: 64.71, overall: 43.94, overallValue: 43.94, isBest: [] },
      { model: "VideoChat2", affiliation: "OpenGV Lab", objectCounting: 22.83, temporalRelationship: 31.43, action: 33.18, spatialRelationship: 38.81, appearance: 34.56, overall: 32.36, overallValue: 32.36, isBest: [] },
      { model: "InternVL2 8B", affiliation: "OpenGV Lab", objectCounting: 18.11, temporalRelationship: 31.43, action: 35.98, spatialRelationship: 32.09, appearance: 39.71, overall: 32.09, overallValue: 32.09, isBest: [] },
      { model: "MiniGPT4-Video", affiliation: "KAUST", objectCounting: 22.05, temporalRelationship: 26.43, action: 22.90, spatialRelationship: 22.39, appearance: 22.06, overall: 23.17, overallValue: 23.17, isBest: [] }
    ];
  
    qaData.forEach((result, index) => {
      const rowClass = '';
      
      tableHTML += `<tr class="${rowClass}">`;
      tableHTML += `<td class="row-number">${index + 1}</td>`;
      
      // Model name with affiliation if available
      if (result.affiliation) {
        tableHTML += `<td><span class="model-name">${result.model}</span><span class="model-affiliation">${result.affiliation}</span></td>`;
      } else {
        tableHTML += `<td><span class="model-name">${result.model}</span></td>`;
      }
      
      // Object Counting
      tableHTML += `<td class="${result.isBest.includes('objectCounting') ? 'highlight' : ''}">${result.objectCounting}</td>`;
      
      // Temporal Relationship
      tableHTML += `<td class="${result.isBest.includes('temporalRelationship') ? 'highlight' : ''}">${result.temporalRelationship}</td>`;
      
      // Action
      tableHTML += `<td class="${result.isBest.includes('action') ? 'highlight' : ''}">${result.action}</td>`;
      
      // Spatial Relationship
      tableHTML += `<td class="${result.isBest.includes('spatialRelationship') ? 'highlight' : ''}">${result.spatialRelationship}</td>`;
      
      // Appearance
      tableHTML += `<td class="${result.isBest.includes('appearance') ? 'highlight' : ''}">${result.appearance}</td>`;
      
      // Overall
      tableHTML += `<td class="${result.isBest.includes('overall') ? 'highlight' : ''}">${result.overall}</td>`;
      
      tableHTML += `</tr>`;
    });
    
    // Add Average row
    // tableHTML += `<tr>`;
    // tableHTML += `<td class="row-number"></td>`;
    // tableHTML += `<td><span class="model-name">Average</span></td>`;
    // tableHTML += `<td>37.29</td>`;
    // tableHTML += `<td>49.29</td>`;
    // tableHTML += `<td>49.37</td>`;
    // tableHTML += `<td>53.57</td>`;
    // tableHTML += `<td>63.92</td>`;
    // tableHTML += `<td>50.69</td>`;
    // tableHTML += `</tr>`;
    
    // Add Human row
    tableHTML += `<tr class="gray-row">`;
    tableHTML += `<td class="row-number"></td>`;
    tableHTML += `<td><span class="model-name">Human</span></td>`;
    tableHTML += `<td>88.98</td>`;
    tableHTML += `<td>89.29</td>`;
    tableHTML += `<td>94.39</td>`;
    tableHTML += `<td>91.04</td>`;
    tableHTML += `<td>89.71</td>`;
    tableHTML += `<td>91.08</td>`;
    tableHTML += `</tr>`;
  
    tableHTML += `
        </tbody>
      </table>
    `;
  
    tableContainer.innerHTML = tableHTML;
    
    // Add caption
    const captionContainer = document.getElementById('qa-caption-container');
    if (captionContainer) {
      // 添加qa-caption-container类
      captionContainer.classList.add('qa-caption-container');
      captionContainer.innerHTML = `<p><strong></p>`;
    }
  }
  
  // Initialize tables when the document is ready
  document.addEventListener('DOMContentLoaded', function() {
    renderCaptioningTable();
    renderQATable();
  }); 