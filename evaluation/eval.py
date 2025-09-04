import os
import fire

import re

import pickle
import polars as pl

SUPPORT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_file')

def eval_dist(df):
    # takes in a polar dataframe df and returns a polar dataframe with added column correct
    # the _response column will have responses to distance (e.g., 40 MILES)
    # the expected_answer column will have expected answer for the distance with acceptable bounds (e.g., 38 \pm 2 MILES)
    # if the _response value exists within the acceptable bound (in the example case 36-40) inclusive, then give 1 to the correct column
    # Otherwise give 0 to column

    regex_pattern = r"\d+\.?\d*"

    df = df.with_columns(
        pl.col('_response').map_elements(
            lambda x: float(re.search(regex_pattern, x).group()))
    )
    return df

def eval_card(df):
    # takes in a polar dataframe df and returns a polar dataframe with added column correct
    # the _response column will have responses to cardinal direction (e.g., North, North West)
    # the expected_answer column will have expected answer for cardinal direction
    # orientation.pkl file consists of cardinal directions and acceptable cardinal directions (e.g., North: [North, North West, North East]). it is a dictionary with the key being the orientation
    # if the _response is within the acceptable cardinal reictions of the expected answer give 1 to correct column
    # Otherwise give 0 to column

    with open(os.path.join(SUPPORT_PATH, 'orientation.pkl'), 'rb') as handle:
        dict_orientation = pickle.load(handle)

    df = df.with_columns(
        pl.col('expected_answer').replace(dict_orientation)
    )
    return df

def eval_text(df):
    # takes in a polar dataframe df and returns a polar dataframe with added column correct
    # the _response column will have responses to textual answers
    # both the _response and expected answer columns are lists.
    # lowercase all items in response and expected answer, then remove special characters
    # compare the set symmetric difference between the two. if the two columns match, they will be considered correct
    # if they do not match, fall to llm-as-evaluators. We will be using mistral for this model on very bottom
    # depending on the answer of mistral give the final answer as 1 or 0
    # some answers for the textual are purely number (e.g., count questions and answers that are numerical), for these do not fall into llm-evaluator; if they are different they are just wrong. only apply these if the content is fully numeric

    df = df.with_columns(
        sdiff = pl.col('_response').list.set_symmetric_difference('expected_answer').list.len()
    )

    df_clear = df.filter

    return df

def main(output_file:str,
         response_col:str=None):
        
    # Load output file
    pl_output = pl.read_json(output_file)

    # Get required column
    list_cols = ['question_ref', 'expected_answer']
    if (response_col not in list(pl_output.columns)) or (not response_col):
        # list_cols.append('^.*_response$')
        response_col = '^.*_response$'
    # else:
    pl_output = pl_output.rename({response_col, '_response'})
    list_cols.append('_response')
    pl_output = pl_output.select(list_cols)
    
    # Load answer_type dataframe
    pl_at = pl.read_json(os.path.join(SUPPORT_PATH, 'ans_type.json')).select(
        pl.col(['question_ref', 'answer_type'])
    )

    # Append answer type information & (and drop empty just in case)
    pl_output = pl.concat(
        [pl_output, pl_at],
        how='align').drop_nulls('question_ref')
    
    # Split mulit_answer column
    pl_output = pl_output.with_columns(
        pl.col(['expected_answer', '^.*_response$'])
        .str.split(';')
        .list.eval(pl.element().str.strip_chars())
    )
    
    pl_evaled = pl.DataFrame()
    # Partition response by the answer type
    for df in pl_output.partition_by('answer_type'):
        ans_type = df.items(0, 'answer_type')

        if ans_type == 'distance':
            pl_evaled = pl.concat(
                [pl_evaled, eval_dist(df)],
                how='diagonal'
            )

        elif ans_type == 'textual':
            pl_evaled = pl.concat(
                [pl_evaled, eval_text(df)],
                how='diagonal'
            )

        else:
            pl_evaled = pl.concat(
                [pl_evaled, eval_card(df)],
                how='diagonal'
            )

    return pl_evaled

if __name__ == '__main__':
    fire.Fire(main)


# from vllm import LLM
# from vllm.sampling_params import SamplingParams

# model_name = "mistralai/Ministral-8B-Instruct-2410"

# sampling_params = SamplingParams(max_tokens=8192)

# # note that running Ministral 8B on a single GPU requires 24 GB of GPU RAM
# # If you want to divide the GPU requirement over multiple devices, please add *e.g.* `tensor_parallel=2`
# llm = LLM(model=model_name, tokenizer_mode="mistral", config_format="mistral", load_format="mistral")

# prompt = "Do we need to think for 10 seconds to find the answer of 1 + 1?"

# messages = [
#     {
#         "role": "user",
#         "content": prompt
#     },
# ]

# outputs = llm.chat(messages, sampling_params=sampling_params)

# print(outputs[0].outputs[0].text)
# # You don't need to think for 10 seconds to find the answer to 1 + 1. The answer is 2,
# # and you can easily add these two numbers in your mind very quickly without any delay.
