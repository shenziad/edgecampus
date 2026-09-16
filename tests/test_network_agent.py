import unittest
from backend.app.network_agent import MockNetworkProvider, NetworkAgent


class NetworkAgentTests(unittest.TestCase):
    def test_baseline_is_healthy_and_explicitly_simulated(self):
        state = NetworkAgent().snapshot()
        self.assertEqual((state["ospf"], state["bgp"], state["ipv6_tunnel"], state["branch_status"]),
                         ("FULL", "ESTABLISHED", "UP", "ONLINE"))
        self.assertEqual(state["source"]["kind"], "SIMULATED")
        self.assertEqual(state["routing"]["bgp"]["neighbor"], "203.0.113.2")

    def test_adapter_and_snapshot_do_not_share_mutable_state(self):
        provider = MockNetworkProvider()
        agent = NetworkAgent(provider)
        state = agent.snapshot()
        state["routing"]["ospf"]["status"] = "DOWN"
        self.assertEqual(agent.snapshot()["ospf"], "FULL")

    def test_provider_is_replaceable(self):
        class DownProvider:
            def get_state(self):
                state = MockNetworkProvider().get_state()
                state["routing"]["bgp"]["status"] = "DOWN"
                return state
        self.assertEqual(NetworkAgent(DownProvider()).snapshot()["network"], "degraded")
