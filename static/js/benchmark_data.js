// 4D-Bench Experimental Results Data

// 4D Object Captioning Results
const captioningResults = [
    {
      model: "GPT-5-Think",
      cider: 69.0,
      bleu4: 6.4,
      meteor: 35.9,
      rouge: 32.1,
      bert: 64.1,
      sbert: 66.4,
      gptAppearance: 3.507,
      gptAction: 3.258,
      gptEval: 3.382,
      isBest: ["gptAppearance", "gptAction", "gptEval"],
      isGray: true
    },
    {
      model: "Gemini 2.5 Pro",
      cider: 94.8,
      bleu4: 11.2,
      meteor: 38.7,
      rouge: 39.0,
      bert: 68.5,
      sbert: 68.8,
      gptAppearance: 3.311,
      gptAction: 2.983,
      gptEval: 3.147,
      isBest: ["bert"],
      isGray: false
    },
    {
      model: "Gemini 1.5 Flash",
      cider: 84.3,
      bleu4: 7.3,
      meteor: 36.5,
      rouge: 32.9,
      bert: 65.3,
      sbert: 68.9,
      gptAppearance: 3.246,
      gptAction: 2.931,
      gptEval: 3.088,
      isBest: ["sbert"],
      isGray: false
    },
    {
      model: "Qwen2-VL 72B",
      cider: 95.1,
      bleu4: 12.4,
      meteor: 40.3,
      rouge: 38.0,
      bert: 66.8,
      sbert: 67.5,
      gptAppearance: 3.324,
      gptAction: 2.791,
      gptEval: 3.057,
      isBest: [],
      isGray: false
    },
    {
      model: "LLaVA-Video 72B",
      cider: 106.2,
      bleu4: 15.1,
      meteor: 39.8,
      rouge: 40.9,
      bert: 68.5,
      sbert: 68.1,
      gptAppearance: 3.138,
      gptAction: 2.471,
      gptEval: 2.804,
      isBest: ["bert"],
      isGray: false
    },
    {
      model: "LLaVA-OneVision 72B",
      cider: 107.4,
      bleu4: 16.1,
      meteor: 41.1,
      rouge: 41.5,
      bert: 68.5,
      sbert: 68.0,
      gptAppearance: 3.180,
      gptAction: 2.268,
      gptEval: 2.724,
      isBest: ["cider", "bleu4", "rouge", "bert"],
      isGray: false
    },
    {
      model: "GPT-4o mini",
      cider: 51.1,
      bleu4: 2.7,
      meteor: 30.8,
      rouge: 24.0,
      bert: 59.3,
      sbert: 63.5,
      gptAppearance: 3.311,
      gptAction: 3.131,
      gptEval: 3.221,
      isBest: [],
      isGray: true
    },
    {
      model: "LLaVA-Video 7B",
      cider: 102.6,
      bleu4: 14.6,
      meteor: 41.7,
      rouge: 38.8,
      bert: 66.7,
      sbert: 68.1,
      gptAppearance: 3.235,
      gptAction: 2.552,
      gptEval: 2.894,
      isBest: ["meteor"],
      isGray: false
    },
    {
      model: "Qwen2-VL 7B",
      cider: 84.5,
      bleu4: 10.1,
      meteor: 36.9,
      rouge: 36.4,
      bert: 65.7,
      sbert: 66.9,
      gptAppearance: 3.170,
      gptAction: 2.666,
      gptEval: 2.918,
      isBest: [],
      isGray: false
    },
    {
      model: "LLaVA-OneVison 7B",
      cider: 86.4,
      bleu4: 10.0,
      meteor: 39.2,
      rouge: 32.7,
      bert: 63.2,
      sbert: 65.6,
      gptAppearance: 3.166,
      gptAction: 2.479,
      gptEval: 2.823,
      isBest: [],
      isGray: false
    },
    {
      model: "InternVL2 76B",
      cider: 72.0,
      bleu4: 5.5,
      meteor: 34.2,
      rouge: 27.1,
      bert: 60.9,
      sbert: 65.3,
      gptAppearance: 3.099,
      gptAction: 2.637,
      gptEval: 2.868,
      isBest: [],
      isGray: false
    },
    {
      model: "VideoChat2-Mistral",
      cider: 79.0,
      bleu4: 6.9,
      meteor: 33.5,
      rouge: 33.5,
      bert: 65.4,
      sbert: 59.7,
      gptAppearance: 2.578,
      gptAction: 1.912,
      gptEval: 2.245,
      isBest: [],
      isGray: false
    },
    {
      model: "InternVL2 8B",
      cider: 48.4,
      bleu4: 2.5,
      meteor: 27.9,
      rouge: 22.6,
      bert: 58.2,
      sbert: 60.3,
      gptAppearance: 2.531,
      gptAction: 1.877,
      gptEval: 2.204,
      isBest: [],
      isGray: false
    },
    {
      model: "MiniGPT4-Video",
      cider: 18.4,
      bleu4: 0.6,
      meteor: 23.1,
      rouge: 13.2,
      bert: 50.7,
      sbert: 51.2,
      gptAppearance: 1.737,
      gptAction: 1.351,
      gptEval: 1.544,
      isBest: [],
      isGray: false
    },
    {
      model: "Average",
      cider: "-",
      bleu4: "-",
      meteor: "-",
      rouge: "-",
      bert: "-",
      sbert: "-",
      gptAppearance: 3.038,
      gptAction: 2.522,
      gptEval: 2.780,
      isBest: [],
      isGray: false
    },
    {
      model: "Human",
      cider: 126.6,
      bleu4: 14.12,
      meteor: 45.01,
      rouge: 43.48,
      bert: 71.69,
      sbert: 76.30,
      gptAppearance: 3.772,
      gptAction: 3.879,
      gptEval: 3.826,
      isBest: [],
      isGray: false,
      isHuman: true
    }
  ];
  
  // 4D Object QA Results
  const qaResults = [
    {
      model: "GPT-4o",
      objectCounting: 44.09,
      temporalRelationship: 59.29,
      action: 63.55,
      spatialRelationship: 69.40,
      appearance: 77.21,
      overall: 62.98,
      isBest: ["temporalRelationship", "action", "spatialRelationship", "overall"]
    },
    {
      model: "LLaVA-Video 72B",
      objectCounting: 54.33,
      temporalRelationship: 58.57,
      action: 57.48,
      spatialRelationship: 66.42,
      appearance: 77.21,
      overall: 62.32,
      isBest: ["objectCounting"]
    },
    {
      model: "LLaVA-OneVision 72B",
      objectCounting: 49.61,
      temporalRelationship: 58.57,
      action: 60.75,
      spatialRelationship: 61.19,
      appearance: 76.47,
      overall: 61.38,
      isBest: []
    },
    {
      model: "Gemini 1.5 Pro",
      objectCounting: 46.46,
      temporalRelationship: 58.57,
      action: 59.35,
      spatialRelationship: 64.18,
      appearance: 68.38,
      overall: 59.52,
      isBest: []
    },
    {
      model: "Qwen2-VL 72B",
      objectCounting: 45.67,
      temporalRelationship: 55.71,
      action: 58.41,
      spatialRelationship: 61.19,
      appearance: 72.06,
      overall: 58.72,
      isBest: []
    },
    {
      model: "LLaVA-Video 7B",
      objectCounting: 42.52,
      temporalRelationship: 55.00,
      action: 52.80,
      spatialRelationship: 56.72,
      appearance: 78.68,
      overall: 56.86,
      isBest: ["appearance"]
    },
    {
      model: "Qwen2-VL 7B",
      objectCounting: 38.58,
      temporalRelationship: 56.43,
      action: 57.94,
      spatialRelationship: 58.96,
      appearance: 71.32,
      overall: 56.99,
      isBest: []
    },
    {
      model: "LLaVA-OneVision 7B",
      objectCounting: 42.52,
      temporalRelationship: 52.86,
      action: 42.99,
      spatialRelationship: 57.46,
      appearance: 74.26,
      overall: 53.00,
      isBest: []
    },
    {
      model: "GPT-4o mini",
      objectCounting: 40.16,
      temporalRelationship: 50.71,
      action: 50.00,
      spatialRelationship: 61.94,
      appearance: 72.06,
      overall: 54.59,
      isBest: []
    },
    {
      model: "Gemini 1.5 Flash",
      objectCounting: 26.77,
      temporalRelationship: 50.00,
      action: 53.27,
      spatialRelationship: 60.45,
      appearance: 66.18,
      overall: 51.80,
      isBest: []
    },
    {
      model: "InternVL2 76B",
      objectCounting: 28.35,
      temporalRelationship: 45.00,
      action: 42.52,
      spatialRelationship: 38.81,
      appearance: 64.71,
      overall: 43.94,
      isBest: []
    },
    {
      model: "InternVL2 8B",
      objectCounting: 18.11,
      temporalRelationship: 31.43,
      action: 35.98,
      spatialRelationship: 32.09,
      appearance: 39.71,
      overall: 32.09,
      isBest: []
    },
    {
      model: "VideoChat2",
      objectCounting: 22.83,
      temporalRelationship: 31.43,
      action: 33.18,
      spatialRelationship: 38.81,
      appearance: 34.56,
      overall: 32.36,
      isBest: []
    },
    {
      model: "MiniGPT4-Video",
      objectCounting: 22.05,
      temporalRelationship: 26.43,
      action: 22.90,
      spatialRelationship: 22.39,
      appearance: 22.06,
      overall: 23.17,
      isBest: []
    },
    {
      model: "Average",
      objectCounting: 37.29,
      temporalRelationship: 49.29,
      action: 49.37,
      spatialRelationship: 53.57,
      appearance: 63.92,
      overall: 50.69,
      isBest: []
    },
    {
      model: "Human",
      objectCounting: 88.98,
      temporalRelationship: 89.29,
      action: 94.39,
      spatialRelationship: 91.04,
      appearance: 89.71,
      overall: 91.08,
      isBest: [],
      isHuman: true
    }
  ];
  
  // Table captions
  const tableCaptions = {
    qa:"",
    captioning:"",
  };
  
  // Update captioningResults to include affiliation
  captioningResults.forEach(result => {
    // Add affiliations based on model names
    if (result.model.includes("Gemini")) {
      result.affiliation = "Google";
    } else if (result.model.includes("GPT")) {
      result.affiliation = "OpenAI";
    } else if (result.model.includes("LLaVA")) {
      result.affiliation = "Bytedance & NTU S-Lab";
    } else if (result.model.includes("Qwen")) {
      result.affiliation = "Alibaba";
    } else if (result.model.includes("InternVL")) {
      result.affiliation = "Shanghai AI Lab";
    } else if (result.model.includes("VideoChat")) {
      result.affiliation = "MLLM Research";
    }
  });
  
  // Update qaResults to include affiliation
  qaResults.forEach(result => {
    // Add affiliations based on model names
    if (result.model.includes("Gemini")) {
      result.affiliation = "Google";
    } else if (result.model.includes("GPT")) {
      result.affiliation = "OpenAI";
    } else if (result.model.includes("LLaVA")) {
      result.affiliation = "Bytedance & NTU S-Lab";
    } else if (result.model.includes("Qwen")) {
      result.affiliation = "Alibaba";
    } else if (result.model.includes("InternVL")) {
      result.affiliation = "Shanghai AI Lab";
    } else if (result.model.includes("VideoChat")) {
      result.affiliation = "MLLM Research";
    } else if (result.model.includes("Oryx")) {
      result.affiliation = "THU & Tencent & NTU";
    }
  }); 