#!/bin/bash
#SBATCH --job-name=test_model
#SBATCH --output=output.out
#SBATCH --time=23:00:00
#SBATCH -p msigpu
#SBATCH --gres gpu:a100:2
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=5gb
#SBATCH --mail-type=ALL
#SBATCH --mail-user={EMAIL}

source ~/.bashrc

export HF_HUB_CACHE=/scratch.global/li002666/.cache/huggingface/hub/

module load cuda/12.0
conda activate carto


nvidia-smi

cd /users/0/li002666/multi-map/carto-reasoning/cartoreasoning 

python run_llava_ov.py --model='llava-hf/llava-onevision-qwen2-72b-ov-hf' --questions='../questions/response_full_d10.json' --images='https://media.githubusercontent.com/media/YOO-uN-ee/carto-image/main/' --batch_size=4 --cache_dir='/scratch.global/li002666/.cache/huggingface'
