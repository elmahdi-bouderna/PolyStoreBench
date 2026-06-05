import csv
import json
import os
import random
from faker import Faker

fake = Faker()

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_records(n=10000):
    data = []
    for i in range(n):
        record = {
            "id": i,
            "customer_name": fake.name(),
            "product": fake.word(),
            "category": random.choice(["tech", "books", "fashion", "food"]),
            "price": round(random.uniform(5, 1000), 2),
            "quantity": random.randint(1, 10),
            "timestamp": fake.iso8601()
        }
        data.append(record)
    return data

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def save_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    for size in [10000, 100000]:
        records = generate_records(size)
        save_json(records, f"{OUTPUT_DIR}/dataset_{size}.json")
        save_csv(records, f"{OUTPUT_DIR}/dataset_{size}.csv")
        print(f"Dataset {size} généré.")