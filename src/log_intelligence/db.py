import duckdb

from log_intelligence.config import config


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Returns a persistent DuckDB connection.
    """
    conn = duckdb.connect(str(config.db_path))
    return conn


def init_db(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Creates base schema for raw ingestion.
    """
    conn.execute("""
    CREATE TABLE IF NOT EXISTS raw_logs (
        raw_id VARCHAR,
        ingested_at TIMESTAMP,
        source_file VARCHAR,
        raw_json VARCHAR,
        record_hash VARCHAR,
        is_valid BOOLEAN,
        rejection_reason VARCHAR
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_runs (
        run_id VARCHAR,
        started_at TIMESTAMP,
        finished_at TIMESTAMP,
        records_seen INTEGER,
        valid_records INTEGER,
        invalid_records INTEGER,
        duplicate_records INTEGER
    );
    """)