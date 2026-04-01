from sklearn.metrics import cohen_kappa_score
import polars as pl


support = pl.read_json('')['correct'].to_list()

list_files = [
    
]

for j in list_files:
    against = pl.read_json(j)['correct'].to_list()

    print(j, cohen_kappa_score(support, against))