from typing import List

import torch
from transformers import Glm4vMoeForConditionalGeneration, AutoProcessor
from transformers import BitsAndBytesConfig             # To reduce memory usage

from frieda.providers.base import DecoderBase
from frieda.providers.utility import (
    make_chat_prompt
)

class GLM4vDecoder(DecoderBase):
    def __init__(self,
                 model_id: str,
                #  dataset: str,
                 quantize: bool=True,
                 attn_implementation: str="sdpa",
                 **kwargs,
    ):
        super().__init__(name=model_id, **kwargs)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        kwargs = {
            "device_map": "auto",
            "trust_remote_code": self.trust_remote_code,
            "torch_dtype": getattr(torch, self.dtype),
            "attn_implementation": "sdpa"
        }

        if quantize:
            # specify how to quantize the model
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )

            kwargs["quantization_config"] = quantization_config

        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = Glm4vMoeForConditionalGeneration.from_pretrained(model_id, **kwargs)

    @torch.inference_mode()
    def respond_q(self,
                  list_batch_input: List[dict],
                  img_lmt: int):
        
        input_chat = []

        for i in list_batch_input:
            content = make_chat_prompt(list_imgs=i['image_lists'],
                                       question=i['question'],
                                       img_lmt=img_lmt)
            
            conversation = [
                {   "role": "system",
                    "content": [{"type": "text", "text": self.instruction_prefix}],
                },
                {
                    "role": "user",
                    "content": content,
                }
            ]

            input_chat.append(conversation)

        inputs = self.processor.apply_chat_template(input_chat, 
                                                    add_generation_prompt=True,
                                                    tokenize=False,
                                                    return_dict=True,
                                                    padding=True,
                                                    padding_side="left",
                                                    return_tensors="pt")
                                                   
        inputs = inputs.to(self.model.device, torch.float16)
        inputs.pop("token_type_ids", None) # Not used in GLM45?

        try:
            with torch.no_grad():    
                # Batch Inference
                generated_ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, 
                                                    do_sample=self.do_sample)
                
            output_texts = self.processor.batch_decode(
                generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )

            list_output = []

            for response in output_texts:
                try:
                    cleaned_response = response.split("Final answer:")[-1].strip()
                    list_output.append(cleaned_response)
                    
                except:
                    list_output.append(response)

            return list_output

        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            return [None] * len(list_batch_input)
        except Exception:
            # Any OOD/processing error → skip this item
            return [None] * len(list_batch_input)