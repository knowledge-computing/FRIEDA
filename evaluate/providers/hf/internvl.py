import os
import re
from typing import List

import torch
from transformers import AutoProcessor

from frieda.providers.base import DecoderBase
from frieda.providers.utility import make_input_message

class InternVLDecoder(DecoderBase):
    def __init__(self,
                 model_name: str,
                 attn_implementation: str='eager',
                 **kwargs):
        super().__init__(model_name=model_name,
                         **kwargs)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")      # TODO: Do we need this? 
        self.model_family = "InternVL"

        pattern = r"InternVL(?P<version>[\d_]+)-(?P<size>\d+)B(?:-(?P<mode>Flash))?"
        match = re.search(pattern, model_name)

        if match:
            version = match.group("version")
            size = match.group("size")
            mode = match.group("mode")
            
        else:
            print(f"[ERROR] Could not parse: {model_name}")
            exit()

        print(f"[INFO] Loading InternVL ver:{version} / size:{size} / mode:{mode}")

        # Arguments
        kwargs = {
            "device_map": "auto",
            "trust_remote_code": self.trust_remote_code,
            "dtype": getattr(torch, self.dtype),
            "quantization_config": self.quantization_config,
            "attn_implementation": attn_implementation,  # "eager", "flash_attention_2", "sdpa"
            "offload_folder": './offload'
        }           # recommended attn = flash_attention

        # Load model (depends on the version)
        try:
            if version == "3_5":
                from transformers import AutoModelForImageTextToText, AutoProcessor
                self.model_family = "InternVL3.5"
                self.processor = AutoProcessor.from_pretrained(model_name)
                self.model = AutoModelForImageTextToText.from_pretrained(model_name, **kwargs)

            elif version in ["2_5", "3"]:
                from transformers import AutoModel, AutoTokenizer
                self.processor = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, use_fast=False)
                self.model = AutoModel.from_pretrained(model_name, **kwargs)

            else:
                print(f"[ERROR] No support for InternVL version lower than 2.5")
                exit()
        except Exception as e:
            print(f"[ERROR] Failed to load processor/tokenizer/model due to: {e}")
            exit()

    @torch.inference_mode()
    def answerq(self,
                questions:List[str],
                images:List[List[str]],
                data_dir:str,
                instruction_prefix:str=None,
                         
                max_new_tokens:int = 1280,
                enable_thinking:bool=False, 
                
                do_sample:bool = True,
                temperature:float = 0.01,
                top_p:float = 1.0,
                top_k:int = 1):
        
        image_paths = [os.path.join(data_dir, i) for i in images]
        
        # Create input_messages
        messages = make_input_message(instruction_prefix=instruction_prefix,
                                      questions=questions,
                                      image_paths=image_paths,
                                      model_family=self.model_family)

        if self.model_family == "InternVL3.5":
            # Run generation
            inputs = self.processor.apply_chat_template(messages,
                                                        add_generation_prompt=True,
                                                        tokenize=True,
                                                        return_dict=True,
                                                        padding=True,
                                                        padding_side="left",
                                                        return_tensors="pt"
                                                        ).to(self.model.device)

            generate_ids = self.model.generate(**inputs,
                                               max_new_tokens=max_new_tokens,
                                               do_sample=do_sample,
                                               temperature=temperature,
                                               top_p=top_p,
                                               top_k=top_k)
            
            output_texts = self.processor.batch_decode(generate_ids,
                                                       skip_special_tokens=True,
                                                       clean_up_tokenization_space=False)
            
        else:
            output_texts = []
            generation_config = dict(max_new_tokens=max_new_tokens, 
                                     do_sample=do_sample)

            for pixel_values, question in messages:
                response = self.model.chat(self.processor, 
                                           pixel_values, 
                                           question, 
                                           generation_config,
                               history=None, return_history=False)
                output_texts.append(response)

        # Obtain the part that is after 'assistant' tag
        list_outputs = []
        for o in output_texts:
            list_outputs.append(o.split('assistant\n')[-1])

        return list_outputs