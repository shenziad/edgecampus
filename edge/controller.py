"""Platform-independent local autonomy logic.

Packet Tracer code should call ``observe_temperature`` and map the returned
fan state to its actuator API. Keeping this decision logic free of networking
and PT-specific APIs makes it directly testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EdgeController:
    mode: str = "AUTO"
    threshold_c: float = 30.0
    hysteresis_c: float = 1.0
    policy_version: int = 1
    fan_state: str = "OFF"

    def observe_temperature(self, temperature_c: float) -> tuple[str, bool]:
        """Apply an AUTO policy with hysteresis; return state and change flag."""
        previous = self.fan_state
        if self.mode == "AUTO":
            if temperature_c >= self.threshold_c:
                self.fan_state = "ON"
            elif temperature_c <= self.threshold_c - self.hysteresis_c:
                self.fan_state = "OFF"
        return self.fan_state, self.fan_state != previous

    def apply_policy(self, message: dict[str, Any]) -> None:
        self.mode = message["mode"]
        self.threshold_c = float(message["threshold_c"])
        self.hysteresis_c = float(message["hysteresis_c"])
        self.policy_version = int(message["version"])

    def apply_command(self, action: str) -> None:
        if action not in {"ON", "OFF"}:
            raise ValueError("fan action must be ON or OFF")
        self.fan_state = action

    def policy_dict(self) -> dict[str, Any]:
        return {
            "policy_id": "thermal-01",
            "version": self.policy_version,
            "mode": self.mode,
            "threshold_c": self.threshold_c,
            "hysteresis_c": self.hysteresis_c,
        }
