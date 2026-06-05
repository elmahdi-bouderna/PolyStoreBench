import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

STORAGE_DIR = Path(__file__).parent
SQLITE_PATH = STORAGE_DIR / "results.db"


class BenchmarkResult(Base):
    __tablename__ = "benchmark_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    system_name = Column(String)
    scenario_name = Column(String)
    operation = Column(String)
    dataset_size = Column(Integer)

    execution_time_sec = Column(Float)
    latency_avg_ms = Column(Float)
    latency_min_ms = Column(Float)
    latency_max_ms = Column(Float)
    throughput_ops_sec = Column(Float)

    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)

    concurrency_level = Column(Integer)
    run_number = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


def _build_engine():
    """Try PostgreSQL first; fall back to SQLite for offline / demo use."""
    pg_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://psb_user:psb_pass@127.0.0.1:5432/polystorebench"
    )
    try:
        eng = create_engine(pg_url, pool_pre_ping=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[DB] Connected to PostgreSQL")
        return eng
    except Exception as exc:
        print(f"[DB] PostgreSQL unavailable ({exc}). Using SQLite: {SQLITE_PATH}")
        return create_engine(
            f"sqlite:///{SQLITE_PATH}",
            connect_args={"check_same_thread": False}
        )


engine = _build_engine()
Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def save_result(result_data: dict):
    init_db()  # ensure table exists
    session = Session()
    try:
        result = BenchmarkResult(**result_data)
        session.add(result)
        session.commit()
    except Exception as exc:
        session.rollback()
        print(f"[DB] Failed to save result: {exc}")
        raise
    finally:
        session.close()


def load_results() -> list[dict]:
    """Return all benchmark results as a list of dicts."""
    init_db()
    session = Session()
    try:
        rows = session.query(BenchmarkResult).all()
        return [
            {c.name: getattr(r, c.name) for c in BenchmarkResult.__table__.columns}
            for r in rows
        ]
    finally:
        session.close()