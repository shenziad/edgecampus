import unittest
from copy import deepcopy
from backend.app.protocol import ProtocolError, envelope, validate_message
from backend.app.state import SystemState


class Gate4StabilityTests(unittest.TestCase):
    def sync(self):
        return envelope("state_sync", edge_id="EDGE-SBC-01", temperature_c=31.8,
                        fan_state="OFF", policy={"policy_id": "thermal-01", "version": 2,
                        "mode": "AUTO", "threshold_c": 33, "hysteresis_c": 1})

    def test_malformed_types_reject_without_type_error(self):
        for kind in ([], {}, True, None, "unsupported"):
            message = envelope("hello", edge_id="EDGE-SBC-01")
            message["type"] = kind
            with self.subTest(kind=kind), self.assertRaises(ProtocolError):
                validate_message(message)

    def test_missing_envelope_rejected(self):
        for field in ("message_id", "timestamp"):
            for value in (None, "", "   "):
                message = self.sync()
                message[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ProtocolError):
                    validate_message(message)

    def test_state_sync_rejects_invalid_restore_fields(self):
        for field, value in (("temperature_c", True), ("fan_state", []), ("policy", [])):
            message = self.sync()
            message[field] = value
            with self.subTest(field=field), self.assertRaises(ProtocolError):
                validate_message(message)

    def test_nested_policy_validation(self):
        for field, value in (("policy_id", "other"), ("version", True), ("version", 0),
                             ("mode", []), ("threshold_c", True), ("threshold_c", 81),
                             ("hysteresis_c", True), ("hysteresis_c", -1)):
            message = self.sync()
            message["policy"][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ProtocolError):
                validate_message(message)

    def test_restore_after_disconnect_preserves_edge_policy_and_owns_copy(self):
        state = SystemState()
        message = validate_message(self.sync())
        expected_policy = deepcopy(message["policy"])
        state.apply_edge_message(message)
        state.mark_edge_offline()
        self.assertFalse(state.edge_online)
        self.assertEqual(state.cloud_state, "DISCONNECTED")
        state.apply_edge_message(message)
        message["policy"]["threshold_c"] = 30
        self.assertTrue(state.edge_online)
        self.assertEqual(state.policy, expected_policy)
        self.assertEqual(state.temperature_c, 31.8)
        self.assertEqual(state.fan_state, "OFF")
        self.assertEqual(state.events[0]["event"], "STATE_SYNC")

    def test_uplink_numeric_fields_reject_bool(self):
        messages = [envelope("telemetry", edge_id="EDGE-SBC-01", device_id="TEMP01",
                            metric="temperature", value=True, unit="C"),
                    envelope("heartbeat", edge_id="EDGE-SBC-01", status="ONLINE",
                            mode="AUTO", policy_version=True)]
        for message in messages:
            with self.subTest(kind=message["type"]), self.assertRaises(ProtocolError):
                validate_message(message)

    def test_fresh_backend_default_is_replaced_by_state_sync(self):
        state = SystemState()
        self.assertEqual(state.policy["version"], 1)
        state.apply_edge_message(validate_message(self.sync()))
        self.assertEqual(state.policy["version"], 2)
        self.assertEqual(state.policy["threshold_c"], 33)


if __name__ == "__main__":
    unittest.main()
