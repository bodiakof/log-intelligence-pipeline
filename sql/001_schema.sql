CREATE TABLE IF NOT EXISTS raw_logs (
        raw_id VARCHAR,
        ingested_at TIMESTAMP NOT NULL,
        source_file VARCHAR NOT NULL,
        raw_json VARCHAR NOT NULL,
        record_hash VARCHAR UNIQUE,
        is_valid BOOLEAN NOT NULL,
        rejection_reason VARCHAR
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