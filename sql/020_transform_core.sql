CREATE TABLE IF NOT EXISTS devices AS
SELECT DISTINCT
    JSON_EXTRACT_STRING(log_payload, '$.device_id') AS device_id,
    JSON_EXTRACT_STRING(log_payload, '$.payload.model') AS model,
    JSON_EXTRACT_STRING(log_payload, '$.payload.firmware_version') AS firmware_version
FROM ingested_logs
WHERE log_payload IS NOT NULL;

CREATE TABLE IF NOT EXISTS events AS
SELECT
    log_id AS event_id,
    JSON_EXTRACT_STRING(log_payload, '$.device_id') AS device_id,
    JSON_EXTRACT_STRING(log_payload, '$.timestamp') AS event_timestamp,
    JSON_EXTRACT_STRING(log_payload, '$.event_type') AS event_type,
    JSON_EXTRACT_STRING(log_payload, '$.message') AS message,
    JSON_EXTRACT(log_payload, '$.payload') AS payload
FROM ingested_logs;

CREATE TABLE IF NOT EXISTS errors AS
SELECT
    event_id,
    device_id,
    event_timestamp,
    JSON_EXTRACT_STRING(payload, '$.error_code') AS error_code,
    message
FROM events
WHERE event_type = 'error';