#!/bin/bash -l
#SBATCH --job-name venv
#SBATCH --output results/download-era5-%A.out
#SBATCH --account airr-p8-rcpp-dawn-gpu
#SBATCH --partition pvc9 # Dawn PVC partition
#SBATCH --cpus-per-task 24  # Number of cores per task
#SBATCH --nodes 1 # Number as nodes
#SBATCH --gpus-per-node 1 # Number of requested GPUs per node
#SBATCH --ntasks-per-node 1 # MPI ranks per node
#SBATCH --time 02:00:00

# Execute using:
# sbatch ./dawn-download-era5.sh

echo
echo "## Aurora download ERA5 data script starting"

# Quit on error
set -e

pushd ../scripts

echo
echo "## Loading modules"

module purge
module load default-dawn
module load lua
module load intel-oneapi-ccl/2021.14.0
module load intel-oneapi-mpi/2021.14.1
module load intel-oneapi-mkl/2025.0.1

echo
echo "## Configuring environment"

VENV_DIR=../../dawn/environments/venv_3_11_11

echo
echo "## Initialising virtual environment"

source ${VENV_DIR}/bin/activate

echo
echo "## Details"
echo
echo "Nodes: ${SLURM_JOB_NUM_NODES}"
echo "GPUs per node: ${SLURM_GPUS_PER_NODE}"
echo "Tasks per node: ${SLURM_NTASKS_PER_NODE}"
echo "CPUS per task: ${SLURM_CPUS_PER_TASK}"
echo "Working directory: $(realpath ${PWD})"
echo "Location of venv: $(realpath $VENV_DIR)"

echo
echo "## Downloading data"

START=$(date +%s)
python era_v_download.py
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
echo "## Aurora download ERA5 data script completed"
