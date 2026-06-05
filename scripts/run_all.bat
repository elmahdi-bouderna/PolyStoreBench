@echo off
echo ============================================================
echo  PolyStoreBench -- Full Benchmark Suite
echo ============================================================

REM ── MongoDB ─────────────────────────────────────────────────
echo [1/6] Benchmarking MongoDB...
python main.py --system mongodb --operation insert  --dataset data\dataset_10000.json  --size 10000  --scenario insert_10k
python main.py --system mongodb --operation read    --dataset data\dataset_10000.json  --size 10000  --scenario read_10k
python main.py --system mongodb --operation update  --dataset data\dataset_10000.json  --size 10000  --scenario update_10k
python main.py --system mongodb --operation delete  --dataset data\dataset_10000.json  --size 10000  --scenario delete_10k
python main.py --system mongodb --operation query   --dataset data\dataset_10000.json  --size 10000  --scenario query_10k
python main.py --system mongodb --operation insert  --dataset data\dataset_100000.json --size 100000 --scenario insert_100k
python main.py --system mongodb --operation read    --dataset data\dataset_100000.json --size 100000 --scenario read_100k
python main.py --system mongodb --operation read    --dataset data\dataset_10000.json  --size 10000  --scenario read_10k_c10 --concurrency 10

REM ── Redis ────────────────────────────────────────────────────
echo [2/6] Benchmarking Redis...
python main.py --system redis --operation insert  --dataset data\dataset_10000.json  --size 10000  --scenario insert_10k
python main.py --system redis --operation read    --dataset data\dataset_10000.json  --size 10000  --scenario read_10k
python main.py --system redis --operation update  --dataset data\dataset_10000.json  --size 10000  --scenario update_10k
python main.py --system redis --operation delete  --dataset data\dataset_10000.json  --size 10000  --scenario delete_10k
python main.py --system redis --operation insert  --dataset data\dataset_100000.json --size 100000 --scenario insert_100k
python main.py --system redis --operation read    --dataset data\dataset_100000.json --size 100000 --scenario read_100k
python main.py --system redis --operation read    --dataset data\dataset_10000.json  --size 10000  --scenario read_10k_c10 --concurrency 10

REM ── Cassandra ────────────────────────────────────────────────
echo [3/6] Benchmarking Cassandra...
python main.py --system cassandra --operation insert  --dataset data\dataset_10000.json  --size 10000  --scenario insert_10k
python main.py --system cassandra --operation read    --dataset data\dataset_10000.json  --size 10000  --scenario read_10k
python main.py --system cassandra --operation update  --dataset data\dataset_10000.json  --size 10000  --scenario update_10k
python main.py --system cassandra --operation delete  --dataset data\dataset_10000.json  --size 10000  --scenario delete_10k
python main.py --system cassandra --operation query   --dataset data\dataset_10000.json  --size 10000  --scenario query_10k
python main.py --system cassandra --operation insert  --dataset data\dataset_100000.json --size 100000 --scenario insert_100k
python main.py --system cassandra --operation read    --dataset data\dataset_100000.json --size 100000 --scenario read_100k
python main.py --system cassandra --operation read    --dataset data\dataset_10000.json  --size 10000  --scenario read_10k_c10 --concurrency 10

REM ── Spark ────────────────────────────────────────────────────
echo [4/6] Benchmarking Spark (local mode)...
python main.py --system spark --operation insert  --dataset data\dataset_10000.csv  --size 10000  --scenario insert_10k
python main.py --system spark --operation read    --dataset data\dataset_10000.csv  --size 10000  --scenario read_10k
python main.py --system spark --operation update  --dataset data\dataset_10000.csv  --size 10000  --scenario update_10k
python main.py --system spark --operation query   --dataset data\dataset_10000.csv  --size 10000  --scenario query_10k
python main.py --system spark --operation delete  --dataset data\dataset_10000.csv  --size 10000  --scenario delete_10k
python main.py --system spark --operation insert  --dataset data\dataset_100000.csv --size 100000 --scenario insert_100k
python main.py --system spark --operation read    --dataset data\dataset_100000.csv --size 100000 --scenario read_100k
python main.py --system spark --operation update  --dataset data\dataset_100000.csv --size 100000 --scenario update_100k
python main.py --system spark --operation query   --dataset data\dataset_100000.csv --size 100000 --scenario query_100k
python main.py --system spark --operation delete  --dataset data\dataset_100000.csv --size 100000 --scenario delete_100k
python main.py --system spark --operation insert  --dataset data\dataset_10000.csv  --size 10000  --scenario insert_10k_preseed
python main.py --system spark --operation read    --dataset data\dataset_10000.csv  --size 10000  --scenario read_10k_c5 --concurrency 5

REM ── Hadoop ───────────────────────────────────────────────────
echo [5/6] Benchmarking Hadoop (HDFS)...
docker exec psb_namenode hdfs dfsadmin -safemode wait 2>nul
python main.py --system hadoop --operation insert  --dataset data\dataset_10000.json  --size 10000  --scenario insert_10k
python main.py --system hadoop --operation read    --dataset data\dataset_10000.json  --size 10000  --scenario read_10k
python main.py --system hadoop --operation update  --dataset data\dataset_10000.json  --size 10000  --scenario update_10k
python main.py --system hadoop --operation query   --dataset data\dataset_10000.json  --size 10000  --scenario query_10k
python main.py --system hadoop --operation delete  --dataset data\dataset_10000.json  --size 10000  --scenario delete_10k
python main.py --system hadoop --operation insert  --dataset data\dataset_100000.json --size 100000 --scenario insert_100k
python main.py --system hadoop --operation read    --dataset data\dataset_100000.json --size 100000 --scenario read_100k
python main.py --system hadoop --operation update  --dataset data\dataset_100000.json --size 100000 --scenario update_100k
python main.py --system hadoop --operation query   --dataset data\dataset_100000.json --size 100000 --scenario query_100k
python main.py --system hadoop --operation delete  --dataset data\dataset_100000.json --size 100000 --scenario delete_100k
python main.py --system hadoop --operation insert  --dataset data\dataset_10000.json  --size 10000  --scenario insert_10k_preseed
python main.py --system hadoop --operation read    --dataset data\dataset_10000.json  --size 10000  --scenario read_10k_c5 --concurrency 5

REM ── Hive ─────────────────────────────────────────────────────
echo [6/6] Benchmarking Hive...
python main.py --system hive --operation insert  --dataset data\dataset_10000.csv  --size 10000  --scenario insert_10k
python main.py --system hive --operation read    --dataset data\dataset_10000.csv  --size 10000  --scenario read_10k
python main.py --system hive --operation update  --dataset data\dataset_10000.csv  --size 10000  --scenario update_10k
python main.py --system hive --operation query   --dataset data\dataset_10000.csv  --size 10000  --scenario query_10k
python main.py --system hive --operation delete  --dataset data\dataset_10000.csv  --size 10000  --scenario delete_10k
python main.py --system hive --operation insert  --dataset data\dataset_100000.csv --size 100000 --scenario insert_100k
python main.py --system hive --operation read    --dataset data\dataset_100000.csv --size 100000 --scenario read_100k
python main.py --system hive --operation update  --dataset data\dataset_100000.csv --size 100000 --scenario update_100k
python main.py --system hive --operation query   --dataset data\dataset_100000.csv --size 100000 --scenario query_100k
python main.py --system hive --operation delete  --dataset data\dataset_100000.csv --size 100000 --scenario delete_100k
python main.py --system hive --operation insert  --dataset data\dataset_10000.csv  --size 10000  --scenario insert_10k_preseed
python main.py --system hive --operation read    --dataset data\dataset_10000.csv  --size 10000  --scenario read_10k_c5 --concurrency 5

echo.
echo ============================================================
echo  All benchmarks complete! Launch dashboard:
echo  streamlit run dashboard\app.py
echo ============================================================
pause