# D — UI & Integration Branch Index

## Branch Information

- Owner: D — UI & Integration
- Working branch: `feat/dashboard`
- Current project status: **ACCEPTANCE COMPLETE — REPORT PREPARATION**
- Gate 1 D status: **PASS**
- Gate 2 D status: **PASS**
- Final Architecture baseline: **v2 / final accepted baseline**

D 长期负责 `dashboard/`、Dashboard 自动测试、`evidence/dashboard/`、D-side Gate 报告和端到端展示证据。D 不直接修改 A Network、B Edge、C Backend 核心实现，也不直接修改 Public Contract。

## Archived Deliverables

Gate 1：

```text
docs/gate1/D_DASHBOARD_REPORT.md
evidence/dashboard/gate1/
tests/test_dashboard_contract.py
```

Gate 2：

```text
docs/gate2/D_DASHBOARD_REPORT.md
evidence/dashboard/gate2/
├── G2-D-01-dashboard-normal-real-pt-pass.png
└── G2-D-02-dashboard-warning-fan-on-real-pt-pass.png
```

Gate 2 已验证真实：

```text
TEMP01 → MCU → EDGE-SBC-01 → RealWSClient → Backend → Dashboard
27.9 C → NORMAL / FAN OFF
34.1 C → WARNING / FAN ON
```

提交时完整仓库测试 14/14 PASS，Dashboard contract tests 5/5 PASS。

## Archived Gate 3 D Mission（历史）

目标：把已有 Policy / Command UI 从 fake 联调升级为真实 PT Edge 双向闭环。

核心路径：

```text
Dashboard Policy / Command
        ↓ /ws/dashboard
Backend
        ↓ /ws/edge
Real EDGE-SBC-01
        ↓
policy_ack / command_ack
        ↓
Backend → Dashboard / Event Stream
```

D 需验证：

1. Policy 表单把 threshold 30→33、version 1→2，传输字段保持 Protocol v1.0。
2. Dashboard 能看到 Policy 被 APPLIED、version/threshold 更新和 ACK/事件。
3. 新策略下真实 32 C 为 FAN OFF、34 C 为 FAN ON。
4. FAN01 手动 ON/OFF Command 能真实执行并收到 `command_ack`。
5. `REMOTE-MANUAL`、`EDGE-AUTO`、Policy 事件来源可解释。
6. Gate2 Telemetry、ONLINE/OFFLINE、WARNING、Event Stream 不退化。

## Public Contract Status

不得改：Protocol `1.0`、`/ws/dashboard`、`/ws/edge`、设备 ID、`thermal-01`、公共 JSON 字段、温度单位 `C`、Final Architecture v2 网络冻结项。

Dashboard 可以改变展示文案，但不得重命名传输字段。

## Truthfulness Boundary

RealWSClient → FastAPI 是带外控制通道；不得暗示真实 WebSocket 经过 Packet Tracer WAN / OSPF / BGP / NAT / Tunnel。

## Final D Evidence — 2026-09-19

D01–D13 已完成（13/13），最终证据归档于：

```text
evidence/final_report/D/
```

覆盖最终中文 Dashboard、Branch 检查、Campus Policy + Policy ACK、安全事件、Cloud Failure、本地自治 FAN、恢复 state_sync，以及 Network Failure 禁用/409。权威完成状态见 `docs/final/EVIDENCE_PENDING.md` 与 `docs/FINAL_REPORT_SCREENSHOT_CHECKLIST.md`。

## Next Action

D 不再开发新功能；保持 Protocol v1.0、真实性边界和现有 Dashboard 行为。后续仅配合最终报告整合、答辩素材引用和必要的回归确认。
