import os
import subprocess
from pathlib import Path


def _ensure_java17():
    """Auto-detect and set JAVA_HOME to JDK 17+ if current one is too old."""
    java_candidates = [
        r"C:\Program Files\Java\jdk-21.0.10",
        r"C:\Program Files\Java\jdk-21",
        r"C:\Program Files\Java\jdk-17",
        r"C:\Program Files\Eclipse Adoptium\jdk-17.0.0+35",
        r"C:\Program Files\Microsoft\jdk-17.0.0.35-hotspot",
    ]
    current = os.environ.get("JAVA_HOME", "")
    try:
        result = subprocess.run(
            [str(Path(current) / "bin" / "java"), "-version"],
            capture_output=True, text=True, timeout=5
        )
        ver_str = result.stderr + result.stdout
        import re
        m = re.search(r'version "(\d+)', ver_str)
        if m and int(m.group(1)) >= 17:
            return
    except Exception:
        pass

    for candidate in java_candidates:
        java_exe = Path(candidate) / "bin" / "java.exe"
        if java_exe.exists():
            os.environ["JAVA_HOME"] = candidate
            os.environ["PATH"] = str(Path(candidate) / "bin") + ";" + os.environ.get("PATH", "")
            return

    raise EnvironmentError(
        "PySpark requires Java 17+. Install JDK 17 or set JAVA_HOME to a JDK 17+ path."
    )


class SparkAdapter:
    """
    Benchmarks Apache Spark using PySpark with fully in-memory operations.

    Avoids ALL local filesystem writes (no Parquet/ORC) which require
    winutils.exe on Windows. Instead, DataFrames are cached in Spark's
    in-memory storage layer — this still exercises real Spark computation:
    DAG planning, task scheduling, in-memory columnar storage, shuffles.

    The runner calls operations in sequence within one Python process:
      insert_data  — load dataset, cache & materialise in Spark memory
      read_data    — collect 100 rows from the cached DataFrame
      update_data  — price * 1.1 transform, re-cache the result
      delete_data  — unpersist the cached DataFrame
    run_query    — GROUP BY category when available, otherwise COUNT
    """

    def __init__(self, master_url="local[2]", app_name="PolyStoreBench"):
        _ensure_java17()

        from pyspark.sql import SparkSession

        self.spark = (
            SparkSession.builder
            .appName(app_name)
            .master(master_url)
            .config("spark.driver.host", "127.0.0.1")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .config("spark.sql.shuffle.partitions", "4")
            .getOrCreate()
        )

        self.spark.sparkContext.setLogLevel("ERROR")
        self.df = None        # active in-memory DataFrame
        self.dataset_path = None

    # ------------------------------------------------------------------ #
    #  Benchmark interface                                                 #
    # ------------------------------------------------------------------ #

    def load_data(self, dataset_path):
        """Record the dataset path — actual read happens inside insert_data."""
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        self.dataset_path = dataset_path

    def _build_df_from_path(self):
        """Read the dataset file into a Spark DataFrame (no caching yet)."""
        if not self.dataset_path:
            raise ValueError("No dataset loaded. Call load_data() first.")
        path = self.dataset_path
        if path.endswith(".json"):
            return self.spark.read.option("multiline", "true").json(path)
        else:
            return self.spark.read.csv(path, header=True, inferSchema=True)

    def insert_data(self):
        """
        Simulate INSERT: load dataset, cache in Spark memory, materialise
        with count() so timing covers real data movement + task execution.
        """
        # Unpersist any previous cache
        if self.df is not None:
            try:
                self.df.unpersist()
            except Exception:
                pass

        raw = self._build_df_from_path()
        self.df = raw.cache()
        count = self.df.count()   # triggers real Spark job
        return {"rows_cached": count}

    def read_data(self):
        """
        Simulate READ: collect 100 rows from the cached DataFrame.
        If no cache exists yet (standalone run), build one first.
        """
        if self.df is None:
            raw = self._build_df_from_path()
            self.df = raw.cache()
            self.df.count()   # materialise
        return self.df.limit(100).collect()

    def update_data(self):
        """
        Simulate UPDATE: add a generic update flag column and materialise.
        Equivalent to INSERT OVERWRITE for the cached DataFrame.
        """
        from pyspark.sql.functions import lit

        if self.df is None:
            raw = self._build_df_from_path()
            self.df = raw.cache()
            self.df.count()

        updated = self.df.withColumn("_psb_updated", lit(True))

        old = self.df
        self.df = updated.cache()
        count = self.df.count()   # materialise new cache
        old.unpersist()
        return {"rows_updated": count}

    def delete_data(self):
        """
        Simulate DELETE: unpersist the cached DataFrame from Spark memory.
        """
        if self.df is not None:
            try:
                self.df.unpersist()
            except Exception:
                pass
            self.df = None
        return {"deleted": True}

    def run_query(self):
        """
        Real aggregation benchmark: GROUP BY category when available, else COUNT.
        Triggers a full Spark shuffle (most compute-intensive operation).
        """
        if self.df is None:
            raw = self._build_df_from_path()
            self.df = raw.cache()
            self.df.count()

        if "category" in self.df.columns:
            result = self.df.groupBy("category").count()
        else:
            result = self.df.selectExpr("count(*) as total_rows")

        return result.collect()

    def close(self):
        if self.df is not None:
            try:
                self.df.unpersist()
            except Exception:
                pass
            self.df = None
        if self.spark:
            try:
                self.spark.stop()
            except Exception:
                pass
            self.spark = None

    def stop(self):
        self.close()