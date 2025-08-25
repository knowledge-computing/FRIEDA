import pickle

with open('/home/yaoyi/pyo00005/p2/carto-reasoning/cartoreasoning/response_cache.pkl', 'rb') as handle:
    pl_data = pickle.load(handle)

print(pl_data)

# with open('/home/yaoyi/pyo00005/p2/carto-reasoning/cartoreasoning/response_cache2.pkl', 'rb') as handle:
#     pl_data = pickle.load(handle)

# pl_data = pl_data.unnest('tmp')

# print(pl_data['gemini_response'].to_list())

# for i in pl_data['gemini_response'].to_list():
#     print(i)