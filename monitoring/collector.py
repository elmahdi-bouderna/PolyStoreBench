import sys
import psutil
import time


class MetricsCollector:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def get_execution_time(self):
        if self.start_time is None or self.end_time is None:
            return 0.0
        return round(self.end_time - self.start_time, 4)

    def get_system_metrics(self):
        # Windows requires a drive letter path; Linux/Mac use '/'
        if sys.platform.startswith("win"):
            disk_path = "C:\\"
        else:
            disk_path = "/"

        try:
            disk_pct = psutil.disk_usage(disk_path).percent
        except Exception:
            disk_pct = 0.0

        return {
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": disk_pct,
        }