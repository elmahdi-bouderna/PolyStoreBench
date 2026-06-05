import json
from adapters._data_loader import load_dataset
import redis

class RedisAdapter:
    def __init__(self, host="localhost", port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.data = []

    def load_data(self, dataset_path):
        self.data = load_dataset(dataset_path)

    def insert_data(self):
        self.client.flushdb()
        for i, record in enumerate(self.data):
            payload = record if isinstance(record, dict) else {"value": record}
            self.client.set(f"record:{i}", json.dumps(payload))

    def read_data(self):
        results = []
        for key in self.client.scan_iter("record:*"):
            results.append(self.client.get(key))
            if len(results) >= 100:
                break
        return results

    def update_data(self):
        for key in self.client.scan_iter("record:*"):
            record = json.loads(self.client.get(key))
            record["_psb_updated"] = True
            self.client.set(key, json.dumps(record))

    def delete_data(self):
        self.client.flushdb()

    def run_query(self):
        count = 0
        for _ in self.client.scan_iter("record:*"):
            count += 1
        return [{"total": count}]