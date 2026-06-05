@echo off
echo ============================================================
echo  PolyStoreBench -- Spark Benchmarks
echo ============================================================
echo  Requires: Java 17+ on PATH (or JAVA_HOME set below).
echo  Spark runs locally - no Docker required.
echo ============================================================

REM --- Set JAVA_HOME to JDK 17 if available ---
if exist "C:\Program Files\Java\jdk-17\bin\java.exe" (
    set JAVA_HOME=C:\Program Files\Java\jdk-17
    set PATH=%JAVA_HOME%\bin;%PATH%
) else if exist "C:\Program Files\Java\jdk-21\bin\java.exe" (
    set JAVA_HOME=C:\Program Files\Java\jdk-21
    set PATH=%JAVA_HOME%\bin;%PATH%
) else if exist "C:\Program Files\Java\jdk-21.0.10\bin\java.exe" (
    set JAVA_HOME=C:\Program Files\Java\jdk-21.0.10
    set PATH=%JAVA_HOME%\bin;%PATH%
)

echo.
echo [Spark] === 10k dataset ===
echo [Spark] insert 10k...
python main.py --system spark --operation insert --dataset data\dataset_10000.csv  --size 10000  --scenario insert_10k
echo [Spark] read 10k...
python main.py --system spark --operation read   --dataset data\dataset_10000.csv  --size 10000  --scenario read_10k
echo [Spark] update 10k...
python main.py --system spark --operation update --dataset data\dataset_10000.csv  --size 10000  --scenario update_10k
echo [Spark] query 10k...
python main.py --system spark --operation query  --dataset data\dataset_10000.csv  --size 10000  --scenario query_10k
echo [Spark] delete 10k...
python main.py --system spark --operation delete --dataset data\dataset_10000.csv  --size 10000  --scenario delete_10k

echo.
echo [Spark] === 100k dataset ===
echo [Spark] insert 100k...
python main.py --system spark --operation insert --dataset data\dataset_100000.csv --size 100000 --scenario insert_100k
echo [Spark] read 100k...
python main.py --system spark --operation read   --dataset data\dataset_100000.csv --size 100000 --scenario read_100k
echo [Spark] update 100k...
python main.py --system spark --operation update --dataset data\dataset_100000.csv --size 100000 --scenario update_100k
echo [Spark] query 100k...
python main.py --system spark --operation query  --dataset data\dataset_100000.csv --size 100000 --scenario query_100k
echo [Spark] delete 100k...
python main.py --system spark --operation delete --dataset data\dataset_100000.csv --size 100000 --scenario delete_100k

echo.
echo [Spark] === Concurrency test ===
echo [Spark] insert 10k (re-seed for concurrency)...
python main.py --system spark --operation insert --dataset data\dataset_10000.csv --size 10000 --scenario insert_10k_preseed
echo [Spark] read 10k concurrency=5...
python main.py --system spark --operation read   --dataset data\dataset_10000.csv --size 10000 --scenario read_10k_c5 --concurrency 5

echo.
echo [Spark] Done!
