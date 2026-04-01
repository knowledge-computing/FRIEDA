import os
from typing import List
from tqdm import tqdm

from datasets import load_dataset

from .hf import download

def check_images(root_dir:str,
                 list_images: List[str],) -> bool:
    """
    Check if all images exists
    """
    for im in tqdm(list_images):
        if not os.path.exists(os.path.join(root_dir, im)):
            return False
        
    return True

def check_exists(data_dir:str,
                 split:str) -> str:
    
    if os.path.exists(data_dir):
        print(f"[INFO] Data path {data_dir} exists")
        print(f"[INFO] Checking to see if all images exist - Target mode: {split}")

        df = load_dataset("knowledge-computing/FRIEDA", split="data")

        if split == "direct":
            list_images = df["images"].to_list()
        else:
            list_images = df["context_images"].to_list()

        if check_images(root_dir=data_dir,
                        list_images=list_images):
            return data_dir
        else:
            print(f"[WARN] Some images are missing. Redownloading image directory")

    else:
        print(f"[INFO] Data does not exists in {data_dir}")

    snap_dir = download(root_dir=data_dir,
                        bool_return_snap=True)
        
    return snap_dir