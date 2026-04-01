# FRIEDA: Benchmarking Multi-Step Cartographic Reasoning in Vision Language Models

<p align="center">
    <a href="https://huggingface.co/datasets/knowledge-computing/FRIEDA/"><img src="https://img.shields.io/badge/🤗-dataset-pink"></a>
    <a href="https://knowledge-computing.github.io/FRIEDA/"><img src="https://img.shields.io/badge/%F0%9F%8F%86-website-8A2BE2"></a>
    <a href="https://arxiv.org/abs/2512.08016"><img src="https://img.shields.io/badge/arXiv-2512.08016-b31b1b.svg"></a>
</p>

<p align="center">
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-data-download">Data Download</a> •
    <a href="#-evaluation">Evaluation</a> •
    <a href="#-lvlm-responses">LVLM Responses</a> •
    <a href="#-citation">Citation</a>
</p>

## <img src="https://github.com/knowledge-computing/FRIEDA/blob/web/static/images/frieda.png?raw=true" width="20" height="20" /> About

**FRIEDA** is a benchmark designed to stress-test **open-ended**, **multi-step cartographic reasoning** in large vision-language models (LVLMs).

FRIEDA is built from *real map figures* collected from documents and technical reports across diverse *domains* (e.g., geology, urban planning, environmental assessment) and *geographic regions*. Grounded in GIS theory, FRIEDA spans a diverse spectrum of spatial relations: **topological** (border, equal, intersect, within), **metric** (distance), and **directional** (orientation). Questions are deliberately compositional: every example requires *multi-hop inference*, and many demand cross-map grounding, where evidence must be located and integrated across multiple maps.

There are two versions of FRIEDA:
- `direct`: This split is to explicitly test cartographic
- `contextual`: This split is to test the capability of getting the correct image and then answer the question

## Quick Start

To get started, please first set up the environment:

```bash
# Install requirements to run FRIEDA evaluation
pip install -r requirements.txt

# Install PyTorch satisfying system requirement
# Refer to: https://pytorch.org/get-started/locally/
pip install torch torchvision

# You are suggested to use `flash-attn` for running LVLMs
pip install packaging ninja
pip install flash-attn --no-build-isolation
# Note: if you have installation problem, consider using pre-built
# wheels from https://github.com/Dao-AILab/flash-attention/releases
```
### API Keys
To use any of the proprietary model, set the API keys:

<details><summary>⏬ View required APIs</summary>
<div>

Access OpenAI APIs from [OpenAI Console](https://platform.openai.com/)
```bash
export OPENAI_API_KEY=<your_openai_api_key>
```

Access Anthropic APIs from [Anthropic Console](https://console.anthropic.com/)
```bash
export ANTHROPIC_API_KEY=<your_anthropic_api_key>
```

Access Gemini APIs from [Google AI Studio](https://aistudio.google.com/)
```bash
export GOOGLE_API_KEY=<your_google_api_key>
```

</div>
</details>

## Data Download

```bash
python3 main.py download \
  --download_dir \                                  # Directory to store FRIEDA
  --method [gdrive|hf]                              # Method to download FRIEDA
```

## Evaluation

```bash
python3 main.py test \
  --model meta-llama/Meta-Llama-3.1-8B-Instruct \   # LVLM model to run
  --split [direct|contextual] \                     # Select between data splits
  --data_dir ./data \                               # Data in which data is stored
  --result_dir ./results \                          # Directory to store the results
  --batch_size 8 \                                  # To set batch size for open_source model
  [--use_flash] \                                   # To run flash attention
  [--evaluate] \                                    # Run performance evaluation
```

- The answer given by the LVLM will be stored as name `[model_name]--frieda-[direct|contextual].json`
- The accuracy result of each LVLM will be stored under name `[model_name]--frieda-[direct|contextual]_eval_results.txt`

<!-- > [!Note]
>
> The `gradio` backend is hosted on the [Hugging Face space](https://huggingface.co/spaces/bigcode/bigcodebench-evaluator) by default.
> The default space can be sometimes slow, so we recommend you to use the `gradio` backend with a cloned [bigcodebench-evaluator](https://huggingface.co/spaces/bigcode/bigcodebench-evaluator) endpoint for faster evaluation.
> Otherwise, you can also use the `e2b` sandbox for evaluation, which is also pretty slow on the default machine.

> [!Note]
>
> BigCodeBench uses different prompts for base and chat models.
> By default it is detected by `tokenizer.chat_template` when using `hf`/`vllm` as backend.
> For other backends, only chat mode is allowed.
>
> Therefore, if your base models come with a `tokenizer.chat_template`,
> please add `--direct_completion` to avoid being evaluated
> in a chat mode.
 -->

## LVLM Responses

We also share the results from LVLMs we have [evaluated]() on both the direct and contextual set:

Check the [results branch](https://github.com/knowledge-computing/FRIEDA/tree/results) which includes them.

<!-- ## 🧑 Advanced Usage

Please refer to the [ADVANCED USAGE](https://github.com/bigcode-project/bigcodebench/blob/main/ADVANCED_USAGE.md) for more details.

## 📰 Result Submission

Please email both the generated code samples and the execution results to [terry.zhuo@monash.edu](mailto:terry.zhuo@monash.edu) if you would like to contribute your model to the leaderboard. Note that the file names should be in the format of `[model_name]--[revision]--[bigcodebench|bigcodebench-hard]-[instruct|complete]--[backend]-[temp]-[n_samples]-sanitized_calibrated.jsonl` and `[model_name]--[revision]--[bigcodebench|bigcodebench-hard]-[instruct|complete]--[backend]-[temp]-[n_samples]-sanitized_calibrated_eval_results.json`. You can [file an issue](https://github.com/bigcode-project/bigcodebench/issues/new/choose) to remind us if we do not respond to your email within 3 days. -->

## Citation

```bibtex
@misc{friedabenchmark2025,
      title={FRIEDA: Benchmarking Multi-Step Cartographic Reasoning in Vision-Language Models}, 
      author={Jiyoon Pyo and Yuankun Jiao and Dongwon Jung and Zekun Li and Leeje Jang and Sofia Kirsanova and Jina Kim and Yijun Lin and Qin Liu and Junyi Xie and Hadi Askari and Nan Xu and Muhao Chen and Yao-Yi Chiang},
      year={2025},
      eprint={2512.08016},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2512.08016}, 
}
```