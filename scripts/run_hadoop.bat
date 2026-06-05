@echo off
echo ============================================================
echo  PolyStoreBench -- Hadoop Benchmarks
echo ============================================================
echo  Requires: psb_namenode container to be running and healthy.
echo ============================================================

echo [Hadoop] Waiting for namenode to leave safemode...
docker exec psb_namenode hdfs dfsadmin -safemode wait 2>nul

echo.
echo [Hadoop] === 10k dataset ===
echo [Hadoop] insert 10k...
python main.py --system hadoop --operation insert --dataset data\dataset_10000.json --size 10000 --scenario insert_10k
echo [Hadoop] read 10k...
python main.py --system hadoop --operation read   --dataset data\dataset_10000.json --size 10000 --scenario read_10k
echo [Hadoop] update 10k...
python main.py --system hadoop --operation update --dataset data\dataset_10000.json --size 10000 --scenario update_10k
echo [Hadoop] query 10k...
python main.py --system hadoop --operation query  --dataset data\dataset_10000.json --size 10000 --scenario query_10k
echo [Hadoop] delete 10k...
python main.py --system hadoop --operation delete --dataset data\dataset_10000.json --size 10000 --scenario delete_10k

echo.
echo [Hadoop] === 100k dataset ===
echo [Hadoop] insert 100k...
python main.py --system hadoop --operation insert --dataset data\dataset_100000.json --size 100000 --scenario insert_100k
echo [Hadoop] read 100k...
python main.py --system hadoop --operation read   --dataset data\dataset_100000.json --size 100000 --scenario read_100k
echo [Hadoop] update 100k...
python main.py --system hadoop --operation update --dataset data\dataset_100000.json --size 100000 --scenario update_100k
echo [Hadoop] query 100k...
python main.py --system hadoop --operation query  --dataset data\dataset_100000.json --size 100000 --scenario query_100k
echo [Hadoop] delete 100k...
python main.py --system hadoop --operation delete --dataset data\dataset_100000.json --size 100000 --scenario delete_100k

echo.
echo [Hadoop] === Concurrency test ===
echo [Hadoop] insert 10k (re-seed for concurrency)...
python main.py --system hadoop --operation insert --dataset data\dataset_10000.json --size 10000 --scenario insert_10k_preseed
echo [Hadoop] read 10k concurrency=5...
python main.py --system hadoop --operation read   --dataset data\dataset_10000.json --size 10000 --scenario read_10k_c5 --concurrency 5

echo.
echo [Hadoop] Done!
