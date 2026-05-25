-- Ensure no null device_ids
SELECT *
FROM events
WHERE device_id IS NULL;


-- Ensure no duplicate event IDs
SELECT event_id, COUNT(*)
FROM events
GROUP BY event_id
HAVING COUNT(*) > 1;


-- Check orphan errors
SELECT e.*
FROM errors e
LEFT JOIN events ev ON e.event_id = ev.event_id
WHERE ev.event_id IS NULL;


-- Validate event types
SELECT DISTINCT event_type FROM events;
