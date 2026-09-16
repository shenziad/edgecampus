import unittest
from backend.app.network_agent import MockNetworkProvider, NetworkAgent


class NetworkAgentTests(unittest.TestCase):
    def test_no_controller_never_returns_mock_health(self):
        state = NetworkAgent().snapshot()
        self.assertEqual((state["ospf"], state["bgp"], state["ipv6_tunnel"]), ("NOT COLLECTED",) * 3)
        self.assertFalse(state["controller"]["configured"])
        self.assertEqual(state["controller"]["devices"], [])
        self.assertEqual(state["source"]["kind"], "PT_CONTROLLER")
        self.assertNotIn("neighbor", state["routing"]["bgp"])

    def test_mock_adapter_snapshot_is_copy_isolated(self):
        provider = MockNetworkProvider()
        state = provider.get_state()
        state["routing"]["ospf"]["status"] = "DOWN"
        self.assertEqual(provider.get_state()["routing"]["ospf"]["status"], "FULL")

    def test_network_health_does_not_read_mock_provider(self):
        class UnreadableProvider:
            def get_state(self):
                raise AssertionError("Network Health must not use mock configuration")
        self.assertEqual(NetworkAgent(UnreadableProvider()).snapshot()["bgp"], "NOT COLLECTED")

class SecurityTests(unittest.TestCase):
    def test_attack_restore_preserves_audit(self):
        agent = NetworkAgent()
        self.assertEqual(agent.security_snapshot()["violations"], 0)
        event = agent.security_attack("PORT_SECURITY_VIOLATION")
        self.assertEqual(event["security"]["port_status"], "BLOCKED")
        self.assertIn("Unauthorized MAC detected", event["detail"])
        restored = agent.restore_security()
        self.assertFalse(restored["active"])
        self.assertEqual(restored["violations"], 1)
        self.assertEqual(agent.event_history()[0]["event"], "SECURITY_RESTORED")
