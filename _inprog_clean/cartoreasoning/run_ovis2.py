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

with open('./cartoreasoning/instruction.pkl', 'rb') as handle:
    instructions = pickle.load(handle)

def check_exist(path_dir, bool_create=True):
    if os.path.exists(path_dir):
        return 1
    
    if bool_create:
        os.makedirs(path_dir)
        return 0
    
    return -1

def define_model(model_id:str,
                 use_flash: bool=False):
    
    # specify how to quantize the model
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    # FLash attention not supported for Ovis2
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=quantization_config,
        multimodal_max_length=32768,
        trust_remote_code=True,
        device_map="auto")
    
    text_tokenizer = model.get_text_tokenizer()
    visual_tokenizer = model.get_visual_tokenizer()

    return model, text_tokenizer, visual_tokenizer

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

    # for idx, f in enumerate(file_list):
    #     if idx > img_limit:
    #         break
    question_default = "Answer in English only."

    if 'https' in dict_im_data[file_list[0]]:
        image = [Image.open(requests.get(dict_im_data[image_path], stream=True).raw) for image_path in file_list]
    else:
        image = [Image.open(dict_im_data[image_path]) for image_path in file_list]

    query = question_default + '\n' + \
            '\n'.join([f'Image {i+1}: <image>' for i in range(len(image))]) + \
            '\n' + question

    return query, image

def respond_q(model,
              text_tokenizer, visual_tokenizer,
              dict_im_data:Dict[str, str],
              input_struct:List[dict],
              img_limit:int,):
    
    batch_input_ids = []
    batch_attention_mask = []
    batch_pixel_values = []

    for i in input_struct:
        query, image = make_chat_prompt(question=i['question_text'],
                                        file_list=i['image_lists'],
                                        dict_im_data=dict_im_data,
                                        img_limit=img_limit)
        
        prompt, input_ids, pixel_values = model.preprocess_inputs(query, image, max_partition=9)
        attention_mask = torch.ne(input_ids, text_tokenizer.pad_token_id)
        batch_input_ids.append(input_ids.to(device=model.device))
        batch_attention_mask.append(attention_mask.to(device=model.device))
        batch_pixel_values.append(pixel_values.to(dtype=visual_tokenizer.dtype, device=visual_tokenizer.device))

    batch_input_ids = torch.nn.utils.rnn.pad_sequence([i.flip(dims=[0]) for i in batch_input_ids], batch_first=True,
                                                      padding_value=0.0).flip(dims=[1])
    batch_input_ids = batch_input_ids[:, -model.config.multimodal_max_length:]
    batch_attention_mask = torch.nn.utils.rnn.pad_sequence([i.flip(dims=[0]) for i in batch_attention_mask],
                                                        batch_first=True, padding_value=False).flip(dims=[1])
    batch_attention_mask = batch_attention_mask[:, -model.config.multimodal_max_length:]

    with torch.inference_mode():
        gen_kwargs = dict(
            max_new_tokens=256,
            do_sample=False,            # Basically temp=0
            top_p=None,
            top_k=None,
            temperature=None,
            repetition_penalty=None,
            eos_token_id=model.generation_config.eos_token_id,
            pad_token_id=text_tokenizer.pad_token_id,
            use_cache=True
        )   
        output_ids = model.generate(batch_input_ids, pixel_values=batch_pixel_values, attention_mask=batch_attention_mask,
                                    **gen_kwargs)

    list_output = []

    for i in range(len(input_struct)):
        response = text_tokenizer.decode(output_ids[i], skip_special_tokens=True)
        try:
            cleaned_response = response.split('Final answer:')[-1].strip()
            list_output.append(cleaned_response)
        except:
            list_output.append(response)

    return list_output

def main(model_name:str,
         question_path:str,
         image_folder:str,
         bool_distractor:bool,
         output_dir:str,
         cache_dir:str,
         use_flash:bool,
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

    # Load model and processor (Ovis2 doesn't have the option for Flash)
    model, text_tokenizer, visual_tokenizer = define_model(model_id=model_name, use_flash=False)

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

        chunk = chunk.with_columns(
            tmp = pl.struct(pl.col(['question_text', 'image_lists']))
        )

        list_input = chunk['tmp'].to_list()
        list_output = respond_q(model=model,
                    text_tokenizer=text_tokenizer,
                    visual_tokenizer=visual_tokenizer,
                    input_struct=list_input,
                    dict_im_data=dict_im_data,
                    img_limit=img_limit)
        
        chunk = chunk.with_columns(
            pl.col('q_answered').replace({False: True}),
            ovis2_response = pl.Series(list_output)
        ).drop(['tmp', 'image_lists'])

        pl_answered = pl.concat(
            [pl_answered, chunk],
            how='diagonal'
        )

        with open(response_cache, 'wb') as handle:
            pickle.dump(pl_answered, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Saving as JSON with model name appended
    pd_answered = pl_answered.to_pandas()

    if bool_distractor:
        new_file_name = os.path.join(output_dir, 'ovis2_w_contextual.json')
    else:
        new_file_name = os.path.join(output_dir, 'ovis2_wo_contextual.json')

    pd_answered.to_json(new_file_name, orient='records', indent=4)

    # Removing response cache pickle file
    os.remove(response_cache)
    os.remove(cache_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cartographical Reasoning Test')

    parser.add_argument('--model', '-m', default='AIDC-AI/Ovis2-34B',
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
    
    parser.add_argument('--flash', action="store_true", default=False, 
                        help="Use flash attention")
    
    parser.add_argument('--batch_size', type=int, default=1,
                        help="Batch size. Default is 1.")
    
    parser.add_argument('--max_images', '-max', type=int, default=20,
                        help="FOR DEVELOPING TEST PURPOSE")
    
    args = parser.parse_args()

    main(model_name=args.model,
         question_path=args.questions,
         image_folder=args.images,
         bool_distractor=args.distractor,
         output_dir=args.output_dir,
         cache_dir=args.cache_dir,
         use_flash=args.flash,
         batch_size=args.batch_size,
         img_limit=args.max_images)

    # main(model_name='AIDC-AI/Ovis2-1B',
    #     question_path='./p2/carto-reasoning/questions/benchmark_data/response_mini.json',
    #     image_folder='https://media.githubusercontent.com/media/YOO-uN-ee/carto-image/main/',
    #     bool_distractor=False,
    #     output_dir='./',
    #     cache_dir='./',
    #     use_flash=True,
    #     batch_size=2,
    #     img_limit=args.max_images)