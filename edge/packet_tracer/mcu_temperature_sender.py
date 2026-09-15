from gpio import *
from time import *
from usb import *

def main():
    # MCU USB0 -> SBC USB0
    usb = USB(0, 9600)

    print("MCU temperature sender started")

    while True:
        raw = analogRead(A0)

        # TEMP01: 0~1023 maps to -100 C ~ 100 C
        temp_c = raw * 200.0 / 1023.0 - 100.0
        temp_str = str(round(temp_c, 1))

        print("RAW: " + str(raw) +
              "   TEMP_C: " + temp_str +
              "   USB_TX: " + temp_str)

        # Newline is used as the frame delimiter for SBC readLine().
        usb.write(temp_str + "\n")

        delay(1000)

if __name__ == "__main__":
    main()
