# Power/Energy Consumption Analysis

## Generating logs

GPU monitoring logs and training output are produced by the batch scripts:

- **Baskerville**: `bask-train-fsdp-*.sh` (uses `nvidia-smi dmon`)
- **Dawn**: `dawn-train-ddp-*.sh` (uses `xpu-smi dump`)

Each script writes one GPU log per node (`gpu-<jobid>-<node>.txt`) and one training output file per run.

## Expected layout

Copy the logs into the corresponding `*_power_consumption/` directory:

```
bask_power_consumption/
  <config>/gpu-<jobid>-<node>.txt   # nvidia-smi dmon output (one per node)
  <config>/<name>.txt               # training output (contains Elapsed, Nodes, GPUs per node)

dawn_power_consumption/
  <config>/gpu-<jobid>-<node>.txt   # xpu-smi dump output (one per node)
  <config>/<name>.out               # training output (contains Elapsed, Nodes, GPUs per node)
```

Where `<config>` is e.g. `1x1`, `1x4`, `2x4`, `4x8` (nodes x GPUs per node).

## Running the analysis

From each `*_power_consumption/` directory:

1. `python get_av_gpu_usage.py` -- computes per-config GPU stats CSVs
2. `python get_energy_usage.py` -- computes energy consumption summary (requires step 1 output)
