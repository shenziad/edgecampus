"""In-memory state for the three-day classroom prototype."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SystemState:
    edge_id: str = "EDGE-SBC-01"
    edge_online: bool = False
    cloud_state: str = "WAITING"
    last_heartbeat: str | None = None
    temperature_c: float | None = None
    fan_state: str = "UNKNOWN"
    control_mode: str = "AUTO"
    policy: dict[str, Any] = field(
        default_factory=lambda: {
            "policy_id": "thermal-01",
            "version": 1,
            "mode": "AUTO",
            "threshold_c": 30.0,
            "hysteresis_c": 1.0,
        }
    )
    events: list[dict[str, Any]] = field(default_factory=list)

    def add_event(self, event: str, source: str, detail: str) -> None:
        self.events.insert(
            0,
            {
                "timestamp": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "event": event,
                "source": source,
                "detail": detail,
            },
        )
        # Frequent telemetry must not evict control results from the dashboard.
        while len(self.events) > 100:
            telemetry_index = next(
                (index for index in range(len(self.events) - 1, -1, -1)
                 if self.events[index]["event"] == "TEMPERATURE"),
                len(self.events) - 1,
            )
            del self.events[telemetry_index]

    def apply_edge_message(self, message: dict[str, Any]) -> None:
        message_type = message["type"]
        if message_type in {"hello", "heartbeat", "state_sync"}:
            self.edge_id = message.get("edge_id", self.edge_id)
            self.edge_online = True
            self.cloud_state = "CONNECTED"

        if message_type == "heartbeat":
            self.last_heartbeat = message["timestamp"]
            self.control_mode = message["mode"]

        elif message_type == "telemetry" and message["metric"] == "temperature":
            self.temperature_c = float(message["value"])
            self.add_event(
                "TEMPERATURE",
                "SENSOR",
                f"{self.temperature_c:.1f} {message['unit']}",
            )

        elif message_type == "status" and message["device_id"] == "FAN01":
            self.fan_state = message["value"]
            self.add_event("FAN", message["source"], self.fan_state)

        elif message_type == "state_sync":
            self.temperature_c = float(message["temperature_c"])
            self.fan_state = message["fan_state"]
            self.policy = deepcopy(message["policy"])
            self.control_mode = self.policy["mode"]
            self.add_event("STATE_SYNC", "EDGE", "state restored after reconnect")

        elif message_type == "policy_ack":
            self.add_event(
                "POLICY_ACK",
                "EDGE",
                f"v{message['version']} {message['result']}",
            )

        elif message_type == "command_ack":
            self.add_event(
                "COMMAND_ACK",
                "EDGE",
                f"{message['device_id']} {message['action']} {message['result']}",
            )

    def apply_dashboard_message(self, message: dict[str, Any]) -> None:
        if message["type"] == "policy":
            self.policy = {
                "policy_id": message["policy_id"],
                "version": message["version"],
                "mode": message["mode"],
                "threshold_c": float(message["threshold_c"]),
                "hysteresis_c": float(message["hysteresis_c"]),
            }
            self.control_mode = message["mode"]
            self.add_event(
                "POLICY_SENT",
                "CLOUD-POLICY",
                f"v{message['version']} threshold={message['threshold_c']}C",
            )
        elif message["type"] == "command":
            self.add_event(
                "COMMAND_SENT",
                "REMOTE-MANUAL",
                f"{message['device_id']} {message['action']}",
            )

    def mark_edge_offline(self) -> None:
        if self.edge_online:
            self.add_event("EDGE_OFFLINE", "SYSTEM", "WebSocket disconnected")
        self.edge_online = False
        self.cloud_state = "DISCONNECTED"

    def snapshot(self) -> dict[str, Any]:
        return {
            "type": "snapshot",
            "edge_id": self.edge_id,
            "edge_online": self.edge_online,
            "cloud_state": self.cloud_state,
            "last_heartbeat": self.last_heartbeat,
            "temperature_c": self.temperature_c,
            "fan_state": self.fan_state,
            "control_mode": self.control_mode,
            "policy": deepcopy(self.policy),
            "events": deepcopy(self.events),
        }
