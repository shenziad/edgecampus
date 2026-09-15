# 验证记录 — Final Architecture v2

## 1. 软件基线已通过的历史验证

仓库初始化与 fake 链路阶段已验证：

- Python 全量语法编译；
- Protocol v1.0 错误字段 / 版本 / 范围校验单元测试；
- Edge 迟滞控制、MANUAL 保持、Policy 更新；
- Backend 状态与 State Sync；
- 公共契约漂移检查；
- Dashboard JavaScript 语法检查；
- Backend + Fake Edge + Dashboard WebSocket 真实进程联调；
- Dashboard 下发 Policy / Command，Fake Edge 返回 ACK；
- 停止 Cloud 后 Fake Edge 持续本地控制；
- Cloud 恢复后 fake Edge 重连并发送 `state_sync`。

这些结果说明软件基线存在，但不替代后续真实 Packet Tracer Gate 验收。

## 2. Gate 0 已实机验证

- Packet Tracer 设备型号 / HQ 端口映射确认；
- `EDGE-SBC-01` FastEthernet 模块确认；
- External Network Access / RealWSClient → `ws://127.0.0.1:8000/ws/edge` 成功；
- SBC 显示 CONNECTED；
- FastAPI 日志出现 Edge connected；
- `/api/state` 出现 `edge_online=true` / connected 状态；
- 保存、关闭、重新打开 `.pkt` 后再次连接成功。

结论：G0 COMPLETE。

## 3. Gate 1 已验证

### A Network — PASS

已归档 / 实测：

- VLAN10/20/30；
- Access 端口；
- LACP EtherChannel / Po1；
- Trunk；
- HQ SVI / `ip routing`；
- OFFICE DHCP；
- VLAN10 / VLAN20 inbound ACL；
- OFFICE→ADMIN 允许；
- OFFICE→IOT 拒绝；
- MANAGEMENT→EDGE 允许。

### B Edge — PASS

真实 Packet Tracer Local Loop 已验证：

```text
TEMP01 A0 → IO-MCU-01 A0
IO-MCU-01 USB0 → EDGE-SBC-01 USB0
EDGE-SBC-01 D0 → FAN01 D0
```

迟滞序列：

```text
30.2 C → TURN_ON  → FAN ON
29.4 C → HOLD     → FAN ON
28.6 C → TURN_OFF → FAN OFF
```

Backend 端口不可达时，本地循环继续运行。

### A+B Integration — PASS

合入 canonical 网络基线后重新验证：

- Po1 / Trunk / VLAN 正常；
- SVI / route / ACL 正常；
- HQ 关键通信矩阵无退化；
- Edge Local Loop / hysteresis / backend-off autonomy 无退化。

证据：`docs/gate1/AB_INTEGRATION_REPORT.md` 及对应 network / edge evidence。

### D Dashboard — PASS

已归档：

```text
G1-D-01-dashboard-normal-pass.png
G1-D-02-dashboard-warning-pass.png
G1-D-03-edge-offline-pass.png
G1-D-04-reconnect-state-sync-pass.png
```

以及 `docs/gate1/D_DASHBOARD_REPORT.md`。

### C Control Plane — CORE EVIDENCE SUBMITTED / STABILITY PENDING

核心 fake-edge / healthz / api-state 证据已在 `evidence/backend/G1-01`–`G1-07`。  
正式部分报告：`docs/gate1/C_BACKEND_REPORT.md`。  
Gate 2 真 PT telemetry 证据已在 `evidence/backend/G2-C-01`–`G2-C-04`。  
invalid-message / offline / reconnect 仍须在 Gate 5 前补齐。  
不得把当前状态写成 C Gate 1 完整 PASS。

Gate 1 管理状态：`CLOSED-WITH-PLACEHOLDER`。

## 4. Final Architecture v2 已冻结但尚未验证的新增项

截至 v2 Re-baseline，下面是**设计已冻结 / 实际配置待 A 实施**：

- SW-CORE Gi1/0/24 ↔ R-HQ；
- R-HQ ↔ R-ISP ↔ R-BRANCH；
- INTERNET-SERVER；
- SW-BRANCH / VLAN40 / VLAN50；
- Router-on-a-Stick；
- Branch IPv4 DHCP / 管理地址；
- HQ OSPF；
- WAN eBGP；
- Branch→HQ business flow；
- HQ PAT；
- DNS / HTTP；
- TCP/80 static mapping；
- SLAAC / DHCPv6 / Static IPv6；
- IPv6-over-IPv4 Tunnel；
- IPv6 static routes；
- HQ central management of Branch；
- Port Security / sticky MAC final acceptance。

这些内容目前必须标记为 `PLANNED / NOT YET VALIDATED`，直到 A 在 Packet Tracer 9.0.1 中完成真实配置和证据。

## 5. Gate 2 尚需验证

### B/C/D

```text
真实 TEMP01
→ MCU
→ SBC
→ RealWSClient
→ FastAPI
→ Dashboard
```

C 段（FastAPI `/api/state`）已于 2026-09-16 观察到真实 31.8 C。  
整关仍须证明 Dashboard 值来自真实 PT，而不是 fake edge（D）。

### A

- Branch VLAN40/50 + ROAS；
- Branch DHCP / 管理地址；
- HQ Transit / HQ-ISP / ISP-Branch / Internet LAN 相邻 IPv4 可达；
- HQ Gate 1 regression 无退化。

## 6. 真实性声明

项目当前只承诺已验证事实。

特别是：

> Packet Tracer 的 VLAN / OSPF / BGP / NAT / Tunnel 是模拟数据平面。真实 FastAPI WebSocket 使用 External Network Access / RealWSClient 带外连接，不经过 Packet Tracer WAN。

任何最终报告、演示稿、AI 输出都必须遵守该边界。
