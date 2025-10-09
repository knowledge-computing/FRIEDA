import os
import json
import argparse

from frieda.data import FRIEDA

def main(bool_download:bool=False):
    FRIEDA(download=bool_download)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FRIEDA Benchmark")

    parser.add_argument("--download", action="store_true", 
                        help="Download image directory, annotation file, and instruction file")

    args = parser.parse_args()

    main(bool_download=args.download)