import os
import argparse
from dotenv import load_dotenv
from typing import List, Dict
from tqdm import tqdm

import json
import pickle
import polars as pl

import torch
from transformers import AutoProcessor, LlavaOnevisionForConditionalGeneration
from transformers import BitsAndBytesConfig             # To reduce memory usage

def check_exist(path_dir, bool_create=True):
    if os.path.exists(path_dir):
        return 1
    
    if bool_create:
        os.makedirs(path_dir)
        return 0
    
    return -1

def define_model(model_id:str,
                 use_flash: bool):
    
    # specify how to quantize the model
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    if use_flash:
        model = LlavaOnevisionForConditionalGeneration.from_pretrained(
            model_id,
            quantization_config=quantization_config, 
            attn_implementation="flash_attention_2",
            ).to(0) # Only works under CUDA suppport
    else:
        # Slow processing
        model = LlavaOnevisionForConditionalGeneration.from_pretrained(
            model_id,
            quantization_config=quantization_config, 
            device_map="auto"
        )

    processor = AutoProcessor.from_pretrained(model_id)

    return model, processor

def upload_images(images:List[str],
                 image_prefix:str=None,
                 save_cache:bool=True,
                 cache_dir:str=None):
    # Recommended for repetitively used files or large files
    dict_im_data = {}   # Storing mapping from image to API images

    for im_path in list(set(images)):
        if image_prefix:
            full_path = os.path.join(image_prefix, im_path)

        dict_im_data[im_path] = full_path

        if save_cache:
            with open(os.path.join(cache_dir, 'image_cache.pkl'), 'wb') as handle:
                pickle.dump(dict_im_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return dict_im_data


def make_chat_prompt(question:str,
                     file_list:List[str],
                     dict_im_data:Dict[str, str],
                     img_limit:int) -> list:

    content = []
    for idx, f in enumerate(file_list):
        if idx > img_limit:
            break
        content.append({"type": "image", "url": f"{dict_im_data[f]}"})

    content.append({"type": "text", "text": f"{question}"})

    return content

def respond_q(model,
              processor,
              dict_im_data:Dict[str, str],
              question_q:str,
              img_list:List[str],
              img_limit:int):
    
    instructions = """
    Answer the question using the provided images. Follow the the following instructions.

    General: 
    * If answer is a text from the map, copy it as it appears

    Numerical Answers
    * Include units as indicated on the map (Don’t convert 1200m to 1.2km)
    * If both map frame and ruler scale is available, use the ruler scale
    * If question asks for an area, use {unit}^2
    * Use numerical values (e.g., 4 instead of four)

    Directional Answers:
    * Use 8 cardinal directions only: North, North East, East, South East, South, South West, West, North West
    * Write 'North' or 'South' before 'East' or 'West'
    * Notice that the north arrow compass do not always point upward

    Multi-Part Answers:
    * Separate with semicolon (;) (e.g., Zone A; Zone B)

    Give ONLY the answer.
    """

    content = make_chat_prompt(question=question_q,
                               file_list=img_list,
                               dict_im_data=dict_im_data,
                               img_limit=img_limit)
    conversation = [
        {   "role": "system",
            "content": [{"type": "text", "text": f"{instructions}"}],
        },
        {
            "role": "user",
            "content": content,
        }
    ]

    inputs = processor.apply_chat_template(
        [conversation],
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        padding=True,
        return_tensors="pt"
    ).to(model.device, torch.float16)

    generate_ids = model.generate(**inputs, max_new_tokens=30)
    input_decode = processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]    # beneficial if submitted in batch; requirement, all convo should be same image size

    return {'llava_next_response': input_decode.split('assistant')[1]}

def main(model_name:str,
         question_path:str,
         image_folder:str,
         bool_distractor:bool,
         output_dir:str,
         cache_dir:str,
         use_flash:bool,
         img_limit:int):
    
    # Create directory paths
    check_exist(output_dir)
    check_exist(cache_dir)

    cache_file = os.path.join(cache_dir, 'image_cache.pkl')
    # Load question JSON file
    with open(question_path, 'r') as file:
        data = json.load(file)
    
    # Uploading all images to path storage
    if check_exist(cache_file, bool_create=False) == -1:
    # if True:
        all_images = []
        for d in data:
            all_images.extend(d['image_urls'])
            all_images.extend(d['distractor_urls'])

        dict_im_data = upload_images(images=all_images,
                                     image_prefix=image_folder,
                                     save_cache=True,
                                     cache_dir=cache_dir)
    else:
        with open(cache_file, 'rb') as handle:
            dict_im_data = pickle.load(handle)

    # Load model and processor
    model, processor = define_model(model_id=model_name, use_flash=use_flash)

    # Set up questions dataframe
    pl_question = pl.read_json(question_path).with_columns(
        q_answered = pl.lit(False),
    ).with_columns(
        pl.when(bool_distractor)
        .then(pl.concat_list('distractor_urls', 'image_urls'))
        .otherwise(pl.col('image_urls')).alias('image_lists')
    )

    # Running inference in chunks (of 20) in case it crashse in middle
    chunk_size = 20 
    pl_answered = pl.DataFrame()

    response_cache = os.path.join(cache_dir, 'response_cache.pkl')
    if check_exist(response_cache, bool_create=False) == 1: 
        with open(response_cache, 'rb') as handle:
            pl_answered = pickle.load(handle)

        cache_length = pl_answered.shape[0]
        pl_question = pl_question[cache_length:]

    for i in tqdm(range(0, pl_question.height, chunk_size)):
        chunk = pl_question.slice(i, chunk_size)
        chunk = chunk.with_columns(
            tmp = pl.struct(pl.all()).map_elements(lambda x: respond_q(model, processor, dict_im_data, x['question_text'], x['image_lists'], img_limit))
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

    new_file_name = f"{question_path.split('.json')[0]}_onevision.json"
    pd_answered.to_json(new_file_name, orient='records', indent=4)

    # Removing response cache pickle file
    os.remove(response_cache)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cartographical Reasoning Test')

    parser.add_argument('--model', '-m', required=True,
                        help='Model name/type')

    parser.add_argument('--questions', '-q', required=True,
                        help='Path to questions JSON file')

    parser.add_argument('--images', '-im', default='./', type=str,
                        help="Directory/link to reporsitory containing images")
    
    parser.add_argument('--distractor', '-d', action="store_true", 
                        help='Use distractor images')
   
    parser.add_argument('--output_dir', '-o', default='./',
                        help="Location to output files")
    
    parser.add_argument('--cache_dir', '-c', default='./',
                        help="Location to cache directory (cache for image names)")
    
    parser.add_argument('--flash', '-im', action="store_true", type=bool,
                        help="Use flash attention")
    
    parser.add_argument('--max_images', '-max', type=int, default=20,
                        help="FOR DEVELOPING TEST PURPOSE")
    
    args = parser.parse_args()
    
    main(model=args.model,
         question_path=args.questions,
         image_folder=args.images,
         bool_distractor=args.distractor,
         output_dir=args.output_dir,
         cache_dir=args.cache_dir,
         use_flash=args.flash,
         img_limit=args.max_images)

    # main(model_name='llava-hf/llava-onevision-qwen2-7b-ov-hf',
    #     question_path='/home/yaoyi/pyo00005/carto-reasoning/questions/unverified/questions_config_distractor_t.json',
    #     image_folder='/home/yaoyi/pyo00005/carto-reasoning/img-raw',
    #     bool_distractor=True,
    #     output_dir='./',
    #     cache_dir='./',
    #     use_flash=False,
    #     img_limit=args.max_images)