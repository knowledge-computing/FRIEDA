import os
import argparse
import dotenv
from typing import List, Dict
from tqdm import tqdm

import json
import pickle
import polars as pl

# # Gemini packages
# from google import genai
# from google.genai import types

# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def check_exist(path_dir):
    if os.path.exists(path_dir):
        return 1
    
    os.makedirs(path_dir)
    return 0

# def upload_images(images:List[str],
#                  image_prefix:str=None,
#                  save_cache:bool=True,
#                  cache_dir:str=None):
#     # Recommended for repetitively used files or large files
#     dict_im_data = {}   # Storing mapping from image to API images

#     for im_path in list(set(images)):
#         if image_prefix:
#             full_path = os.path.join(image_prefix, im_path)
        
#         loaded_im = client.files.upload(file=full_path)

#         dict_im_data[im_path] = loaded_im.name

#         if save_cache:
#             with open(os.path.join(cache_dir, 'image_cache.pkl'), 'wb') as handle:
#                 pickle.dump(dict_im_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

#     return dict_im_data

# def make_chat_prompt(question:str,
#                      file_list:List[str],) -> list:
    
#     if len(distractor_list) > 0:
#         img_list.extend(distractor_list)

#     myfile = client.files.get(name=file_name)

#     content = [question]
#     return content

# def respond_q(model:str,
#               dict_im_data:Dict[str, str],
#               question_q:str,
#               img_list:List[str],
#               distractor_list:List[str]=[]):
    
#     content = make_chat_prompt(question_q, 
#                                img_list)

#     response = client.models.generate_content(
#         model = model,
#         contents = content
#     )
#     return response.text

def main(model:str,
         question_path:str,
         image_folder:str,
         bool_distractor:bool,
         output_dir:str,
         cache_dir:str):
    
    # Create directory paths
    check_exist(output_dir)
    check_exist(cache_dir)

    # # Load question JSON file
    # with open(question_path, 'r') as file:
    #     data = json.load(file)
    
    # # Uploading images to path storage
    # if len(client.files.list()) == 0:
    # # if True:
    #     all_images = []
    #     for d in data:
    #         all_images.extend(d['image_urls'])
    #         all_images.extend(d['distractor_urls'])

    #     dict_im_data = upload_images(images=all_images,
    #                                  image_prefix=image_folder,
    #                                  save_cache=True,
    #                                  cache_dir=cache_dir)
    # else:
    #     with open(os.path.join(cache_dir, 'image_cache.pkl'), 'rb') as handle:
    #         dict_im_data = pickle.load(handle)
    
    pl_question = pl.read_json(question_path).with_columns(
        q_answered = pl.lit(False),
        distractor_urls = pl.lit(['fake'])      # remove after adding distractor urls
    ).with_columns(
        pl.when(bool_distractor)
        .then(pl.concat_list('distractor_urls', 'image_urls'))
        .otherwise(pl.col('image_urls')).alias('image_lists')
    )

    print(pl_question)

    answer_cache = os.path.join(output_dir, 'response_cache.pkl')

    if bool_distractor:
        return 0

    return 0

# if __name__ == "main":
#     parser = argparse.ArgumentParser(description='Cartographical Reasoning Test')

#     parser.add_argument('--model', '-m', required=True,
#                         help='Model name/type')

#     parser.add_argument('--questions', '-q', required=True,
#                         help='Path to questions JSON file')

#     parser.add_argument('--images', '-im', default='./', type=str,
#                         help="Directory/link to reporsitory containing images")
    
#     parser.add_argument('--distractor', '-d', action="store_true", 
#                         help='Use distractor images')
   
#     parser.add_argument('--output_dir', '-o', default='./',
#                         help="Location to output files")
    
#     parser.add_argument('--cache_dir', '-c', default='./',
#                         help="Location to cache directory (cache for image names)")
    
#     main(model=parser.model,
#          question_path=parser.questions,
#          image_folder=parser.images,
#          bool_distractor=parser.distractor,
#          output_dir=parser.output_dir,
#          cache_dir=parser.cache_dir)

main(model='gemini-2.5-flash',
    question_path='/home/yaoyi/pyo00005/carto-reasoning/questions/all-agree/border.json',
    image_folder='/home/yaoyi/pyo00005/carto-reasoning/img-raw',
    bool_distractor=False,
    output_dir='./',
    cache_dir='./')