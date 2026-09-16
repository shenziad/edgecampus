"""Real local HTTP transport tests using a PT-shaped fixture, not PT evidence."""
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from backend.app.pt_controller import PacketTracerController
from backend.app.network_agent import NetworkAgent

class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.inventory = [{"id": "r1", "hostname": "R-HQ", "managementIpAddress": "192.168.30.1", "reachabilityStatus": "Reachable", "password": "never-export"}]
        self.inventory_code = 200
        self.topology_code = 200
        self.reject_once = False
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def reply(self, code, response):
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"response": response}).encode())
            def do_POST(self):
                owner.calls.append(("POST", self.path))
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if body == {"username": "test", "password": "local-fixture"}:
                    self.reply(200, {"serviceTicket": "fixture-token"})
                else:
                    self.reply(401, {"detail": "secret must not be relayed"})
            def do_GET(self):
                owner.calls.append(("GET", self.path))
                if self.headers.get("X-Auth-Token") != "fixture-token" or owner.reject_once:
                    owner.reject_once = False
                    self.reply(401, {})
                elif self.path.endswith("/network-device"):
                    self.reply(owner.inventory_code, owner.inventory)
                else:
                    self.reply(owner.topology_code, {"nodes": [{"id": "r1"}], "links": []})
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.client = PacketTracerController(self.url, "test", "local-fixture", cache_seconds=0)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_inventory_topology_auth_and_secret_filter(self):
        result = self.client.snapshot()
        self.assertEqual(result["status"], "CONNECTED")
        self.assertEqual(result["devices"][0]["hostname"], "R-HQ")
        self.assertEqual(result["topology"]["nodes"][0]["id"], "r1")
        self.assertNotIn("never-export", json.dumps(result))
        self.assertEqual(self.calls, [("POST", "/api/v1/ticket"), ("GET", "/api/v1/network-device"), ("GET", "/api/v1/topology/physical-topology")])

    def test_expired_ticket_reauth_once(self):
        self.client.snapshot()
        self.reject_once = True
        self.assertEqual(self.client.snapshot()["status"], "CONNECTED")
        self.assertEqual(self.calls.count(("POST", "/api/v1/ticket")), 2)

    def test_failure_clears_previous_inventory_without_mock_fallback(self):
        self.client.snapshot()
        self.inventory_code = 500
        result = self.client.snapshot()
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertEqual(result["devices"], [])
        self.assertIsNone(result["observed_at"])
        state = NetworkAgent(controller=self.client).snapshot()
        self.assertEqual(state["source"]["kind"], "PT_CONTROLLER")
        self.assertEqual(state["bgp"], "UNKNOWN")
        self.assertEqual(state["network"], "unknown")

    def test_topology_failure_does_not_hide_valid_inventory(self):
        self.topology_code = 501
        result = self.client.snapshot()
        self.assertEqual(result["status"], "CONNECTED")
        self.assertEqual(len(result["devices"]), 1)
        self.assertEqual(result["topology_error"], "TOPOLOGY_UNAVAILABLE")

    def test_empty_inventory_and_invalid_schema(self):
        self.inventory = []
        self.assertEqual(self.client.snapshot()["devices"], [])
        self.inventory = {"unexpected": []}
        self.assertEqual(self.client.snapshot()["error"], "INVALID_INVENTORY_RESPONSE")

    def test_credentials_failure_is_sanitized(self):
        client = PacketTracerController(self.url, "test", "wrong-password", cache_seconds=0)
        result = client.snapshot()
        self.assertEqual(result["error"], "AUTH_FAILED")
        self.assertNotIn("wrong-password", json.dumps(result))
        self.assertNotIn("secret", json.dumps(result))
        self.assertEqual(PacketTracerController(self.url, "", "").snapshot()["error"], "MISSING_CREDENTIALS")

    def test_cache_and_copy_isolation(self):
        self.client.cache_seconds = 5
        first = self.client.snapshot()
        first["devices"].clear()
        self.assertEqual(len(self.client.snapshot()["devices"]), 1)
        self.assertEqual(len(self.calls), 3)

    def test_external_or_credential_urls_are_rejected(self):
        for url in ("http://192.168.30.30", "http://user:pass@localhost:58000", "http://localhost:58000/other"):
            with self.assertRaises(ValueError):
                PacketTracerController(url, "", "")
