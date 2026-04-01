from abc import ABC, abstractmethod
from typing import List

from frieda.providers.utility import config_bnb

class DecoderBase(ABC):
    def __init__(self,
                 model_name: str,
                 trust_remote_code: bool=True,

                 dtype: str = "bfloat16",  # default
                 bnb_4bit: bool = True,
                 bnb_8bit: bool = False,) -> None:
        # print(f"Initializing inference model: {model_name}")

        self.model_name = model_name
        self.trust_remote_code = trust_remote_code

        self.dtype = dtype

        if bnb_4bit:
            self.quantization_config = config_bnb(4)
        elif bnb_8bit:
            self.quantization_config = config_bnb(8)
        else:
            self.quantization_config = None

    @abstractmethod
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
                top_k:int = 1,) -> List[str]:
        pass

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name