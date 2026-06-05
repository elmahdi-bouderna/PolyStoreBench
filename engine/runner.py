import time
import threading
from monitoring.collector import MetricsCollector
from storage.results_db import save_result


class BenchmarkRunner:
    def __init__(self, adapter, system_name):
        self.adapter = adapter
        self.system_name = system_name

    def run_concurrent_reads(self, num_threads=10, reads_per_thread=20):
        latencies = []

        def worker():
            for _ in range(reads_per_thread):
                t1 = time.perf_counter()
                self.adapter.read_data()
                t2 = time.perf_counter()
                latencies.append((t2 - t1) * 1000)

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]

        start = time.perf_counter()
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        end = time.perf_counter()

        total_ops = num_threads * reads_per_thread
        total_time = end - start
        throughput = total_ops / total_time if total_time > 0 else 0

        return {
            "latency_avg_ms": sum(latencies) / len(latencies) if latencies else 0,
            "latency_min_ms": min(latencies) if latencies else 0,
            "latency_max_ms": max(latencies) if latencies else 0,
            "throughput_ops_sec": throughput,
            "execution_time_sec": round(total_time, 4)
        }

    def run(self, scenario_name, operation, dataset_path, dataset_size, concurrency_level=1, run_number=1):
        self.adapter.load_data(dataset_path)

        collector = MetricsCollector()
        latencies = []
        op_count = 0

        if operation == "insert":
            collector.start()
            t1 = time.perf_counter()
            self.adapter.insert_data()
            t2 = time.perf_counter()
            collector.stop()

            latencies.append((t2 - t1) * 1000)
            op_count = dataset_size
            execution_time = collector.get_execution_time()

        elif operation == "read":
            if concurrency_level > 1:
                concurrent_result = self.run_concurrent_reads(
                    num_threads=concurrency_level,
                    reads_per_thread=20
                )
                execution_time = concurrent_result["execution_time_sec"]
                latency_avg_ms = concurrent_result["latency_avg_ms"]
                latency_min_ms = concurrent_result["latency_min_ms"]
                latency_max_ms = concurrent_result["latency_max_ms"]
                throughput_ops_sec = concurrent_result["throughput_ops_sec"]
            else:
                collector.start()
                for _ in range(100):
                    t1 = time.perf_counter()
                    self.adapter.read_data()
                    t2 = time.perf_counter()
                    latencies.append((t2 - t1) * 1000)
                collector.stop()

                execution_time = collector.get_execution_time()
                op_count = len(latencies)

                latency_avg_ms = sum(latencies) / len(latencies) if latencies else 0
                latency_min_ms = min(latencies) if latencies else 0
                latency_max_ms = max(latencies) if latencies else 0
                throughput_ops_sec = op_count / execution_time if execution_time > 0 else 0

        elif operation == "update":
            collector.start()
            t1 = time.perf_counter()
            self.adapter.update_data()
            t2 = time.perf_counter()
            collector.stop()

            latencies.append((t2 - t1) * 1000)
            op_count = dataset_size
            execution_time = collector.get_execution_time()

        elif operation == "delete":
            collector.start()
            t1 = time.perf_counter()
            self.adapter.delete_data()
            t2 = time.perf_counter()
            collector.stop()

            latencies.append((t2 - t1) * 1000)
            op_count = dataset_size
            execution_time = collector.get_execution_time()

        elif operation == "query":
            collector.start()
            t1 = time.perf_counter()
            if hasattr(self.adapter, "run_query"):
                self.adapter.run_query()
            else:
                raise ValueError(f"L'adapter {self.system_name} ne supporte pas run_query()")
            t2 = time.perf_counter()
            collector.stop()

            latencies.append((t2 - t1) * 1000)
            op_count = dataset_size
            execution_time = collector.get_execution_time()

        elif operation == "write":
            collector.start()
            t1 = time.perf_counter()
            self.adapter.insert_data()
            t2 = time.perf_counter()
            collector.stop()

            latencies.append((t2 - t1) * 1000)
            op_count = dataset_size
            execution_time = collector.get_execution_time()

        else:
            raise ValueError(f"Opération inconnue: {operation}")

        if operation != "read" or concurrency_level == 1:
            latency_avg_ms = sum(latencies) / len(latencies) if latencies else 0
            latency_min_ms = min(latencies) if latencies else 0
            latency_max_ms = max(latencies) if latencies else 0
            throughput_ops_sec = op_count / execution_time if execution_time > 0 else 0

        sys_metrics = collector.get_system_metrics()

        result_data = {
            "system_name": self.system_name,
            "scenario_name": scenario_name,
            "operation": operation,
            "dataset_size": dataset_size,
            "execution_time_sec": round(execution_time, 4),
            "latency_avg_ms": round(latency_avg_ms, 4),
            "latency_min_ms": round(latency_min_ms, 4),
            "latency_max_ms": round(latency_max_ms, 4),
            "throughput_ops_sec": round(throughput_ops_sec, 4),
            "concurrency_level": concurrency_level,
            "run_number": run_number,
            **sys_metrics
        }

        save_result(result_data)
        return result_data