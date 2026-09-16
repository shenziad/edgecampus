"""Host-only WebSocket regressions; never substitutes for PT evidence."""
import asyncio
import contextlib
import io
import json
import socket
import tempfile
import unittest
from pathlib import Path
try:
    import uvicorn
    import websockets
    from backend.app import main as backend
except ImportError:
    uvicorn = None
from backend.app.protocol import envelope
from backend.app.state import SystemState


@unittest.skipIf(uvicorn is None, "install requirements.txt for host WebSocket tests")
class Gate4WebSocketTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_log = backend.EVENT_LOG
        backend.EVENT_LOG = Path(self.temp.name) / "events.jsonl"
        backend.state = SystemState()
        backend.edge_socket = None
        backend.dashboard_sockets.clear()
        self.listener = socket.socket()
        self.listener.bind(("127.0.0.1", 0))
        self.port = self.listener.getsockname()[1]
        config = uvicorn.Config(backend.app, log_level="error", lifespan="off", ws="auto")
        self.server = uvicorn.Server(config)
        self.task = asyncio.create_task(self.server.serve(sockets=[self.listener]))
        for _ in range(100):
            if self.server.started:
                break
            await asyncio.sleep(.01)
        self.assertTrue(self.server.started)
        self.url = f"ws://127.0.0.1:{self.port}"

    async def asyncTearDown(self):
        self.server.should_exit = True
        await asyncio.wait_for(self.task, 5)
        self.listener.close()
        backend.EVENT_LOG = self.old_log
        self.temp.cleanup()

    async def receive(self, ws, kind):
        for _ in range(20):
            message = json.loads(await asyncio.wait_for(ws.recv(), 3))
            if message["type"] == kind:
                return message
        self.fail("expected message did not arrive")

    async def test_invalid_json_and_container_fields_preserve_socket(self):
        for path in ("/ws/edge", "/ws/dashboard"):
            async with websockets.connect(self.url + path) as ws:
                if path == "/ws/dashboard":
                    await self.receive(ws, "snapshot")
                for raw in ('{broken', json.dumps(envelope([]))):
                    await ws.send(raw)
                    self.assertEqual((await self.receive(ws, "error"))["code"], "INVALID_MESSAGE")
                await ws.send(json.dumps(envelope("hello", edge_id="EDGE-SBC-01")))
                if path == "/ws/dashboard":
                    self.assertEqual((await self.receive(ws, "error"))["code"], "UNSUPPORTED_FROM_DASHBOARD")
                else:
                    for _ in range(100):
                        if backend.state.edge_online:
                            break
                        await asyncio.sleep(.01)
                    self.assertTrue(backend.state.edge_online)

    async def test_disconnect_and_reconnect_restore_nondefault_policy(self):
        policy = dict(policy_id="thermal-01", version=2, mode="AUTO", threshold_c=33, hysteresis_c=1)
        async with websockets.connect(self.url + "/ws/dashboard") as dashboard:
            await self.receive(dashboard, "snapshot")
            for _ in range(2):
                async with websockets.connect(self.url + "/ws/edge") as edge:
                    await edge.send(json.dumps(envelope("state_sync", edge_id="EDGE-SBC-01",
                                                        temperature_c=31.8, fan_state="OFF", policy=policy)))
                    restored = await self.receive(dashboard, "snapshot")
                    self.assertTrue(restored["edge_online"])
                    self.assertEqual(restored["policy"], policy)
                    self.assertEqual(restored["temperature_c"], 31.8)
                    self.assertEqual(restored["fan_state"], "OFF")
                offline = await self.receive(dashboard, "snapshot")
                self.assertFalse(offline["edge_online"])
                self.assertEqual(offline["cloud_state"], "DISCONNECTED")

    async def test_gate4_invalid_script_checks_real_server(self):
        from scripts import gate4_invalid_ws_test as script
        old_url = script.WS_URL
        script.WS_URL = self.url + "/ws/dashboard"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(await script.main(), 0)
        finally:
            script.WS_URL = old_url
