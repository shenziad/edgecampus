import unittest

from backend.app.protocol import ProtocolError, envelope, validate_message


class ProtocolTests(unittest.TestCase):
    def test_valid_telemetry(self):
        message = envelope(
            "telemetry",
            edge_id="EDGE-SBC-01",
            device_id="TEMP01",
            metric="temperature",
            value=31.4,
            unit="C",
        )
        self.assertIs(validate_message(message), message)

    def test_rejects_renamed_device_field(self):
        message = envelope(
            "telemetry",
            edge_id="EDGE-SBC-01",
            device="TEMP01",
            metric="temperature",
            value=31.4,
            unit="C",
        )
        with self.assertRaisesRegex(ProtocolError, "device_id"):
            validate_message(message)

    def test_rejects_wrong_protocol_version(self):
        message = envelope("hello", edge_id="EDGE-SBC-01")
        message["protocol_version"] = "2.0"
        with self.assertRaisesRegex(ProtocolError, "protocol_version"):
            validate_message(message)

    def test_rejects_invalid_policy_range(self):
        message = envelope(
            "policy",
            policy_id="thermal-01",
            version=2,
            mode="AUTO",
            threshold_c=100,
            hysteresis_c=1,
        )
        with self.assertRaisesRegex(ProtocolError, "threshold_c"):
            validate_message(message)


if __name__ == "__main__":
    unittest.main()
