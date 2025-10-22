import os
import re
import pickle
import polars as pl

from vllm import LLM
from vllm.sampling_params import SamplingParams

def load_model() -> LLM:
    model_name = "mistralai/Ministral-8B-Instruct-2410"
    sampling_params = SamplingParams(max_tokens=1024)
    llm = LLM(model=model_name, tokenizer_mode="mistral", config_format="mistral", load_format="mistral")

    return llm, sampling_params

def _normalize_text_list(lst):
    """
    Lowercase, remove special chars, and strip spaces from list of strings.
    
    Args:
        lst (list)
    """
    if lst is None:
        return []
    if isinstance(lst, str):
        lst = [lst]
    normalized = []
    for s in lst:
        clean = re.sub(r"[^a-zA-Z0-9]+", "", s.strip().lower())
        if clean:
            normalized.append(clean)
    return normalized

def _is_numeric_list(lst):
    """
    Check if entire list contains only numeric values.

    Args:
        lst (list): 
    """
    if not lst:
        return False
    return all(re.fullmatch(r"^\d+(\.\d+)?$", str(x)) for x in lst)

def _llm_eval_mismatch(question_ref, response, expected, llm, sampling_params) -> int:
    """
    Ask Mistral LLM whether the response matches the expected answer.

    Args:
        question_ref
        reponse
        expected
        sampling_params
    """
    prompt = (
        f"Question reference: {question_ref}\n"
        f"Expected answer: {expected}\n"
        f"Given response: {response}\n\n"
        "Does the response correctly answer the question based on expected answer? "
        "Answer strictly 'yes' or 'no'."
    )
    messages = [{"role": "user", "content": prompt}]
    outputs = llm.chat(messages, sampling_params=sampling_params)
    ans = outputs[0].outputs[0].text.strip().lower()

    return 1 if ans.startswith("yes") else 0

def eval_card(df):
    """
    Evaluate cardinal direction answers.

    Args:
        df
    """
    # with open(os.path.join(SUPPORT_PATH, 'orientation.pkl'), 'rb') as handle:
    #     dict_orientation = pickle.load(handle)

    dict_orientation = {}

    def is_correct(row):
        expected = row["expected_answer"]
        response = row["_response"]
        valid_dirs = dict_orientation.get(expected, [expected])
        return 1 if response in valid_dirs else 0

    df = df.with_columns(pl.struct(df.columns).map_elements(is_correct).alias("correct"))
    return df