from typing import List
import requests
from PIL import Image

def make_chat_prompt(list_imgs: List[str],
                     question: str,
                     img_lmt: int) -> list:
    content = [{"type": "text", "text": "Answer in English only."}]
    for idx, f in enumerate(list_imgs):
        if idx > img_lmt:
            break

        if 'https' in f:
            # Case where image is a link
            content.append({"type": "image", "image": Image.open(requests.get(f, stream=True).raw)})
        else:
            content.append({"type": "image", "image": f"{f}"})

    content.append({"type": "text", "text": f"{question}. "})

    return content