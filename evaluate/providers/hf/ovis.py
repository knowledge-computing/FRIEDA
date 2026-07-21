import os
import re
from typing import List

import torch
from transformers import AutoProcessor, AutoModelForCausalLM

from evaluate.providers.base import DecoderBase
from evaluate.providers.utility import make_input_message

class OvisDecoder(DecoderBase):
    def __init__(self,
                 model_name: str,
                 attn_implementation: str='eager',
                 **kwargs):
        super().__init__(model_name=model_name,
                         **kwargs)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")      # TODO: Do we need this? 

        pattern = r"Ovis(?P<version>[\d\.]+).*?-(?P<size>\d+)B.*?(?:-(?P<mode>[a-zA-Z]+))?$"
        match = re.search(pattern, model_name)

        if match:
            version = match.group("version")
            size = match.group("size")

            self.model_family = f"Ovis{version}"
            
        else:
            print(f"[ERROR] Could not parse: {model_name}")
            exit()

        print(f"[INFO] Loading Ovis ver:{version} / size:{size}")

        if version == "2":
            if attn_implementation == "flash_attention_2":
                print(f"[INFO] Ovis2 does not support flash attention")
                attn_implementation = "eager"

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
            self.model = AutoModelForCausalLM.from_pretrained(model_name, **kwargs)

        except Exception as e:
            print(f"[ERROR] Failed to load model due to: {e}")
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
        
        if self.model_family == "2.5":
            list_outputs = []
            for m in messages:
                input_ids, pixel_values, grid_thws = self.model.preprocess_inputs(messages=m, 
                                                                                  add_generation_prompt=True,
                                                                                  enable_thinking=enable_thinking)
                input_ids = input_ids.cuda()
                pixel_values = pixel_values.cuda().to(self.model.dtype) if pixel_values is not None else None
                grid_thws = grid_thws.cuda() if grid_thws is not None else None

                if enable_thinking:         # With thinking enabled
                    outputs = self.model.generate(inputs=input_ids, pixel_values=pixel_values, grid_thws=grid_thws,
                                                max_new_tokens=max_new_tokens, thinking_budget=max_new_tokens-512,
                                                enable_thinking=enable_thinking, enable_thinking_budget=enable_thinking,
                                                eos_token_id=self.model.text_tokenizer.eos_token_id,
                                                pad_token_id=self.model.text_tokenizer.pad_token_id,)
                else:                       # With no thinking enabled
                    outputs = self.model.generate(inputs=input_ids, pixel_values=pixel_values, grid_thws=grid_thws,
                                                max_new_tokens=max_new_tokens, do_sample=do_sample,
                                                temperature=temperature, top_p=top_p, top_k=top_k,
                                                eos_token_id=self.model.text_tokenizer.eos_token_id,
                                                pad_token_id=self.model.text_tokenizer.pad_token_id,)
                
                list_outputs.append(self.model.text_tokenizer.decode(outputs[0], skip_special_tokens=True))

        else:
            batch_input_ids = []
            batch_attention_mask = []
            batch_pixel_values = []

            for image, query in messages:
                input_ids, pixel_values, grid_thws = self.model.preprocess_inputs(query, image,
                                                                                  max_partition=9)
                attention_mask = torch.ne(input_ids, self.model.text_tokenizer.pad_token_id)
                batch_input_ids.append(input_ids.to(device=self.model.device))
                batch_attention_mask.append(attention_mask.to(device=self.model.device))
                batch_pixel_values.append(pixel_values.to(dtype=self.model.visual_tokenizer.dtype, 
                                                          device=self.visual_tokenizer.device))
                
            batch_input_ids = torch.nn.utils.rnn.pad_sequence([i.flip(dims=[0]) for i in batch_input_ids], 
                                                              batch_first=True,
                                                              padding_value=0.0).flip(dims=[1])
            batch_input_ids = batch_input_ids[:, -self.model.config.multimodal_max_length:]
            batch_attention_mask = torch.nn.utils.rnn.pad_sequence([i.flip(dims=[0]) for i in batch_attention_mask],
                                                                   batch_first=True, 
                                                                   padding_value=False).flip(dims=[1])
            batch_attention_mask = batch_attention_mask[:, -self.model.config.multimodal_max_length:]

            gen_kwargs = dict(
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                top_p=top_p,
                top_k=top_k,
                temperature=temperature,
                repetition_penalty=None,
                eos_token_id=self.model.generation_config.eos_token_id,
                pad_token_id=self.modeltext_tokenizer.pad_token_id,
                use_cache=True
            )   

            output_ids = self.model.generate(batch_input_ids, 
                                             pixel_values=batch_pixel_values, 
                                             attention_mask=batch_attention_mask,
                                             **gen_kwargs)
            
            list_outputs = []
            for o in output_ids:
                list_outputs.append(self.model.text_tokenizer.decode(o, skip_special_tokens=True))

        return list_outputs