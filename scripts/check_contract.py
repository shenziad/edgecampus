"""Fail fast when AI-assisted edits drift from the frozen v1 contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "system.json").read_text(encoding="utf-8"))


def main() -> None:
    required_text = {
        "EDGE-SBC-01": ["docs/PROTOCOL.md", "dashboard/index.html"],
        "TEMP01": ["docs/PROTOCOL.md", "dashboard/index.html"],
        "FAN01": ["docs/PROTOCOL.md", "dashboard/app.js"],
        '"protocol_version": "1.0"': ["config/system.json"],
        '"edge_ws_path": "/ws/edge"': ["config/system.json"],
        '"dashboard_ws_path": "/ws/dashboard"': ["config/system.json"],
    }
    failures: list[str] = []
    for needle, paths in required_text.items():
        for relative in paths:
            content = (ROOT / relative).read_text(encoding="utf-8")
            if needle not in content:
                failures.append(f"{relative}: missing {needle!r}")

    if CONFIG["devices"] != {"temperature": "TEMP01", "fan": "FAN01"}:
        failures.append("config/system.json: device IDs changed")
    if CONFIG["edge"]["edge_id"] != "EDGE-SBC-01":
        failures.append("config/system.json: edge ID changed")
    fake_edge = (ROOT / "edge" / "fake_edge.py").read_text(encoding="utf-8")
    for access in (
        'CONFIG["edge"]["edge_id"]',
        'CONFIG["devices"]["temperature"]',
        'CONFIG["devices"]["fan"]',
    ):
        if access not in fake_edge:
            failures.append(f"edge/fake_edge.py: no longer reads {access}")

    if failures:
        raise SystemExit("Contract drift detected:\n- " + "\n- ".join(failures))
    print("PASS: EdgeCampus public contract v1.0 is consistent")


if __name__ == "__main__":
    main()
