window.FRIEDA_LEADERBOARD = {
    meta: {
      dataset: "FRIEDA",
      note: "Some slices are available only for Direct/Full based on current paper tables."
    },
  
    models: [
      // Always show human
      { id: "human", name: "Human Average", group: "Human", sizeB: null, alwaysShow: true },
  
      // Proprietary (unknown sizes)
      { id: "gemini_25_pro", name: "Gemini-2.5-Pro", group: "Proprietary LVLMs", sizeB: null },
      { id: "gpt5_think", name: "GPT-5-Think", group: "Proprietary LVLMs", sizeB: null },
      { id: "claude_sonnet_4", name: "Claude-Sonnet-4", group: "Proprietary LVLMs", sizeB: null },
  
      // Open (known sizes from names)
      { id: "llava_next_110b", name: "LLaVA-NeXT-110B", group: "Open Source LVLMs", sizeB: 110 },
      { id: "glm_45v_108b", name: "GLM-4.5V-108B", group: "Open Source LVLMs", sizeB: 108 },
      { id: "internvl3_78b", name: "InternVL3-78B", group: "Open Source LVLMs", sizeB: 78 },
      { id: "llava_onevision_72b", name: "LLaVA-OneVision-72B", group: "Open Source LVLMs", sizeB: 72 },
      { id: "qwen25_vl_72b", name: "Qwen2.5-VL-72B", group: "Open Source LVLMs", sizeB: 72 },
      { id: "internvl35_38b", name: "InternVL3.5-38B", group: "Open Source LVLMs", sizeB: 38 },
      { id: "ovis2_34b", name: "Ovis2-34B", group: "Open Source LVLMs", sizeB: 34 },
      { id: "ovis25_9b_think", name: "Ovis2.5-9B-Think", group: "Open Source LVLMs", sizeB: 9 }
    ],
  
    // Scores:
    // splits: direct/contextual
    // subset: full/all_agree
    // dimension: overall/spatial_relation/map_count/answer_type/map_element_type/map_element_count/domain
    // slice: a key inside the dimension (e.g., "Border", "Single", etc.)
    scores: {
      direct: {
        full: {
          overall: {
            Overall: {
              human: 84.87,
              gemini_25_pro: 38.20,
              gpt5_think: 37.20,
              claude_sonnet_4: 31.60,
              llava_next_110b: 8.60,
              glm_45v_108b: 6.40,
              internvl3_78b: 11.00,
              llava_onevision_72b: 13.00,
              qwen25_vl_72b: 25.60,
              internvl35_38b: 14.20,
              ovis2_34b: 17.80,
              ovis25_9b_think: 25.80
            }
          },
  
          spatial_relation: {
            Border: {
              human: 89.00,
              gemini_25_pro: 32.39,
              gpt5_think: 25.35,
              claude_sonnet_4: 33.80,
              llava_next_110b: 4.23,
              glm_45v_108b: 5.41,
              internvl3_78b: 1.41,
              llava_onevision_72b: 9.86,
              qwen25_vl_72b: 11.27,
              internvl35_38b: 11.27,
              ovis2_34b: 25.35,
              ovis25_9b_think: 12.68
            },
            Distance: {
              human: 78.28,
              gemini_25_pro: 25.27,
              gpt5_think: 27.47,
              claude_sonnet_4: 23.08,
              llava_next_110b: 10.99,
              glm_45v_108b: 2.15,
              internvl3_78b: 4.40,
              llava_onevision_72b: 10.99,
              qwen25_vl_72b: 14.29,
              internvl35_38b: 8.79,
              ovis2_34b: 13.19,
              ovis25_9b_think: 20.88
            },
            Equal: {
              human: 89.10,
              gemini_25_pro: 33.33,
              gpt5_think: 44.44,
              claude_sonnet_4: 37.04,
              llava_next_110b: 11.11,
              glm_45v_108b: 21.57,
              internvl3_78b: 12.96,
              llava_onevision_72b: 5.56,
              qwen25_vl_72b: 25.93,
              internvl35_38b: 14.81,
              ovis2_34b: 25.93,
              ovis25_9b_think: 24.07
            },
            Intersect: {
              human: 85.53,
              gemini_25_pro: 28.75,
              gpt5_think: 31.25,
              claude_sonnet_4: 22.50,
              llava_next_110b: 16.25,
              glm_45v_108b: 6.17,
              internvl3_78b: 5.00,
              llava_onevision_72b: 8.75,
              qwen25_vl_72b: 17.50,
              internvl35_38b: 2.50,
              ovis2_34b: 26.25,
              ovis25_9b_think: 22.50
            },
            Orientation: {
              human: 91.80,
              gemini_25_pro: 71.59,
              gpt5_think: 69.32,
              claude_sonnet_4: 56.82,
              llava_next_110b: 0.00,
              glm_45v_108b: 1.16,
              internvl3_78b: 34.09,
              llava_onevision_72b: 29.55,
              qwen25_vl_72b: 55.68,
              internvl35_38b: 36.36,
              ovis2_34b: 2.27,
              ovis25_9b_think: 51.14
            },
            Within: {
              human: 88.08,
              gemini_25_pro: 35.34,
              gpt5_think: 28.45,
              claude_sonnet_4: 21.55,
              llava_next_110b: 9.48,
              glm_45v_108b: 7.83,
              internvl3_78b: 7.76,
              llava_onevision_72b: 10.34,
              qwen25_vl_72b: 25.86,
              internvl35_38b: 11.21,
              ovis2_34b: 18.97,
              ovis25_9b_think: 21.55
            }
          },
  
          map_count: {
            Single: {
              human: 84.91,
              gemini_25_pro: 32.67,
              gpt5_think: 23.76,
              claude_sonnet_4: 24.26,
              llava_next_110b: 7.43,
              glm_45v_108b: 4.81,
              internvl3_78b: 6.93,
              llava_onevision_72b: 15.35,
              qwen25_vl_72b: 21.78,
              internvl35_38b: 11.88,
              ovis2_34b: 17.33,
              ovis25_9b_think: 22.28
            },
            Multi: {
              human: 88.08,
              gemini_25_pro: 41.95,
              gpt5_think: 46.31,
              claude_sonnet_4: 36.58,
              llava_next_110b: 9.40,
              glm_45v_108b: 7.53,
              internvl3_78b: 13.76,
              llava_onevision_72b: 11.41,
              qwen25_vl_72b: 28.19,
              internvl35_38b: 15.77,
              ovis2_34b: 18.12,
              ovis25_9b_think: 28.19
            }
          },
  
          answer_type: {
            Textual: {
              human: 87.93,
              gemini_25_pro: 33.06,
              gpt5_think: 30.65,
              claude_sonnet_4: 25.81,
              llava_next_110b: 10.48,
              glm_45v_108b: 8.33,
              internvl3_78b: 6.18,
              llava_onevision_72b: 9.41,
              qwen25_vl_72b: 21.24,
              internvl35_38b: 9.68,
              ovis2_34b: 22.58,
              ovis25_9b_think: 20.43
            },
            Distance: {
              human: 67.18,
              gemini_25_pro: 15.56,
              gpt5_think: 26.67,
              claude_sonnet_4: 28.89,
              llava_next_110b: 8.89,
              glm_45v_108b: 0.00,
              internvl3_78b: 4.44,
              llava_onevision_72b: 11.11,
              qwen25_vl_72b: 8.89,
              internvl35_38b: 66.67,
              ovis2_34b: 11.11,
              ovis25_9b_think: 20.00
            },
            Direction: {
              human: 92.15,
              gemini_25_pro: 73.49,
              gpt5_think: 72.29,
              claude_sonnet_4: 59.04,
              llava_next_110b: 0.00,
              glm_45v_108b: 1.23,
              internvl3_78b: 36.14,
              llava_onevision_72b: 30.12,
              qwen25_vl_72b: 54.22,
              internvl35_38b: 38.55,
              ovis2_34b: 0.00,
              ovis25_9b_think: 53.01
            }
          },
  
          map_element_type: {
            "Map text": {
              human: 80.97,
              gemini_25_pro: 38.80,
              gpt5_think: 38.52,
              claude_sonnet_4: 31.69,
              llava_next_110b: 7.38,
              glm_45v_108b: 5.72,
              internvl3_78b: 9.84,
              llava_onevision_72b: 13.39,
              qwen25_vl_72b: 26.23,
              internvl35_38b: 14.48,
              ovis2_34b: 16.12,
              ovis25_9b_think: 26.78
            },
            Legend: {
              human: 83.61,
              gemini_25_pro: 37.41,
              gpt5_think: 34.05,
              claude_sonnet_4: 31.41,
              llava_next_110b: 8.87,
              glm_45v_108b: 5.74,
              internvl3_78b: 10.31,
              llava_onevision_72b: 11.27,
              qwen25_vl_72b: 24.46,
              internvl35_38b: 12.23,
              ovis2_34b: 18.47,
              ovis25_9b_think: 23.26
            },
            Compass: {
              human: 75.91,
              gemini_25_pro: 56.20,
              gpt5_think: 53.28,
              claude_sonnet_4: 51.83,
              llava_next_110b: 0.73,
              glm_45v_108b: 3.62,
              internvl3_78b: 23.36,
              llava_onevision_72b: 20.44,
              qwen25_vl_72b: 40.88,
              internvl35_38b: 25.55,
              ovis2_34b: 4.38,
              ovis25_9b_think: 38.69
            },
            Scale: {
              human: 63.78,
              gemini_25_pro: 17.39,
              gpt5_think: 28.26,
              claude_sonnet_4: 30.43,
              llava_next_110b: 8.70,
              glm_45v_108b: 0.00,
              internvl3_78b: 4.35,
              llava_onevision_72b: 10.87,
              qwen25_vl_72b: 10.87,
              internvl35_38b: 6.52,
              ovis2_34b: 10.87,
              ovis25_9b_think: 21.74
            }
          },
  
          map_element_count: {
            "1": {
              human: 84.09,
              gemini_25_pro: 35.61,
              gpt5_think: 36.36,
              claude_sonnet_4: 24.24,
              llava_next_110b: 14.39,
              glm_45v_108b: 12.12,
              internvl3_78b: 9.85,
              llava_onevision_72b: 10.61,
              qwen25_vl_72b: 21.97,
              internvl35_38b: 12.12,
              ovis2_34b: 27.27,
              ovis25_9b_think: 23.48
            },
            "2": {
              human: 81.84,
              gemini_25_pro: 35.13,
              gpt5_think: 34.41,
              claude_sonnet_4: 29.75,
              llava_next_110b: 8.24,
              glm_45v_108b: 5.00,
              internvl3_78b: 9.32,
              llava_onevision_72b: 13.62,
              qwen25_vl_72b: 24.37,
              internvl35_38b: 14.34,
              ovis2_34b: 17.20,
              ovis25_9b_think: 24.73
            },
            "3": {
              human: 80.00,
              gemini_25_pro: 55.00,
              gpt5_think: 48.75,
              claude_sonnet_4: 47.50,
              llava_next_110b: 0.00,
              glm_45v_108b: 2.47,
              internvl3_78b: 20.00,
              llava_onevision_72b: 16.25,
              qwen25_vl_72b: 37.50,
              internvl35_38b: 17.50,
              ovis2_34b: 6.25,
              ovis25_9b_think: 33.75
            },
            "4": {
              human: 51.85,
              gemini_25_pro: 22.22,
              gpt5_think: 33.33,
              claude_sonnet_4: 55.56,
              llava_next_110b: 11.11,
              glm_45v_108b: 0.00,
              internvl3_78b: 0.00,
              llava_onevision_72b: 0.00,
              qwen25_vl_72b: 11.11,
              internvl35_38b: 11.11,
              ovis2_34b: 0.00,
              ovis25_9b_think: 22.22
            }
          },
  
          domain: {
            Planning: {
              human: 86.60,
              gemini_25_pro: 37.25,
              gpt5_think: 35.29,
              claude_sonnet_4: 33.33,
              llava_next_110b: 9.80,
              glm_45v_108b: 3.92,
              internvl3_78b: 12.75,
              llava_onevision_72b: 16.67,
              qwen25_vl_72b: 29.41,
              internvl35_38b: 13.73,
              ovis2_34b: 18.63,
              ovis25_9b_think: 21.57
            },
            Investment: {
              human: 88.89,
              gemini_25_pro: 33.33,
              gpt5_think: 25.93,
              claude_sonnet_4: 22.22,
              llava_next_110b: 18.52,
              glm_45v_108b: 0.00,
              internvl3_78b: 7.41,
              llava_onevision_72b: 11.11,
              qwen25_vl_72b: 18.52,
              internvl35_38b: 22.22,
              ovis2_34b: 14.81,
              ovis25_9b_think: 22.22
            },
            Environment: {
              human: 82.33,
              gemini_25_pro: 43.00,
              gpt5_think: 40.00,
              claude_sonnet_4: 28.00,
              llava_next_110b: 6.00,
              glm_45v_108b: 5.00,
              internvl3_78b: 12.00,
              llava_onevision_72b: 11.00,
              qwen25_vl_72b: 21.00,
              internvl35_38b: 15.00,
              ovis2_34b: 19.00,
              ovis25_9b_think: 23.00
            },
            Disaster: {
              human: 83.13,
              gemini_25_pro: 49.40,
              gpt5_think: 54.22,
              claude_sonnet_4: 42.17,
              llava_next_110b: 8.43,
              glm_45v_108b: 8.43,
              internvl3_78b: 16.87,
              llava_onevision_72b: 7.23,
              qwen25_vl_72b: 34.94,
              internvl35_38b: 18.07,
              ovis2_34b: 21.69,
              ovis25_9b_think: 33.73
            },
            Parks: {
              human: 75.76,
              gemini_25_pro: 45.45,
              gpt5_think: 68.18,
              claude_sonnet_4: 50.00,
              llava_next_110b: 13.64,
              glm_45v_108b: 9.09,
              internvl3_78b: 22.73,
              llava_onevision_72b: 22.73,
              qwen25_vl_72b: 22.73,
              internvl35_38b: 18.18,
              ovis2_34b: 22.73,
              ovis25_9b_think: 40.91
            },
            Geology: {
              human: 76.91,
              gemini_25_pro: 30.12,
              gpt5_think: 25.90,
              claude_sonnet_4: 26.51,
              llava_next_110b: 7.23,
              glm_45v_108b: 8.33,
              internvl3_78b: 5.42,
              llava_onevision_72b: 13.86,
              qwen25_vl_72b: 22.89,
              internvl35_38b: 10.24,
              ovis2_34b: 14.46,
              ovis25_9b_think: 24.70
            }
          }
        },
  
        // For now: only overall is available for all_agree (from your table)
        all_agree: {
          overall: {
            Overall: {
              human: 93.93,
              gemini_25_pro: 46.13,
              gpt5_think: 44.11,
              claude_sonnet_4: 24.26,
              llava_next_110b: 9.43,
              glm_45v_108b: 8.67,
              internvl3_78b: 13.80,
              llava_onevision_72b: 14.48,
              qwen25_vl_72b: 28.28,
              internvl35_38b: 14.81,
              ovis2_34b: 20.54,
              ovis25_9b_think: 29.97
            }
          }
        }
      },
  
      contextual: {
        // Only overall is available from your table
        full: {
          overall: {
            Overall: {
              gemini_25_pro: 33.06,
              gpt5_think: 30.65,
              claude_sonnet_4: 25.81,
              llava_next_110b: 10.48,
              glm_45v_108b: 8.33,
              internvl3_78b: 6.18,
              llava_onevision_72b: 9.41,
              qwen25_vl_72b: 21.24,
              internvl35_38b: 9.68,
              ovis2_34b: 22.58,
              ovis25_9b_think: 20.43
            }
          }
        },
        all_agree: {
          overall: {
            Overall: {
              gemini_25_pro: 15.56,
              gpt5_think: 26.67,
              claude_sonnet_4: 28.89,
              llava_next_110b: 8.89,
              glm_45v_108b: 0.00,
              internvl3_78b: 4.44,
              llava_onevision_72b: 11.11,
              qwen25_vl_72b: 8.89,
              internvl35_38b: 6.67,
              ovis2_34b: 11.11,
              ovis25_9b_think: 20.00
            }
          }
        }
      }
    }
  };
  