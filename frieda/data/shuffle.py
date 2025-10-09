import polars as pl

pl_r = pl.read_json('/projects/standard/yaoyi/pyo00005/carto-reasoning/frieda/data/response_full_d10.json').with_columns(
    pl.col('contextual_urls').list.sample(fraction=1, shuffle=True)
).to_pandas()

pl_r.to_json('./test.json', indent=4, orient='records')

print(pl_r)
