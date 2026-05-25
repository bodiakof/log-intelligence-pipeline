"""
Ingestion layer for raw device logs.

Reads JSONL records, validates required fields, skips duplicate records, writes
rejected records for auditability, and tracks pipeline run statistics.
"""

import argparse
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from log_intelligence.config import config
from log_intelligence.db import get_connection, run_sql_file
from log_intelligence.validation import compute_hash, validate


def ingest(file_path: Path) -> None:
    """
    Ingest a JSONL log file into DuckDB.

    Valid records are inserted into the raw table, invalid records are written
    to the rejected dataset, and duplicate records are counted but skipped.
    """
    conn = get_connection()
    run_sql_file(conn, "sql/001_schema.sql")

    run_id = str(uuid.uuid4())
    started_at = datetime.now(UTC)

    seen_hashes = set()

    stats = {
        "seen": 0,
        "valid": 0,
        "invalid": 0,
        "duplicates": 0,
    }

    rejected_path = config.rejected_dir / f"rejected_{run_id}.jsonl"

    with open(file_path, encoding="utf-8") as f, open(rejected_path, "w") as rejected:

        for line in f:
            stats["seen"] += 1
            line = line.strip()

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                stats["invalid"] += 1
                rejected.write(json.dumps({
                    "reason": "malformed_json",
                    "raw": line
                }) + "\n")
                continue

            is_valid, reason = validate(record)
            record_hash = compute_hash(record) if isinstance(record, dict) else None

            if not is_valid:
                stats["invalid"] += 1
                rejected.write(json.dumps({
                    "reason": reason,
                    "record": record
                }) + "\n")
                continue

            if record_hash in seen_hashes:
                stats["duplicates"] += 1
                continue

            seen_hashes.add(record_hash)

            conn.execute("""
                INSERT INTO ingested_logs (
                    log_id,
                    ingested_at,
                    source_file,
                    log_payload,
                    record_hash
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(record.get("event_id")),
                datetime.now(UTC),
                str(file_path),
                json.dumps(record),
                record_hash
            ))

            stats["valid"] += 1

    finished_at = datetime.now(UTC)

    conn.execute("""
        INSERT INTO pipeline_runs VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        started_at,
        finished_at,
        stats["seen"],
        stats["valid"],
        stats["invalid"],
        stats["duplicates"],
    ))

    conn.close()

    print("INGESTION COMPLETE")
    print(stats)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path")

    args = parser.parse_args()

    ingest(Path(args.file_path))
