from gpio import *
from usb import *
from time import *

# EdgeCampus Gate 1 - B Edge Local Controller
# Packet Tracer 9.0.1
#
# MCU USB0 -> SBC USB0
# SBC D0   -> FAN01 D0
#
# AUTO policy:
#   TEMP >= 30.0 C       -> FAN ON
#   TEMP <= 29.0 C       -> FAN OFF
#   29.0 C < TEMP < 30 C -> keep previous state

MODE = "AUTO"
THRESHOLD_C = 30.0
HYSTERESIS_C = 1.0
POLICY_VERSION = 1

fan_state = "OFF"


def set_fan(state):
    """Map public ON/OFF state to Packet Tracer FAN01 actuator values."""
    if state == "ON":
        customWrite(0, "2")   # FAN01 high speed
    else:
        customWrite(0, "0")   # FAN01 off


def main():
    global fan_state

    usb = USB(0, 9600)

    # Deterministic startup state.
    set_fan("OFF")

    print("==============================================")
    print(" EdgeCampus Gate 1 - Local Edge Controller")
    print(" Packet Tracer: 9.0.1")
    print("==============================================")
    print("MODE           : " + MODE)
    print("THRESHOLD_C    : " + str(THRESHOLD_C))
    print("HYSTERESIS_C   : " + str(HYSTERESIS_C))
    print("POLICY_VERSION : " + str(POLICY_VERSION))
    print("----------------------------------------------")
    print("TEMP >= 30.0C        -> FAN ON")
    print("TEMP <= 29.0C        -> FAN OFF")
    print("29.0C < TEMP < 30.0C -> HOLD")
    print("----------------------------------------------")

    while True:
        if usb.inWaiting() > 0:
            data = usb.readLine()

            try:
                temp_c = float(data)
                previous_state = fan_state
                decision = "HOLD"

                if MODE == "AUTO":
                    if temp_c >= THRESHOLD_C:
                        fan_state = "ON"
                        decision = "TURN_ON"
                    elif temp_c <= THRESHOLD_C - HYSTERESIS_C:
                        fan_state = "OFF"
                        decision = "TURN_OFF"
                    else:
                        # Hysteresis band: preserve the previous actuator state.
                        decision = "HOLD"

                if fan_state != previous_state:
                    set_fan(fan_state)

                print(
                    "TEMP_C: " + str(round(temp_c, 1)) +
                    "   MODE: " + MODE +
                    "   DECISION: " + decision +
                    "   FAN: " + fan_state +
                    "   POLICY: v" + str(POLICY_VERSION)
                )

            except:
                print("Invalid USB data: " + str(data))

        delay(100)


if __name__ == "__main__":
    main()
