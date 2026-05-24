CREATE TABLE IF NOT EXISTS ingested_logs (
        log_id VARCHAR,
        ingested_at TIMESTAMP NOT NULL,
        source_file VARCHAR NOT NULL,
        log_payload VARCHAR NOT NULL,
        record_hash VARCHAR
    );
    
CREATE TABLE IF NOT EXISTS pipeline_runs (
        run_id VARCHAR NOT NULL,
        started_at TIMESTAMP NOT NULL,
        finished_at TIMESTAMP NOT NULL,

        records_seen INTEGER NOT NULL,
        valid_records INTEGER NOT NULL,
        invalid_records INTEGER NOT NULL,
        duplicate_records INTEGER NOT NULL
    );