from adapters._data_loader import load_dataset
from pymongo import MongoClient


class MongoDBAdapter:
    def __init__(self, host="127.0.0.1", port=27018, username="admin", password="admin123", database="polystorebench"):
        self.client = MongoClient(
            f"mongodb://{username}:{password}@{host}:{port}/?authSource=admin",
            serverSelectionTimeoutMS=5000
        )
        self.db = self.client[database]
        self.collection = self.db["benchmark_data"]
        self.data = []

    def load_data(self, dataset_path):
        self.data = load_dataset(dataset_path)

    def insert_data(self):
        if self.data:
            self.collection.delete_many({})
            docs = []
            for i, record in enumerate(self.data):
                doc = dict(record) if isinstance(record, dict) else {"value": record}
                if "_id" in doc:
                    doc.pop("_id")
                doc["_psb_id"] = i
                docs.append(doc)
            self.collection.insert_many(docs)

    def read_data(self):
        return list(self.collection.find().limit(100))

    def update_data(self):
        self.collection.update_many({}, {"$set": {"_psb_updated": True}})

    def delete_data(self):
        self.collection.delete_many({})

    def run_query(self):
        total = self.collection.count_documents({})
        return [{"total": total}]