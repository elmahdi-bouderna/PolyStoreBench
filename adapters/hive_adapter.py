import csv
import json
import os
import subprocess
import tempfile

from adapters._data_loader import load_dataset


class HiveAdapter:
    """
    Benchmarks Apache Hive via HiveServer2 using impyla (Windows-compatible).
    Uses NOSASL auth — no Kerberos/SASL libs required.
    Connects lazily (on first operation) so import never crashes.
    Converts any dataset into a generic CSV with (id, payload, updated).
    """

    def __init__(self, host="127.0.0.1", port=10000, database="default",
                 namenode_container="psb_namenode", hdfs_path="/hive/benchmark"):
        self.host = host
        self.port = port
        self.database = database
        self.namenode_container = namenode_container
        self.hdfs_path = hdfs_path
        self._conn = None
        self.dataset_path = None
        self._local_csv_path = None
        self._row_count = 0

    # ------------------------------------------------------------------ #
    #  Connection (lazy)                                                   #
    # ------------------------------------------------------------------ #

    def _connect(self):
        if self._conn is None:
            try:
                from impala.dbapi import connect
            except ImportError:
                raise ImportError(
                    "impyla is required for HiveAdapter. "
                    "Install with: pip install impyla thrift"
                )
            self._conn = connect(
                host=self.host,
                port=self.port,
                database=self.database,
                auth_mechanism="PLAIN",
            )
        return self._conn

    def _cursor(self):
        return self._connect().cursor()

    def _exec(self, sql):
        cur = self._cursor()
        try:
            cur.execute(sql)
            return cur
        except Exception:
            cur.close()
            raise

    # ------------------------------------------------------------------ #
    #  Table bootstrap                                                     #
    # ------------------------------------------------------------------ #

    def _ensure_table(self):
        self._exec("DROP TABLE IF EXISTS benchmark_data")
        self._exec("""
            CREATE TABLE IF NOT EXISTS benchmark_data (
                id      INT,
                payload STRING,
                updated BOOLEAN
            )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
            TBLPROPERTIES ("skip.header.line.count"="1")
        """)

    # ------------------------------------------------------------------ #
    #  Benchmark interface                                                 #
    # ------------------------------------------------------------------ #

    def load_data(self, dataset_path):
        """Load any dataset and write a generic CSV for Hive."""
        records = load_dataset(dataset_path)
        if not records:
            raise ValueError("Dataset is empty.")

        tmp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv",
            prefix="psb_generic_",
            mode="w",
            newline="",
            encoding="utf-8"
        )
        writer = csv.writer(tmp)
        writer.writerow(["id", "payload", "updated"])
        for i, record in enumerate(records):
            payload = json.dumps(record, ensure_ascii=True)
            writer.writerow([i, payload, False])
        tmp.close()

        self.dataset_path = tmp.name
        self._local_csv_path = tmp.name
        self._row_count = len(records)

    def insert_data(self):
        if not self.dataset_path:
            raise ValueError("No dataset loaded for Hive.")

        filename = os.path.basename(self.dataset_path)

        # 1. Copy CSV into the namenode container
        subprocess.run(
            ["docker", "cp", self.dataset_path,
             f"{self.namenode_container}:/tmp/{filename}"],
            check=True
        )

        # 2. Push to HDFS
        subprocess.run(
            ["docker", "exec", self.namenode_container,
             "hdfs", "dfs", "-mkdir", "-p", self.hdfs_path],
            check=True
        )
        subprocess.run(
            ["docker", "exec", self.namenode_container,
             "hdfs", "dfs", "-put", "-f",
             f"/tmp/{filename}", f"{self.hdfs_path}/{filename}"],
            check=True
        )

        # 3. Create table & load from HDFS
        self._ensure_table()
        self._exec(
            f"LOAD DATA INPATH '{self.hdfs_path}/{filename}' "
            f"OVERWRITE INTO TABLE benchmark_data"
        )

    def read_data(self):
        cur = self._exec("SELECT * FROM benchmark_data LIMIT 100")
        rows = cur.fetchall()
        cur.close()
        return rows

    def update_data(self):
        # Hive does not support UPDATE — rewrite via INSERT OVERWRITE
        self._exec("""
            INSERT OVERWRITE TABLE benchmark_data
            SELECT id, payload, true AS updated
            FROM benchmark_data
        """)

    def delete_data(self):
        self._exec("TRUNCATE TABLE benchmark_data")

    def run_query(self):
        cur = self._exec("""
            SELECT COUNT(*) AS total
            FROM benchmark_data
        """)
        rows = cur.fetchall()
        cur.close()
        return rows

    def execute_sql(self, sql_query):
        cur = self._exec(sql_query)
        rows = cur.fetchall()
        cur.close()
        return rows

    def close(self):
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
        if self._local_csv_path and os.path.exists(self._local_csv_path):
            try:
                os.remove(self._local_csv_path)
            except Exception:
                pass
            self._local_csv_path = None