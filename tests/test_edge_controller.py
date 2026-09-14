import unittest

from edge.controller import EdgeController


class EdgeControllerTests(unittest.TestCase):
    def test_auto_control_uses_hysteresis(self):
        controller = EdgeController(threshold_c=30, hysteresis_c=1)
        self.assertEqual(controller.observe_temperature(30), ("ON", True))
        self.assertEqual(controller.observe_temperature(29.5), ("ON", False))
        self.assertEqual(controller.observe_temperature(29), ("OFF", True))

    def test_manual_mode_does_not_override_command(self):
        controller = EdgeController(mode="MANUAL")
        controller.apply_command("ON")
        self.assertEqual(controller.observe_temperature(10), ("ON", False))

    def test_policy_update_changes_version_and_threshold(self):
        controller = EdgeController()
        controller.apply_policy(
            {
                "mode": "AUTO",
                "threshold_c": 33,
                "hysteresis_c": 1.5,
                "version": 4,
            }
        )
        self.assertEqual(controller.policy_version, 4)
        self.assertEqual(controller.threshold_c, 33)
        self.assertEqual(controller.hysteresis_c, 1.5)


if __name__ == "__main__":
    unittest.main()
