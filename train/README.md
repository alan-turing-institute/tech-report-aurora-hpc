# Aurora Training Experiments

The code in this folder is for performing various training related experiments.
See below for instructions for how to run them.

## Baskerville

### Running within an interactive session

To run the interactives session scripts, first ensure you're on a compute node by running the following or an equiavlent `srun` command (you'll need to update the QoS and account details):

```sh
srun --qos turing --account usjs9456-ati-test --time 1:00:00 --nodes 1 --gpus 1 --cpus-per-gpu 36 --mem 16384 --pty /bin/bash
```

### Queued jobs using sbatch

All sbatch scripts have a QoS and account details set in them.
The parameters used for these will depend on your account and so should be adjusted accordingly.

```
#SBATCH --qos turing
#SBATCH --account usjs9456-ati-test
```

### Training using FSDP

The case of a single node can be run within an srun interactive session or scheduled using the sbatch scripts.

All scripts should be run from within the `aurora-hpc/train/batch` directory.

To run in an interactive session use:

```sh
./bask-local-train-fsdp.sh
```

Only one node and one GPU is supported interacively (although up to four GPUs would be possible by editing the bash script).
Since the `NO_SHARD` option is set no model sharding is performed, only data parallel, meaning that the strategy is equivalent to Distributed Data Parallel.

The script will set up the environment, including creating an appropriate virtual environment, automatically.
The only part that must be performed manually is downloading of the data.

To schedule the experiments for 1 node with 1 GPUs, 1 node with 4 GPUs, 2 nodes each with 2 GPUs (4 GPUs total), 2 nodes each with 4 GPUs (8 GPUs total) and 4 nodes each with 4 GPUs (16 GPUs total), run the following respectively.:

```sh
sbatch ./bask-train-fsdp-1x1.sh
sbatch ./bask-train-fsdp-1x4.sh
sbatch ./bask-train-fsdp-2x4.sh
sbatch ./bask-train-fsdp-2x8.sh
sbatch ./bask-train-fsdp-4x4.sh
```

These will schedule the jobs to run when the resources become available.
The scripts will set up the virtual environment and everything needed apart from downloading the data.

Each of the scheduled jobs will perform four runs to allow averaging of the results.

If you just want a single run, the following script can be used:

```sh
sbatch bask-train-fsdp-4x4.sh
```

This is set up to run on 2 nodes with 2 GPUs and to perform just a single run.
Edit the script header to test other combinations.

### Bandwidth

All bandwidth experiments should be run within an interactive session and from within the `aurora-hpc/train/batch` directory.

To run the disk bandwidth experiments:

```sh
./bask-srun-diskbw.sh
```

To run the GPU bandwidth experiments:

```sh
./bask-srun-gpubw.sh
```

## Dawn

The Dawn scripts are all done through batch jobs, no interactive session scripts.

All scripts should be run directly from the `aurora-hpc/train/batch` directory.


### Creating the virtual environment

Before performing any training the virtual environment should be created by running the following script:

```sh
cd aurora-hpc/train/batch
sbatch dawn-create-venv.sh
```

This will create a virtual environment in the `aurora-hpc/dawn/environments/venv_3_11_11` directory.

## Download the data

The data must also be downloaded before training can commence.
This also requires that you've created an account with the Climate Data Store and created a `.cdsapirc` file in your homd directory with the following contents:

```sh
url: https://cds.climate.copernicus.eu/api
key: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx
```

Here the `x` values must be replaced by your access key.
You can find out more about how to do this on the [Aurora ERA5 page](https://microsoft.github.io/aurora/example_era5.html).

Once you've set up your access key you can then download the data directly to Dawn using the following sbatch script.

```sh
aurora-hpc/dawn/batch/dawn-download-era5.sh
```

If successful this will result in the following files being downoaded to the `aurora-hpc/dawn/era5/era_v_inf` directory.

```
2023-01-atmospheric-36.nc
2023-01-surface-level-36.nc
static.nc
```

### Training

Once the virtual environment is set up, the training can be executed by queueing the appropriate script for the number of nodes and GPUs you want to use.

The following example is for one node and one GPU:

```sh
cd aurora-hpc/train/batch
sbatch dawn-train-ddp-1x1.sh
```

The other available configurations are the following:

```sh
dawn-train-ddp-1x1.sh # One node with one GPU (one GPU total)
dawn-train-ddp-1x4.sh # One node with four GPUs (four GPUs total)
dawn-train-ddp-2x4.sh # Two nodes with two GPUs each (four GPUs total)
dawn-train-ddp-2x8.sh # Two nodes with four GPUs each (eight GPUs total)
dawn-train-ddp-4x4.sh # Four nodes with one GPU each (four GPUs total)
dawn-train-ddp-4x8.sh # Four nodes with two GUUs each (eight GPUs total)
```

After each run the output logs will be sent to the `aurora-hpc/train/batch/results` directory.
