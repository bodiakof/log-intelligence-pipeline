"""
Executes metrics layer SQL.

This generates analytical views used for dashboards and monitoring.
"""

from pathlib import Path

from log_intelligence.db import get_connection, run_sql_file


def build_metrics() -> None:
    """
    Builds analytical metric views in DuckDB.
    """
    conn = get_connection()

    run_sql_file(conn, Path("sql/030_metrics.sql"))

    conn.close()
