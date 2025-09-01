import os
import argparse

from dotenv import load_dotenv
from typing import List, Dict

import time
from tqdm import tqdm

import json
import pickle
import polars as pl

# Gemini packages
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

with open('./instruction.pkl', 'rb') as handle:
    instructions = pickle.load(handle)
    instructions += "DO NOT use web search."    # Adding in case they use search

def check_exist(path_dir, bool_create=True):
    if os.path.exists(path_dir):
        return 1
    
    if bool_create:
        os.makedirs(path_dir)
        return 0
    
    return -1

def upload_images(images:List[str],
                 image_prefix:str=None,
                 save_cache:bool=True,
                 cache_dir:str=None):
    # Recommended for repetitively used files or large files
    dict_im_data = {}   # Storing mapping from image to API images

    for im_path in list(set(images)):
        if image_prefix:
            full_path = os.path.join(image_prefix, im_path)
        
        loaded_im = client.files.upload(file=full_path)

        dict_im_data[im_path] = loaded_im.name

        if save_cache:
            with open(os.path.join(cache_dir, 'image_cache.pkl'), 'wb') as handle:
                pickle.dump(dict_im_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return dict_im_data

def make_chat_prompt(question:str,
                     file_list:List[str],
                     dict_im_data:Dict[str, str],
                     bool_async:bool=False) -> list:
    
    if bool_async:
        imgs = [{"file_data": 
                    {"file_uri": dict_im_data[fn],
                     "mime_type": client.files.get(name=dict_im_data[fn]).mime_type}} 
               for fn in file_list]
        content = [{"text": question}]
        
    else:
        imgs = [client.files.get(name=dict_im_data[fn]) for fn in file_list]

        content = [question]
    content.extend(imgs)

    return content

def respond_q(model:str,
              dict_im_data:Dict[str, str],
              question_q:str,
              img_list:List[str]):
    
    content = make_chat_prompt(question_q, 
                               img_list,
                               dict_im_data)

    response = client.models.generate_content(
        model = model,
        config=types.GenerateContentConfig(
            system_instruction=[
                instructions
            ]
        ),
        contents = content
    )

    return {'gemini_response': response.text}

def gemini_sync(model,
                dict_im_data,
                pl_question,
                response_cache):
    # Running inference in chunks (of 20) in case it crashs in middle
    chunk_size = 20 
    pl_answered = pl.DataFrame()

    if check_exist(response_cache) == 1: 
        with open(response_cache, 'rb') as handle:
            pl_answered = pickle.load(handle)

        cache_length = pl_answered.shape[0]
        pl_question = pl_question[cache_length:]

    for i in tqdm(range(0, pl_question.height, chunk_size)):
        chunk = pl_question.slice(i, chunk_size)
        chunk = chunk.with_columns(
            tmp = pl.struct(pl.all()).map_elements(lambda x: respond_q(model, dict_im_data, x['question_text'], x['image_lists']))
        ).with_columns(
            pl.col('q_answered').replace({False: True})
        ).unnest('tmp').drop('image_lists')

        pl_answered = pl.concat(
            [pl_answered, chunk],
            how='diagonal'
        )

        with open(response_cache, 'wb') as handle:
            pickle.dump(pl_answered, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Saving as JSON with model name appended
    pd_answered = pl_answered.to_pandas()

    return pd_answered, response_cache

def gemini_async(model,
                 dict_im_data,
                 pl_question,
                 cache_dir,):
    
    input_struct = pl_question.select(
        tmp = pl.struct(pl.all())
    )['tmp'].to_list()

    with open(os.path.join(cache_dir, "batch_requests.jsonl"), "w") as f:
        for i in input_struct:
            content = make_chat_prompt(i["question_text"], 
                                       i["image_lists"],
                                       dict_im_data,
                                       True)
            
            request = {
                "key": i["question_ref"],
                "request": {
                    "system_instruction": {
                        "parts": [{"text": instructions}]
                    },
                    "contents": content
                }
            }

            f.write(json.dumps(request) + '\n')

    # Upload batch file to File API
    batch_input = client.files.upload(
        file=os.path.join(cache_dir, "batch_requests.jsonl"),
        config=types.UploadFileConfig(display_name="carto-reason-batch", mime_type="jsonl"),
    )

    # Create batch job
    job = client.batches.create(
        model=model,
        src=batch_input.name,  # the uploaded JSONL File name
        config={"display_name": "carto-eval-run-01"},
    )
    print("Batch job:", job.name)  # e.g., "batches/abcdef123"

    return job.name

def main(model:str,
         question_path:str,
         image_folder:str,
         bool_distractor:bool,
         output_dir:str,
         cache_dir:str,
         bool_batch:bool,
         img_limit:int,):
    
    # Create directory paths
    check_exist(output_dir)
    check_exist(cache_dir)

    # Load question JSON file
    with open(question_path, 'r') as file:
        data = json.load(file)
    
    # Uploading all images to path storage
    if len(client.files.list()) == 0:
    # if True:
        all_images = []
        for d in data:
            all_images.extend(d['image_urls'])
            all_images.extend(d['contextual_urls'])

        dict_im_data = upload_images(images=all_images,
                                     image_prefix=image_folder,
                                     save_cache=True,
                                     cache_dir=cache_dir)
    else:
        with open(os.path.join(cache_dir, 'image_cache.pkl'), 'rb') as handle:
            dict_im_data = pickle.load(handle)
    
    pl_question = pl.read_json(question_path).with_columns(
        q_answered = pl.lit(False),
    ).with_columns(
        pl.when(bool_distractor)
        .then(pl.concat_list('contextual_urls', 'image_urls'))
        .otherwise(pl.col('image_urls')).alias('image_lists')
    )

    # Common file names amonst async/sync
    response_cache = os.path.join(cache_dir, 'response_cache.pkl')
    if bool_distractor:
        new_file_name = os.path.join(output_dir, 'gemini_w_contextual.json')
    else:
        new_file_name = os.path.join(output_dir, 'gemini_wo_contextual.json')
    new_file_name = f"{question_path.split('.json')[0]}_{model}.json"
    
    if not bool_batch:
        # Run Sync
        pd_answered, response_cache = gemini_sync(model=model, 
                                  dict_im_data=dict_im_data, pl_question=pl_question,
                                  response_cache=response_cache)
        
        pd_answered.to_json(new_file_name, orient='records', indent=4)

        # Removing response cache pickle file
        os.remove(response_cache)

    else:
        # Run Async
        job_name = gemini_async(model=model, 
                                dict_im_data=dict_im_data, pl_question=pl_question,
                                cache_dir=cache_dir)
        
        # Information while running async
        dict_info = {
            "job_name": job_name,
            "output_dir": output_dir,
            "cache_dir": cache_dir,
            "output_fn": new_file_name
        }

        with open(response_cache, 'wb') as handle:
            pickle.dump(dict_info, handle, protocol=pickle.HIGHEST_PROTOCOL)

        print(f"Batch job information stored in dir {cache_dir}")
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cartographical Reasoning Test')

    parser.add_argument('--model', '-m', default='gemini-2.5-pro',
                        help='Model name/type')

    parser.add_argument('--questions', '-q', required=True,
                        help='Path to questions JSON file')

    parser.add_argument('--images', '-im', type=str,
                        help="Directory/link to repository containing images")
    
    parser.add_argument('--distractor', '-d', action="store_true", 
                        help='Use distractor images')
   
    parser.add_argument('--output_dir', '-o', default='./responses',
                        help="Location to output files")
    
    parser.add_argument('--cache_dir', '-c', default='./',
                        help="Location to cache directory (cache for image names)")
    
    parser.add_argument('--batch', action="store_true", 
                        help="Use batch mode")
    
    parser.add_argument('--max_images', '-max', type=int, default=20,
                        help="FOR DEVELOPING TEST PURPOSE")
    
    args = parser.parse_args()
    
    main(model=args.model,
         question_path=args.questions,
         image_folder=args.images,
         bool_distractor=args.distractor,
         output_dir=args.output_dir,
         cache_dir=args.cache_dir,
         bool_batch=args.batch,
         img_limit=args.max_images)

    # main(model='gemini-2.5-flash-lite',
    #     question_path='/home/yaoyi/pyo00005/p2/carto-reasoning/questions/benchmark_data/response_mini.json',
    #     image_folder='/home/yaoyi/pyo00005/p2/carto-image',
    #     bool_distractor=True,
    #     output_dir='./',
    #     cache_dir='./',
    #     bool_batch=False,
    #     img_limit=args.max_images)