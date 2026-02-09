#!/bin/bash
# vim: et:ts=4:sts=4:sw=4
#SBATCH --qos turing
#SBATCH --account usjs9456-ati-test
#SBATCH --time 1:00:0
#SBATCH --nodes 4
#SBATCH --ntasks-per-node 1
#SBATCH --gpus-per-node 1
#SBATCH --mem 65536
#SBATCH --constraint=a100_80
#SBATCH --job-name aurora-train
#SBATCH --output results/four_nodes_one_gpu.txt

# Execute using:
# sbatch ./bask-train-fsdp-4x4.sh

echo
echo "## Aurora fine-tuning script starting"

# Quit on error
set -e

pushd ../scripts

if [ ! -d ../../downloads ]; then
  echo "Please run the batch-download.sh script to download the data."
  exit 1
fi

echo
echo "## Loading modules"

module -q purge
module -q load baskerville
module -q load bask-apps/live
module -q load PyTorch/2.0.1-foss-2022a-CUDA-11.7.0
module -q load torchvision/0.15.2-foss-2022a-CUDA-11.7.0

echo
echo "## Configuring environment"

export PRIMARY_PORT=$((16384 + $RANDOM % 16384))
export PRIMARY_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export OMP_NUM_THREADS=1
#export HF_HOME="/bask/projects/u/usjs9456-ati-test/"

echo
echo "## Initialising virtual environment"

python3 -m venv venv
. ./venv/bin/activate

pip install --quiet --upgrade pip
pip install --quiet ../../.[bask]

echo
echo "## Details"
echo
echo "Date: $(date)"
echo "Nodes: ${SLURM_JOB_NUM_NODES}"
echo "GPUs per node: ${SLURM_GPUS_PER_NODE}"
echo "Primary address: ${PRIMARY_ADDR}"
echo "Primary port: ${PRIMARY_PORT}"
echo "Tasks per node: ${SLURM_NTASKS_PER_NODE}"
echo "CPUS per task: ${SLURM_CPUS_PER_TASK}"
echo "Working directory: $(realpath ${PWD})"
echo "Node list: ${SLURM_JOB_NODELIST}"
echo "GPUs: ${SLURM_JOB_GPUS}"

echo
echo "## Running model"

# Track GPU and CPU metrics
mpirun --host ${SLURM_NODELIST} bash -c 'stdbuf -o0 nvidia-smi dmon -o TD -s puct -d 1 > ../batch/results/gpu-${SLURM_JOB_ID}-${OMPI_COMM_WORLD_RANK}.txt' &
mpirun --host ${SLURM_NODELIST} bash -c 'stdbuf -o0 vmstat -t 1 > ../batch/results/cpu-${SLURM_JOB_ID}-${OMPI_COMM_WORLD_RANK}.txt' &

# Perform the prediction
# Repeat this 4 times so we get better logs
START=$(date +%s)
for i in {0..3}; do
    srun bash -c \
        'python -m torch.distributed.run \
        --nnodes ${SLURM_JOB_NUM_NODES} \
        --nproc-per-node ${SLURM_GPUS_PER_NODE} \
        --master_addr ${PRIMARY_ADDR} \
        --master_port ${PRIMARY_PORT} \
        --node_rank ${SLURM_NODEID} \
        train.py \
        -d ../../downloads'
done
END=$(date +%s)
ELAPSED=$((${END}-${START}))

echo
echo "## Details post"
echo
echo "Time completed: $(date --iso-8601=ns)"
echo "Epoch start: ${START}"
echo "Epoch end: ${END}"
echo "Elapsed: ${ELAPSED} seconds"

echo
echo "## Tidying up"

deactivate
popd

echo
echo "## Aurora fine-tuning script completed"
