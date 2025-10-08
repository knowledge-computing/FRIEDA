import os
import argparse

import json
import pickle

from dotenv import load_dotenv

# Gemini packages
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

def main(cache_dir:str):
    with open(os.path.join(cache_dir, ''), 'rb') as handle:
        dict_info = pickle.load(handle)

    job_name = dict_info['job_name']
    output_filename = dict_info["output_fn"]
    
    batch_job = client.batches.get(name=job_name)

    if batch_job.state.name == 'JOB_STATE_SUCCEEDED':

        # If batch job was created with a file
        if batch_job.dest and batch_job.dest.file_name:
            # Results are in a file
            result_file_name = batch_job.dest.file_name
            print(f"Results are in file: {result_file_name}")

            print("Downloading result file content...")
            file_content = client.files.download(file=result_file_name)
            # Process file_content (bytes) as needed
            print(file_content.decode('utf-8'))

        # If batch job was created with inline request
        elif batch_job.dest and batch_job.dest.inlined_responses:
            # Results are inline
            print("Results are inline:")
            for i, inline_response in enumerate(batch_job.dest.inlined_responses):
                print(f"Response {i+1}:")
                if inline_response.response:
                    # Accessing response, structure may vary.
                    try:
                        print(inline_response.response.text)
                    except AttributeError:
                        print(inline_response.response) # Fallback
                elif inline_response.error:
                    print(f"Error: {inline_response.error}")
        else:
            print("No results found (neither file nor inline).")
    else:
        print(f"Job did not succeed. Final state: {batch_job.state.name}")
        if batch_job.error:
            print(f"Error: {batch_job.error}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cartographical Reasoning Test; Gemini get')

    parser.add_argument('--cache_dir', '-c', default='./',
                        help="Location to cache directory (cache for image names)")
    
    args = parser.parse_args()

    main(cache_dir=args.cache_dir)