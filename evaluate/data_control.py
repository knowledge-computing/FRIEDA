from typing import List, Tuple

import polars as pl
from datasets import load_dataset

def load_data(data_path:str=None,
              backend:str='hf') -> pl.DataFrame:        
    if data_path:
        pl_data = pl.read_json(data_path)
    else:
        ds = load_dataset('knowledge-computing/FRIEDA', split="data")
        pl_data = pl.from_pandas(ds)
    
    return _initiate_data(pl_data)

def _initiate_data(pl_data:pl.DataFrame) -> pl.DataFrame:
    if 'answered' not in list(pl_data.columns):
        pl_data = pl_data.with_columns(
            answered=pl.lit(False),
            prediction=pl.lit("NA")
        )

    return pl_data

def _finalize_data(pl_data: pl.DataFrame,
                   bool_revert: bool=False) -> pl.DataFrame:
    """
    """
    unique_ans = pl_data.unique('answered')
    if (unique_ans.shape[0] == 1) and (unique_ans.item(0, 'answered') == True):
        # Either there is a mix of True and False on the answered column
        # Or it is freshly initiated    
        pl_data = pl_data.drop('answered')
        
        if bool_revert:
            pl_data = pl_data.drop('prediction')

    return pl_data

def save_data(pl_data: pl.DataFrame,
              pl_data2: List[pl.DataFrame]=[],
              save_path: str='./dummy.json',
              bool_revert: bool=False) -> None:
    """
    
    """
    if not pl_data2:
        pl_data2.extend(pl_data)
        pl_data = pl.concat(
            pl_data2,
            how='diagonal'
        ).to_pandas()
        print(f"[INFO] Intermediate result saved to {save_path}")

    else:
        pd_data = _finalize_data(pl_data, bool_revert).to_pandas()
        print(f"[INFO] Final result saved to {save_path}")

    pd_data.to_json(save_path,
                    orient='records',
                    indent=4)

def partition_data(pl_data: pl.DataFrame,
                   batch_size: int) -> Tuple[pl.DataFrame, List[pl.DataFrame]]:
    """

    """
    pl_answered = pl_data.filter(pl.col('answered') == True)
    pl_unanswered = pl_data.filter(pl.col('answered') == False)

    batched_questions = []
    for i in range(0, pl_unanswered.height, batch_size):
        chunk = pl_unanswered.slice(i, batch_size)
        batched_questions.append(chunk)

    return pl_answered, batched_questions