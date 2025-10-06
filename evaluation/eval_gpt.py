import os
import fire
import re
import pickle
import polars as pl
from vllm import LLM
from vllm.sampling_params import SamplingParams

SUPPORT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_file')

# Load Mistral LLM once at the top (optional: lazy load later if speed matters)
model_name = "mistralai/Ministral-8B-Instruct-2410"
sampling_params = SamplingParams(max_tokens=1024)
llm = LLM(model=model_name, tokenizer_mode="mistral", config_format="mistral", load_format="mistral")

def _normalize_text_list(lst):
    """Lowercase, remove special chars, and strip spaces from list of strings."""
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
    """Check if entire list contains only numeric values."""
    if not lst:
        return False
    return all(re.fullmatch(r"^\d+(\.\d+)?$", str(x)) for x in lst)

def _llm_eval_mismatch(question_ref, response, expected):
    """Ask Mistral LLM whether the response matches the expected answer."""
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

def eval_dist(df):
    """
    Evaluate distance answers.
    """
    regex_pattern = r"\d+\.?\d*"

    def is_correct(row):
        # Parse numeric response
        resp_match = re.search(regex_pattern, row["_response"])
        if not resp_match:
            return 0
        response_val = float(resp_match.group())

        # Parse expected answer (e.g., "38 ± 2 MILES")
        expected = row["expected_answer"]
        expected_match = re.findall(regex_pattern, expected)
        if not expected_match:
            return 0

        expected_val = float(expected_match[0])
        tolerance = 0
        if "±" in expected:
            tol_match = re.findall(regex_pattern, expected)
            if len(tol_match) >= 2:
                tolerance = float(tol_match[1])

        lower_bound = expected_val - tolerance
        upper_bound = expected_val + tolerance

        return 1 if lower_bound <= response_val <= upper_bound else 0

    df = df.with_columns(pl.struct(df.columns).map_elements(is_correct).alias("correct"))
    return df

def eval_card(df):
    """
    Evaluate cardinal direction answers.
    """
    with open(os.path.join(SUPPORT_PATH, 'orientation.pkl'), 'rb') as handle:
        dict_orientation = pickle.load(handle)

    def is_correct(row):
        expected = row["expected_answer"]
        response = row["_response"]
        valid_dirs = dict_orientation.get(expected, [expected])
        return 1 if response in valid_dirs else 0

    df = df.with_columns(pl.struct(df.columns).map_elements(is_correct).alias("correct"))
    return df

def eval_text(df):
    """
    Evaluate textual answers, using LLM fallback if necessary.
    """
    def is_correct(row):
        resp_list = _normalize_text_list(row["_response"])
        exp_list = _normalize_text_list(row["expected_answer"])

        # Numeric-only case → strict comparison
        if _is_numeric_list(resp_list) and _is_numeric_list(exp_list):
            return 1 if resp_list == exp_list else 0

        # Compare sets directly
        if set(resp_list) == set(exp_list):
            return 1

        # If mismatch → fallback to LLM
        return _llm_eval_mismatch(row["question_ref"], resp_list, exp_list)

    df = df.with_columns(pl.struct(df.columns).map_elements(is_correct).alias("correct"))
    return df

def main(output_file: str, response_col: str = None):
    # Load output file
    pl_output = pl.read_json(output_file)

    # Get required columns
    list_cols = ["question_ref"]
    if not response_col or response_col not in pl_output.columns:
        response_col = next((col for col in pl_output.columns if col.endswith("_response")), None)
        if response_col is None:
            raise ValueError("No response column found matching pattern '*_response'")
    pl_output = pl_output.rename({response_col: "_response"})
    list_cols.append("_response")
    pl_output = pl_output.select(list_cols)

    # Load answer type dataframe
    with open(os.path.join(SUPPORT_PATH, "answer.pkl"), 'rb') as handle:
        pl_at = pickle.load(handle)
    # pl_at = pl.read_json(os.path.join(SUPPORT_PATH, "ans_type.json")).select(
    #     pl.col(["question_ref", "answer_type"])
    # )

    # Append answer type
    pl_output = pl.concat([pl_output, pl_at], how="align").drop_nulls("question_ref")

    # Split multi-answer columns into lists and clean strings
    pl_output = pl_output.with_columns(
        pl.col(["expected_answer", "_response"])
        .str.split(";")
        .list.eval(pl.element().str.strip_chars())
    )

    # Partition and evaluate by answer type
    pl_evaled = pl.DataFrame()
    for df in pl_output.partition_by("answer_type"):
        ans_type = df["answer_type"][0]
        if ans_type == "distance":
            pl_evaled = pl.concat([pl_evaled, eval_dist(df)], how="diagonal")
        elif ans_type == "textual":
            pl_evaled = pl.concat([pl_evaled, eval_text(df)], how="diagonal")
        else:
            pl_evaled = pl.concat([pl_evaled, eval_card(df)], how="diagonal")

    return pl_evaled

if __name__ == "__main__":
    fire.Fire(main)
