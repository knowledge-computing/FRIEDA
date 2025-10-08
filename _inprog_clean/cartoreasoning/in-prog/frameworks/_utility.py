from typing import List

def make_chat_prompt(model:str,
                     instruction:str, 
                     question:str,
                     api_base:bool) -> str:
    
    task_prompt = f"""
    {instruction}
    {question}
    Give ONLY the answer.
    """

    if api_base:

    return ""