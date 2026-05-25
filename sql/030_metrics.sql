CREATE OR REPLACE VIEW v_event_volume_hourly AS
SELECT
    DATE_TRUNC('hour', CAST(event_timestamp AS TIMESTAMP)) AS hour,
    COUNT(*) AS total_events
FROM events
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW v_error_rate_per_device AS
SELECT
    e.device_id,
    COUNT(*) AS total_events,
    SUM(CASE WHEN e.event_type = 'error' THEN 1 ELSE 0 END) AS error_events,
    ROUND(
        SUM(CASE WHEN e.event_type = 'error' THEN 1 ELSE 0 END)::DOUBLE
        / COUNT(*),
        4
    ) AS error_rate
FROM events e
GROUP BY e.device_id;

CREATE OR REPLACE VIEW v_top_error_codes AS
SELECT
    error_code,
    COUNT(*) AS occurrences
FROM errors
GROUP BY error_code
ORDER BY occurrences DESC;

CREATE OR REPLACE VIEW v_device_activity AS
SELECT
    device_id,
    MAX(CAST(event_timestamp AS TIMESTAMP)) AS last_seen,
    CASE
        WHEN MAX(CAST(event_timestamp AS TIMESTAMP)) > NOW() - INTERVAL 1 DAY
        THEN 'active'
        ELSE 'inactive'
    END AS status
FROM events
GROUP BY device_id;

CREATE OR REPLACE VIEW v_failure_trends AS
SELECT
    DATE_TRUNC('hour', CAST(event_timestamp AS TIMESTAMP)) AS hour,
    COUNT(*) AS error_count
FROM events
WHERE event_type = 'error'
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW v_mtbe_per_device AS
WITH ordered_errors AS (
    SELECT
        device_id,
        CAST(event_timestamp AS TIMESTAMP) AS ts,
        LAG(CAST(event_timestamp AS TIMESTAMP))
            OVER (PARTITION BY device_id ORDER BY event_timestamp) AS prev_ts
    FROM errors
)
SELECT
    device_id,
    AVG(EXTRACT(EPOCH FROM (ts - prev_ts))) AS mtbe_seconds
FROM ordered_errors
WHERE prev_ts IS NOT NULL
GROUP BY device_id;

CREATE OR REPLACE VIEW v_error_spikes AS
WITH hourly AS (
    SELECT
        DATE_TRUNC('hour', CAST(event_timestamp AS TIMESTAMP)) AS hour,
        COUNT(*) AS error_count
    FROM events
    WHERE event_type = 'error'
    GROUP BY 1
),
stats AS (
    SELECT
        hour,
        error_count,
        AVG(error_count) OVER (
            ORDER BY hour
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_avg
    FROM hourly
)
SELECT
    hour,
    error_count,
    rolling_avg,
    CASE
        WHEN error_count > rolling_avg * 2 THEN 'SPIKE'
        ELSE 'NORMAL'
    END AS anomaly_flag
FROM stats;
