import os
import argparse
# from fire import Fire         # for CLI
from warnings import warn

import time
from datetime import datetime
from tqdm import tqdm

import json
import pickle
import polars as pl

def evaluate():
    return 0

def main():
    evaluate()

if __name__ == "main":
    parser = argparse.ArgumentParser(description='Cartographical Reasoning Test')

    parser.add_argument('--model', '-m', required=True,
                        help='Model name/type')

    parser.add_argument('--questions', '-q', required=True,
                        help='Path to questions JSON file')

    parser.add_argument('--images', '-im', default='./', type=str,
                        help="Directory/link to reporsitory containing images")
   
    parser.add_argument('--output_dir', '-o', default='./',
                        help="Location to output files")
    
    main()