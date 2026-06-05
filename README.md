# PolyStoreBench 🚀

> **A Unified Benchmarking Framework for Big Data and NoSQL Systems**

PolyStoreBench is an open-source platform for comparing the performance of multiple Big Data and NoSQL technologies — including **Hadoop**, **Spark**, **Hive**, **MongoDB**, **Cassandra**, and **Redis** — across a wide variety of workloads. It provides a reusable, extensible tool to evaluate, visualize, and analyze key performance metrics such as execution time, latency, throughput, scalability, and resource utilization, helping researchers and practitioners choose the most suitable data architecture for their needs.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Supported Systems](#supported-systems)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Running Benchmarks](#running-benchmarks)
- [Dashboard](#dashboard)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Authors](#authors)

---

## Overview

Ce projet consiste à développer une plateforme unifiée de benchmarking permettant de comparer les performances de plusieurs technologies Big Data et NoSQL sur différents types de charges de travail. L'objectif est de fournir un outil réutilisable capable d'évaluer, visualiser et analyser des critères comme le **temps d'exécution**, la **latence**, le **débit**, la **scalabilité** et l'**utilisation des ressources**.

---

## ✨ Features

- 🔌 **Pluggable Adapter Architecture** — Each database system has its own adapter implementing a common `BaseAdapter` interface (`insert`, `read`, `update`, `delete`, `query`).
- ⚙️ **Benchmark Engine** — A centralized `BenchmarkRunner` orchestrates workloads, collects timing data, and measures system resource usage.
- 📊 **Interactive Dashboard** — A rich Streamlit dashboard with real-time charts: radar charts, heatmaps, box plots, scalability curves, and resource usage breakdowns.
- 🗄️ **Dual Storage Backend** — Results are persisted in **PostgreSQL** (primary) or **SQLite** (fallback), with automatic detection.
- 🐳 **Docker-First Setup** — All required services (MongoDB, Redis, Cassandra, PostgreSQL, Hadoop, Hive) are configured in a single `docker-compose.yml`.
- 📈 **Scalability Testing** — Run benchmarks at different dataset sizes (10K, 100K rows) and concurrency levels to measure how systems scale.
- 🖥️ **System Monitoring** — CPU, memory, and disk usage are captured for every benchmark run using `psutil`.
- 📁 **Upload & Benchmark** — Upload any CSV or JSON dataset directly from the dashboard and run benchmarks without touching the CLI.
- 📤 **Export Results** — Download benchmark results as CSV for further offline analysis.

---

## 🗄️ Supported Systems

| System        | Version  | Type           | Operations Supported              |
|---------------|----------|----------------|-----------------------------------|
| **MongoDB**   | 7        | Document Store | Insert, Read, Update, Delete      |
| **Redis**     | 7        | Key-Value Store| Insert, Read, Update, Delete      |
| **Cassandra** | 4.1      | Wide-Column    | Insert, Read, Update, Delete      |
| **Apache Spark** | Latest | Processing Engine | Insert, Read, Query, Write     |
| **Apache Hive** | 2.3.2  | Data Warehouse | Insert, Read, Query               |
| **Apache Hadoop** | 3.2.1 | Distributed FS | Insert, Read, Query, Write       |

---

## 🏗️ Architecture

```
polystorebench/
│
├── main.py                  # CLI entry point
│
├── adapters/                # Database adapters (one per system)
│   ├── base_adapter.py      # Abstract base class
│   ├── mongodb_adapter.py
│   ├── redis_adapter.py
│   ├── cassandra_adapter.py
│   ├── spark_adapter.py
│   ├── hive_adapter.py
│   └── hadoop_adapter.py
│
├── engine/
│   └── runner.py            # BenchmarkRunner: orchestrates runs, captures metrics
│
├── monitoring/
│   └── collector.py         # MetricsCollector: CPU, memory, disk via psutil
│
├── storage/
│   └── results_db.py        # Saves results to PostgreSQL or SQLite
│
├── dashboard/
│   └── app.py               # Streamlit dashboard (8 tabs of charts)
│
├── config/
│   ├── systems.yaml         # DB connection settings
│   └── workloads.yaml       # Workload definitions
│
├── scripts/
│   ├── init_db.py           # Initialize the results database
│   ├── run_all.bat          # Run all benchmarks (Windows)
│   ├── run_fast.bat         # Quick benchmark suite
│   ├── run_cassandra.bat
│   ├── run_hadoop.bat
│   ├── run_hive.bat
│   └── run_spark.bat
│
├── datasets/
│   └── generator.py         # Synthetic dataset generator
│
└── docker-compose.yml       # All services in one file
```

**Data Flow:**

```
  CLI / Dashboard
       │
       ▼
  BenchmarkRunner  ──────►  Adapter (MongoDB / Redis / Cassandra / Spark / Hive / Hadoop)
       │                         │
       │◄────── timing ──────────┘
       │
  MetricsCollector (CPU / Memory / Disk)
       │
  Results DB (PostgreSQL or SQLite)
       │
  Streamlit Dashboard (live charts)
```

---

## 📦 Prerequisites

- **Python** 3.10+
- **Docker** & **Docker Compose**
- **Git**

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/elmahdi-bouderna/PolyStoreBench.git
cd PolyStoreBench
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start all Docker services

```bash
docker compose up -d
```

> ⏳ Wait ~60 seconds for all services (especially Cassandra and Hive) to become healthy.

### 5. Initialize the results database

```bash
python scripts/init_db.py
```

---

## 🚀 Quick Start

Run a full benchmark suite (all systems, all operations):

```bash
# Windows
scripts\run_all.bat

# Or run a faster subset
scripts\run_fast.bat
```

Then launch the dashboard:

```bash
streamlit run dashboard/app.py
```

Open your browser at **http://localhost:8501**.

---

## ⚡ Running Benchmarks

### CLI Usage

```bash
python main.py \
  --system   <system>    \   # mongodb | redis | cassandra | spark | hive | hadoop
  --operation <op>        \   # insert | read | update | delete | query | write
  --dataset  <path>       \   # path to CSV or JSON dataset file
  --size     <int>        \   # number of rows in the dataset
  --scenario <name>       \   # label for this benchmark run
  --concurrency <int>         # (optional) number of concurrent threads, default=1
```

**Examples:**

```bash
# Insert 10,000 records into MongoDB
python main.py --system mongodb --operation insert --dataset data/sample.csv --size 10000 --scenario test_run

# Read benchmark with 10 concurrent threads on Redis
python main.py --system redis --operation read --dataset data/sample.csv --size 10000 --scenario concurrent_test --concurrency 10

# Run an analytical query on Hive
python main.py --system hive --operation query --dataset data/sample.csv --size 100000 --scenario hive_analytics
```

### Predefined Workloads (`config/workloads.yaml`)

| Workload Name         | Operation | Dataset Size | Concurrency |
|-----------------------|-----------|--------------|-------------|
| `insert_10k`          | insert    | 10,000       | 1           |
| `insert_100k`         | insert    | 100,000      | 1           |
| `read_10k`            | read      | 10,000       | 1           |
| `read_100k`           | read      | 100,000      | 1           |
| `read_10k_concurrent` | read      | 10,000       | 10          |

### Per-System Scripts (Windows)

```bash
scripts\run_cassandra.bat
scripts\run_hadoop.bat
scripts\run_hive.bat
scripts\run_spark.bat
```

---

## 📊 Dashboard

Launch with:

```bash
streamlit run dashboard/app.py
```

The dashboard features **8 tabs**:

| Tab | Content |
|-----|---------|
| **Overview** | Multi-metric radar chart, performance heatmap (system × operation), summary statistics table |
| **Execution Time** | Grouped bar charts, box plots, average execution time per system |
| **Latency** | Latency distribution, min/avg/max latency grouped bars, latency by operation |
| **Throughput** | Average ops/sec per system, latency vs throughput bubble chart |
| **Scalability** | Execution time, throughput, and latency vs dataset size (line charts) |
| **Resources** | CPU, memory, disk usage grouped bars, CPU vs memory scatter plot, stacked utilization |
| **Raw Data** | Full results table with filters + CSV export |
| **Run Benchmark** | Upload a dataset, choose systems & operations, run benchmarks directly from the browser |

**Sidebar** provides live filters by scenario, system, operation, and dataset size. A **Service Status** panel shows which Docker services are online/offline.

---

## ⚙️ Configuration

### `config/systems.yaml`

Edit connection settings for each system:

```yaml
mongodb:
  host: localhost
  port: 27017        # Note: Docker exposes on 27018
  username: admin
  password: admin123
  database: polystorebench

redis:
  host: localhost
  port: 6379

cassandra:
  host: localhost
  port: 9042
  keyspace: polystorebench

postgres:
  host: localhost
  port: 5432
  username: psb_user
  password: psb_pass
  database: polystorebench

hadoop:
  hdfs_url: hdfs://127.0.0.1:8020

hive:
  host: 127.0.0.1
  port: 10000
  username: hive
  database: default
```

### Environment Variables

| Variable       | Default                                                 | Description                        |
|----------------|---------------------------------------------------------|------------------------------------|
| `DATABASE_URL` | `postgresql://psb_user:psb_pass@127.0.0.1:5432/polystorebench` | PostgreSQL connection URL |

---

## 📊 Metrics Collected

Every benchmark run captures:

| Metric                | Description                              |
|-----------------------|------------------------------------------|
| `execution_time_sec`  | Total wall-clock time for the operation  |
| `latency_avg_ms`      | Average per-operation latency            |
| `latency_min_ms`      | Minimum per-operation latency            |
| `latency_max_ms`      | Maximum per-operation latency            |
| `throughput_ops_sec`  | Operations per second                    |
| `cpu_percent`         | CPU utilization during the run           |
| `memory_percent`      | RAM utilization during the run           |
| `disk_percent`        | Disk utilization during the run          |
| `concurrency_level`   | Number of concurrent threads used        |
| `dataset_size`        | Number of records processed              |
| `run_number`          | Run repetition index                     |

---

## 🐳 Docker Services

| Service            | Container Name    | Port(s)          | Description                  |
|--------------------|-------------------|------------------|------------------------------|
| MongoDB            | `psb_mongodb`     | `27018:27017`    | Document store               |
| Redis              | `psb_redis`       | `6379:6379`      | Key-value store              |
| PostgreSQL         | `psb_postgres`    | `5432:5432`      | Results database             |
| Cassandra          | `psb_cassandra`   | `9042:9042`      | Wide-column store            |
| Hadoop NameNode    | `psb_namenode`    | `9870`, `8020`   | HDFS NameNode UI + RPC       |
| Hadoop DataNode    | `psb_datanode`    | `9864`           | HDFS DataNode                |
| Hive Server        | `psb_hive`        | `10000`, `10002` | HiveServer2 + Web UI         |
| Hive Metastore DB  | `psb_hive_postgres` | `5433:5432`   | Hive schema store (pg 9.5)   |

---

## 👥 Authors

| Name | Role |
|------|------|
| **EL MAHDI BOUDERNA** | Lead Developer |
| **KAWTER ALOUANE** | Developer |
| **YOUSSEF NAFAE** | Developer |

---

## 📄 License

This project was developed as part of an academic Big Data systems course. All rights reserved by the authors.

---

<div align="center">
  <sub>Built with ❤️ using Python · Streamlit · Docker · Plotly</sub>
</div>