import os
import argparse
from dotenv import load_dotenv
from typing import List, Dict
from tqdm import tqdm

import json
import pickle
import polars as pl

import torch
from transformers import AutoTokenizer, AutoModel
from PIL import Image
from torchvision.transforms.functional import InterpolationMode
import torchvision.transforms as T

from functools import reduce
from math import floor

import pickle
import polars as pl
import pandas as pd

path = "OpenGVLab/InternVL3-8B"
model = AutoModel.from_pretrained(
    path,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    use_flash_attn=True,
    trust_remote_code=True).eval().cuda()

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

def build_transform(input_size):
    MEAN, STD = IMAGENET_MEAN, IMAGENET_STD
    transform = T.Compose([
        T.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
        T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(mean=MEAN, std=STD)
    ])
    return transform

def find_closest_aspect_ratio(aspect_ratio, target_ratios, width, height, image_size):
    best_ratio_diff = float('inf')
    best_ratio = (1, 1)
    area = width * height
    for ratio in target_ratios:
        target_aspect_ratio = ratio[0] / ratio[1]
        ratio_diff = abs(aspect_ratio - target_aspect_ratio)
        if ratio_diff < best_ratio_diff:
            best_ratio_diff = ratio_diff
            best_ratio = ratio
        elif ratio_diff == best_ratio_diff:
            if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                best_ratio = ratio
    return best_ratio


def dynamic_preprocess(image, min_num=1, max_num=12, image_size=448, use_thumbnail=False):
    orig_width, orig_height = image.size
    aspect_ratio = orig_width / orig_height

    # calculate the existing image aspect ratio
    target_ratios = set(
        (i, j) for n in range(min_num, max_num + 1) for i in range(1, n + 1) for j in range(1, n + 1) if
        i * j <= max_num and i * j >= min_num)
    target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

    # find the closest aspect ratio to the target
    target_aspect_ratio = find_closest_aspect_ratio(
        aspect_ratio, target_ratios, orig_width, orig_height, image_size)

    # calculate the target width and height
    target_width = image_size * target_aspect_ratio[0]
    target_height = image_size * target_aspect_ratio[1]
    blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

    # resize the image
    resized_img = image.resize((target_width, target_height))
    processed_images = []
    for i in range(blocks):
        box = (
            (i % (target_width // image_size)) * image_size,
            (i // (target_width // image_size)) * image_size,
            ((i % (target_width // image_size)) + 1) * image_size,
            ((i // (target_width // image_size)) + 1) * image_size
        )
        # split the image
        split_img = resized_img.crop(box)
        processed_images.append(split_img)
    assert len(processed_images) == blocks
    if use_thumbnail and len(processed_images) != 1:
        thumbnail_img = image.resize((image_size, image_size))
        processed_images.append(thumbnail_img)
    return processed_images

def load_image(image_file, input_size=448, max_num=12):
    image = Image.open(image_file).convert('RGB')
    transform = build_transform(input_size=input_size)
    images = dynamic_preprocess(image, image_size=input_size, use_thumbnail=True, max_num=max_num)
    pixel_values = [transform(image) for image in images]
    pixel_values = torch.stack(pixel_values)
    return pixel_values


tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True, use_fast=False)

def testing(question_text:str, items_in_folder:List[str]):
    list_pixels = []

    for item in items_in_folder:
        list_pixels.append(load_image(os.path.join('/home/yaoyi/pyo00005/carto-reasoning/img-raw', item), max_num=12).to(torch.bfloat16).cuda())

    if len(list_pixels) > 1:
        pixel_values = reduce(lambda x,y: torch.cat((x,y), dim=0), list_pixels[:-1])
    else:
        pixel_values = list_pixels[0]

    generation_config = dict(max_new_tokens=1024, do_sample=True)

    question = f"""Answer the question using the provided images. If the question asks about distance, answer with the unit as indicated on the map. Use numerical values for numerical answers. For orientation questions, respond only in the 8 cardinal direction. For answers that have multiple components separate the components with a semicolon (;) Give only the answer.
    {question_text}\n
    <image>
    """

    response, history = model.chat(tokenizer, pixel_values, question, generation_config,
                                history=None, return_history=True)
    print(f'User: {question}\nAssistant: {response}')

    return str(response)

for i in os.listdir('/home/yaoyi/pyo00005/carto-reasoning/questions/accept'):
    relation = i.split('.json')[0]

    pl_data = pl.read_json(os.path.join('/home/yaoyi/pyo00005/carto-reasoning/questions/accept', i))

    pl_data = pl_data.with_columns(
        pl.struct(pl.all()).map_elements(lambda x: testing(x['question_text'], x['image_urls'])).alias('response_internvl3')
    )

    with open(f'/home/yaoyi/pyo00005/carto-reasoning/llm-test/intervl3/accept_{relation}.pkl', 'wb') as handle:
        pickle.dump(pl_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    pl_data = pl_data.drop('image_urls')
    pl_data.write_csv(f'/home/yaoyi/pyo00005/carto-reasoning/llm-test/intervl3/accept_{relation}.csv')


def check_exist(path_dir, bool_create=True):
    if os.path.exists(path_dir):
        return 1
    
    if bool_create:
        os.makedirs(path_dir)
        return 0
    
    return -1

def make_chat_prompt(question:str,
                     file_list:List[str],
                     dict_im_data:Dict[str, str]) -> list:
    
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

def main(model:str,
         question_path:str,
         image_folder:str,
         bool_distractor:bool,
         output_dir:str,
         cache_dir:str):
    
    # Create directory paths
    check_exist(output_dir)
    check_exist(cache_dir)
    
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
    if check_exist(response_cache) == 1: 
        with open(response_cache, 'rb') as handle:
            pl_answered = pickle.load(handle).unnest('tmp')

        cache_length = pl_answered.shape[0]
        pl_question = pl_question[cache_length:]

    for i in tqdm(range(0, pl_question.height, chunk_size)):
        chunk = pl_question.slice(i, chunk_size)
        chunk = chunk.with_columns(
            tmp = pl.struct(pl.all()).map_elements(lambda x: respond_q(model, x['question_text'], x['image_lists']))
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

    new_file_name = f"{question_path.split('.json')[0]}_{model}.json"
    pd_answered.to_json(new_file_name, orient='records', indent=4)

    # Removing response cache pickle file
    os.remove(response_cache)



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
    question_path='/home/yaoyi/pyo00005/carto-reasoning/questions/unverified/questions_config_distractor_t.json',
    image_folder='/home/yaoyi/pyo00005/carto-reasoning/img-raw',
    bool_distractor=True,
    output_dir='./',
    cache_dir='./')