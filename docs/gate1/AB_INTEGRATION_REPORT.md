# Gate 1 — A+B Integration Check

## Baseline

- Base branch: `feat/network`
- Integrated module: `feat/edge`
- Canonical Packet Tracer topology remains A-owned: `packet_tracer/EdgeCampus.pkt`
- Packet Tracer version: 9.0.1

## Minimal integration scope

A's network baseline is kept unchanged. B is integrated only around the existing `EDGE-SBC-01`:

```text
TEMP01 A0 -> IO-MCU-01 A0
IO-MCU-01 USB0 -> EDGE-SBC-01 USB0
EDGE-SBC-01 D0 -> FAN01 D0  (Custom Cable)
```

No VLAN, IP, trunk, EtherChannel, SVI, DHCP, ACL, access-port or public protocol contract was changed.

## Regression checks performed

### 1. Access-layer baseline

```text
SW-ACCESS# show etherchannel summary
SW-ACCESS# show interfaces trunk
SW-ACCESS# show vlan brief
```

Result: PASS

- `Po1(SU)` remains up/in use.
- Member links remain bundled.
- VLAN 10/20/30 remain allowed on the trunk.
- `Fa0/2` remains in VLAN 20 for `EDGE-SBC-01`.

### 2. Core-layer baseline

```text
SW-CORE# show ip interface brief
SW-CORE# show ip route
SW-CORE# show access-lists
```

Result: PASS

- VLAN 10/20/30 SVIs remain up/up.
- Three directly connected `/24` networks remain present.
- `OFFICE-IN` and `IOT-IN` remain active.

### 3. Network behavior after integration

```text
OFFICE-PC> ping 192.168.30.20
```

Result: PASS — OFFICE -> ADMIN remains reachable.

```text
OFFICE-PC> ping 192.168.20.10
```

Result: PASS — expected deny; OFFICE -> IOT remains blocked by ACL.

```text
ADMIN-PC> ping 192.168.20.10
```

Result: PASS — MANAGEMENT -> EDGE-SBC-01 remains reachable.

### 4. B local autonomy after integration

Observed sequence:

```text
30.2 C -> TURN_ON  -> FAN ON
29.4 C -> HOLD     -> FAN ON
28.6 C -> TURN_OFF -> FAN OFF
```

Result: PASS

This confirms that the hysteresis loop still works after being placed into A's canonical network baseline.

### 5. Backend-off autonomy

Previously verified evidence remains valid:

```text
Test-NetConnection 127.0.0.1 -Port 8000
TcpTestSucceeded : False
```

while the Packet Tracer local loop continued to control `FAN01`.

Result: PASS

## Integration conclusion

A+B Gate 1 integration passed with the intended minimal-change strategy:

```text
A network baseline unchanged
        +
B local Edge loop added behind EDGE-SBC-01
        =
A+B integrated Gate 1 baseline
```

No public contract change was required.
