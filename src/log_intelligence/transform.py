"""
Executes transformation layer SQL.

This module isolates transformation logic from orchestration.
"""

from pathlib import Path

from log_intelligence.db import get_connection, run_sql_file


def run_transformations() -> None:
    """
    Executes core transformation SQL script.
    """
    conn = get_connection()

    run_sql_file(conn, Path("sql/020_transform_core.sql"))

    conn.close()
