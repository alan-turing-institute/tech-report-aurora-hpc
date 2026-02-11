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

    for log_file in log_files:
        # column names
        cols = [
            "Timestamp",
            "DeviceId",
            "GPU Util (%)",
            "Power (W)",
            "Freq (MHz)",
            "CE0/0",
            "CE0/1",
            "CE0/2",
            "CE0/3",
            "CE1/0",
            "CE1/1",
            "CE1/2",
            "CE1/3",
        ]

        ts_re = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}")  # timestamp
        num_re = re.compile(r"-?\d+(?:\.\d+)?")  # valid number

        def clean_num(x):
            x = x.strip()
            if x == "N/A":
                return None
            return float(num_re.match(x).group()) if num_re.match(x) else 0.0

        # read whole file
        with open(log_file) as f:
            text = f.read()

        # split on timestamps (row starts)
        rows = re.split(r"(?=\d{2}:\d{2}:\d{2}\.\d{3})", text)

        data = []

        for r in rows:
            # split into parts
            parts = [p.strip() for p in r.split(",")]

            # parts[0] should be full timestamp
            if len(parts) < 2 or not ts_re.fullmatch(parts[0]):
                continue
            if len(parts) != len(cols):
                continue

            try:
                device_id = int(parts[1])
            except ValueError:
                continue

            row = [parts[0], device_id, *[clean_num(x) for x in parts[2:]]]

            data.append(row)

        df = pd.DataFrame(data, columns=cols)
        df.to_csv(f"{log_file}_cleaned.csv", index=False)

        stats_df = df[["GPU Util (%)", "Power (W)"]].describe(percentiles=[])
        stats_df.to_csv(f"{log_file}_stats.csv")

        cfg_avg_stats = pd.concat([cfg_avg_stats, stats_df], axis=0)

    grouped = cfg_avg_stats.groupby(cfg_avg_stats.index)
    cfg_avg_stats = grouped.mean()
    cfg_avg_stats.loc["min"] = grouped.min().loc["min"]
    cfg_avg_stats.loc["max"] = grouped.max().loc["max"]
    cfg_avg_stats.to_csv(f"{cfg}_avg_gpu_stats.csv")
