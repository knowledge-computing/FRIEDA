import os
import polars as pl
import pickle

from providers import (DecoderBase, 
                              init_model, determine_backend)
from data_control import (load_data, save_data,
                                 partition_data)

def respond_q(model: DecoderBase,
              instruction_prefix: str,
              data: pl.DataFrame,
              data_dir:str, 
              max_new_tokens:int,
              enable_thinking:bool,

              do_sample: bool,
              temperature: float,
              top_p: float,
              top_k: int):
    
    list_output = model.answerq(questions=data['question_text'].to_list(),
                                images=data['images'].to_list(),
                                data_dir=data_dir,
                                instruction_prefix=instruction_prefix,
                                
                                max_new_tokens=max_new_tokens,
                                enable_thinking=enable_thinking,
                                
                                do_sample=do_sample,
                                temperature=temperature,
                                top_p=top_p,
                                top_k=top_k)
    
    data = data.drop(['prediction', 'answered']).with_columns(
        answered = pl.lit(True),
        prediction = pl.Series(list_output)
    )

    return data

def run_frieda(model:str,
               
               data_dir:str,
               result_dir:str,
               split:bool='direct',
               
               batch_size:int=1,

               # huggingface specific
               use_flash:bool=True,
               enable_thinking:bool=False,
               max_new_tokens:int=2048,
               
               # deterministic setting
               do_sample: bool=False,
               temperature: float=0.01,
               top_p: float=1.0,
               top_k: int=1,) -> None:
    
    # Set up basics
    backend = determine_backend(model)
    save_path = os.path.join(result_dir, f"{model}--frieda-{split}.json")

    # Create directory
    os.makedirs(result_dir, exist_ok=True)

    # Load instruction
    with open(os.path.join(data_dir, "instruction.pkl"), 'rb') as handle:
        instruction_prefix = pickle.load(handle)

    # Load question through Huggingface dataset
    data = load_data()

    # Check if save_path already exists; if exists, load that; else load from huggingface
    if os.path.exists(save_path):
        data = load_data(save_path)
    else:
        data = load_data()

    # Batch the data
    if (backend == 'anthropic') and (batch_size > 50):
        print(f"[INFO] Lowering batch size for {model} to 50 due to chances of failure")
        batch_size = 50

    data, list_unanswered = partition_data(data, batch_size)

    # Set up flash attention
    if use_flash:
        attn_implementation = 'flash_attention_2'
    else:
        attn_implementation = 'eager'

    # Initialize model with all the settings
    model = init_model(model=model,
                       backend=backend,
                       attn_implementation=attn_implementation)

    # Save data file before running the model (just in case)
    save_data(pl_data=data,
              pl_data2=list_unanswered,
              save_path=save_path)

    # Run model only on the questions that have 'answered'=False 
    while list_unanswered:
        i = respond_q(model=model,
                      instruction_prefix=instruction_prefix,
                      data=list_unanswered[0],
                      data_dir=data_dir,

                      max_new_tokens=max_new_tokens,
                      enable_thinking=enable_thinking,
                        
                      do_sample=do_sample,
                      temperature=temperature,
                      top_p=top_p,
                      top_k=top_k)
        
        list_unanswered.pop(0)
        
        data = pl.concat(
            [data, i],
            how='diagonal'
        )

        save_data(pl_data=data, 
                  pl_data2=list_unanswered,
                  save_path=save_path)
        
    save_data(pl_data=data, 
              save_path=save_path,
              bool_revert=True)