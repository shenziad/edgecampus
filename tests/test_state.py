import unittest

from backend.app.protocol import envelope
from backend.app.state import SystemState


class StateTests(unittest.TestCase):
    def test_telemetry_and_status_update_snapshot(self):
        state = SystemState()
        state.apply_edge_message(
            envelope(
                "telemetry",
                edge_id="EDGE-SBC-01",
                device_id="TEMP01",
                metric="temperature",
                value=31.4,
                unit="C",
            )
        )
        state.apply_edge_message(
            envelope(
                "status",
                edge_id="EDGE-SBC-01",
                device_id="FAN01",
                value="ON",
                source="EDGE-AUTO",
            )
        )
        snapshot = state.snapshot()
        self.assertEqual(snapshot["temperature_c"], 31.4)
        self.assertEqual(snapshot["fan_state"], "ON")
        self.assertEqual(snapshot["events"][0]["source"], "EDGE-AUTO")

    def test_state_sync_restores_edge_truth(self):
        state = SystemState()
        state.apply_edge_message(
            envelope(
                "state_sync",
                edge_id="EDGE-SBC-01",
                temperature_c=34,
                fan_state="ON",
                policy={
                    "policy_id": "thermal-01",
                    "version": 3,
                    "mode": "AUTO",
                    "threshold_c": 33,
                    "hysteresis_c": 1,
                },
            )
        )
        snapshot = state.snapshot()
        self.assertTrue(snapshot["edge_online"])
        self.assertEqual(snapshot["policy"]["version"], 3)


if __name__ == "__main__":
    unittest.main()
