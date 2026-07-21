import torch
import gc

from evaluate.providers.base import DecoderBase
from evaluate.providers.utility import determine_backend

# GC and cuda cache empty
try:
    gc.collect()
    torch.cuda.empty_cache()
    print("[INFO] GC collection & CUDA cache emptying")
except: pass

if torch.cuda.is_available():
    num_gpus = torch.cuda.device_count()
    print(f"\tNumber of dedicated GPUs available: {num_gpus}")
else:
    print("[ERROR] No NVIDIA GPUs found or CUDA is not available\n")
    # exit()            # TODO: deactivate later

def init_model(model:str,
               backend:str,
               attn_implementation:str,) -> DecoderBase:
    if backend == "hf":
        if 'Qwen/' in model:
            from evaluate.providers.hf.qwen import QwenDecoder
            return QwenDecoder(model,
                               attn_implementation)

        elif 'OpenGVLab/' in model:
            from evaluate.providers.hf.internvl import InternVLDecoder
            return InternVLDecoder(model,
                                   attn_implementation)

        elif 'AIDC-AI/' in model:
            from evaluate.providers.hf.ovis import OvisDecoder
            return OvisDecoder(model,
                               attn_implementation)

        elif 'llava-hf/' in model:
            from evaluate.providers.hf.llava import LLaVADecoder
            return LLaVADecoder(model,
                                attn_implementation)
        
        elif 'zai-org/' in model:
            from evaluate.providers.hf.glm import GLMDecoder
            return GLMDecoder(model,)

        else:
            print(f"[ERROR] Model:{model} is not supported")
            exit()

    elif backend == 'openai':
        # Support for GPT family
        from evaluate.providers.openai import GPTDecoder
        print()
    
    elif backend == 'anthropic':
        # Support for Claude family
        from evaluate.providers.anthropic import ClaudeDecoder
        print()

    elif backend == 'google':
        # Supoort for Gemini
        from evaluate.providers.google import GeminiDecoder
        print()