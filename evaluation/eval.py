import polars as pl
import re
import statistics

# Update response all

pl_data = pl.read_json('/home/yaoyi/pyo00005/p2/carto-reasoning/questions/response_full_d20.json').select(
    pl.col(['question_ref', 'question_text', 'expected_answer'])
)

pl_annotator = pl.read_json('/home/yaoyi/pyo00005/p2/carto-reasoning/questions/annotator_response/response_all.json').select(
    pl.col(['question_ref', 'annotator_response'])
)

pl_full = pl.concat(
    [pl_data, pl_annotator],
    how='align'
).select(
    pl.col(['question_ref', 'question_text', 'expected_answer', 'annotator_response'])
)

pd_full = pl_full.to_pandas()
pd_full.to_json('/home/yaoyi/pyo00005/p2/carto-reasoning/questions/annotator_response/response_all.json', orient='records', indent=4)


# regex_pattern = r"\d+\.?\d*"

# pl_data = pl.read_json('/home/yaoyi/pyo00005/p2/carto-reasoning/questions/response_full_d20.json').filter(
#     pl.col('answer_type') == 'distance'
# )

# def std_calculation(expected_answer, annotator_response):
#     expected_answer = float(re.search(regex_pattern, expected_answer).group())
#     # annotator_response = list(filter(None, annotator_response))
#     # list_response = []

#     # for r in annotator_response:
#     #     if r:
#     #         list_response.append(float(re.search(regex_pattern, r).group()))

#     print(expected_answer, annotator_response)
    
#     return 0

# pl_annotator = pl.read_json('/home/yaoyi/pyo00005/p2/carto-reasoning/questions/annotator_response/response_all.json')

# pl_full = pl.concat(
#     [pl_data, pl_annotator],
#     how='align_left'
# ).with_columns(
#     pl.struct(pl.all()).map_elements(lambda x: std_calculation(x['expected_answer'], x['annotator_response']))
# )


# print(pl_full)

# text = "Hello, world! 1234"
# regex_pattern = r"\d+\.?\d*"

# match = re.search(regex_pattern, text).group()

# print(match)





####


# orientation = ['North',
#                'North West',
#                'West',
#                'South West',
#                'South',
#                'South East',
#                'East',
#                'North East']

# answer = 'North'

# answer_idx = orientation.index(answer)
# list_indexes = [answer_idx, answer_idx-1, answer_idx+1]
# acceptable = [orientation[i] for i in list_indexes]

# print(acceptable)

# import statistics

# data = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# # Calculate the mean
# mean_value = statistics.mean(data)
# print(f"Mean: {mean_value}")

# # Calculate the median
# median_value = statistics.median(data)
# print(f"Median: {median_value}")
