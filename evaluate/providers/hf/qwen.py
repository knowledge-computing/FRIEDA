import os
import re
from typing import List

import torch
from transformers import AutoProcessor

from evaluate.providers.base import DecoderBase
from evaluate.providers.utility import make_input_message

class QwenDecoder(DecoderBase):
    def __init__(self,
                 model_name: str,
                 attn_implementation: str='eager',
                 **kwargs):
        super().__init__(model_name=model_name,
                         **kwargs)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")      # TODO: Do we need this? 
        self.model_family = "Qwen"

        pattern = r"Qwen(?P<version>[\d\.]+).*?-(?P<size>\d+)B.*?(?:-(?P<mode>[a-zA-Z]+))?$"
        match = re.search(pattern, model_name)

        if match:
            version = match.group("version")
            size = match.group("size")
            mode = match.group("mode")
            
        else:
            print(f"[ERROR] Could not parse: {model_name}")
            exit()

        print(f"[INFO] Loading QwenVL ver:{version} / size:{size} / mode:{mode}")

        # Arguments
        kwargs = {
            "device_map": "auto",
            "trust_remote_code": self.trust_remote_code,
            "dtype": getattr(torch, self.dtype),
            "quantization_config": self.quantization_config,
            "attn_implementation": attn_implementation,  # "eager", "flash_attention_2", "sdpa"
            "offload_folder": './offload'
        }           # recommended attn = flash_attention

        # Load autoprocessor
        try:
            self.processor = AutoProcessor.from_pretrained(model_name)
        except Exception as e:
            print(f"[ERROR] Failed to load procesor due to: {e}")

        # Load model (depends on the version)
        try:
            if version == "2.5":
                from transformers import Qwen2_5_VLForConditionalGeneration
                self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_name, **kwargs)

            elif version == "3":
                if size in ["2", "4", "8", "32"]:
                    # MoE variants
                    from transformers import Qwen3VLForConditionalGeneration
                    self.model = Qwen3VLForConditionalGeneration.from_pretrained(model_name, **kwargs)

                elif size in ["30", "235"]:
                    from transformers import Qwen3VLMoeForConditionalGeneration
                    self.model = Qwen3VLMoeForConditionalGeneration.from_pretrained(model_name, **kwargs)

                else:
                    print(f"[ERROR] QwenVL{version} not supported for size {size}")

            else:
                print(f"[ERROR] No support for QwenVL version lower than 2.5")
                exit()
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
        for o in output_texts:
            list_outputs.append(o.split('assistant\n')[-1])

        return list_outputs