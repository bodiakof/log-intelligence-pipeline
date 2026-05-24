import duckdb

from log_intelligence.config import config


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Returns a persistent DuckDB connection.
    """
    conn = duckdb.connect(str(config.db_path))
    return conn


def run_sql_file(conn, path: Path):
    """
    Execute all SQL statements from a .sql file using the provided database connection.

    Args:
        conn: Active database connection object with an execute() method.
        path (Path): Path to the SQL file.
    """
    with open(path, "r", encoding="utf-8") as f:
        conn.execute(f.read())
