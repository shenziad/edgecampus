import unittest
from backend.app.state import SystemState
from backend.app.protocol import envelope, validate_message

class AckRetentionTests(unittest.TestCase):
    def test_real_command_ack_survives_telemetry_flood(self):
        state = SystemState()
        ack = envelope('command_ack', command_id='test-command', device_id='FAN01', action='ON', result='APPLIED')
        state.apply_edge_message(validate_message(ack))
        state.apply_edge_message(envelope('policy_ack', policy_id='thermal-01', version=3, result='APPLIED'))
        for _ in range(250):
            state.apply_edge_message(envelope('telemetry', edge_id='EDGE-SBC-01', device_id='TEMP01', metric='temperature', value=31.8, unit='C'))
        events = state.snapshot()['events']
        self.assertEqual(len(events), 100)
        self.assertIn('FAN01 ON APPLIED', [e['detail'] for e in events])
        self.assertIn('v3 APPLIED', [e['detail'] for e in events])

    def test_control_only_history_remains_bounded_and_newest_first(self):
        state = SystemState()
        for i in range(150):
            state.add_event('COMMAND_ACK', 'EDGE', str(i))
        self.assertEqual(len(state.events), 100)
        self.assertEqual(state.events[0]['detail'], '149')
        self.assertEqual(state.events[-1]['detail'], '50')
