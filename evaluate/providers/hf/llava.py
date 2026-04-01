import os
import re
from typing import List

import torch
from transformers import AutoProcessor

from frieda.providers.base import DecoderBase
from frieda.providers.utility import make_input_message

class LLaVADecoder(DecoderBase):
    def __init__(self,
                 model_name: str,
                 attn_implementation: str='eager',
                 **kwargs):
        super().__init__(model_name=model_name,
                         **kwargs)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")      # TODO: Do we need this? 
        self.model_family = 'LLaVA'

        kwargs = {
            "device_map": "auto",
            "trust_remote_code": self.trust_remote_code,
            "dtype": getattr(torch, self.dtype),
            "quantization_config": self.quantization_config,
            "attn_implementation": attn_implementation,  # "eager", "flash_attention_2", "sdpa"
            "offload_folder": './offload'
        }           # recommended attn = flash_attention

        # Identifying model version to load correct generation object
        pattern = r"(?:llava-hf/)?(?:[\w]+-)?(?:llava)-(?P<version>[\w\.]+)-(?:.*?-)?(?P<size>[\d\.]+)[bB]"
        match = re.search(pattern, model_name)

        if match:
            version = match.group("version")
            size = match.group("size")
        else:
            print(f"[ERROR] Could not parse: {model_name}")
            exit()

        print(f"[INFO] Loading LLaVA ver:{version} / size:{size}")

        # Load processor & model (depends on the version)
        try:
            if version in ["v1.6", "next"]:
                from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
                self.processor = LlavaNextProcessor.from_pretrained(model_name)
                self.model = LlavaNextForConditionalGeneration.from_pretrained(model_name, **kwargs)

            elif version== "1.5":
                # TODO: Need to test the logic
                from transformers import AutoProcessor, LlavaForConditionalGeneration
                self.processor = AutoProcessor.from_pretrained(model_name)
                self.model = LlavaForConditionalGeneration.from_pretrained(model_name, **kwargs)

            elif version == "onevision":
                from transformers import AutoProcessor, LlavaOnevisionForConditionalGeneration
                self.processor = AutoProcessor.from_pretrained(model_name)
                self.model = LlavaOnevisionForConditionalGeneration.from_pretrained(model_name, **kwargs)
        except Exception as e:
            print(f"[ERROR] Failed to load procesor/model due to: {e}")

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

        # Run generation
        inputs = self.processor.apply_chat_template(messages,
                                                    add_generation_prompt=True,
                                                    tokenize=True,
                                                    return_dict=True,
                                                    padding=True,
                                                    padding_side="left",
                                                    return_tensors="pt"
                                                    ).to(self.model.device, torch.float16)

        generate_ids = self.model.generate(**inputs,
                                           max_new_tokens=max_new_tokens,
                                           do_sample=do_sample,
                                           temperature=temperature,
                                           top_p=top_p,
                                           top_k=top_k)
        
        output_texts = self.processor.batch_decode(generate_ids,
                                                   skip_special_tokens=True,
                                                   clean_up_tokenization_space=False)

        # Obtain the part that is after 'assistant' tag
        list_outputs = []
        # for o in output_texts:
        #     list_outputs.append(o.split('assistant\n')[-1])
        list_outputs = output_texts

        return list_outputs