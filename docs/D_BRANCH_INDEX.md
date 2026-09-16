# D — UI & Integration Branch Index

## Branch Information

- Owner: D — UI & Integration
- Working branch: `feat/dashboard`
- Current project Gate: **Gate 2**
- Gate 1 D status: **PASS**
- Gate 2 D status: **PASS**
- Final Architecture baseline: **v2**

D 长期负责：

- `dashboard/`
- Dashboard 相关自动测试
- `evidence/dashboard/`
- D-side Gate validation reports
- 端到端展示与验收证据整合

D 不直接修改 A Network、B Edge、C Backend 核心实现，也不直接修改 Public Contract。

## Gate 1 Archived Deliverables

```text
docs/gate1/D_DASHBOARD_REPORT.md

evidence/dashboard/gate1/
├── G1-D-01-dashboard-normal-pass.png
├── G1-D-02-dashboard-warning-pass.png
├── G1-D-03-edge-offline-pass.png
└── G1-D-04-reconnect-state-sync-pass.png

tests/test_dashboard_contract.py
```

Gate 1 已验证：Dashboard Normal、Threshold WARNING、Edge Offline、Reconnect / State Sync；D 新增 Dashboard contract tests 5/5 PASS，提交时完整仓库测试 14/14 PASS。

## Gate 2 Archived Deliverables

```text
docs/gate2/D_DASHBOARD_REPORT.md

evidence/dashboard/gate2/
├── G2-D-01-dashboard-normal-real-pt-pass.png
└── G2-D-02-dashboard-warning-fan-on-real-pt-pass.png
```

Gate 2 D-side 已验证真实 PT TEMP01 → MCU → EDGE-SBC-01 → RealWSClient → Backend → Dashboard。
实测 27.9 C 为 NORMAL / FAN OFF，34.1 C 为 WARNING / FAN ON；Gate 1 软件回归 14/14 PASS。

## Public Contract Status

D 不得改动：

- Protocol Version `1.0`
- `/ws/dashboard`
- `/ws/edge`
- `EDGE-SBC-01`
- `TEMP01`
- `FAN01`
- `thermal-01`
- 公共 JSON 字段
- Final Architecture v2 冻结网络项

Dashboard 可以翻译展示文案，但传输字段不能重命名。

## Gate 2 D Mission

当前目标不是继续做视觉包装，而是证明 Dashboard 展示的是**真实 Packet Tracer TEMP01 Telemetry**。

关键路径：

```text
TEMP01
→ MCU
→ EDGE-SBC-01
→ RealWSClient
→ FastAPI
→ Dashboard
```

D 需要验证并留证：

1. Edge ONLINE / OFFLINE 显示正确；
2. Dashboard 温度与 PT TEMP01 的实际变化一致；
3. 约 28 C 时为 NORMAL；约 32 C 时出现 WARNING；
4. Fan 状态与 Edge 实际状态一致；
5. Policy Version / threshold / hysteresis 保持正确；
6. Event Stream 出现 SENSOR / EDGE-AUTO 等可解释事件；
7. fake edge 路径仍可作为独立开发替身。

Gate 2 不要求真实 Policy 已作用于 PT Edge；该项属于 Gate 3。

## Truthfulness Boundary

Packet Tracer VLAN / OSPF / BGP / NAT / Tunnel 是模拟 Data Plane；`RealWSClient` 到真实 FastAPI 是带外控制通道。Dashboard 文案、截图说明和报告不得暗示真实 WebSocket 经过 Packet Tracer WAN。

## Update Rule

每完成一个 Gate，更新：

- 新增/修改文件；
- Evidence 数量和路径；
- 自动测试结果；
- Public Contract 是否变化；
- 当前阻塞项；
- 下一步 Integration 动作。

当前 D 下一动作：Gate 2 D-side 已 PASS；等待全组 Gate 2 Definition of Done。进入 Gate 3 后执行 Dashboard Policy / Command → Backend → Edge → ACK 真实闭环验收。
