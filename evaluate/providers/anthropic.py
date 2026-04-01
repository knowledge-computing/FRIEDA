import os
import re
from typing import List
from time import time

import torch

from frieda.providers.base import DecoderBase
from frieda.providers.utility import make_input_message

class ClaudeDecoder(DecoderBase):
    def __init__(self,
                 model_name: str,
                 api_key: str=None,):
        super().__init__(model_name=model_name,
                         **kwargs)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_family = "Claude"
        self.api_key = os.getenv("ANTHROPIC_API_KEY") or api_key

        pattern = r"^claude-(?P<name>opus|sonnet|haiku)-(?P<version>\d+)-(?P<patch>\d+)(?:-(?P<date>\d{8}))?$"
        match = re.search(pattern, model_name)

        if match:
            version = match.group("version")
            patch = match.group("patch")
            
        else:
            print(f"[ERROR] Could not parse: {model_name}")
            exit()

        print(f"[INFO] Loading Claude Model: {version}-{patch}")
        

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
                top_k:int = 1,
                
                mode_batch:bool = True):
        
        if mode_batch:
            # Concat  per batch size
            pass

        else:
            # This is synchronous
            pass
        

        # Max to submit batch size 50 and add time gap of 1 min
        # Create input_messages
        messages = make_input_message(prompt=prompt,
                                      image_path=questions,
                                      instruction_prefix=instruction_prefix,
                                      model_family=self.model_family)

        # Run generation
        inputs = self.processor.apply_chat_template(messages,
                                                    add_generation_prompt=True,
                                                    tokenize=True,
                                                    return_dict=True,
                                                    padding=True,
                                                    padding_side="left",
                                                    return_tensors="pt"
                                                    ).to(self.model.device, torch.float16)
        inputs.pop("token_type_ids", None)

        generate_ids = self.model.generate(**inputs,
                                           max_new_tokens=max_new_tokens,
                                           do_sample=do_sample,
                                           temperature=temperature,
                                           top_p=top_p,
                                           top_k=top_k)
        
        output_texts = self.processor.batch_decode(generate_ids,
                                                   skip_special_tokens=True,
                                                   clean_up_tokenization_space=False)

        list_outputs = output_texts

        return list_outputs