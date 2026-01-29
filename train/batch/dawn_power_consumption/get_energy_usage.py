import pathlib
import re
from glob import glob

import pandas as pd

TDP_1550_GPU = 600  # Watts

all_out_files = glob("./*/*.out")
all_out_files = [pathlib.Path(f) for f in all_out_files]

# configs are like 1x1, 1x4, 2x4, 2x8, 4x4, etc.
# sort all_out_files by configuration in order of total no of GPUs used
all_out_files.sort(
    key=lambda f: int(f.parent.name.split("x")[0]) * int(f.parent.name.split("x")[1])
)

# Extract unique configurations from log files
configs = set(f.parent.name for f in all_out_files)
print(f"Configurations found: {configs}")

energy_data = []

for out_file in all_out_files:
    cfg = out_file.parent.name
    n_gpus = int(cfg.split("x")[0]) * int(cfg.split("x")[1])

    with open(out_file) as f:
        text = f.read()

    # e.g. Elapsed: 1194 seconds
    elapsed_match = re.search(r"Elapsed\:\s+" + r"([0-9]+(?:\.[0-9]+)?) seconds", text)
    nnodes = re.search(r"Nodes:\s*(\d+)", text)
    ngpus = re.search(r"GPUs per node:\s*(\d+)", text)

    if elapsed_match:
        elapsed_time = float(elapsed_match.group(1))
    else:
        raise ValueError(f"Elapsed time not found in {out_file}")

    if nnodes and ngpus:
        nnodes_value = int(nnodes.group(1))
        ngpus_value = int(ngpus.group(1))
        total_gpus = nnodes_value * ngpus_value
    else:
        raise ValueError(f"Node/GPU info not found in {out_file}")

    stats_df = pd.read_csv(f"./{cfg}_avg_gpu_stats.csv", index_col=0)

    mean_power_watt = stats_df.loc["mean", "Power (W)"]

    energy_joules = mean_power_watt * elapsed_time * total_gpus
    print(
        f"Energy consumption for {cfg}:\n{energy_joules:.2f} Joules over {elapsed_time:.2f} seconds using {mean_power_watt:.2f} Watts average power."
    )

    energy_data.append([cfg, energy_joules, elapsed_time, mean_power_watt])

print(energy_data)
energy_df = pd.DataFrame(
    energy_data,
    columns=["Config", "Energy (J)", "Elapsed Time (S)", "Mean Power (W)"],
)

energy_df = energy_df.round(2)
energy_df.to_csv("dawn_energy_consumption_summary.csv", index=False)
print("Energy consumption summary saved to dawn_energy_consumption_summary.csv")
