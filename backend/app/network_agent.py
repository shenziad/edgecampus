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
    def __init__(self, provider: NetworkProvider | None = None, controller=None) -> None:
        self.provider = provider or MockNetworkProvider()
        self.controller = controller
        self.events: list[dict[str, Any]] = []
        self.sequence = 0
        self.network_failed = False
        self.security_active = False
        self.violations = 0
        self.last_security_event = None

    def snapshot(self) -> dict[str, Any]:
        baseline = self.provider.get_state()
        controller = self.controller.snapshot() if self.controller is not None else None
        if controller is not None:
            baseline["routing"] = {name: {"status": "UNKNOWN", "reason": "NOT_OBSERVED"} for name in ("ospf", "bgp")}
            baseline["ipv6"] = {"tunnel": {"name": "Tunnel0", "status": "UNKNOWN", "reason": "NOT_OBSERVED"}}
            baseline["branch"] = {"status": "UNKNOWN", "reason": "NOT_OBSERVED"}
        if self.network_failed and controller is None:
            baseline["routing"]["bgp"]["status"] = "DOWN"
            baseline["ipv6"]["tunnel"]["status"] = "DOWN"
            baseline["branch"]["status"] = "OFFLINE"
        ospf = baseline["routing"]["ospf"]["status"]
        bgp = baseline["routing"]["bgp"]["status"]
        tunnel = baseline["ipv6"]["tunnel"]["status"]
        branch = baseline["branch"]["status"]
        return {
            "type": "network_state",
            "network": "unknown" if controller is not None else "healthy" if (ospf, bgp, tunnel, branch) == ("FULL", "ESTABLISHED", "UP", "ONLINE") else "degraded",
            "ospf": ospf, "bgp": bgp, "ipv6_tunnel": tunnel, "branch_status": branch,
            "routing": baseline["routing"], "ipv6": baseline["ipv6"],
            "branch": baseline["branch"],
            "source": {"kind": "PT_CONTROLLER", "provider": "pt-controller", "detail": "Live inventory/topology only; routing protocol state not exposed"} if controller is not None else {"kind": "SIMULATED", "provider": "mock", "detail": "Configuration-backed adapter; not live PT telemetry"},
            "controller": controller,
        }

    def event_history(self) -> list[dict[str, Any]]:
        return deepcopy(self.events)

    def record(self, category, event, detail):
        self.sequence += 1
        item = {"id": self.sequence, "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": category, "event": event, "detail": detail, "source": "SIMULATED"}
        self.events.insert(0, item)
        del self.events[100:]
        return deepcopy(item)

    def security_snapshot(self):
        baseline = self.provider.get_state()["security"]
        port_blocked = self.security_active and self.last_security_event["event"] == "PORT_SECURITY_VIOLATION"
        return {**baseline, "port_security": "VIOLATION" if port_blocked else "SECURE",
                "port_status": "BLOCKED" if port_blocked else "FORWARDING",
                "violations": self.violations, "active": self.security_active,
                "last_event": deepcopy(self.last_security_event), "source": "SIMULATED"}

    def security_attack(self, event):
        self.security_active = True
        self.violations += 1
        detail = "Unauthorized MAC detected · Port blocked" if event == "PORT_SECURITY_VIOLATION" else "Unauthorized traffic detected · ACL blocked traffic"
        item = self.record("SECURITY", event, detail)
        self.last_security_event = item
        return {**item, "security": self.security_snapshot()}

    def restore_security(self):
        self.security_active = False
        self.record("SECURITY", "SECURITY_RESTORED", "Simulated port recovered; cumulative violation count retained")
        return self.security_snapshot()

    def set_network_failure(self, failed):
        if self.network_failed != failed:
            self.network_failed = failed
            self.record("NETWORK", "BRANCH_LINK_DOWN" if failed else "BRANCH_LINK_RESTORED", "Mock branch link transition")
        return self.snapshot()

    def check_device(self, device, source):
        management = self.provider.get_state()["management"]
        allowed = source == management["allowed_source"]
        reachable = not self.network_failed and self.provider.get_state()["branch"]["status"] == "ONLINE"
        return {"device": device, "ip": management["devices"][device], "source_ip": source,
                "management": "PASS" if allowed and reachable else "DENIED" if not allowed else "UNAVAILABLE",
                "acl": "ALLOW" if allowed else "DENY", "status": "AVAILABLE" if reachable else "UNAVAILABLE",
                "source": "SIMULATED", "path": "ADMIN-PC → VTY ACL → Branch"}
