"""Public message contract validation shared by the control plane tests.

The validator is intentionally dependency-free. FastAPI remains the only web
framework dependency, while malformed public messages are rejected explicitly.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


PROTOCOL_VERSION = "1.0"
MESSAGE_TYPES = {
    "hello",
    "heartbeat",
    "telemetry",
    "status",
    "command",
    "command_ack",
    "policy",
    "policy_ack",
    "state_sync",
    "error",
}

REQUIRED_FIELDS: dict[str, set[str]] = {
    "hello": {"edge_id"},
    "heartbeat": {"edge_id", "status", "mode", "policy_version"},
    "telemetry": {"edge_id", "device_id", "metric", "value", "unit"},
    "status": {"edge_id", "device_id", "value", "source"},
    "command": {"command_id", "device_id", "action"},
    "command_ack": {"command_id", "device_id", "action", "result"},
    "policy": {
        "policy_id",
        "version",
        "mode",
        "threshold_c",
        "hysteresis_c",
    },
    "policy_ack": {"policy_id", "version", "result"},
    "state_sync": {"edge_id", "temperature_c", "fan_state", "policy"},
    "error": {"code", "message"},
}


class ProtocolError(ValueError):
    """Raised when a message violates the frozen public contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def envelope(message_type: str, **fields: Any) -> dict[str, Any]:
    """Build a v1 message with the mandatory envelope fields."""
    return {
        "type": message_type,
        "protocol_version": PROTOCOL_VERSION,
        "message_id": str(uuid4()),
        "timestamp": utc_now(),
        **fields,
    }


def validate_message(message: Any) -> dict[str, Any]:
    """Validate the stable fields used across Edge, Backend and Dashboard."""
    if not isinstance(message, dict):
        raise ProtocolError("message must be a JSON object")

    message_type = message.get("type")
    if message_type not in MESSAGE_TYPES:
        raise ProtocolError(f"unknown message type: {message_type!r}")

    if message.get("protocol_version") != PROTOCOL_VERSION:
        raise ProtocolError(
            f"protocol_version must be {PROTOCOL_VERSION!r}"
        )

    if not isinstance(message.get("timestamp"), str):
        raise ProtocolError("timestamp must be an ISO-8601 string")

    missing = REQUIRED_FIELDS[message_type] - message.keys()
    if missing:
        raise ProtocolError(
            f"{message_type} missing fields: {', '.join(sorted(missing))}"
        )

    if message_type in {"command", "command_ack"}:
        action = message["action"]
        if action not in {"ON", "OFF"}:
            raise ProtocolError("command action must be ON or OFF")

    if message_type in {"policy", "policy_ack"}:
        if not isinstance(message["version"], int) or message["version"] < 1:
            raise ProtocolError("policy version must be a positive integer")

    if message_type == "policy":
        if message["mode"] not in {"AUTO", "MANUAL"}:
            raise ProtocolError("policy mode must be AUTO or MANUAL")
        threshold = message["threshold_c"]
        hysteresis = message["hysteresis_c"]
        if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 80:
            raise ProtocolError("threshold_c must be between 0 and 80")
        if not isinstance(hysteresis, (int, float)) or not 0 <= hysteresis <= 10:
            raise ProtocolError("hysteresis_c must be between 0 and 10")

    return message
