"""
Shared dataset loader utility for all adapters.
Supports both CSV and JSON files transparently.
"""
import csv
import json


def _normalize_records(records: list) -> list[dict]:
    normalized = []
    for i, record in enumerate(records):
        if isinstance(record, dict):
            normalized.append(record)
        else:
            normalized.append({"value": record, "_psb_index": i})
    return normalized


def load_dataset(dataset_path: str) -> list[dict]:
    """
    Load a CSV or JSON dataset file into a list of dicts.
    Handles:
      - JSON arrays:   [{"id": 1, ...}, ...]
      - JSON lines:    {"id": 1, ...}\n{"id": 2, ...}
      - CSV with header row
    """
    path = dataset_path.strip()

    if path.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        # Try standard JSON array first
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return _normalize_records(data)
            if isinstance(data, dict):
                return _normalize_records([data])
        except json.JSONDecodeError:
            pass
        # Fall back to JSON Lines (one JSON object per line)
        records = []
        for line in content.splitlines():
            line = line.strip().rstrip(",")
            if line and line.startswith("{"):
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        if records:
            return _normalize_records(records)
        raise ValueError(f"Cannot parse JSON file: {path}")

    else:
        # Treat as CSV
        records = []
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
        return _normalize_records(records)
