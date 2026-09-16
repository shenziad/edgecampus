import asyncio
import json
import sys
from uuid import uuid4
from datetime import datetime, timezone

import websockets


WS_URL = "ws://127.0.0.1:8000/ws/dashboard"


def base_message(message_type):
    return {
        "type": message_type,
        "protocol_version": "1.0",
        "message_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def send_case(name, message):
    print()
    print("=" * 70)
    print("CASE:", name)
    print("TX:")
    print(json.dumps(message, indent=2, ensure_ascii=False))

    async with websockets.connect(WS_URL) as ws:
        # Dashboard WS connects and receives an initial snapshot first.
        initial = await ws.recv()

        print()
        print("Initial snapshot received.")

        await ws.send(json.dumps(message))

        response = await asyncio.wait_for(ws.recv(), timeout=5)

        print()
        print("RX:")
        print(response)

        parsed = json.loads(response)

        if parsed.get("type") == "error" and parsed.get("code") == "INVALID_MESSAGE":
            print()
            print(
                "PASS:",
                parsed.get("code"),
                "-",
                parsed.get("message"),
            )
            return True

        print()
        print("FAIL: expected error response")
        return False


async def main():
    results = []

    # ---------------------------------------------------------
    # Case 1
    # Malformed Policy:
    # required threshold_c is deliberately missing.
    # ---------------------------------------------------------

    malformed = base_message("policy")

    malformed.update(
        {
            "policy_id": "thermal-01",
            "version": 999,
            "mode": "AUTO",
            # threshold_c deliberately missing
            "hysteresis_c": 1.0,
        }
    )

    results.append(
        await send_case(
            "MALFORMED / MISSING FIELD",
            malformed,
        )
    )

    # ---------------------------------------------------------
    # Case 2
    # Unsupported message type
    # ---------------------------------------------------------

    unsupported = base_message(
        "totally_unknown_message"
    )

    results.append(
        await send_case(
            "UNSUPPORTED MESSAGE TYPE",
            unsupported,
        )
    )

    # ---------------------------------------------------------
    # Case 3
    # Wrong protocol version
    # ---------------------------------------------------------

    wrong_version = base_message("command")

    wrong_version.update(
        {
            "protocol_version": "9.9",
            "command_id": str(uuid4()),
            "device_id": "FAN01",
            "action": "ON",
        }
    )

    results.append(
        await send_case(
            "WRONG PROTOCOL VERSION",
            wrong_version,
        )
    )

    print()
    print("=" * 70)

    if all(results):
        print("G4-SW-03 RESULT: PASS")
        print("All invalid messages were safely rejected.")
        return 0
    else:
        print("G4-SW-03 RESULT: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))