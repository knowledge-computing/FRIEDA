import os
import argparse
from dotenv import load_dotenv
from typing import List, Dict
from tqdm import tqdm

import json
import pickle
import polars as pl

import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from transformers import BitsAndBytesConfig             # To reduce memory usage
from qwen_vl_utils import process_vision_info

with open('./instruction.pkl', 'rb') as handle:
    instructions = pickle.load(handle)

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
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_id,
            quantization_config=quantization_config, 
            attn_implementation="flash_attention_2",
            device_map="auto",
            trust_remote_code=True
        )        # Only works under CUDA suppport

    else:
        # Slow processing
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_id, 
            quantization_config=quantization_config, 
            device_map="auto",
            trust_remote_code=True
        )

    processor = AutoProcessor.from_pretrained(model_id)

    return model, processor

def upload_images(images:List[str],
                 image_prefix:str=None,
                 save_cache:bool=True,
                 cache_dir:str=None):

    dict_im_data = {}   # Storing mapping ffor images

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
        content.append({"type": "image", "image": f"{dict_im_data[f]}"})

    content.append({"type": "text", "text": f"{question}. "})

    return content

def respond_q(model,
              processor,
              dict_im_data:Dict[str, str],
              input_struct:List[dict],
              img_limit:int):
    
    messages = []
    for i in input_struct:
        content = make_chat_prompt(question=i['question_text'],
                                   file_list=i['image_lists'],
                                   dict_im_data=dict_im_data,
                                   img_limit=img_limit)
        conversation = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": content}
        ]

        messages.append(conversation)

    texts = [
        processor.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
        for msg in messages
    ]

    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=texts,
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(model.device, torch.float16)

    with torch.no_grad():    
        # Batch Inference
        generated_ids = model.generate(**inputs, max_new_tokens=256, 
                                       do_sample=False, temperature=None, top_p=None, top_k=None)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_texts = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )

    list_output = []

    for response in output_texts:
        try:
            cleaned_response = response.split("Final answer:")[-1].strip()
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

    # Load model and processor
    model, processor = define_model(model_id=model_name, use_flash=use_flash)

    # Set up questions dataframe
    pl_question = pl.read_json(question_path).with_columns(
        q_answered = pl.lit(False),
    ).with_columns(
        pl.when(bool_distractor==True)
        .then(pl.concat_list('contextual_urls', 'image_urls'))
        .otherwise(pl.col('image_urls')).alias('image_lists')
    ).sort(pl.col('image_lists').list.len(), descending=True, maintain_order=True)

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
        list_output = respond_q(model=model, processor=processor,
                                input_struct=list_input,
                                dict_im_data=dict_im_data,
                                img_limit=img_limit)
        
        chunk = chunk.with_columns(
            pl.col('q_answered').replace({False: True}),
            qwenvl_response = pl.Series(list_output)
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
        new_file_name = os.path.join(output_dir, 'qwen_w_contextual.json')
    else:
        new_file_name = os.path.join(output_dir, 'qwen_wo_contextual.json')

    pd_answered.to_json(new_file_name, orient='records', indent=4)

    # Removing response cache pickle file
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

    # main(model_name='Qwen/Qwen2.5-VL-7B-Instruct',
    #     question_path='./p2/carto-reasoning/questions/benchmark_data/response_mini.json',
    #     image_folder='https://media.githubusercontent.com/media/YOO-uN-ee/carto-image/main/',
    #     bool_distractor=True,
    #     output_dir='./',
    #     cache_dir='./',
    #     use_flash=True,
    #     batch_size=2,
    #     img_limit=args.max_images)