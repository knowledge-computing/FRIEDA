import os
import fire

import pickle
import polars as pl


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Contextual Image Append Tool')

#     parser.add_argument('--file_data', type=str, required=True)
#     parser.add_argument('--image_dir', type=str, required=True)
#     parser.add_argument('--context_size', type=int, required=True)

#     parser.add_argument('--start_index', type=int, default=0)
#     parser.add_argument('--last_index', type=int, default=None)
    

#     args = parser.parse_args()

#     append_contextual_info(file_name=args.file_data, 
#                            dir_image=args.image_dir,
#                            contextual_size=args.context_size,
#                            start_idx=args.start_index,
#                            last_idx=args.last_index)

def test_orientation(expected_answer):
    with open('', 'rb') as handle:
        dict_orientation = pickle.load(handle)

    ea_idx = list_orientation.index(expected_answer)


    return 0

def main(output:str,
         response_col:str=None):
    pl_vlm_output = pl.read_json()

    # Load orientation dictionary
    with open('./orientation.pkl', 'rb') as handle:
        dict_orientation = pickle.load(handle)

    # Expected answer always in expected answer column
    # Partition by answer_type column

    if not response_col:
        # Identify column with the name 'response'
        response_col = 'response'
        pass

    for df in pl_vlm_output.partition_by('answer_type'):
        if df.items(0, 'answer_type') == 'cardinal':
            df = df.with_columns(
                pl.col('expected_answer').replace(dict_orientation)
            ).with_columns(
                correct = pl.col(response_col).is_in('expected_answer')
            )

        pass

    print(output)

if __name__ == '__main__':
    fire.Fire(main)