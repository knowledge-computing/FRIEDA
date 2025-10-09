from abc import ABC, abstractmethod
from typing import LiteralString

class DecoderBase(ABC):
    def __init__(self,
                 name:str,
                 temperature:float=0.0,
                 max_new_tokens:int=2048,
                 truth_remote_code:bool=True,
                 instruction_prefix:str=None) -> None:
        
        print(f"[INFO] Initializing decoder model: {name}")

        self.name = name
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.truth_remote_code = truth_remote_code
        self.instruction_prefix = instruction_prefix

    @abstractmethod
    def upload_images(self,):
        pass

    @abstractmethod
    def make_chat_prompt(self,):
        pass

    @abstractmethod
    def respond_q(self,):
        pass

    # Return information on the model
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name