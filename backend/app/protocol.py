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
    "hello": {
        "edge_id",
    },
    "heartbeat": {
        "edge_id",
        "status",
        "mode",
        "policy_version",
    },
    "telemetry": {
        "edge_id",
        "device_id",
        "metric",
        "value",
        "unit",
    },
    "status": {
        "edge_id",
        "device_id",
        "value",
        "source",
    },
    "command": {
        "command_id",
        "device_id",
        "action",
    },
    "command_ack": {
        "command_id",
        "device_id",
        "action",
        "result",
    },
    "policy": {
        "policy_id",
        "version",
        "mode",
        "threshold_c",
        "hysteresis_c",
    },
    "policy_ack": {
        "policy_id",
        "version",
        "result",
    },
    "state_sync": {
        "edge_id",
        "temperature_c",
        "fan_state",
        "policy",
    },
    "error": {
        "code",
        "message",
    },
}


class ProtocolError(ValueError):
    """Raised when a message violates the frozen public contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def envelope(message_type: str, **fields: Any) -> dict[str, Any]:
    """Build a Protocol v1.0 message with the mandatory envelope fields."""

    return {
        "type": message_type,
        "protocol_version": PROTOCOL_VERSION,
        "message_id": str(uuid4()),
        "timestamp": utc_now(),
        **fields,
    }


def validate_message(message: Any) -> dict[str, Any]:
    """Validate one public Protocol v1.0 message.

    Validation is intentionally strict enough to reject malformed,
    unsupported and wrong-version messages without crashing the
    WebSocket connection handler or Backend process.
    """

    # ------------------------------------------------------------
    # 1. Message itself must be a JSON object
    # ------------------------------------------------------------

    if not isinstance(message, dict):
        raise ProtocolError("message must be a JSON object")

    # ------------------------------------------------------------
    # 2. Common Protocol v1.0 envelope
    # ------------------------------------------------------------

    message_type = message.get("type")

    if not isinstance(message_type, str) or message_type not in MESSAGE_TYPES:
        raise ProtocolError(
            f"unknown message type: {message_type!r}"
        )

    if message.get("protocol_version") != PROTOCOL_VERSION:
        raise ProtocolError(
            f"protocol_version must be {PROTOCOL_VERSION!r}"
        )

    # Gate 4 stability hardening:
    # PROTOCOL.md defines message_id as mandatory for EVERY message.
    message_id = message.get("message_id")

    if not isinstance(message_id, str) or not message_id.strip():
        raise ProtocolError(
            "message_id must be a non-empty string"
        )

    timestamp = message.get("timestamp")

    if not isinstance(timestamp, str) or not timestamp.strip():
        raise ProtocolError(
            "timestamp must be an ISO-8601 string"
        )

    # ------------------------------------------------------------
    # 3. Message-type-specific required fields
    # ------------------------------------------------------------

    missing = REQUIRED_FIELDS[message_type] - message.keys()

    if missing:
        raise ProtocolError(
            f"{message_type} missing fields: "
            f"{', '.join(sorted(missing))}"
        )

    # ------------------------------------------------------------
    # 4. Command / command_ack validation
    # ------------------------------------------------------------

    if message_type in {"command", "command_ack"}:
        action = message["action"]

        if action not in ("ON", "OFF"):
            raise ProtocolError(
                "command action must be ON or OFF"
            )

    # ------------------------------------------------------------
    # 5. Policy version validation
    # ------------------------------------------------------------

    if message_type in {"policy", "policy_ack"}:
        version = message["version"]

        # bool is technically an int subclass in Python,
        # so reject it explicitly.
        if (
            isinstance(version, bool)
            or not isinstance(version, int)
            or version < 1
        ):
            raise ProtocolError(
                "policy version must be a positive integer"
            )

    # ------------------------------------------------------------
    # 6. Policy contents
    # ------------------------------------------------------------

    if message_type == "policy":
        if message["policy_id"] != "thermal-01":
            raise ProtocolError("unknown policy_id")
        mode = message["mode"]

        if mode not in ("AUTO", "MANUAL"):
            raise ProtocolError(
                "policy mode must be AUTO or MANUAL"
            )

        threshold = message["threshold_c"]
        hysteresis = message["hysteresis_c"]

        if (
            isinstance(threshold, bool)
            or not isinstance(threshold, (int, float))
            or not 0 <= threshold <= 80
        ):
            raise ProtocolError(
                "threshold_c must be between 0 and 80"
            )

        if (
            isinstance(hysteresis, bool)
            or not isinstance(hysteresis, (int, float))
            or not 0 <= hysteresis <= 10
        ):
            raise ProtocolError(
                "hysteresis_c must be between 0 and 10"
            )

    # ------------------------------------------------------------
    # 7. State-sync basic validation
    #
    # Keep Protocol v1.0 structure unchanged.
    # Only validate the fields that are important for safe restore.
    # ------------------------------------------------------------

    if message_type == "state_sync":
        temperature = message["temperature_c"]
        fan_state = message["fan_state"]
        policy = message["policy"]

        if (
            isinstance(temperature, bool)
            or not isinstance(temperature, (int, float))
        ):
            raise ProtocolError(
                "state_sync temperature_c must be numeric"
            )

        if fan_state not in ("ON", "OFF"):
            raise ProtocolError(
                "state_sync fan_state must be ON or OFF"
            )

        if not isinstance(policy, dict):
            raise ProtocolError(
                "state_sync policy must be a JSON object"
            )

        required_policy_fields = {
            "policy_id",
            "version",
            "mode",
            "threshold_c",
            "hysteresis_c",
        }

        missing_policy_fields = (
            required_policy_fields - policy.keys()
        )

        if missing_policy_fields:
            raise ProtocolError(
                "state_sync policy missing fields: "
                + ", ".join(
                    sorted(missing_policy_fields)
                )
            )

        if policy["policy_id"] != "thermal-01":
            raise ProtocolError("unknown state_sync policy_id")

        policy_version = policy["version"]

        if (
            isinstance(policy_version, bool)
            or not isinstance(policy_version, int)
            or policy_version < 1
        ):
            raise ProtocolError(
                "state_sync policy version must be "
                "a positive integer"
            )

        if policy["mode"] not in ("AUTO", "MANUAL"):
            raise ProtocolError(
                "state_sync policy mode must be "
                "AUTO or MANUAL"
            )

        policy_threshold = policy["threshold_c"]
        policy_hysteresis = policy["hysteresis_c"]

        if (
            isinstance(policy_threshold, bool)
            or not isinstance(
                policy_threshold,
                (int, float),
            )
            or not 0 <= policy_threshold <= 80
        ):
            raise ProtocolError(
                "state_sync threshold_c must be "
                "between 0 and 80"
            )

        if (
            isinstance(policy_hysteresis, bool)
            or not isinstance(
                policy_hysteresis,
                (int, float),
            )
            or not 0 <= policy_hysteresis <= 10
        ):
            raise ProtocolError(
                "state_sync hysteresis_c must be "
                "between 0 and 10"
            )

    if message_type == "telemetry":
        value = message["value"]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ProtocolError("telemetry value must be numeric")

    if message_type == "heartbeat":
        version = message["policy_version"]
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise ProtocolError("heartbeat policy_version must be a positive integer")

    return message
