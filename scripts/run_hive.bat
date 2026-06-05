@echo off
echo ============================================================
echo  PolyStoreBench -- Hive Benchmarks
echo ============================================================
echo  Requires: psb_namenode, psb_datanode, psb_hive containers
echo  to be running and healthy. Hive uses CSV datasets.
echo ============================================================

echo.
echo [Hive] === 10k dataset ===
echo [Hive] insert 10k...
python main.py --system hive --operation insert --dataset data\dataset_10000.csv  --size 10000  --scenario insert_10k
echo [Hive] read 10k...
python main.py --system hive --operation read   --dataset data\dataset_10000.csv  --size 10000  --scenario read_10k
echo [Hive] update 10k...
python main.py --system hive --operation update --dataset data\dataset_10000.csv  --size 10000  --scenario update_10k
echo [Hive] query 10k...
python main.py --system hive --operation query  --dataset data\dataset_10000.csv  --size 10000  --scenario query_10k
echo [Hive] delete 10k...
python main.py --system hive --operation delete --dataset data\dataset_10000.csv  --size 10000  --scenario delete_10k

echo.
echo [Hive] === 100k dataset ===
echo [Hive] insert 100k...
python main.py --system hive --operation insert --dataset data\dataset_100000.csv --size 100000 --scenario insert_100k
echo [Hive] read 100k...
python main.py --system hive --operation read   --dataset data\dataset_100000.csv --size 100000 --scenario read_100k
echo [Hive] update 100k...
python main.py --system hive --operation update --dataset data\dataset_100000.csv --size 100000 --scenario update_100k
echo [Hive] query 100k...
python main.py --system hive --operation query  --dataset data\dataset_100000.csv --size 100000 --scenario query_100k
echo [Hive] delete 100k...
python main.py --system hive --operation delete --dataset data\dataset_100000.csv --size 100000 --scenario delete_100k

echo.
echo [Hive] === Concurrency test ===
echo [Hive] insert 10k (re-seed for concurrency)...
python main.py --system hive --operation insert --dataset data\dataset_10000.csv --size 10000 --scenario insert_10k_preseed
echo [Hive] read 10k concurrency=5...
python main.py --system hive --operation read   --dataset data\dataset_10000.csv --size 10000 --scenario read_10k_c5 --concurrency 5

echo.
echo [Hive] Done!
