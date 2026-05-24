import json
import hashlib
from datetime import datetime
from typing import Any


VALID_EVENT_TYPES = {"info", "warning", "error"}


def compute_hash(record: dict[str, Any]) -> str:
    normalized = json.dumps(record, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()


def validate(record: Any) -> tuple[bool, str | None]:
    """
    Validate a log record.
    Returns: (is_valid, reason_if_invalid)
    """

    if not isinstance(record, dict):
        return False, "not_a_dict"

    required_fields = ["timestamp", "device_id", "event_type"]

    for field in required_fields:
        if field not in record:
            return False, f"missing_{field}"

    if record["event_type"] not in VALID_EVENT_TYPES:
        return False, "invalid_event_type"

    try:
        datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
    except Exception:
        return False, "invalid_timestamp"

    payload = record.get("payload", {})
    if not isinstance(payload, dict):
        return False, "invalid_payload_type"

    return True, None
