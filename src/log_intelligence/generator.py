from __future__ import annotations

import argparse
import json
import random
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from log_intelligence.config import config


DEVICE_MODELS = [
    "CardioSense-X",
    "VascuTrack-Pro",
    "NeuroPulse-Mini",
    "EndoCam-4K",
]

FIRMWARE_VERSIONS = [
    "1.0.0",
    "1.1.2",
    "1.2.0",
    "1.3.5",
    "2.0.0",
]

EVENT_TYPES = [
    "info",
    "warning",
    "error",
]

INFO_MESSAGES = [
    "Device heartbeat received",
    "Session started",
    "Session completed successfully",
    "Configuration synchronized",
    "Firmware health check passed",
]

WARNING_MESSAGES = [
    "Battery level below recommended threshold",
    "Signal quality degraded",
    "Temperature approaching upper limit",
    "Calibration recommended",
    "Procedure duration longer than expected",
]

ERROR_MESSAGES_BY_CODE = {
    "E_PRESSURE_HIGH": "Pump pressure exceeded threshold",
    "E_SENSOR_TIMEOUT": "Sensor did not respond within expected time",
    "E_BATTERY_CRITICAL": "Battery level critically low",
    "E_TEMP_HIGH": "Device temperature exceeded safe operating range",
    "E_CONNECTION_LOST": "Connection to monitoring station was lost",
}


def build_device_pool(device_count: int) -> list[dict[str, str]]:
    """Create a stable pool of simulated devices."""
    devices = []

    for index in range(1, device_count + 1):
        devices.append(
            {
                "device_id": f"DEV-{index:03d}",
                "model": random.choice(DEVICE_MODELS),
                "firmware_version": random.choice(FIRMWARE_VERSIONS),
            }
        )

    return devices


def random_timestamp(start: datetime, end: datetime) -> str:
    """Return a random UTC timestamp between start and end in ISO-8601 format."""
    total_seconds = int((end - start).total_seconds())
    offset_seconds = random.randint(0, total_seconds)
    timestamp = start + timedelta(seconds=offset_seconds)

    return timestamp.isoformat().replace("+00:00", "Z")


def build_valid_log(devices: list[dict[str, str]], start: datetime, end: datetime) -> dict[str, Any]:
    """Build one valid simulated device log record."""
    device = random.choice(devices)
    event_type = random.choices(
        EVENT_TYPES,
        weights=[0.72, 0.20, 0.08],
        k=1,
    )[0]

    payload: dict[str, Any] = {
        "session_id": f"S-{random.randint(1000, 9999)}",
        "duration_ms": random.randint(50, 8_000),
        "status": "success",
        "model": device["model"],
        "firmware_version": device["firmware_version"],
    }

    if event_type == "info":
        message = random.choice(INFO_MESSAGES)
    elif event_type == "warning":
        message = random.choice(WARNING_MESSAGES)
        payload["status"] = random.choice(["success", "degraded"])
    else:
        error_code, message = random.choice(list(ERROR_MESSAGES_BY_CODE.items()))
        payload["status"] = "failed"
        payload["error_code"] = error_code

    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": random_timestamp(start, end),
        "device_id": device["device_id"],
        "event_type": event_type,
        "message": message,
        "payload": payload,
    }


def build_invalid_log(valid_log: dict[str, Any]) -> dict[str, Any] | str:
    """
    Build an intentionally invalid record.

    Invalid records are useful because the ingestion layer must prove that it
    can reject bad data instead of silently loading everything.
    """
    mutation_type = random.choice(
        [
            "missing_timestamp",
            "missing_device_id",
            "invalid_timestamp",
            "invalid_event_type",
            "payload_not_object",
            "malformed_json",
        ]
    )

    invalid_log = valid_log.copy()

    if mutation_type == "missing_timestamp":
        invalid_log.pop("timestamp", None)
    elif mutation_type == "missing_device_id":
        invalid_log.pop("device_id", None)
    elif mutation_type == "invalid_timestamp":
        invalid_log["timestamp"] = "not-a-real-timestamp"
    elif mutation_type == "invalid_event_type":
        invalid_log["event_type"] = "critical"
    elif mutation_type == "payload_not_object":
        invalid_log["payload"] = "this should be an object"
    elif mutation_type == "malformed_json":
        return '{"timestamp": "2026-05-22T10:00:00Z", "device_id": '

    return invalid_log


def generate_logs(
    output_path: Path,
    record_count: int,
    invalid_ratio: float,
    duplicate_ratio: float,
    device_count: int,
    seed: int,
) -> None:
    """Generate simulated device logs as JSON Lines."""
    random.seed(seed)
    config.ensure_directories()

    devices = build_device_pool(device_count)

    end = datetime.now(UTC)
    start = end - timedelta(days=7)

    records: list[dict[str, Any] | str] = []

    for _ in range(record_count):
        valid_log = build_valid_log(devices, start, end)

        if random.random() < invalid_ratio:
            records.append(build_invalid_log(valid_log))
        else:
            records.append(valid_log)

    valid_records = [record for record in records if isinstance(record, dict)]

    duplicate_count = int(record_count * duplicate_ratio)
    for _ in range(duplicate_count):
        if valid_records:
            records.append(random.choice(valid_records))

    random.shuffle(records)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            if isinstance(record, str):
                file.write(record + "\n")
            else:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Generated {len(records)} log lines at: {output_path}")
    print(f"Base records: {record_count}")
    print(f"Approx. invalid records: {int(record_count * invalid_ratio)}")
    print(f"Duplicate records added: {duplicate_count}")
    print(f"Device count: {device_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate simulated device logs.")

    parser.add_argument(
        "--records",
        type=int,
        default=1_000,
        help="Number of base records to generate.",
    )
    parser.add_argument(
        "--invalid-ratio",
        type=float,
        default=0.05,
        help="Approximate ratio of invalid records.",
    )
    parser.add_argument(
        "--duplicate-ratio",
        type=float,
        default=0.03,
        help="Approximate ratio of duplicate records to append.",
    )
    parser.add_argument(
        "--devices",
        type=int,
        default=25,
        help="Number of unique simulated devices.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible log generation.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=config.raw_dir / "device_logs.jsonl",
        help="Output JSONL file path.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    generate_logs(
        output_path=args.output,
        record_count=args.records,
        invalid_ratio=args.invalid_ratio,
        duplicate_ratio=args.duplicate_ratio,
        device_count=args.devices,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
