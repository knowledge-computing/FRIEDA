import os
import fire
import re
import pickle
import polars as pl
from vllm import LLM
from vllm.sampling_params import SamplingParams

import torch, gc
import torch.distributed as dist

# Due to some vllm update
# os.environ["FLASHINFER_USE_CUDNN"] = "0"
# os.environ["VLLM_DISABLE_FP8_ATTENTION"] = "1"
# os.environ["VLLM_USE_FP8_ATTENTION"] = "0"
# os.environ["VLLM_ATTENTION_BACKEND"] = "FLASHINFER"

try:
    gc.collect()
    torch.cuda.empty_cache()
    print("[INFO] GC collection & CUDA cache emptying")
except: pass

if torch.cuda.is_available():
    num_gpus = torch.cuda.device_count()
    print(f"Number of dedicated GPUs available: {num_gpus}")
else:
    print("No NVIDIA GPUs found or CUDA is not available.")

SUPPORT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_file')

model_name = "mistralai/Mistral-Small-Instruct-2409"
sampling_params = SamplingParams(max_tokens=512, top_p=1.0, temperature=0.0)
llm = LLM(
    model=model_name,
    tokenizer_mode="mistral",
    load_format="mistral",
    config_format="mistral",
    gpu_memory_utilization=0.98,   # default is conservative; try 0.92–0.98
    max_model_len=4096,
    max_num_seqs=16,
    # kv_cache_dtype="bfloat16",
    dtype="bfloat16",
    tensor_parallel_size=1,
    pipeline_parallel_size=1,
    distributed_executor_backend="mp",
    # attention_backend="cuda",
    # enforce_eager=True,
)

def _llm_extract_ans(question_text, response):
    response = "; ".join(sorted(response))
    prompt = (
        "Given the question and answer, extract only the exact portion of the text that serves as the answer."
        f"Question: {question_text}\n"
        f"Answer: {response}\n\n"
        "Exact answer portion: "
    )

    messages = [{"role": "user", "content": prompt}]
    outputs = llm.chat(messages, sampling_params=sampling_params)
    ans = outputs[0].outputs[0].text.strip()

    return ans.split('Exact answer portion: ')[-1]

def _llm_eval_mismatch(question_text, response, expected):
    """Ask Mistral LLM whether the response matches the expected answer."""
    expected = "; ".join(sorted(expected))
    response = "; ".join(sorted(response))
    # response = "2"

    prompt_eg1 = (
        f"Question: Which team walks through the ABC path?\n"
        f"Expected answer: 2\n"
        f"Given response: Team - 2\n\n"
        "Does the response correctly answer the question based on expected answer?"
        "Answer strictly 'yes' or 'no'."
    )

    prompt_eg2 = (
        f"Question: What are the names of the items on the ground?\n"
        f"Expected answer: Apple; Banana\n"
        f"Given response: Banana; Grape; Apple\n\n"
        "Does the response correctly answer the question based on expected answer?"
        "Answer strictly 'yes' or 'no'."
    )

    prompt = (
        f"Question: {question_text}\n"
        f"Expected answer: {expected}\n"
        f"Given response: {response}\n\n"
        "Does the response correctly answer the question based on expected answer?"
        "Answer strictly 'yes' or 'no'."
    )

    # prompt_eg1 = (
    #     f"Question: Which team walks through the ABC path?\n"
    #     f"Provided Answer: 2\n"
    #     f"Reference Answer: Team - 2\n\n"
    #     "Evaluation:"
    #     "Provide your response in the following format:"
    #     "Decision: [True/False]"
    # )

    

    # prompt_eg2 = (
    #     f"Question: What are the names of the items on the ground?\n"
    #     f"Provided Answer: Apple; Banana\n"
    #     f"Reference Answer: Banana; Grape; Apple\n\n"
    #     "Evaluation:"
    #     "Provide your response in the following format:"
    #     "Decision: [True/False]"
    # )

    # prompt = (
    #     f"Question: {question_text}"
    #     f"Provided Answer: "
    #     f"Reference Answer: {response}"
    #     "Evaluation:"
    #     "Provide your response in the following format:"
    #     "Decision: [True/False]"
    # )

    # system1 = """You are a helpful assistant acting as an impartial judge. You will be given a Question, a Reference Answer, and a Provided Answer. Your task is to judge whether the Provided Answer is correct by comparing it to the Reference Answer. If the Provided Answer is correct, choose ‘True’, otherwise, choose ‘False’."""
    system1 = "You will be given a triple consisting of a question, an expected answer, and a given response. Your task is to output either 'yes' or 'no'. Given the question and response, extract only the exact portion of the text that serves as the answer from the given response. Then output 'yes' if the user response conveys the same meaning as the expected answer in relation to the question. Output 'no' if it does not. For question with multiple correct answers, the expected answers are separated by semicolons. The user response is correct if it matches all required answers, regardless of order. When the user provides more items than required, the response is treated as incorrect. If the user lists fewer items than expected, mark the response as incorrect. Differences in plurality, extra details such as acronyms or counts, minor typographical errors (e.g., 'Corp' vs 'Crop' and 'Cupress' v. 'Cypress'), and differences in wording style do not affect correctness. Focus only on whether the meaning matches."
    messages = [{"role": "assistant", "content": system1},
                {"role": "user", "content": prompt_eg1}, {"role": "assistant", "content": "yes"}, 
                {"role": "user", "content": prompt_eg2}, {"role": "assistant", "content": "no"}, 
                {"role": "user", "content": prompt}]
    outputs = llm.chat(messages, sampling_params=sampling_params)
    ans = outputs[0].outputs[0].text.strip().lower()

    return True if ans.startswith("yes") else False

def _check_mape(expected, response, bool_t:bool=True):
    """Check if entire list contains only numeric values."""
    try:
        flt_expected = float(re.findall(r"\d+\.?\d*", expected[-1])[0])
        flt_response = float(re.findall(r"\d+\.?\d*", response[-1])[0])

        mape_val = (abs(flt_expected - flt_response) / flt_expected) * 100

        if bool_t:
            return True if mape_val <= 20 else False
        else:
            return mape_val
    except: 
        if bool_t:
            return False
        return float('inf')

def eval_dist(df):
    """
    Evaluate distance answers
    """

    df = df.with_columns(
        correct = pl.struct(pl.all()).map_elements(lambda x: _check_mape(x['expected_answer'], x['_response'], bool_t=True))
    )

    print(df)

    return df

def eval_card(df):
    """
    Evaluate cardinal direction answers.
    """
    with open(os.path.join(SUPPORT_PATH, 'orientation.pkl'), 'rb') as handle:
        dict_orientation = pickle.load(handle)

    # .replace(dict_orientation)

    df = df.with_columns(
        pl.col('expected_answer').list.eval(pl.element().str.to_lowercase()),
        pl.col('_response').list.eval(pl.element().str.to_lowercase())
    ).with_columns(
        correct = pl.col('_response').list.set_intersection('expected_answer').list.len() > 0
    )

    print(df.filter(pl.col('correct') == True))

    return df

def eval_text(df):
    """
    Evaluate textual answers, using LLM fallback if necessary.
    """
    
    # First do exact string match
    df = df.with_columns(
        tmp_expected = pl.col('expected_answer').list.eval(pl.element().str.to_lowercase().str.replace_all(r"[^a-z0-9\s]", "")),
        tmp_response = pl.col('_response').list.eval(pl.element().str.to_lowercase().str.replace_all(r"[^a-z0-9\s]", ""))
    ).with_columns(
        correct = pl.col('tmp_expected').list.set_symmetric_difference('tmp_response').list.len() == 0
    ).drop(['tmp_expected', 'tmp_response'])

    # Run llm on eval only on those that are false
    df_false = df.filter(pl.col('correct') == False).drop('correct').with_columns(
        correct = pl.struct(pl.all()).map_elements(lambda x: _llm_eval_mismatch(x['question_text'], x['_response'], x['expected_answer']))
    )
    
    df_true = df.filter(pl.col('correct') == True)

    df_full = pl.concat(
        [df_true, df_false],
        how='diagonal'
    )

    print(df_full)

    return df_full

def main(output_file, gt_file: str, 
         output_path:str,
         response_col: str = None):
    pl_output = output_file

    # Get required columns
    list_cols = ["question_ref"]
    if not response_col or response_col not in pl_output.columns:
        response_col = next((col for col in pl_output.columns if col.endswith("_response")), None)
        if response_col is None:
            raise ValueError("No response column found matching pattern '*_response'")
    pl_output = pl_output.rename({response_col: "_response"})
    list_cols.append("_response")
    pl_output = pl_output.select(list_cols)

    print(pl_output)

    # Load answer dataframe
    pl_ans = pl.read_json(gt_file).drop('contextual_urls')

    # Append response dataframe to ground truth dataframe
    pl_output = pl.concat([pl_output, pl_ans], how="align").drop_nulls("_response")

    # TODO: REMOVE TEMPORARY FOR ANNOTATORS
    pl_output = pl_output.drop_nulls("question_text")

    # Obtain part after 'final answer:' just for checking purpose (TODO: delete?)
    pl_output = pl_output.with_columns(
        pl.col("_response").str.split('final answer: ').list.get(-1)
    )

    # Split multi-answer columns into lists and clean strings
    pl_output = pl_output.with_columns(
        pl.col(["expected_answer", "_response"])
        .str.split(";")
        .list.eval(pl.element().str.strip_chars())
    )

    # TODO: REMOVE ONLY USED FOR EVAL-ING CARDINAL
    # pl_output = pl_output.filter(
    #     pl.col('answer_type') == 'cardinal'
    # )

    # Answer extraction
    # pl_output = pl_output.with_columns(
    #     pl.struct(pl.all()).map_elements(lambda x: _llm_extract_ans(x['question_text'], x['_response'])).alias('extracted_ans')
    # )
    
    pd_evaled = pl_output.to_pandas()
    
    # Partition and evaluate by answer type
    pl_evaled = pl.DataFrame()

    # Answer extraction

    for df in pl_output.partition_by("answer_type"):

        # print(df)
        ans_type = df["answer_type"][0]
        if ans_type == "distance":
            pl_evaled = pl.concat([pl_evaled, eval_dist(df)], how="diagonal")
            pass
        elif ans_type == "textual":
            pl_evaled = pl.concat([pl_evaled, eval_text(df)], how="diagonal")
            pass
        else:   # Cardinal
            pl_evaled = pl.concat([pl_evaled, eval_card(df)], how="diagonal")
            # print(pl_evaled)

    try:
        print(pl_evaled.filter(pl.col('correct') == True))
    except:
        pass

    pd_evaled = pl_evaled.to_pandas()
    pd_evaled.to_json(output_path, orient='records', indent=4)


if __name__ == "__main__":
    # fire.Fire(main)
    # for i in range(3):
    # result_dir = '/users/2/pyo00005/HOME/carto-reasoning/run_results'
    # output_directory = '/users/2/pyo00005/HOME/carto-reasoning/evaluation_results'
    # for model_name in ['glm45v']:
    # # for model_name in ['no_think', 'think']:
    #     # if not os.path.exists(os.path.join(output_directory, model_name)):
    #     #     os.makedirs(os.path.join(output_directory, model_name))

    #     for i in os.listdir(os.path.join(result_dir, model_name)): 
    #         output_file = f'{result_dir}/{model_name}/{i}'

    list_items = [
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/gemini25pro/gemini_wo_contextual.json', 'gemini'),
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/claude-sonnet4/sonnet_wo_contextual.json', 'sonnet'), 
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/glm45v/glm45v-108B_wo_contextual.json', 'glm45v'), 
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/gpt5/gpt5_wo_contextual.json', 'gpt5'), 
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/internvl3/internvl3-78B_wo_contextual.json', 'internvl3'), 
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/internvl35/no_think/internvl35-38B_wo_contextual.json', 'internvl35'), 
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/llava-next/llava-next-110B_wo_contextual.json', 'llavanext'), 
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/llava-ov/llava-ov-72B_wo_contextual.json', 'llavaov'), 
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/ovis2/ovis2-34B_wo_contextual.json', 'ovis2'), 
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/ovis25/ovis25-9B-think_wo_contextual.json', 'ovis25'),
        # ('/users/2/pyo00005/HOME/carto-reasoning/evaluation_results/qwen25vl/qwen25vl-72B_wo_contextual.json', 'qwen25'),
        ('/users/2/pyo00005/HOME/carto_reason/human_result/annot1.json', 'h1'),
        ('/users/2/pyo00005/HOME/carto_reason/human_result/annot2.json', 'h2'), 
        ('/users/2/pyo00005/HOME/carto_reason/human_result/annot3.json', 'h3'), 
    ]

    for i, j in list_items:
        pl_output = pl.read_json(i)

            # output_file = '/home/yaoyi/pyo00005/carto-reasoning/questions/annotator_response/response_all.json'
            # pl_output = pl.read_json(output_file)
            # pl_output = pl_output.with_columns(
            #     pl.col('annotator_response').list.get(i)
            # )

                # 
                # gt_file = f'/home/yaoyi/pyo00005/carto-reasoning/questions/response_full_d10.json'
                # output_path = f'{output_directory}/{model_name}/{i}'

            # output_path = f'./tmp_ver5_{i}.json'
        main(output_file=pl_output, gt_file="/projects/standard/yaoyi/pyo00005/FRIEDA-dataset/data/frieda_q_bank.json", output_path=f"/users/2/pyo00005/HOME/carto_reason/new_prompt/{j}.json")