# Gate 2 — D UI & Integration Report

## 1. Owner

- Module: D — UI & Integration
- Branch: `feat/dashboard`
- Gate: Gate 2 — 真实单向 Telemetry + 多园区网络基础层
- Scope:
  - Dashboard real Packet Tracer telemetry validation
  - B+C+D end-to-end integration validation
  - Dashboard evidence
  - Gate 1 regression

本阶段未修改 Protocol v1.0、WebSocket/API 路径、设备 ID、网络冻结项，也未修改 A Network、B Edge、C Backend 的核心实现。

---

## 2. Gate 2 Goal

D 模块在 Gate 2 的目标是将 Gate 1 基于 fake edge 的 Dashboard 验证升级为真实 Packet Tracer Telemetry 验证。

真实链路：

TEMP01
→ IO-MCU-01
→ EDGE-SBC-01
→ RealWSClient
→ FastAPI Backend
→ Dashboard

需要验证：

- Dashboard 能显示真实 TEMP01 温度；
- EDGE-SBC-01 显示 ONLINE；
- Control Mode 为 AUTO；
- Policy Version / threshold / hysteresis 保持正确；
- 正常温度显示 NORMAL；
- 高于阈值后显示 WARNING；
- FAN01 ON/OFF 与 Edge 实际控制状态一致；
- Event Stream 持续显示真实 SENSOR Telemetry；
- Backend 中能够观察到 SENSOR / EDGE-AUTO 事件。

---

## 3. Validation Environment

Dashboard branch: `feat/dashboard`

Dashboard baseline: `4343fcf`

Backend Gate 2 branch:

- `origin/feat/backend`
- `ab562be`

Backend start command:

`python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`

Dashboard:

`http://127.0.0.1:8000`

Protocol Version: `1.0`

Policy:

- mode = AUTO
- threshold_c = 30.0
- hysteresis_c = 1.0
- version = 1

---

## 4. Real Telemetry Integration Validation

真实 Packet Tracer TEMP01 数据成功通过 MCU 和 EDGE-SBC-01 进入 Backend。

Backend `/api/state` 实测：

- `edge_online = true`
- `cloud_state = CONNECTED`
- `temperature_c` 为真实 PT 温度
- `fan_state = OFF / ON`
- `control_mode = AUTO`

事件记录持续出现：

- `TEMPERATURE / SENSOR`
- `FAN / EDGE-AUTO / ON`
- `FAN / EDGE-AUTO / OFF`

说明真实 Packet Tracer 状态已正确进入 Backend 并更新 SystemState。

Result: **PASS**

---

## 5. Dashboard Browser Validation

### G2-D-01 — Real PT Normal State

Evidence:

`evidence/dashboard/gate2/G2-D-01-dashboard-normal-real-pt-pass.png`

实测：

- Temperature ≈ 27.9 C
- Thermal State = NORMAL
- EDGE-SBC-01 = ONLINE
- Control Mode = AUTO
- Cloud State = CONNECTED
- Policy Version = v1
- FAN01 = OFF
- Event Stream 持续显示 `TEMPERATURE / SENSOR`

Result: **PASS**

### G2-D-02 — Real PT Warning + Fan ON

Evidence:

`evidence/dashboard/gate2/G2-D-02-dashboard-warning-fan-on-real-pt-pass.png`

实测：

- Temperature ≈ 34.1 C
- Thermal State = WARNING
- EDGE-SBC-01 = ONLINE
- Control Mode = AUTO
- Cloud State = CONNECTED
- Policy Version = v1
- FAN01 = ON
- Event Stream 持续显示 `TEMPERATURE / SENSOR`

结合 Backend 中的 `FAN / EDGE-AUTO / ON` 记录，可以确认温度越过 30.0 C 阈值后，Edge 本地 AUTO 控制打开 FAN01，并将实际状态同步至 Backend 和 Dashboard。

Result: **PASS**

---

## 6. Gate 1 Regression

执行：

`python -m compileall backend edge tests`

`python -m unittest discover -s tests -v`

结果：

- Repository Tests: 14 / 14 PASS
- Dashboard Contract Tests: 5 / 5 PASS

Result: **PASS**

---

## 7. Truthfulness Boundary

本次真实 Telemetry 路径为：

Packet Tracer TEMP01
→ MCU
→ EDGE-SBC-01
→ External Network Access / RealWSClient
→ Real FastAPI Backend
→ Dashboard

RealWSClient 属于带外 Edge–Cloud 控制通道。

本报告不将真实 WebSocket 描述为经过 Packet Tracer 中模拟的 VLAN、WAN、OSPF、BGP、NAT 或 IPv6 Tunnel。

---

## 8. Public Contract Check

本阶段未修改：

- Protocol Version `1.0`
- `/ws/dashboard`
- `/ws/edge`
- `EDGE-SBC-01`
- `TEMP01`
- `FAN01`
- `thermal-01`
- 温度单位 `C`
- Policy 字段与默认语义
- 公共 JSON 字段
- Final Architecture v2 网络冻结项

Public Contract Impact: **NONE**

---

## 9. Gate 2 D Conclusion

完成内容：

- Real PT Telemetry → Dashboard：PASS
- Real Normal State：PASS
- Real Threshold WARNING：PASS
- FAN OFF / ON Dashboard Sync：PASS
- Edge ONLINE：PASS
- AUTO / CONNECTED / Policy v1：PASS
- SENSOR Event Stream：PASS
- Backend SENSOR / EDGE-AUTO Event：PASS
- Gate 1 Regression：14 / 14 PASS

真实温度变化验证：

27.9 C → NORMAL → FAN OFF

34.1 C → WARNING → FAN ON

D Gate 2 Status: **PASS**

D-side Blocker: **NONE**

Public Contract Impact: **NONE**

下一动作：等待 Gate 2 全组 Definition of Done 汇总；Gate 3 再进行 Dashboard Policy / Command → Backend → Edge → ACK 的真实闭环验收。
