"""Exercise NOC REST over HTTP alongside the unchanged Edge WebSocket."""
import asyncio
import json
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import test_gate4_ws as gate4


@unittest.skipIf(gate4.uvicorn is None, "install requirements.txt for HTTP/WS tests")
class NocApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from backend.app import noc
        from backend.app.network_agent import NetworkAgent
        noc.agent = NetworkAgent()
        noc.cloud_failed = False
        noc.sync_status = "NOT_RUN"
        await gate4.Gate4WebSocketTests.asyncSetUp(self)
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
        self.assertEqual(network["ospf"], "NOT COLLECTED")
        self.assertEqual(network["bgp"], "NOT COLLECTED")
        self.assertEqual(network["ipv6_tunnel"], "NOT COLLECTED")
        self.assertEqual(network["branch_status"], "NOT COLLECTED")
        self.assertEqual(network["source"]["kind"], "PT_CONTROLLER")
        _, edge = await self.request("/api/state")
        self.assertNotIn("routing", edge)
        self.assertNotIn("network", edge)
        self.assertEqual(edge["policy"]["policy_id"], "thermal-01")

    async def test_security_validation_attack_restore(self):
        code, _ = await self.request("/api/simulation/security", {"event": "INVALID"})
        self.assertEqual(code, 422)
        _, state = await self.request("/api/security/state")
        self.assertEqual(state["violations"], 0)
        _, attack = await self.request("/api/simulation/security", {})
        self.assertEqual(attack["event"], "PORT_SECURITY_VIOLATION")
        self.assertEqual(attack["security"]["port_status"], "BLOCKED")
        _, restored = await self.request("/api/simulation/security/restore", {})
        self.assertFalse(restored["active"])
        self.assertEqual(restored["violations"], 1)

    async def test_network_failure_management_and_policy_overlay(self):
        _, result = await self.request("/api/branch/check", {"device": "R-BRANCH"})
        self.assertEqual(result["management"], "PASS")
        _, denied = await self.request("/api/branch/check", {"device": "SW-BRANCH", "source_ip": "192.168.20.1"})
        self.assertEqual(denied["acl"], "DENY")
        code, _ = await self.request("/api/simulation/network", {})
        self.assertEqual(code, 409)
        code, _ = await self.request("/api/simulation/network/restore", {})
        self.assertEqual(code, 409)
        _, policy = await self.request("/api/campus-policy")
        self.assertEqual(policy["thermal"], gate4.backend.state.policy)
        self.assertEqual(policy["security"]["port_security"], "STRICT")

    async def test_cloud_closes_socket_and_requires_actual_state_sync(self):
        from backend.app.protocol import envelope
        from backend.app import noc
        policy = dict(policy_id="thermal-01", version=3, mode="AUTO", threshold_c=33, hysteresis_c=1)
        async with gate4.websockets.connect(self.url + "/ws/edge") as edge:
            await edge.send(json.dumps(envelope("state_sync", edge_id="EDGE-SBC-01", temperature_c=35, fan_state="ON", policy=policy)))
            for _ in range(100):
                if gate4.backend.state.edge_online: break
                await asyncio.sleep(.01)
            _, outage = await self.request("/api/simulation/cloud", {})
            self.assertEqual(outage["cloud"], "OFFLINE")
            await asyncio.wait_for(edge.wait_closed(), 3)
            self.assertFalse(gate4.backend.state.edge_online)
            async with gate4.websockets.connect(self.url + "/ws/edge") as rejected:
                await asyncio.wait_for(rejected.wait_closed(), 3)
            _, restored = await self.request("/api/simulation/cloud/restore", {})
            self.assertEqual(restored["state_sync"], "WAITING_FOR_STATE_SYNC")
        async with gate4.websockets.connect(self.url + "/ws/edge") as edge:
            await edge.send(json.dumps(envelope("hello", edge_id="EDGE-SBC-01")))
            await asyncio.sleep(.03)
            self.assertNotEqual(noc.sync_status, "SUCCESS")
            await edge.send(json.dumps(envelope("state_sync", edge_id="EDGE-SBC-01", temperature_c=35, fan_state="ON", policy=policy)))
            for _ in range(100):
                if noc.sync_status == "SUCCESS": break
                await asyncio.sleep(.01)
            self.assertEqual(noc.sync_status, "SUCCESS")
            self.assertEqual(gate4.backend.state.policy, policy)

    async def test_controller_configuration_and_live_simulation_guard(self):
        _, unconfigured = await self.request("/api/controller/state")
        self.assertFalse(unconfigured["configured"])
        class FixtureController:
            def snapshot(self):
                return {"configured": True, "status": "CONNECTED", "devices": []}
        from backend.app import noc
        noc.agent.controller = FixtureController()
        _, network = await self.request("/api/network/state")
        self.assertEqual(network["source"]["kind"], "PT_CONTROLLER")
        self.assertEqual(network["ospf"], "NOT COLLECTED")
        code, _ = await self.request("/api/simulation/network", {})
        self.assertEqual(code, 409)
        _, combined = await self.request("/api/noc/state")
        self.assertEqual(combined["network"]["controller"]["status"], "CONNECTED")
        self.assertEqual(combined["branch"]["source"], "SIMULATED")
