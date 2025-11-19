# ...existing code...
import os
import psutil as ps
import subprocess
import pandas as pd
import time
import math

CSV_PATH = os.path.join(os.path.dirname(__file__), "PcPerformanceData.csv")
SAMPLE_INTERVAL = 5  # seconds

try:
    df = pd.read_csv(CSV_PATH)
except (FileNotFoundError, pd.errors.EmptyDataError):
    df = pd.DataFrame(columns=[
        'timestamp',
        'cpu_usage_percent',
        'gpu_usage_percent',
        'memory_percent',
        'disk_read',
        'disk_write',
        'past_cpu',
        'past_gpu',
        'past_memory',
        'future_cpu',
        'future_gpu',
        'future_memory'
    ])


def _first_int_from_output(output):
    if not output:
        return None
    for line in str(output).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            return int(line)
        except ValueError:
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
    except Exception:
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


if __name__ == "__main__":
    print("Starting continuous collection. Ctrl-C to stop.")
    pending_row = None  # row waiting for its future values
    try:
        while True:
            # collect current sample
            sample = collect_performance_data()

            # build current row with past values (from pending_row if present)
            current_row = {
                'timestamp': sample['timestamp'],
                'cpu_usage_percent': sample['cpu_usage_percent'],
                'gpu_usage_percent': sample['gpu_usage_percent'],
                'memory_percent': sample['memory_percent'],
                'disk_read': sample['disk_read'],
                'disk_write': sample['disk_write'],
                'past_cpu': float('nan'),
                'past_gpu': float('nan'),
                'past_memory': float('nan'),
                'future_cpu': float('nan'),
                'future_gpu': float('nan'),
                'future_memory': float('nan'),
            }

            if pending_row is not None:
                # set past fields for current row (values from 5s ago)
                current_row['past_cpu'] = pending_row.get('cpu_usage_percent', float('nan'))
                current_row['past_gpu'] = pending_row.get('gpu_usage_percent', float('nan'))
                current_row['past_memory'] = pending_row.get('memory_percent', float('nan'))

                # fill future fields for the pending row using current sample
                pending_row['future_cpu'] = sample['cpu_usage_percent']
                pending_row['future_gpu'] = sample['gpu_usage_percent']
                pending_row['future_memory'] = sample['memory_percent']

                # append completed pending_row to dataframe and save
                df = pd.concat([df, pd.DataFrame([pending_row])], ignore_index=True)
                try:
                    df.to_csv(CSV_PATH, index=False)
                except Exception as e:
                    print("Failed to save CSV:", e)

                print(f"Appended row (timestamp {pending_row['timestamp']}) with future filled.")

            # pending_row becomes current_row (will get future when next sample arrives)
            pending_row = current_row

            # wait interval before next sample
            time.sleep(SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        # on exit, append the pending_row (without future) so no data is lost
        if pending_row is not None:
            df = pd.concat([df, pd.DataFrame([pending_row])], ignore_index=True)
            try:
                df.to_csv(CSV_PATH, index=False)
            except Exception as e:
                print("Failed to save CSV on exit:", e)
            print(f"Saved pending row (timestamp {pending_row['timestamp']}) on exit.")
        print("Stopped by user.")
# ...existing code...