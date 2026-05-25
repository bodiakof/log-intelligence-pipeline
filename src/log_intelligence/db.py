"""
DuckDB connection and SQL execution utilities.

These helpers keep database access consistent across ingestion,
transformation, metrics, and dashboard workflows.
"""

from pathlib import Path

import duckdb

from log_intelligence.config import config


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Creates and returns a DuckDB connection.
    """
    return duckdb.connect(str(config.db_path))


def run_sql_file(conn, path: Path) -> None:
    """
    Execute all SQL statements from a SQL file using the provided database connection.

    Args:
        conn: Active DuckDB connection.
        path (Path): Path to the SQL file.
    """
    with open(path, encoding="utf-8") as f:
        conn.execute(f.read())
