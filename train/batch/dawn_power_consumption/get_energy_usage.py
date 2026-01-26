import pathlib
import re
from glob import glob

import pandas as pd

TDP_1550_GPU = 600  # Watts

all_out_files = glob("./*/*.out")
all_out_files = [pathlib.Path(f) for f in all_out_files]

# Extract unique configurations from log files
configs = set(f.parent.name for f in all_out_files)
print(f"Configurations found: {configs}")

for out_file in all_out_files:
    cfg = out_file.parent.name

    with open(out_file) as f:
        text = f.read()

    # e.g. Elapsed: 1194 seconds
    elapsed_match = re.search(r"Elapsed\:\s+" + r"([0-9]+(?:\.[0-9]+)?) seconds", text)

    if elapsed_match:
        elapsed_time = float(elapsed_match.group(1))
    else:
        raise ValueError(f"Elapsed time not found in {out_file}")

    stats_df = pd.read_csv(f"./{cfg}_avg_gpu_stats.csv", index_col=0)

    mean_power_watt = stats_df.loc["mean", "Power (W)"]

    energy_joules = mean_power_watt * elapsed_time
    print(
        f"Energy consumption for {cfg}:\n{energy_joules:.2f} Joules over {elapsed_time:.2f} seconds using {mean_power_watt:.2f} Watts average power."
    )
