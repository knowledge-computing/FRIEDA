import polars as pl
import pandas as pd

updated_data = pl.read_json('./response_full.json')

distractor_data = ['./response_full_d20.json', './response_full_30.json']

for d in distractor_data:
    t_data = pl.read_json(d).select(
        pl.col(['question_ref', 'contextual_urls'])
    )

    pl_data = pl.concat(
        [updated_data, t_data],
        how='align'
    ).sort('question_ref')

    pd_data = pl_data.to_pandas()
    pd_data.to_json(d, orient='records', indent=4)