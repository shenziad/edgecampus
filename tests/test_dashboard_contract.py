import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "dashboard" / "index.html"
APP_JS = ROOT / "dashboard" / "app.js"


class DashboardContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8")
        cls.js = APP_JS.read_text(encoding="utf-8")

    def test_gate1_required_dashboard_elements_exist(self):
        """Gate 1 页面必须包含现场验收所需的核心状态与控制元素。"""
        required_ids = [
            "socketBadge",
            "temperature",
            "thermalState",
            "edgeState",
            "controlMode",
            "cloudState",
            "policyVersion",
            "heartbeat",
            "fanState",
            "policyForm",
            "policyMode",
            "threshold",
            "hysteresis",
            "policyAck",
            "commandAck",
            "events",
            "eventCount",
        ]

        for element_id in required_ids:
            with self.subTest(element_id=element_id):
                self.assertRegex(
                    self.html,
                    rf'id=["\']{re.escape(element_id)}["\']',
                    f"Dashboard missing required element #{element_id}",
                )

    def test_public_contract_constants_are_preserved(self):
        """D 不得擅自修改冻结的协议版本、WS 路径和设备/策略 ID。"""
        required_contract_tokens = [
            'const protocolVersion = "1.0"',
            "/ws/dashboard",
            '"FAN01"',
            '"thermal-01"',
        ]

        for token in required_contract_tokens:
            with self.subTest(token=token):
                self.assertIn(token, self.js)

    def test_warning_and_offline_rendering_exist(self):
        """Gate 1 必须能表现阈值告警以及 Edge 在线/离线状态。"""
        self.assertIn(
            "temperature >= state.policy.threshold_c",
            self.js,
        )
        self.assertIn(
            'state.edge_online ? "ONLINE" : "OFFLINE"',
            self.js,
        )
        self.assertIn(
            '"WARNING · 达到阈值"',
            self.js,
        )

    def test_policy_form_keeps_frozen_ranges(self):
        """策略表单保留项目定义的阈值与迟滞范围。"""
        self.assertRegex(
            self.html,
            r'id="threshold"[^>]*min="0"[^>]*max="80"',
        )
        self.assertRegex(
            self.html,
            r'id="hysteresis"[^>]*min="0"[^>]*max="10"',
        )

    def test_event_stream_rendering_exists(self):
        """Dashboard 必须能够持续渲染 Backend 提供的事件。"""
        self.assertIn("function renderEvents(events)", self.js)
        self.assertIn("item.event", self.js)
        self.assertIn("item.source", self.js)
        self.assertIn("item.detail", self.js)

    def test_gate3_ack_rendering_exists(self):
        """Gate 3 Dashboard 必须明确展示 Policy / Command ACK。"""
        self.assertIn('"POLICY_ACK"', self.js)
        self.assertIn('"COMMAND_ACK"', self.js)
        self.assertIn('"policyAck"', self.js)
        self.assertIn('"commandAck"', self.js)

    def test_gate3_policy_and_command_contract_is_preserved(self):
        """Gate 3 下发仍必须沿用冻结的 Protocol v1.0 字段。"""
        self.assertIn('envelope("policy"', self.js)
        self.assertIn('policy_id: "thermal-01"', self.js)
        self.assertIn("threshold_c:", self.js)
        self.assertIn("hysteresis_c:", self.js)
        self.assertIn('envelope("command"', self.js)
        self.assertIn('device_id: "FAN01"', self.js)
        self.assertIn("command_id:", self.js)


if __name__ == "__main__":
    unittest.main()
