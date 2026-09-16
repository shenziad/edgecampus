"""Replaceable network adapter, separate from the frozen Edge protocol."""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

BASELINE = Path(__file__).resolve().parents[2] / "config" / "network_baseline.json"


class NetworkProvider(Protocol):
    def get_state(self) -> dict[str, Any]: ...


class MockNetworkProvider:
    """Configuration fixture; never claims to read live Packet Tracer devices."""
    def __init__(self, path: Path = BASELINE) -> None:
        self.baseline = json.loads(path.read_text(encoding="utf-8"))

    def get_state(self) -> dict[str, Any]:
        return deepcopy(self.baseline)


class NetworkAgent:
    def __init__(self, provider: NetworkProvider | None = None) -> None:
        self.provider = provider or MockNetworkProvider()
        self.events: list[dict[str, Any]] = []
        self.sequence = 0

    def snapshot(self) -> dict[str, Any]:
        baseline = self.provider.get_state()
        ospf = baseline["routing"]["ospf"]["status"]
        bgp = baseline["routing"]["bgp"]["status"]
        tunnel = baseline["ipv6"]["tunnel"]["status"]
        branch = baseline["branch"]["status"]
        return {
            "type": "network_state",
            "network": "healthy" if (ospf, bgp, tunnel, branch) == ("FULL", "ESTABLISHED", "UP", "ONLINE") else "degraded",
            "ospf": ospf, "bgp": bgp, "ipv6_tunnel": tunnel, "branch_status": branch,
            "routing": baseline["routing"], "ipv6": baseline["ipv6"],
            "branch": baseline["branch"],
            "source": {"kind": "SIMULATED", "provider": "mock", "detail": "Configuration-backed adapter; not live PT telemetry"},
        }

    def event_history(self) -> list[dict[str, Any]]:
        return deepcopy(self.events)
