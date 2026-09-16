# 验证记录 — Final Architecture v2

## 1. 软件基线历史验证

初始化 / fake 阶段已验证：

- Python 全量语法编译；
- Protocol v1.0 字段 / 版本 / 范围校验；
- Edge 迟滞控制、MANUAL 保持、Policy 更新；
- Backend 状态 / State Sync；
- 公共契约漂移检查；
- Backend + Fake Edge + Dashboard WebSocket 联调；
- Dashboard Policy / Command → Fake Edge → ACK；
- fake Cloud 停止后本地控制继续；
- fake Cloud 恢复后重连 + `state_sync`。

这些是开发基线，不替代真实 PT Gate 验收。

## 2. Gate 0 — COMPLETE

已实机验证：

- Packet Tracer 设备型号 / HQ 端口；
- `EDGE-SBC-01` FastEthernet 模块；
- External Network Access / RealWSClient → `ws://127.0.0.1:8000/ws/edge`；
- FastAPI 接受 Edge connection；
- `/api/state` connected；
- 保存关闭再打开 `.pkt` 后可再次连接。

## 3. Gate 1

### A Network — PASS

VLAN10/20/30、Access、LACP EtherChannel、Trunk、SVI/IP routing、OFFICE DHCP、HQ ACL 与关键行为矩阵均通过。

### B Edge — PASS

真实 PT Local Loop：

```text
TEMP01 A0 → IO-MCU-01 A0 → USB0 → EDGE-SBC-01 → D0 → FAN01
```

迟滞和 Backend-off local autonomy 已验证。

### A+B Integration — PASS

canonical 基线合入后网络与 Edge regression 无退化。

### D Dashboard — PASS

Gate1 NORMAL / WARNING / OFFLINE / RECONNECT evidence 已归档；Dashboard contract tests 5/5 PASS。

### C Control Plane — CORE PASS / STABILITY PENDING

已提交：

- unit tests；
- `/ws/edge` fake edge connection；
- `/healthz`；
- `/api/state` telemetry / temperature；
- AUTO FAN events。

仍欠：

- malformed / wrong-version / unsupported message 拒绝且服务不崩；
- Edge 停止后 offline；
- reconnect + `state_sync`。

管理状态：**CLOSED-WITH-PENDING-STABILITY**。三项欠账 Gate5 前必须清零。

## 4. Gate 2 — COMPLETE

### A Network Foundation — PASS

已验证：

- 新增 7 条冻结链路与接口映射；
- Branch VLAN40 / VLAN50；
- SW-BRANCH trunk / access / management SVI；
- R-BRANCH Router-on-a-Stick；
- BR-OFFICE DHCP、BR-ADMIN 管理地址；
- HQ Transit、HQ↔ISP、ISP↔Branch、Internet LAN IPv4 Underlay；
- 四段相邻三层连通；
- HQ Gate1 EtherChannel / trunk / VLAN / SVI / ACL / 行为 regression 无退化。

证据：`docs/gate2/A_NETWORK_REPORT.md` 与 `evidence/network/G2-A-*`。

### B Edge Real Telemetry — PASS

已验证：

- RealWSClient connected；
- Protocol v1 hello；
- 固定 telemetry；
- 真实 TEMP01 telemetry；
- Local AUTO + Telemetry + FAN Status + Heartbeat 同时运行；
- 高温真实 FAN01 PT state=2，协议状态为 `ON`；
- Cloud 通信不作为 Local Loop 前置条件。

证据：`docs/gate2/B_EDGE_REPORT.md`、`edge/packet_tracer/evidence/gate2/`。

### C Control Plane Real Telemetry — PASS

真实 PT 环境升温后观察到：

```text
TEMP01 ≈ 32 C
→ SBC TX TELEMETRY ≈31.8 C
→ FastAPI /api/state SENSOR event ≈31.8 C
→ FAN ON
```

未修改 Backend 业务代码和 Protocol v1。

证据：`evidence/backend/G2-C-*`、`evidence/backend/GATE2_C_REPORT.md`。

### D Dashboard Real PT — PASS

真实 PT 两组浏览器证据：

```text
≈27.9 C → NORMAL  → FAN OFF
≈34.1 C → WARNING → FAN ON
```

Edge ONLINE、AUTO、CONNECTED、Policy v1、SENSOR events 正常；提交时 repository tests 14/14 PASS，Dashboard contract tests 5/5 PASS。

证据：`docs/gate2/D_DASHBOARD_REPORT.md`、`evidence/dashboard/gate2/`。

### B+C+D End-to-End — PASS

```text
TEMP01
→ IO-MCU-01
→ EDGE-SBC-01
→ External Network Access / RealWSClient
→ Real FastAPI
→ Dashboard
```

这是带外 Edge–Cloud 控制通道，不经过 PT WAN。

### Gate 2 canonical package

2026-09-16 项目 Owner 提供 A+B Gate2 整合 `.pkt`，作为 Gate2 canonical 基线归档到 `packet_tracer/EdgeCampus.pkt`。该包在仓库层作为后续 G3/G4 的 canonical 起点；PT 内部功能结论仍以 A/B 各自实测报告和证据为依据。

Gate2 集成记录：`docs/gate2/INTEGRATION_REPORT.md`。

## 5. Gate 3 — IN PROGRESS

待验证网络项：

- HQ OSPF Area0；
- WAN eBGP AS65001/65000/65002；
- BR-OFFICE → HQ-SERVICE；
- HQ OFFICE PAT → Internet；
- DNS / HTTP；
- Static TCP/80 mapping；
- WAN / Branch business ACL；
- 每层后的 HQ/Branch regression。

待验证软件 / IoT 项：

- RealWSClient 服务端下行消息；
- Dashboard Policy → Backend → real Edge → `policy_ack`；
- threshold 30→33 / version 1→2；
- 32 C FAN OFF / 34 C FAN ON；
- Dashboard Command → real FAN → `command_ack`。

## 6. Gate 4 尚未验证

- SLAAC / DHCPv6 / Static IPv6；
- IPv6-over-IPv4 Tunnel + static IPv6 routes；
- HQ central administration of Branch；
- Port Security / sticky MAC；
- real Cloud-off → local autonomy → reconnect → state_sync 完整恢复。

## 7. 真实性声明

Packet Tracer 的 VLAN / ACL / OSPF / BGP / NAT / Tunnel 是模拟企业数据平面。真实 FastAPI WebSocket 通过 Packet Tracer External Network Access / RealWSClient 带外连接，不经过 Packet Tracer WAN。

任何最终报告、演示稿或 AI 输出都必须维持该边界，只把已有 evidence 支持的能力写成已验证。
