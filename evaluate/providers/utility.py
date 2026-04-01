from typing import Union, List

import requests
from PIL import Image

import torch
from transformers import BitsAndBytesConfig
from torchvision.transforms.functional import InterpolationMode
import torchvision.transforms as T

from huggingface_hub import HfApi

def determine_backend(model:str) -> Union[str, None]:
    api = HfApi()

    if 'gemini' in model.lower():
        return 'google'
    elif 'gpt' in model.lower():
        return 'openai'
    elif 'claude' in model.lower():
        return 'anthropic'
    elif api.model_info(model):
        return 'hf'
        
    raise RuntimeError(f"Backend of the model-{model} cannot be determined")

def config_bnb(bnb_type:int=None) -> Union[BitsAndBytesConfig, None]:
    if bnb_type == 4:
        print("[INFO] Setting to BnB-4bit")
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            # llm_int8_enable_fp32_cpu_offload=True 
        )
    elif bnb_type == 8:
        print("[INFO] Setting to BnB-8bit")
        return BitsAndBytesConfig(load_in_8bit=True)

    print("[INFO] BnB skipped")
    return None

def build_transform(input_size):
    """
    From InternVL source code
    """
    MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
    transform = T.Compose([
        T.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
        T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(mean=MEAN, std=STD)
    ])
    return transform

def find_closest_aspect_ratio(aspect_ratio, target_ratios, width, height, image_size):
    """
    From InternVL source code
    """
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
    """
    From InternVL source code
    """
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
    """
    From InternVL source code
    """
    if 'http' in image_file:    # Just this added
        image = Image.open(requests.get(image_file, stream=True).raw).convert('RGB')
    else:
        image = Image.open(image_file).convert('RGB')
    transform = build_transform(input_size=input_size)
    images = dynamic_preprocess(image, image_size=input_size, use_thumbnail=True, max_num=max_num)
    pixel_values = [transform(image) for image in images]
    pixel_values = torch.stack(pixel_values)
    return pixel_values

def make_input_message(question:str, 
                       list_image_paths:List[List[str]],
                       instruction_prefix:str=None,
                       model_family:str=None):

    messages = []
    for li in list_image_paths:
        indiv_input = []

        if instruction_prefix:
            indiv_input.append({"role": "system", "content": instruction_prefix})

        if model_family == 'Qwen':
            content = [{"type": "text", "text": question}]
            for i in li:
                content.append({"type": "image", "image": i})
            
            indiv_input.append({"role": "user", "content": content})
        
        # InternVL
        elif model_family == ['InternVL3.5', 'LLaVA', 'GLM']:
            content = [{"type": "text", "text": question}]
            for i in li:
                content.append({"type": "image", "url": i})

            indiv_input.append({"role": "user", "content": content})

        elif model_family == 'InternVL':    # All models excluding 3.5 variant
            # TODO: update for multi-image support
            if instruction_prefix:
                question = instruction_prefix + "\n\n" + question
            else: question = question

            pixel_values = load_image(i, max_num=12).to(torch.bfloat16).cuda()
            indiv_input = [pixel_values, question]

        # Ovis
        elif model_family == 'Ovis2.5':
            content = [{"type": "text", "text": question}]
            for i in li:
                if 'http' in i: 
                    image = Image.open(requests.get(i, stream=True).raw)
                else: image = i
                content.append({"type": "image", "image": image})

            indiv_input.append({"role": "user", "content": content})

        elif model_family == 'Ovis2':
            # TODO: update for multi-image support
            if instruction_prefix:
                question = instruction_prefix + "\n" + question + "\n<image>"
            else: question = question + "\n<image>"

            if 'http' in i:    # Just this added
                image = Image.open(requests.get(i, stream=True).raw)
            else:
                image = Image.open(i)

            indiv_input = [image, question]

        messages.append(indiv_input)

    return messages