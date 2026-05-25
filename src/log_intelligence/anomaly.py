"""
Anomaly detection layer.

Uses SQL-based spike detection from metrics layer.
"""

from pathlib import Path

from log_intelligence.db import get_connection, run_sql_file


def run_anomaly_detection() -> None:
    """
    Executes anomaly detection logic using SQL views.
    """
    conn = get_connection()

    run_sql_file(conn, Path("sql/030_metrics.sql"))

    result = conn.execute("""
        SELECT *
        FROM v_error_spikes
        WHERE anomaly_flag = 'SPIKE'
    """).fetchall()

    print("\n=== ANOMALIES DETECTED ===")
    for row in result:
        print(row)

    conn.close()
