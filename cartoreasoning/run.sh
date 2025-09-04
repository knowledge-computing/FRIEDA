#!/bin/bash
#SBATCH --job-name=test_model
#SBATCH --output=output.out
#SBATCH --time=24:00:00
#SBATCH -p preempt-gpu
#SBATCH --gres=gpu:a40:8
#SBATCH --ntasks=1
#SBATCH --mem=100g
#SBATCH --mail-type=ALL
#SBATCH --mail-user={EMAIL}

source ~/.bashrc

export HF_HOME=./.models
export HF_HUB_CACHE=./.models

conda init bash
conda activate testenv

export CUDA_HOME=$CONDA_PREFIX

nvidia-smi

cd ./p2/carto-reasoning/cartoreasoning
python3 run_llava_ov.py --question ./responses/mini_runs/response_mini.json --images https://media.githubusercontent.com/media/YOO-uN-ee/carto-image/main/ --flash
