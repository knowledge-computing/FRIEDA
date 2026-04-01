import os
import json
import argparse

from download import gdrive, hf, check
from evaluate import run_frieda, evaluate_model

def download_data(download_dir:str,
                  method:str) -> None:
    if method == "gdown":
        gdrive.download(root_dir=download_dir)
    else:
        hf.download(root_dir=download_dir)

def eval_frieda(model:str,
                split:str,
                data_dir:str,
                result_dir:str,
                batch_size:int,
                thinking:bool,
                use_flash:bool,
                evaluate:bool,) -> None:
    
    # Load FRIEDA dataset
    if data_dir:
        # Attempt to load data and if not download it
        data_dir = check.check_exists(data_dir=data_dir,
                                      split=split)
    else:
        data_dir = hf.download(bool_return_snap=True)

    # Run with loaded model
    run_frieda(model=model,
               split=split,

               data_dir=data_dir,
               result_dir=result_dir,

               batch_size=batch_size,
               use_flash=use_flash,
               enable_thinking=thinking,)

    if evaluate:
        print("[INFO] Running evaluation")
        pass
    print("[INFO] ")

def collect_data(data_dir:str) -> None:
    print(f"[INFO] Extracted all images from files in {data_dir}")
    print("[INFO] Merging splitted image based on height and weight.\n       There might be errors.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FRIEDA Benchmark")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_download = sub.add_parser("download")
    parser.add_argument("--download_dir", default="./data", 
                        help="Path to download data to. Default path is ./data")
    parser.add_arugment("--method", type=str, default='hf', choices=['gdrive', 'hf'],
                        help="Method of downloading FRIEDA (either Google Drive or HuggingFace)")
    
    p_eval = sub.add_parser("test")
    parser.add_argument("--model", type=str, default=None,
                        help="Name/model_id/path of LVLM to test on")
    parser.add_argument("--split", type=str, default='direct', choices=['direct', 'contextual'],
                        help="FRIEDA evaluation subset (either -direct or -contextual)"),
    parser.add_argument('--data_dir', type=str, default=None,
                        help="")
    parser.add_argument("--result_dir", type=str, default='./results',
                        help="Path to save evaluation results to. Default path is ./results")
    parser.add_argument("--batch_size", type=int, default=8,
                        help="Batch size")
    parser.add_argument("--thinking", action="store_true",
                        help="Run in thinking mode. e.g., Ovis2.5-Thinking")
    parser.add_argument("--use_flash", action="store_true",
                        help="Use flash attention 2")
    parser.add_argument("--evaluate", action="store_true",
                        help="Run final output evaluation")
    
    # p_visualize = sub.add_parser("visualize")

    p_preprocess = sub.add_parser("collection")
    parser.add_argument("--data_dir", type=str, required=True,
                        help="Directory with raw PDF files")

    args = parser.parse_args()

    if args.cmd == "download":
        download_data(download_dir=args.download_dir,
                      method=args.method)

    if args.cmd == "test":
        eval_frieda(model=args.model,
                    data_dir=args.data_dir,
                    split=args.split,
                    result_dir=args.result_dir,
                    batch_size=args.batch_size,
                    thinking=args.thinking,
                    use_flash=args.use_flash,
                    evaluate=args.evaluate)