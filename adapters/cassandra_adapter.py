import json
import sys
import types
from adapters._data_loader import load_dataset

# ── Python 3.13 compatibility fix ────────────────────────────────────────────
# cassandra-driver checks for `asyncore` at import time; Python 3.13 removed it.
# We inject a minimal stub so the import succeeds, then switch to asyncio reactor.
if "asyncore" not in sys.modules:
    _stub = types.ModuleType("asyncore")
    _stub.dispatcher = object
    _stub.loop = lambda *a, **k: None
    sys.modules["asyncore"] = _stub

from cassandra.cluster import Cluster
from cassandra.io.asyncioreactor import AsyncioConnection


class CassandraAdapter:
    def __init__(self, host="127.0.0.1", port=9042, keyspace="polystorebench"):
        self.cluster = Cluster(
            [host],
            port=port,
            connection_class=AsyncioConnection,
        )
        self.session = self.cluster.connect()
        self.keyspace = keyspace
        self.data = []
        self.record_ids = []
        self._setup()

    def _setup(self):
        self.session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {self.keyspace}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};
        """)
        self.session.set_keyspace(self.keyspace)
        self.session.execute("DROP TABLE IF EXISTS benchmark_data")
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_data (
                id int PRIMARY KEY,
                payload text,
                updated boolean
            );
        """)

    def load_data(self, dataset_path):
        self.data = load_dataset(dataset_path)
        self.record_ids = list(range(len(self.data)))

    def insert_data(self):
        self.session.execute("TRUNCATE benchmark_data")
        prepared = self.session.prepare("""
            INSERT INTO benchmark_data (id, payload, updated)
            VALUES (?, ?, ?)
        """)
        for i, record in enumerate(self.data):
            self.session.execute(prepared, (
                i,
                json.dumps(record, ensure_ascii=True),
                False
            ))
        self.record_ids = list(range(len(self.data)))

    def read_data(self):
        rows = self.session.execute("SELECT * FROM benchmark_data LIMIT 100")
        return list(rows)

    def update_data(self):
        if not self.record_ids:
            return
        prepared = self.session.prepare("""
            UPDATE benchmark_data SET updated = ? WHERE id = ?
        """)
        for record_id in self.record_ids:
            self.session.execute(prepared, (True, record_id))

    def delete_data(self):
        self.session.execute("TRUNCATE benchmark_data")

    def run_query(self):
        rows = self.session.execute(
            f"SELECT COUNT(*) AS total FROM {self.keyspace}.benchmark_data"
        )
        return list(rows)