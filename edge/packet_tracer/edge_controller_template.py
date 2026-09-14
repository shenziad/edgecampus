"""Packet Tracer SBC logic template — replace TODO adapters only.

Do not change device IDs or message fields without a team RFC.
"""

EDGE_ID = "EDGE-SBC-01"
TEMP_ID = "TEMP01"
FAN_ID = "FAN01"

mode = "AUTO"
threshold_c = 30.0
hysteresis_c = 1.0
policy_version = 1
fan_state = "OFF"


def read_temperature():
    """TODO: map to the verified Packet Tracer sensor API."""
    raise NotImplementedError


def write_fan(state):
    """TODO: map ON/OFF to the verified Packet Tracer actuator API."""
    raise NotImplementedError


def local_control_step():
    """This loop must continue even when the cloud connection is unavailable."""
    global fan_state
    temperature_c = read_temperature()
    target = fan_state
    if mode == "AUTO":
        if temperature_c >= threshold_c:
            target = "ON"
        elif temperature_c <= threshold_c - hysteresis_c:
            target = "OFF"
    if target != fan_state:
        fan_state = target
        write_fan(fan_state)
    return temperature_c, fan_state
