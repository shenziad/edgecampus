# AI 共享上下文（Final Architecture v2）

## 项目定义

EdgeCampus 是“面向多园区智慧校园的边缘—云协同网络控制平台”。

- Packet Tracer：总部 HQ、企业 WAN、Internet、异地 Branch，以及 IoT 物理世界。
- `EDGE-SBC-01`：Edge Controller，负责本地自治。
- 真实主机 FastAPI：Cloud / Control Plane。
- 网页 Dashboard：Management Plane。
- Final Architecture v2：在不破坏 Gate 1 HQ Core 的前提下，向外增加 R-HQ / R-ISP / R-BRANCH / SW-BRANCH / Internet Service，并覆盖前五次组网实验的核心能力。

## 不可破坏的 Core

Gate 1 已验证的 HQ Core 视为稳定基线：

```text
VLAN10 OFFICE      192.168.10.0/24
VLAN20 IOT         192.168.20.0/24
VLAN30 MANAGEMENT  192.168.30.0/24

SW-CORE ⇄(LACP EtherChannel)⇄ SW-ACCESS
TEMP01 → IO-MCU-01 → EDGE-SBC-01 → FAN01
```

Final Architecture v2 采用**只向外扩展，不重构 HQ Core**的原则。新增网络从 `SW-CORE Gi1/0/24` 向 R-HQ 延伸。

## 双控制环

```text
Edge Local Loop:
TEMP01 → MCU → EDGE-SBC-01 → FAN01
Cloud 断开仍继续运行最后有效 AUTO 策略。

Cloud Global Loop:
Dashboard → FastAPI → EDGE-SBC-01
用于策略、人工命令、状态汇聚和恢复同步。
```

## Final Architecture v2 网络层次

```text
HQ Core --OSPF-- R-HQ --eBGP-- R-ISP --eBGP-- R-BRANCH --802.1Q-- SW-BRANCH
                         |
                   INTERNET-SERVER
```

业务角色：

- `BR-OFFICE-PC`：异地普通员工，访问 HQ-SERVICE。
- `BR-ADMIN-PC`：异地运维人员，通过 IPv6 Overlay 访问 HQ MANAGEMENT。
- `ADMIN-PC`：总部 NOC 管理员，可管理 Branch 网络设备。
- `BACKEND-STUB`：Packet Tracer 中的 HQ-SERVICE / CONTROL-PLANE-STUB；不是真实 FastAPI。

## Public Contract — 软件部分完全冻结

- 协议版本：`1.0`
- Edge WebSocket：`/ws/edge`
- Dashboard WebSocket：`/ws/dashboard`
- 设备 ID：`EDGE-SBC-01`、`TEMP01`、`FAN01`
- 核心消息：Telemetry、Status、Command、Policy、Heartbeat
- 恢复消息：Hello、State Sync、ACK、Error
- 温度单位：`C`
- 权威定义：`docs/PROTOCOL.md` 和 `config/system.json`

**Final Architecture v2 不修改 Protocol v1.0。**

## Public Contract — 网络新增冻结项

现有 HQ VLAN/IP 不变。新增设计由 `docs/NETWORK_PLAN.md` 统一定义，核心包括：

- `SW-CORE Gi1/0/24 ↔ R-HQ G0/0`
- `R-HQ G0/1 ↔ R-ISP G0/0`
- `R-ISP G0/1 ↔ R-BRANCH G0/0`
- `R-ISP G0/2 ↔ INTERNET-SERVER Fa0`
- `R-BRANCH G0/1 ↔ SW-BRANCH Gi0/1`
- Branch VLAN 40 / BR-OFFICE
- Branch VLAN 50 / BR-MGMT
- OSPF 仅用于 HQ 内部；eBGP 用于 WAN AS 边界；IPv6 跨站点使用 IPv6-over-IPv4 Tunnel + 静态 IPv6 路由。

任何 AI 不得自行重新编号接口、VLAN、IPv4/IPv6 前缀或 AS Number。

## 真实性边界：必须严格遵守

Packet Tracer 的 VLAN / ACL / Routing / OSPF / BGP / NAT / IPv6 Tunnel 属于**模拟数据平面**。

真实 Edge 控制通道是：

```text
EDGE-SBC-01
  ↓ Packet Tracer External Network Access / RealWSClient
ws://127.0.0.1:8000/ws/edge
  ↓
Real FastAPI
```

它是**带外控制通道**。不得描述成真实 WebSocket 流量经过 VLAN20/30、R-HQ、R-ISP、BGP、NAT 或 IPv6 Tunnel。

## 当前 Gate

- G0：COMPLETE。
- G1：`CLOSED-WITH-PLACEHOLDER`。A/B/D 已验证，A+B 已集成；C 的 Owner 专属 Gate 1 证据暂以 `docs/gate1/C_BACKEND_REPORT.md` 占位，Gate 5 前必须补齐。
- 当前：**Gate 2**。B/C/D 打通真实 PT Telemetry；A 并行建设 Branch LAN 与 IPv4 WAN Underlay。

当前唯一指挥文件：`docs/CURRENT_GATE.md`。

## 实现约束

1. 已验证 HQ Core 只允许增量扩展，不得为 WAN 功能重做 VLAN/ACL/Edge 接线。
2. 不引入 Kubernetes、微服务、MQ、数据库、多租户等非必要架构。
3. 软件协议字段、设备 ID、WS/API 路径不得改变。
4. 网络新增项按 `NETWORK_PLAN.md` 分层实现；每层先验收，再继续 OSPF/BGP/NAT/IPv6。
5. A 是 canonical `.pkt` 的唯一 Owner。
6. 每个软件功能尽量保持 fake 对端可独立验证。
7. PT IOS / API 未实测的命令必须标记为待验证，不得把模板写成已通过。
8. 错误处理优先保证：Cloud 失联不影响 Edge 本地控制。
9. 新增网络功能不得改变 RealWSClient 的带外控制事实。
10. 跨 Owner / 跨公共契约的变更先输出 RFC，不直接修改。

## Owner 边界

- A Network：`packet_tracer/`、网络证据、Final Canonical `.pkt`。
- B Edge：`edge/`、Edge 证据。
- C Control Plane：`backend/`、Backend 证据。
- D UI & Integration：`dashboard/`、`tests/`、集成证据。

## 每次交付格式

```text
完成内容：
修改文件：
公共接口影响：无 / 有（若有必须暂停并走 RFC）
运行命令：
测试结果：
待联调项：
建议截图证据：
```
