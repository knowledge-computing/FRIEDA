import os
import argparse

import json
import polars as pl

# Gemini packages
from google import genai
from google.genai import types

from cartoreasoning.frameworks._base import DecoderBase
from cartoreasoning.frameworks._utility import make_chat_prompt

class GeminiDecoder(DecoderBase):
    def __init__(self,
                 name: str,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.model = name
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def upload_image(self,
                     img_path:str):
        # Recommended for repetitively used files or large files
        loaded_im = self.client.files.upload(file=img_path)

        return loaded_im
    
    def respond_q():
        return 0






client = genai.Client()

my_file = client.files.upload(file="path/to/sample.jpg")

def upload_image(img_path:str):
    # Recommended for repetitively used files or large files
    loaded_im = client.files.upload(file=img_path)

    return loaded_im


list_imgs = []

contents = [question, images, images]
[for i in list_imgs]

# Upload the first image
image1_path = "path/to/image1.jpg"
uploaded_file = upload_image(image1_path)

# Prepare the second image as inline data
image2_path = "path/to/image2.png"
uploaded_file2 = upload_image(image2_path)
uploaded_file2 = client.files.upload(file=image2_path)
with open(image2_path, 'rb') as f:
    img2_bytes = f.read()

# Create the prompt with text and multiple images
response = client.models.generate_content(
    model=model,
    contents=[
        "What is different between these two images?",
        uploaded_file,  # Use the uploaded file reference
        # types.Part.from_bytes(
        #     data=img2_bytes,
        #     mime_type='image/png'
        # )
        uploaded_file2
    ]
)

print(response.text)
