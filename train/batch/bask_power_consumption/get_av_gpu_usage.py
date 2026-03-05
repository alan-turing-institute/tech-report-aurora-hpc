import pathlib
import re
from glob import glob

import pandas as pd

all_log_files = glob("./*/gpu-*.txt")
all_log_files = [pathlib.Path(f) for f in all_log_files]

# Extract unique configurations from log files
configs = set(f.parent.name for f in all_log_files)
print(f"Configurations found: {configs}")

grouped_logs = {
    cfg: [f for f in all_log_files if f.parent.name == cfg] for cfg in configs
}
for cfg, log_files in grouped_logs.items():
    cfg_avg_stats = pd.DataFrame()
    cfg_acc_stats = pd.DataFrame()

    for log_file in log_files:
        # column names
        cols = [
            "Date",
            "Time",
            "GPU Idx",
            "Power (W)",
            "GPU Temp (C)",
            "Mem Temp (C)",
            "SM (%)",
            "Mem (%)",
            "Enc (%)",
            "Dec (%)",
            "JPG (%)",
            "OFA (%)",
            "Mem Clock (MHz)",
            "Proc Clock (MHz)",
            "RX PCI (MB/s)",
            "TX PCI (MB/s)",
        ]

        num_re = re.compile(r"-?\d+(?:\.\d+)?")  # valid number

        def clean_num(x):
            x = x.strip()
            if x == "N/A":
                return None
            return float(num_re.match(x).group()) if num_re.match(x) else 0.0

        # read whole file
        with open(log_file) as f:
            lines = f.readlines()

        data = []

        for line in lines:
            # skip header lines (start with #)
            if line.strip().startswith("#"):
                continue

            # skip empty lines
            if not line.strip():
                continue

            # split on whitespace
            parts = line.split()

            # should have 16 columns
            if len(parts) != len(cols):
                continue

            try:
                # parts[0] = date (YYYYMMDD), parts[1] = time (HH:MM:SS), parts[2] = gpu index
                date = parts[0]
                time = parts[1]
                gpu_idx = int(parts[2])

                # convert all numeric values
                row = [date, time, gpu_idx, *[clean_num(x) for x in parts[3:]]]
                data.append(row)
            except (ValueError, IndexError):
                continue

        df = pd.DataFrame(data, columns=cols)
        df.to_csv(f"{log_file}_cleaned.csv", index=False)

        stats_df = df[["SM (%)", "Power (W)"]].describe(percentiles=[])
        stats_df.to_csv(f"{log_file}_stats.csv")

        cfg_avg_stats = pd.concat([cfg_avg_stats, stats_df], axis=0)
        cfg_acc_stats = pd.concat([cfg_acc_stats, df[["SM (%)", "Power (W)"]]], axis=0)

    grouped = cfg_avg_stats.groupby(cfg_avg_stats.index)
    cfg_avg_stats = grouped.mean()
    cfg_avg_stats.loc["min"] = grouped.min().loc["min"]
    cfg_avg_stats.loc["max"] = grouped.max().loc["max"]
    cfg_avg_stats.to_csv(f"{cfg}_avg_gpu_stats.csv")

    cfg_acc_stats.describe(percentiles=[]).to_csv(f"{cfg}_acc_gpu_stats.csv")
