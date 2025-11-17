# ...existing code...
import psutil as ps
import subprocess
import requests
import pandas as pd
import time
import math

FUTURE_STEPS = 25

try:
    df = pd.read_csv("PcPerformanceData.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        'timestamp',
        'cpu_usage_percent',
        'gpu_usage_percent',
        'memory_percent',
        'disk_read',
        'disk_write',
    ])


def _first_int_from_output(output):
    if not output:
        return None
    # handle multiple lines, pick first non-empty numeric line
    for line in str(output).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            return int(line)
        except ValueError:
            # try to extract digits
            import re
            m = re.search(r"\d+", line)
            if m:
                return int(m.group())
    return None

def get_gpu_usage():
    try:
        result = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            encoding='utf-8', stderr=subprocess.DEVNULL
        )
        return _first_int_from_output(result) or 0
    except Exception as e:
        print("Error getting GPU usage:", e)
    return None


def collect_performance_data():
    cpuUsage = ps.cpu_percent(interval=None, percpu=False)
    memoryUsage = ps.virtual_memory()
    diskUsage = ps.disk_io_counters()
    performance_data = {
        'timestamp': time.time(),
        'cpu_usage_percent': cpuUsage,
        'gpu_usage_percent': get_gpu_usage(),
        'memory_percent': memoryUsage.percent,
        'disk_read': getattr(diskUsage, "read_count", None),
        'disk_write': getattr(diskUsage, "write_count", None),
    }
    return performance_data

# ...existing code...
if __name__ == "__main__":
        data = collect_performance_data()
        print("Collected data:", data)
        new_df = pd.DataFrame([data])
        print("New df dtypes:\n", new_df.dtypes)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv("PcPerformanceData.csv", index=False)
        print("Saved PcPerformanceData.csv, rows:", len(df))