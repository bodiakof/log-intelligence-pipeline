"""
Main orchestration entry point for the Log Intelligence Pipeline.

This script runs the full end-to-end workflow:

1. Generate synthetic device logs
2. Ingest logs into DuckDB (validation + deduplication)
3. Execute schema creation (SQL)
4. Run transformations (raw → analytical models)
5. Build metrics views
6. Run data quality checks
7. Run anomaly detection layer

This simulates a production-grade data pipeline in a local environment.
"""

from pathlib import Path

from log_intelligence.config import config
from log_intelligence.db import get_connection, run_sql_file
from log_intelligence.generator import generate_logs
from log_intelligence.ingestion import ingest


def run_pipeline(records: int = 1000) -> None:
    """
    Executes full pipeline end-to-end.

    Args:
        records: number of synthetic logs to generate
    """

    print("\n=== LOG INTELLIGENCE PIPELINE STARTED ===\n")

    # Step 1: Generate logs
    print("[1/6] Generating logs...")
    generate_logs(
        output_path=config.raw_dir / "device_logs.jsonl",
        record_count=records,
        invalid_ratio=0.05,
        duplicate_ratio=0.03,
        device_count=25,
        seed=42,
    )

    # Step 2: Ingest logs
    print("[2/6] Ingesting logs...")
    ingest(config.raw_dir / "device_logs.jsonl")

    conn = get_connection()

    # Step 3: Schema
    print("[3/6] Creating schema...")
    run_sql_file(conn, Path("sql/001_schema.sql"))

    # Step 4: Transformations
    print("[4/6] Running transformations...")
    run_sql_file(conn, Path("sql/020_transform_core.sql"))

    # Step 5: Metrics
    print("[5/6] Building metrics...")
    run_sql_file(conn, Path("sql/030_metrics.sql"))

    # Step 6: Quality checks + anomaly detection
    print("[6/6] Running quality checks...")
    run_sql_file(conn, Path("sql/040_quality_checks.sql"))

    print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===\n")

    conn.close()


if __name__ == "__main__":
    run_pipeline(records=1000)
