"""Exercise NOC REST over HTTP alongside the unchanged Edge WebSocket."""
import asyncio
import json
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import test_gate4_ws as gate4


@unittest.skipIf(gate4.uvicorn is None, "install requirements.txt for HTTP/WS tests")
class NocApiTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = gate4.Gate4WebSocketTests.asyncSetUp
    asyncTearDown = gate4.Gate4WebSocketTests.asyncTearDown
    receive = gate4.Gate4WebSocketTests.receive

    async def request(self, path, payload=None):
        def send():
            data = None if payload is None else json.dumps(payload).encode()
            req = Request(f"http://127.0.0.1:{self.port}" + path, data=data,
                          headers={"Content-Type": "application/json"})
            try:
                with urlopen(req, timeout=5) as response:
                    return response.status, json.load(response)
            except HTTPError as error:
                return error.code, json.load(error)
        return await asyncio.to_thread(send)

    async def test_network_health_api_and_edge_snapshot_are_separate(self):
        code, network = await self.request("/api/network/state")
        self.assertEqual(code, 200)
        self.assertEqual(network["ospf"], "FULL")
        self.assertEqual(network["bgp"], "ESTABLISHED")
        self.assertEqual(network["ipv6_tunnel"], "UP")
        self.assertEqual(network["branch_status"], "ONLINE")
        self.assertEqual(network["source"]["kind"], "SIMULATED")
        _, edge = await self.request("/api/state")
        self.assertNotIn("routing", edge)
        self.assertNotIn("network", edge)
        self.assertEqual(edge["policy"]["policy_id"], "thermal-01")
