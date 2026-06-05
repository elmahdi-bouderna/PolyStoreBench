import argparse
from engine.runner import BenchmarkRunner

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--system",
        required=True,
        choices=["mongodb", "redis", "cassandra", "spark", "hive", "hadoop"]
    )
    parser.add_argument(
        "--operation",
        required=True,
        choices=["insert", "read", "update", "delete", "query", "write"]
    )
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--size", required=True, type=int)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--concurrency", required=False, type=int, default=1)

    args = parser.parse_args()

    if args.system == "mongodb":
        from adapters.mongodb_adapter import MongoDBAdapter
        adapter = MongoDBAdapter()

    elif args.system == "redis":
        from adapters.redis_adapter import RedisAdapter
        adapter = RedisAdapter()

    elif args.system == "cassandra":
        from adapters.cassandra_adapter import CassandraAdapter
        adapter = CassandraAdapter()

    elif args.system == "spark":
        from adapters.spark_adapter import SparkAdapter
        adapter = SparkAdapter()

    elif args.system == "hive":
        from adapters.hive_adapter import HiveAdapter
        adapter = HiveAdapter()

    elif args.system == "hadoop":
        from adapters.hadoop_adapter import HadoopAdapter
        adapter = HadoopAdapter()

    else:
        raise ValueError("Système non supporté")

    runner = BenchmarkRunner(adapter, args.system)
    result = runner.run(
        args.scenario,
        args.operation,
        args.dataset,
        args.size,
        concurrency_level=args.concurrency
    )
    print(result)

if __name__ == "__main__":
    main()