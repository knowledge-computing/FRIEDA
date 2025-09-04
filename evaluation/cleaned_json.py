import polars as pl
import pickle

# pl_data = pl.read_json('/home/yaoyi/pyo00005/p2/carto-reasoning/questions/response_full_d20.json').select(
#     pl.col(['question_ref', 'map_count', 'spatial_relationship', 'answer_type']),
#     pl.col('expected_answer').str.split(';')
# ).explode('expected_answer').with_columns(
#     pl.col('expected_answer').str.strip_chars()
# ).group_by(['question_ref', 'map_count', 'spatial_relationship', 'answer_type']).agg([pl.all()]).sort('question_ref')

# with open('/home/yaoyi/pyo00005/p2/carto-reasoning/evaluation/data_file/answer.pkl', 'wb') as handle:
#     pickle.dump(pl_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

# print(pl_data)

# list_orientation = ['North', 'North East', 'East', 'South East', 'South', 'South West', 'West', 'North West']

# dict_orientation = {}

# for i in list_orientation:
#     idx_o = list_orientation.index(i)
#     try:
#         dict_orientation[i] = [list_orientation[idx_o],
#                             list_orientation[idx_o-1],
#                             list_orientation[idx_o+1]]
#     except:
#         dict_orientation[i] = [list_orientation[idx_o],
#                             list_orientation[idx_o-1],
#                             list_orientation[0]]

# with open('/home/yaoyi/pyo00005/p2/carto-reasoning/evaluation/data_file/orientation.pkl', 'wb') as handle:
#     pickle.dump(dict_orientation, handle, protocol=pickle.HIGHEST_PROTOCOL) 

# print(dict_orientation)