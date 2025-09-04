#!/bin/bash
#SBATCH --job-name=test_model
#SBATCH --output=/users/2/pyo00005/HOME/MMNIAmapH/output4.out
#SBATCH --time=24:00:00
#SBATCH -p interactive-gpu
#SBATCH --gres=gpu:a40:1
#SBATCH --ntasks=1
#SBATCH --mem=100g
#SBATCH --mail-type=ALL
#SBATCH --mail-user=pyo00005@umn.edu

source ~/.bashrc

export HF_HOME=/home/yaoyi/pyo00005/.models
export HF_HUB_CACHE=/home/yaoyi/pyo00005/.models

conda init bash
conda activate testenv

export CUDA_HOME=$CONDA_PREFIX

nvidia-smi

cd /home/yaoyi/pyo00005/p2/carto-reasoning/cartoreasoning
python3 run_llava_ov.py --question /home/yaoyi/pyo00005/carto-reasoning/cartoreasoning/responses/mini_runs/response_mini.json --images https://media.githubusercontent.com/media/YOO-uN-ee/carto-image/main/ --flash
