from gpio import *
from usb import *
from realhttp import *
from time import *

EDGE_ID = "EDGE-SBC-01"
TEMP_ID = "TEMP01"
FAN_ID = "FAN01"
POLICY_ID = "thermal-01"
WS_URL = "ws://127.0.0.1:8000/ws/edge"
PROTOCOL_VERSION = "1.0"

MODE = "AUTO"
THRESHOLD_C = 30.0
HYSTERESIS_C = 1.0
POLICY_VERSION = 1

LOOP_DELAY_MS = 100
TELEMETRY_INTERVAL_MS = 1000
HEARTBEAT_INTERVAL_MS = 5000
TEMP_PRINT_DELTA_C = 0.5

fan_state = "OFF"
current_temp = None
connection_ready = False
hello_sent = False
last_reported_fan_state = "UNKNOWN"
last_control_source = "EDGE-AUTO"
last_printed_temp = None
message_counter = 1
pending_messages = []

client = RealWSClient()


def next_message_id():
    global message_counter
    value = str(message_counter)
    while len(value) < 12:
        value = "0" + value
    message_counter += 1
    return "00000000-0000-4000-8000-" + value


def timestamp():
    # Packet Tracer compatibility: keep a valid ISO-8601 UTC string.
    return "2026-09-16T06:30:00.000+00:00"


def envelope(message_type):
    return (
        '{"type":"' + message_type + '",'
        '"protocol_version":"' + PROTOCOL_VERSION + '",'
        '"message_id":"' + next_message_id() + '",'
        '"timestamp":"' + timestamp() + '"'
    )


def json_value(raw, key):
    marker = '"' + key + '"'
    start = raw.find(marker)
    if start < 0:
        return None
    colon = raw.find(":", start + len(marker))
    if colon < 0:
        return None

    index = colon + 1
    while index < len(raw):
        if raw[index] != " " and raw[index] != "\t":
            break
        index += 1
    if index >= len(raw):
        return None

    if raw[index] == '"':
        index += 1
        end = index
        while end < len(raw):
            if raw[end] == '"':
                return raw[index:end]
            end += 1
        return None

    end = index
    while end < len(raw):
        if raw[end] == "," or raw[end] == "}":
            break
        end += 1
    return raw[index:end].strip()


def write_fan(state):
    if state == "ON":
        customWrite(0, "2")
    else:
        customWrite(0, "0")


def on_connection_change(state):
    global connection_ready
    global hello_sent
    global last_reported_fan_state

    connection_ready = client.connected()
    print("")
    print("WS state: " + str(state))

    if connection_ready:
        print(">>> CLOUD CONNECTED <<<")
        print("Remote: 127.0.0.1:8000")
        hello_sent = False
        last_reported_fan_state = "UNKNOWN"
    else:
        print(">>> CLOUD DISCONNECTED <<<")
        print("Local control remains active.")


def on_receive(data):
    # Callback only queues messages. No delay/blocking here.
    pending_messages.append(str(data))
    print("")
    print(">>> CLOUD MESSAGE RECEIVED <<<")


def send_hello():
    if not client.connected():
        return
    message = envelope("hello") + ',"edge_id":"' + EDGE_ID + '"}'
    client.send(message)
    print("TX HELLO: " + EDGE_ID)


def send_telemetry():
    if not client.connected() or current_temp is None:
        return
    value = round(current_temp, 1)
    message = (
        envelope("telemetry")
        + ',"edge_id":"' + EDGE_ID + '"'
        + ',"device_id":"' + TEMP_ID + '"'
        + ',"metric":"temperature"'
        + ',"value":' + str(value)
        + ',"unit":"C"}'
    )
    client.send(message)
    print("TX TELEMETRY  TEMP=" + str(value) + " C  FAN=" + fan_state)


def send_status(source):
    global last_reported_fan_state
    if not client.connected():
        return
    message = (
        envelope("status")
        + ',"edge_id":"' + EDGE_ID + '"'
        + ',"device_id":"' + FAN_ID + '"'
        + ',"value":"' + fan_state + '"'
        + ',"source":"' + source + '"}'
    )
    client.send(message)
    last_reported_fan_state = fan_state
    print("TX STATUS     FAN=" + fan_state + "  SOURCE=" + source)


def send_heartbeat():
    if not client.connected():
        return
    message = (
        envelope("heartbeat")
        + ',"edge_id":"' + EDGE_ID + '"'
        + ',"status":"ONLINE"'
        + ',"mode":"' + MODE + '"'
        + ',"policy_version":' + str(POLICY_VERSION)
        + '}'
    )
    client.send(message)
    print("TX HEARTBEAT  MODE=" + MODE + "  POLICY=v" + str(POLICY_VERSION))


def send_policy_ack(policy_id, version):
    if not client.connected():
        return
    message = (
        envelope("policy_ack")
        + ',"policy_id":"' + policy_id + '"'
        + ',"version":' + str(version)
        + ',"result":"APPLIED"}'
    )
    client.send(message)
    print("TX POLICY_ACK  v" + str(version) + " APPLIED")


def send_command_ack(command_id, action):
    if not client.connected():
        return
    message = (
        envelope("command_ack")
        + ',"command_id":"' + command_id + '"'
        + ',"device_id":"' + FAN_ID + '"'
        + ',"action":"' + action + '"'
        + ',"result":"APPLIED"}'
    )
    client.send(message)
    print("TX COMMAND_ACK  FAN=" + action + " APPLIED")


def apply_local_control(temp_c):
    global fan_state
    global last_control_source

    previous_state = fan_state
    decision = "MANUAL"

    if MODE == "AUTO":
        if temp_c >= THRESHOLD_C:
            fan_state = "ON"
            if previous_state == "OFF":
                decision = "TURN_ON"
            else:
                decision = "KEEP_ON"
        elif temp_c <= THRESHOLD_C - HYSTERESIS_C:
            fan_state = "OFF"
            if previous_state == "ON":
                decision = "TURN_OFF"
            else:
                decision = "KEEP_OFF"
        else:
            decision = "HOLD"

        if fan_state != previous_state:
            write_fan(fan_state)
            last_control_source = "EDGE-AUTO"
            print("")
            print(">>> LOCAL CONTROL EVENT <<<")
            print(
                "TEMP=" + str(round(temp_c, 1))
                + " C  DECISION=" + decision
                + "  FAN=" + fan_state
            )
    else:
        decision = "MANUAL-HOLD"

    return decision


def print_local_state(temp_c, decision):
    global last_printed_temp

    should_print = False
    if last_printed_temp is None:
        should_print = True
    elif abs(temp_c - last_printed_temp) >= TEMP_PRINT_DELTA_C:
        should_print = True

    if should_print:
        print(
            "LOCAL          TEMP=" + str(round(temp_c, 1))
            + " C  FAN=" + fan_state
            + "  MODE=" + MODE
            + "  TH=" + str(THRESHOLD_C)
            + "  DECISION=" + decision
        )
        last_printed_temp = temp_c


def process_policy(raw):
    global MODE
    global THRESHOLD_C
    global HYSTERESIS_C
    global POLICY_VERSION

    message_protocol = json_value(raw, "protocol_version")
    policy_id = json_value(raw, "policy_id")
    version_text = json_value(raw, "version")
    mode = json_value(raw, "mode")
    threshold_text = json_value(raw, "threshold_c")
    hysteresis_text = json_value(raw, "hysteresis_c")

    if message_protocol != PROTOCOL_VERSION:
        print("POLICY REJECTED: protocol version mismatch")
        return
    if policy_id != POLICY_ID:
        print("POLICY REJECTED: unknown policy_id")
        return

    try:
        new_version = int(version_text)
        new_threshold = float(threshold_text)
        new_hysteresis = float(hysteresis_text)
    except:
        print("POLICY REJECTED: invalid numeric fields")
        return

    if mode != "AUTO" and mode != "MANUAL":
        print("POLICY REJECTED: invalid mode")
        return
    if new_threshold < 0 or new_threshold > 80:
        print("POLICY REJECTED: threshold out of range")
        return
    if new_hysteresis < 0 or new_hysteresis > 10:
        print("POLICY REJECTED: hysteresis out of range")
        return
    if new_version <= POLICY_VERSION:
        print(
            "POLICY IGNORED: stale version v"
            + str(new_version)
            + " <= current v"
            + str(POLICY_VERSION)
        )
        return

    MODE = mode
    THRESHOLD_C = new_threshold
    HYSTERESIS_C = new_hysteresis
    POLICY_VERSION = new_version

    print("")
    print(">>> CLOUD POLICY APPLIED <<<")
    print(
        "POLICY=v" + str(POLICY_VERSION)
        + " MODE=" + MODE
        + " THRESHOLD=" + str(THRESHOLD_C)
        + " C HYSTERESIS=" + str(HYSTERESIS_C)
        + " C"
    )

    if MODE == "AUTO" and current_temp is not None:
        apply_local_control(current_temp)

    send_policy_ack(policy_id, POLICY_VERSION)


def process_command(raw):
    global fan_state
    global last_control_source
    global last_reported_fan_state

    message_protocol = json_value(raw, "protocol_version")
    command_id = json_value(raw, "command_id")
    device_id = json_value(raw, "device_id")
    action = json_value(raw, "action")

    if message_protocol != PROTOCOL_VERSION:
        print("COMMAND REJECTED: protocol version mismatch")
        return
    if device_id != FAN_ID:
        print("COMMAND REJECTED: unsupported device")
        return
    if action != "ON" and action != "OFF":
        print("COMMAND REJECTED: action must be ON/OFF")
        return
    if command_id is None:
        print("COMMAND REJECTED: missing command_id")
        return

    fan_state = action
    write_fan(fan_state)
    last_control_source = "REMOTE-MANUAL"

    print("")
    print(">>> REMOTE MANUAL COMMAND <<<")
    print("FAN=" + fan_state + "  MODE=" + MODE)

    send_status("REMOTE-MANUAL")
    last_reported_fan_state = fan_state
    send_command_ack(command_id, action)

    if MODE == "AUTO":
        print("NOTE: AUTO mode is active; local policy may override this command.")


def process_cloud_message(raw):
    message_type = json_value(raw, "type")

    print("")
    print("RX CLOUD:")
    print(raw)
    print("PARSED TYPE=" + str(message_type))

    if message_type == "policy":
        process_policy(raw)
    elif message_type == "command":
        process_command(raw)
    elif message_type == "error":
        code = json_value(raw, "code")
        message = json_value(raw, "message")
        print("CLOUD ERROR: " + str(code) + " " + str(message))
    else:
        print("CLOUD MESSAGE IGNORED: " + str(message_type))


def main():
    global current_temp
    global hello_sent
    global last_reported_fan_state
    global last_control_source

    usb = USB(0, 9600)
    write_fan("OFF")

    client.onReceive(on_receive)
    client.onConnectionChange(on_connection_change)

    print("")
    print("====================================================")
    print(" EdgeCampus Gate 3 - EDGE-SBC-01")
    print(" Real Edge + Cloud Policy / Command")
    print("====================================================")
    print("Initial Policy : v" + str(POLICY_VERSION))
    print("Mode           : " + MODE)
    print("Threshold      : " + str(THRESHOLD_C) + " C")
    print("Hysteresis     : " + str(HYSTERESIS_C) + " C")
    print("Cloud          : " + WS_URL)
    print("----------------------------------------------------")
    print("Local Loop always has priority over Cloud transport.")
    print("Policy changes runtime AUTO behavior.")
    print("MANUAL mode preserves remote FAN commands.")
    print("====================================================")
    print("")

    client.connect(WS_URL)

    telemetry_elapsed_ms = TELEMETRY_INTERVAL_MS
    heartbeat_elapsed_ms = HEARTBEAT_INTERVAL_MS

    while True:
        # A. Real local loop
        if usb.inWaiting() > 0:
            data = usb.readLine()
            try:
                current_temp = float(data)
                decision = apply_local_control(current_temp)
                print_local_state(current_temp, decision)
            except:
                print("Invalid USB data: " + str(data))

        # B. Cloud downlink: process outside callback
        while len(pending_messages) > 0:
            raw_message = pending_messages.pop(0)
            process_cloud_message(raw_message)

        # C. Cloud uplink
        if connection_ready and client.connected():
            if not hello_sent:
                send_hello()
                hello_sent = True

            if last_reported_fan_state != fan_state:
                send_status(last_control_source)

            if current_temp is not None and telemetry_elapsed_ms >= TELEMETRY_INTERVAL_MS:
                send_telemetry()
                telemetry_elapsed_ms = 0

            if heartbeat_elapsed_ms >= HEARTBEAT_INTERVAL_MS:
                send_heartbeat()
                heartbeat_elapsed_ms = 0

        delay(LOOP_DELAY_MS)
        telemetry_elapsed_ms += LOOP_DELAY_MS
        heartbeat_elapsed_ms += LOOP_DELAY_MS


if __name__ == "__main__":
    main()
