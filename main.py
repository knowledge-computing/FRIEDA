import os
import json
import argparse

from frieda.data import FRIEDA
# from frieda.eval import evaluation

def main(bool_download:bool,
         download_dir:str,
         model:str,
         bool_contextual:bool):
    
    frieda = FRIEDA(download=bool_download,
                    root_dir=download_dir)
    
    # if model:

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FRIEDA Benchmark")

    parser.add_argument("--download", action="store_true", 
                        help="Download image directory, annotation file, and instruction file")
    
    parser.add_argument("--download_dir", default="./data", 
                        help="Path to download data to. Default path is ./data")
    
    parser.add_argument("--model", type=str, default=None,
                        help="Name/model_id/path of LVLM to test on")

    parser.add_argument("--contextual", action="store_true", 
                        help="Evaluate VLM in contextual (with other images from the same document) mode")

    args = parser.parse_args()

    main(bool_download=args.download,
         download_dir=args.download_dir,
         model=args.model,
         bool_contextual=args.contextual)