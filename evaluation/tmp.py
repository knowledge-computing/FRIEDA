import polars as pl
import re
import statistics
import copy


regex_pattern = r"\d+\.?\d*"

pl_data = pl.read_json('/home/yaoyi/pyo00005/p2/carto-reasoning/questions/response_full_d20.json').filter(
    pl.col('answer_type') == 'distance'
)

def std_calculation(expected_answer, annotator_response):
    expected_answer = float(re.search(regex_pattern, expected_answer).group())

    list_response = []
    for r in annotator_response:
        if (r == "None") or (not r):
            pass
        else:
            list_response.append(float(re.search(regex_pattern, r).group()))

    list_annotator = copy.deepcopy(list_response)
    list_annotator.append(expected_answer)
    list_response.append(expected_answer)
    # list_response = 

    while True:
        mean_value = statistics.mean(list_response)
        median_value = statistics.median(list_response)
        std_value = statistics.stdev(list_response)

        list_tf = []

        count = 0
        for a in list_response:
            if (a < expected_answer-(2*std_value)) or (a > expected_answer+(2*std_value)):
                list_response.remove(a)
                count += 1
            else:
                pass

        if count == 0:
            break

    # print(mean_value, median_value, std_value)
    
    return {'annotator_response': list_annotator, 
            'mean': mean_value,
            'median': median_value,
            'std': std_value,
            'expected_value': expected_answer,}

pl_annotator = pl.read_json('/home/yaoyi/pyo00005/p2/carto-reasoning/questions/annotator_response/response_all.json')

pl_full = pl.concat(
    [pl_data, pl_annotator],
    how='align_left'
).select(
    pl.col('question_ref'),
    tmp = pl.struct(pl.all()).map_elements(lambda x: std_calculation(x['expected_answer'], x['annotator_response']))
).unnest('tmp').explode('annotator_response')

pl_full.write_csv('./tmp.csv')

print(pl_full)

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
