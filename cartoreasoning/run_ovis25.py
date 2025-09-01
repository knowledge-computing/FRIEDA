import os
import argparse
from dotenv import load_dotenv
from typing import List, Dict
from tqdm import tqdm

import json
import pickle
import polars as pl

import requests
from PIL import Image

import torch
from transformers import AutoModelForCausalLM
from transformers import BitsAndBytesConfig             # To reduce memory usage

import warnings
warnings.filterwarnings("ignore", category=pl.MapWithoutReturnDtypeWarning)

with open('./instruction.pkl', 'rb') as handle:
    instructions = pickle.load(handle)

# Paraemter specific to Ovis
# Thinking mode & budget
enable_thinking = True
enable_thinking_budget = True  # Only effective if enable_thinking is True.

# Total tokens for thinking + answer. Ensure: max_new_tokens > thinking_budget + 25
max_new_tokens = 3072
thinking_budget = 2048

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
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quantization_config, 
            attn_implementation="flash_attention_2",
            device_map="auto",
            trust_remote_code=True,
        )

    else:
        # Slow processing
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quantization_config, 
            torch_dtype="auto", device_map="auto",
            trust_remote_code=True
        )

    return model

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

    content = [{"type": "text", "text": "Answer in English only."}]
    for idx, f in enumerate(file_list):
        if idx > img_limit:
            break

        if 'https' in dict_im_data[f]:
            content.append({"type": "image", "image": Image.open(requests.get(dict_im_data[f], stream=True).raw)})
        else:
            content.append({"type": "image", "image": f"{dict_im_data[f]}"})

    content.append({"type": "text", "text": f"{question}. "})

    return content

def respond_q(model,
              processor,
              dict_im_data:Dict[str, str],
              question_q:str,
              img_list:List[str],
              img_limit:int,
              allow_thinking:bool=True):
    
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

    input_ids, pixel_values, grid_thws = model.preprocess_inputs(messages=conversation, 
                                                                 add_generation_prompt=True,)
    
    if allow_thinking:
        input_ids, pixel_values, grid_thws = model.preprocess_inputs(messages=conversation, 
                                                                     add_generation_prompt=True,
                                                                     enable_thinking=enable_thinking)
    input_ids = input_ids.cuda()
    pixel_values = pixel_values.cuda().to(model.dtype) if pixel_values is not None else None
    grid_thws = grid_thws.cuda() if grid_thws is not None else None

    with torch.no_grad():
        
        if allow_thinking:
            outputs = model.generate(inputs=input_ids, pixel_values=pixel_values, grid_thws=grid_thws,
                                     enable_thinking=enable_thinking, enable_thinking_budget=enable_thinking_budget,
                                     max_new_tokens=max_new_tokens, thinking_budget=thinking_budget,)
        else:
            outputs = model.generate(inputs=input_ids, pixel_values=pixel_values, grid_thws=grid_thws,
                                    max_new_tokens=256, do_sample=False,
                                    eos_token_id=model.text_tokenizer.eos_token_id,
                                    pad_token_id=model.text_tokenizer.pad_token_id,)

    response = model.text_tokenizer.decode(outputs[0], skip_special_tokens=True)

    try:
        cleaned_response = response.split('Final answer:')[-1].strip()
        return {'ovis2.5_response': cleaned_response}
    except:
        return {'ovis2.5_response': response}
    

def main(model_name:str,
         question_path:str,
         image_folder:str,
         bool_distractor:bool,
         output_dir:str,
         cache_dir:str,
         use_flash:bool,
         allow_thinking:bool,
         batch_size:int,
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
            all_images.extend(d['contextual_urls'])
 
        dict_im_data = upload_images(images=all_images,
                                     image_prefix=image_folder,
                                     save_cache=True,
                                     cache_dir=cache_dir)
    else:
        with open(cache_file, 'rb') as handle:
            dict_im_data = pickle.load(handle)

    # Load model and processor
    model = define_model(model_id=model_name, use_flash=use_flash)

    # Set up questions dataframe
    pl_question = pl.read_json(question_path).with_columns(
        q_answered = pl.lit(False),
    ).with_columns(
        pl.when(bool_distractor)
        .then(pl.concat_list('contextual_urls', 'image_urls'))
        .otherwise(pl.col('image_urls')).alias('image_lists')
    )

    pl_answered = pl.DataFrame()

    response_cache = os.path.join(cache_dir, 'response_cache.pkl')
    if check_exist(response_cache, bool_create=False) == 1: 
        with open(response_cache, 'rb') as handle:
            pl_answered = pickle.load(handle)

        cache_length = pl_answered.shape[0]
        pl_question = pl_question[cache_length:]

    for i in tqdm(range(0, pl_question.height, batch_size)):
        chunk = pl_question.slice(i, batch_size)

        if batch_size > 1:
            pass

        else:
            chunk = chunk.with_columns(
                tmp = pl.struct(pl.all()).map_elements(lambda x: respond_q(model, None, dict_im_data, x['question_text'], x['image_lists'], img_limit, allow_thinking))
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

    if bool_distractor:
        new_file_name = os.path.join(output_dir, 'ovis25_w_contextual.json')
    else:
        new_file_name = os.path.join(output_dir, 'ovis25_wo_contextual.json')

    pd_answered.to_json(new_file_name, orient='records', indent=4)

    # Removing response cache & image cache pickle file
    os.remove(response_cache)
    os.remove(cache_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cartographical Reasoning Test')

    parser.add_argument('--model', '-m', default='Qwen/Qwen2.5-VL-72B-Instruct',
                        help='Model name/type')

    parser.add_argument('--questions', '-q', required=True, 
                        help='Path to questions JSON file')

    parser.add_argument('--images', '-im', required=True, type=str,
                        help="Directory/link to reporsitory containing images")
        
    parser.add_argument('--distractor', '-d', action="store_true", 
                        help='Use distractor images')
   
    parser.add_argument('--output_dir', '-o', default='./responses',
                        help="Location to output files")
    
    parser.add_argument('--cache_dir', '-c', default='./',
                        help="Location to cache directory (cache for image names)")
    
    parser.add_argument('--flash', action="store_true",
                        help="Use flash attention")
    
    parser.add_argument('--thinking', action="store_true",
                        help="Allow reasoning capability")
    
    parser.add_argument('--batch_size', default=1,
                        help="Batch size. Default is 1.")
    
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
         allow_thinking=args.thinking,
         batch_size=args.batch_size,
         img_limit=args.max_images)

    # main(model_name='AIDC-AI/Ovis2.5-2B',
    #     question_path='./p2/carto-reasoning/questions/benchmark_data/response_mini.json',
    #     image_folder='https://media.githubusercontent.com/media/YOO-uN-ee/carto-image/main/',
    #     bool_distractor=False,
    #     output_dir='./',
    #     cache_dir='./',
    #     use_flash=True,
    #     allow_thinking=True,
    #     batch_size=1,
    #     img_limit=args.max_images)