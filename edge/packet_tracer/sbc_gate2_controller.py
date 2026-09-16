from gpio import *
from usb import *
from realhttp import *
from time import *

# EdgeCampus Gate 2 - verified Packet Tracer 9.0.1 controller
#
# Local control always runs before the optional cloud send path.  Packet
# Tracer RealWSClient callbacks must not call delay() or another suspending API.

EDGE_ID = "EDGE-SBC-01"
TEMP_ID = "TEMP01"
FAN_ID = "FAN01"
WS_URL = "ws://127.0.0.1:8000/ws/edge"

MODE = "AUTO"
THRESHOLD_C = 30.0
HYSTERESIS_C = 1.0
POLICY_VERSION = 1

TELEMETRY_INTERVAL_MS = 1000
HEARTBEAT_INTERVAL_MS = 5000
LOOP_DELAY_MS = 100

fan_state = "OFF"
connection_ready = False


def set_fan(state):
    """Map Protocol ON/OFF to Packet Tracer FAN01 physical values."""
    if state == "ON":
        customWrite(0, "2")
    else:
        customWrite(0, "0")


def on_connection_change(state):
    """Record connection state only; callbacks may not suspend in PT."""
    global connection_ready
    connection_ready = client.connected()
    print("WS state: " + str(state))
    if connection_ready:
        print("CONNECTED")
    else:
        print("DISCONNECTED - local loop continues")


def envelope(message_type, message_id, timestamp):
    return (
        '{"type":"' + message_type + '",'
        '"protocol_version":"1.0",'
        '"message_id":"' + message_id + '",'
        '"timestamp":"' + timestamp + '"'
    )


def send_hello():
    message = (
        envelope(
            "hello",
            "11111111-1111-4111-8111-111111111111",
            "2026-09-15T13:15:00.000+00:00",
        )
        + ',"edge_id":"' + EDGE_ID + '"}'
    )
    client.send(message)
    print("TX HELLO")


def send_telemetry(temp_c):
    message = (
        envelope(
            "telemetry",
            "22222222-2222-4222-8222-222222222222",
            "2026-09-15T13:29:00.000+00:00",
        )
        + ',"edge_id":"' + EDGE_ID + '"'
        + ',"device_id":"' + TEMP_ID + '"'
        + ',"metric":"temperature"'
        + ',"value":' + str(round(temp_c, 1))
        + ',"unit":"C"}'
    )
    client.send(message)
    print("TX TELEMETRY: TEMP=" + str(round(temp_c, 1)) + " C")


def send_status():
    message = (
        envelope(
            "status",
            "33333333-3333-4333-8333-333333333333",
            "2026-09-15T13:29:00.010+00:00",
        )
        + ',"edge_id":"' + EDGE_ID + '"'
        + ',"device_id":"' + FAN_ID + '"'
        + ',"value":"' + fan_state + '"'
        + ',"source":"EDGE-AUTO"}'
    )
    client.send(message)
    print("TX FAN STATUS: " + fan_state)


def send_heartbeat():
    message = (
        envelope(
            "heartbeat",
            "44444444-4444-4444-8444-444444444444",
            "2026-09-15T13:30:00.000+00:00",
        )
        + ',"edge_id":"' + EDGE_ID + '"'
        + ',"status":"ONLINE"'
        + ',"mode":"' + MODE + '"'
        + ',"policy_version":' + str(POLICY_VERSION) + '}'
    )
    client.send(message)
    print("TX HEARTBEAT")


def main():
    global fan_state

    usb = USB(0, 9600)
    set_fan("OFF")

    client.onConnectionChange(on_connection_change)
    client.connect(WS_URL)

    hello_sent = False
    cloud_fan_state = "UNKNOWN"
    telemetry_elapsed_ms = TELEMETRY_INTERVAL_MS
    heartbeat_elapsed_ms = HEARTBEAT_INTERVAL_MS

    while True:
        if usb.inWaiting() > 0:
            data = usb.readLine()
            try:
                temp_c = float(data)
                previous_state = fan_state
                decision = "HOLD"

                # Local Loop is deliberately evaluated before cloud state.
                if temp_c >= THRESHOLD_C:
                    fan_state = "ON"
                    decision = "TURN_ON"
                elif temp_c <= THRESHOLD_C - HYSTERESIS_C:
                    fan_state = "OFF"
                    decision = "TURN_OFF"

                if fan_state != previous_state:
                    set_fan(fan_state)

                print(
                    "LOCAL TEMP: " + str(round(temp_c, 1))
                    + " C FAN=" + fan_state
                    + " DECISION=" + decision
                )

                # Cloud is an optional side path; failure never gates FAN control.
                if connection_ready and client.connected():
                    if not hello_sent:
                        send_hello()
                        hello_sent = True

                    if fan_state != cloud_fan_state:
                        send_status()
                        cloud_fan_state = fan_state

                    if telemetry_elapsed_ms >= TELEMETRY_INTERVAL_MS:
                        send_telemetry(temp_c)
                        telemetry_elapsed_ms = 0

                    if heartbeat_elapsed_ms >= HEARTBEAT_INTERVAL_MS:
                        send_heartbeat()
                        heartbeat_elapsed_ms = 0

            except:
                print("Invalid USB data: " + str(data))

        delay(LOOP_DELAY_MS)
        telemetry_elapsed_ms += LOOP_DELAY_MS
        heartbeat_elapsed_ms += LOOP_DELAY_MS


client = RealWSClient()

if __name__ == "__main__":
    main()
