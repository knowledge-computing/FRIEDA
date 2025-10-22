from typing import List

import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from transformers import BitsAndBytesConfig             # To reduce memory usage
from qwen_vl_utils import process_vision_info

from frieda.providers.base import DecoderBase
from frieda.providers.utility import (
    make_chat_prompt
)

class HuggingFaceDecoder(DecoderBase):
    def __init__(self,
                 model_id: str,
                #  dataset: str,
                 quantize: bool=True,
                 attn_implementation: str="eager",
                 **kwargs,
    ):
        super().__init__(name=model_id, **kwargs)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        kwargs = {
            "device_map": "auto",
            "trust_remote_code": self.trust_remote_code,
            "torch_dtype": getattr(torch, self.dtype),
            "attn_implementation": attn_implementation,  # "eager", "flash_attention_2", "sdpa"
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
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_id, **kwargs)

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
                {"role": "system", "content": self.instruction_prefix},
                {"role": "user", "content": content}
            ]

            input_chat.append(conversation)

        texts = [
            self.processor.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
            for msg in input_chat
        ]

        try:
            image_inputs, video_inputs = process_vision_info(input_chat)
        except Exception as e:
            print("⚠️ Failed to load image(s) for this message:")
            print("Question:", i['question_text'])
            return [None] * len(list_batch_input)
        
        inputs = self.processor(
            text=texts,
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(self.model.device, torch.float16)

        try:
            with torch.no_grad():    
                # Batch Inference
                generated_ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, 
                                                    do_sample=self.do_sample)
                generated_ids_trimmed = [
                    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_texts = self.processor.batch_decode(
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

        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            return [None] * len(list_batch_input)
        except Exception:
            # Any OOD/processing error → skip this item
            return [None] * len(list_batch_input)