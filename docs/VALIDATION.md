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

VLAN10/20/30、Access、静态EtherChannel、Trunk、SVI/IP routing、OFFICE DHCP、HQ ACL 与关键行为矩阵均通过；课程补强图47–54提供Branch PAT/ACL、双DROTHER、E2重分发及双端口安全证据。

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

已提交：unit tests、`/ws/edge` fake edge、`/healthz`、`/api/state` telemetry/temperature、AUTO FAN events。

仍欠：malformed 安全拒绝、Edge offline、reconnect + `state_sync`。管理状态为 **CLOSED-WITH-PENDING-STABILITY**，Gate5 前必须清零。

## 4. Gate 2 — COMPLETE

### A Network Foundation — PASS

已验证：

- 7 条新增冻结链路与接口映射；
- Branch VLAN40 / VLAN50；
- SW-BRANCH trunk / access / management SVI；
- R-BRANCH Router-on-a-Stick；
- BR-OFFICE DHCP、BR-ADMIN 管理地址；
- HQ Transit、HQ↔ISP、ISP↔Branch、Internet LAN IPv4 Underlay；
- 四段相邻三层连通；
- HQ Gate1 EtherChannel / trunk / VLAN / SVI / ACL / 行为 regression 无退化。

证据：`docs/gate2/A_NETWORK_REPORT.md` 与 `evidence/network/G2-A-*`。

### B Edge Real Telemetry — PASS

已验证 RealWSClient、Protocol v1 hello、固定 telemetry、真实 TEMP01 telemetry、Local AUTO、FAN Status、Heartbeat，以及高温真实 FAN01 PT state=2 ↔ Protocol `ON`。Cloud 通信不作为 Local Loop 前置条件。

证据：`docs/gate2/B_EDGE_REPORT.md`、`edge/packet_tracer/evidence/gate2/`。

### C Control Plane Real Telemetry — PASS

真实 PT 环境升温后：

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

### Gate 2 Packet Tracer 文件状态

A 分支提交的 Gate2 canonical 网络文件已保留在仓库 `packet_tracer/EdgeCampus.pkt`，并与 A 的 Gate2 网络 evidence/CONFIG_LOG 对应。

2026-09-16 项目 Owner 另提供 A+B Gate2 整合 `.pkt`：

```text
SHA-256 = 8a299abad7ec701bcc17505cc1dd9f578eb9f11dbe0af448c4bc0d2077ebdae6
size    = 117338 bytes
```

当前 GitHub 连接器无法可靠写入该完整二进制附件，因此仓库没有用截断内容覆盖 canonical 文件。该 A+B 整合包应由 A 在本地正常替换并 `git add/commit/push` 后成为新的 canonical `.pkt`。Gate2 功能 PASS 结论来自四位 Owner 的实测报告/evidence，不依赖对二进制文件内容的文本推断。

Gate2 集成记录：`docs/gate2/INTEGRATION_REPORT.md`。

## 5. Gate 3 — EVIDENCE PENDING

待验证网络项：HQ OSPF、WAN eBGP、BR-OFFICE→HQ-SERVICE、HQ OFFICE PAT→Internet、DNS/HTTP、Static TCP/80、业务 ACL 及每层 regression。

待验证软件 / IoT 项：RealWSClient 服务端下行、Dashboard Policy → Backend → real Edge → `policy_ack`、threshold 30→33/version 1→2、32 C FAN OFF / 34 C FAN ON，以及真实 Command → `command_ack`。

## 6. Gate 4 尚未验证

- SLAAC / DHCPv6 / Static IPv6；
- IPv6-over-IPv4 Tunnel + static IPv6 routes；
- HQ central administration of Branch；
- Port Security / sticky MAC；
- real Cloud-off → local autonomy → reconnect → state_sync 完整恢复。

## 7. 真实性声明

Packet Tracer 的 VLAN / ACL / OSPF / BGP / NAT / Tunnel 是模拟企业数据平面。真实 FastAPI WebSocket 通过 Packet Tracer External Network Access / RealWSClient 带外连接，不经过 Packet Tracer WAN。

任何最终报告、演示稿或 AI 输出都必须维持该边界，只把已有 evidence 支持的能力写成已验证。

## 2026-09-17 Gate4 归档更新

2026-09-17 当前审计：Gate4 已实现并有用户现场实测确认；B 离线 ON、真实 reconnect/hello/state_sync、Backend 恢复与 D 失联有截图，C 三项 Gate1 stability debt 清零。A N12-N15 用户确认已测，截图本次跳过后补；离线 OFF/Attributes、恢复后 Dashboard、G4 N1-N11 全量回归及 G3 修复后 ACK/完整 events 仍需归档。Gate4 为 IMPLEMENTED / USER-TESTED / EVIDENCE PENDING，未正式 COMPLETE；Gate5 NOT STARTED。

过程与配置：`docs/gate4/A_NETWORK_REPORT.md`、B/C/D/BCD 报告；自动验证：`docs/gate4/VALIDATION_REPORT.md`。报告应解释 Cloud outage/Edge restart、临时默认值/state_sync、NAT 业务入口、IPv4-only ISP、static IPv6、VTY ACL 和 sticky/restrict。
