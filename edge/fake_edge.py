"""Runnable Edge simulator for independent Backend/Dashboard development."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from itertools import cycle
from pathlib import Path
from typing import Any

from websockets.asyncio.client import connect

from backend.app.protocol import envelope, validate_message
from edge.controller import EdgeController


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "system.json").read_text(encoding="utf-8"))
EDGE_ID = CONFIG["edge"]["edge_id"]
TEMP_ID = CONFIG["devices"]["temperature"]
FAN_ID = CONFIG["devices"]["fan"]


class FakeEdge:
    def __init__(self, temperatures: list[float], interval: float) -> None:
        policy = CONFIG["policy"]
        self.controller = EdgeController(
            mode=policy["mode"],
            threshold_c=policy["threshold_c"],
            hysteresis_c=policy["hysteresis_c"],
            policy_version=policy["version"],
        )
        self.temperatures = cycle(temperatures)
        self.interval = interval
        self.current_temperature = temperatures[0]
        self.last_control_source = "EDGE-AUTO"

    async def send_initial_state(self, socket: Any) -> None:
        await socket.send(json.dumps(envelope("hello", edge_id=EDGE_ID)))
        await socket.send(
            json.dumps(
                envelope(
                    "state_sync",
                    edge_id=EDGE_ID,
                    temperature_c=self.current_temperature,
                    fan_state=self.controller.fan_state,
                    policy=self.controller.policy_dict(),
                )
            )
        )

    async def local_control_loop(self) -> None:
        """Keep sensing and controlling regardless of cloud connectivity."""
        while True:
            self.current_temperature = float(next(self.temperatures))
            fan_state, changed = self.controller.observe_temperature(
                self.current_temperature
            )
            if changed:
                self.last_control_source = "EDGE-AUTO"
                print(
                    f"EDGE-AUTO temperature={self.current_temperature:.1f}C "
                    f"fan={fan_state}"
                )
            await asyncio.sleep(self.interval)

    async def telemetry_loop(self, socket: Any) -> None:
        last_reported_fan: str | None = None
        while True:
            await socket.send(
                json.dumps(
                    envelope(
                        "telemetry",
                        edge_id=EDGE_ID,
                        device_id=TEMP_ID,
                        metric="temperature",
                        value=self.current_temperature,
                        unit="C",
                    )
                )
            )
            if self.controller.fan_state != last_reported_fan:
                await self.send_fan_status(socket, self.last_control_source)
                last_reported_fan = self.controller.fan_state
            await asyncio.sleep(self.interval)

    async def heartbeat_loop(self, socket: Any) -> None:
        heartbeat_interval = CONFIG["edge"]["heartbeat_interval_sec"]
        while True:
            await socket.send(
                json.dumps(
                    envelope(
                        "heartbeat",
                        edge_id=EDGE_ID,
                        status="ONLINE",
                        mode=self.controller.mode,
                        policy_version=self.controller.policy_version,
                    )
                )
            )
            await asyncio.sleep(heartbeat_interval)

    async def receive_loop(self, socket: Any) -> None:
        async for raw in socket:
            message = validate_message(json.loads(raw))
            if message["type"] == "policy":
                self.controller.apply_policy(message)
                print(
                    f"CLOUD-POLICY v{message['version']} "
                    f"mode={message['mode']} threshold={message['threshold_c']}C"
                )
                await socket.send(
                    json.dumps(
                        envelope(
                            "policy_ack",
                            policy_id=message["policy_id"],
                            version=message["version"],
                            result="APPLIED",
                        )
                    )
                )
            elif message["type"] == "command":
                self.controller.apply_command(message["action"])
                self.last_control_source = "REMOTE-MANUAL"
                print(f"REMOTE-MANUAL fan={message['action']}")
                await self.send_fan_status(socket, "REMOTE-MANUAL")
                await socket.send(
                    json.dumps(
                        envelope(
                            "command_ack",
                            command_id=message["command_id"],
                            device_id=message["device_id"],
                            action=message["action"],
                            result="APPLIED",
                        )
                    )
                )

    async def send_fan_status(self, socket: Any, source: str) -> None:
        await socket.send(
            json.dumps(
                envelope(
                    "status",
                    edge_id=EDGE_ID,
                    device_id=FAN_ID,
                    value=self.controller.fan_state,
                    source=source,
                )
            )
        )

    async def cloud_loop(self, uri: str) -> None:
        async for socket in connect(uri, open_timeout=5):
            try:
                print("Cloud connected; synchronizing current state")
                await self.send_initial_state(socket)
                async with asyncio.TaskGroup() as group:
                    group.create_task(self.telemetry_loop(socket))
                    group.create_task(self.heartbeat_loop(socket))
                    group.create_task(self.receive_loop(socket))
            except Exception as exc:
                print(f"Cloud lost ({exc}); local autonomy remains active")
                await asyncio.sleep(2)

    async def run(self, uri: str) -> None:
        print(f"Fake Edge starting: {uri}")
        await asyncio.gather(self.local_control_loop(), self.cloud_loop(uri))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EdgeCampus fake Edge node")
    parser.add_argument(
        "--server",
        default=os.getenv(
            "EDGECAMPUS_SERVER_URL", "ws://127.0.0.1:8000/ws/edge"
        ),
    )
    parser.add_argument(
        "--temperatures",
        default="27,29,30,32,34,31,28,26",
        help="comma-separated repeating demo scenario",
    )
    parser.add_argument("--interval", type=float, default=3.0)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    values = [float(item) for item in args.temperatures.split(",")]
    try:
        asyncio.run(FakeEdge(values, args.interval).run(args.server))
    except KeyboardInterrupt:
        print("Fake Edge stopped")
