import json
import uuid
from datetime import datetime, UTC
from pathlib import Path

from log_intelligence.db import get_connection, run_sql_file
from log_intelligence.validation import validate, compute_hash
from log_intelligence.config import config


def ingest(file_path: Path) -> None:
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

    with open(file_path, "r", encoding="utf-8") as f, open(rejected_path, "w") as rejected:

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
                INSERT INTO raw_logs VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(record.get("event_id")),
                datetime.now(UTC),
                str(file_path),
                json.dumps(record),
                record_hash,
                True,
                None
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
