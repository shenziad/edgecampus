# AI 共享上下文（Final Architecture v2）

## 项目定义

EdgeCampus 是“面向多园区智慧校园的边缘—云协同网络控制平台”。

- Packet Tracer：HQ、企业 WAN、Internet、异地 Branch 与 IoT 物理世界。
- `EDGE-SBC-01`：Edge Controller，负责本地自治。
- 真实主机 FastAPI：Cloud / Control Plane。
- Web Dashboard：Management Plane。
- Final Architecture v2：只向 Gate1/2 已验证 Core 外扩，不重构稳定基线。

## 不可破坏 Core

```text
VLAN10 OFFICE      192.168.10.0/24
VLAN20 IOT         192.168.20.0/24
VLAN30 MANAGEMENT  192.168.30.0/24

SW-CORE ⇄ LACP EtherChannel ⇄ SW-ACCESS
TEMP01 → IO-MCU-01 → EDGE-SBC-01 → FAN01
```

Gate 2 又新增并验证：

```text
SW-CORE Gi1/0/24 ↔ R-HQ ↔ R-ISP ↔ R-BRANCH ↔ SW-BRANCH
                              |
                       INTERNET-SERVER

VLAN40 BR-OFFICE  172.16.40.0/26
VLAN50 BR-MGMT    172.16.40.64/27
```

任何 Gate 3 工作不得为实现新功能重做上述已验证配置。

## 双控制环

```text
Edge Local Loop:
TEMP01 → MCU → EDGE-SBC-01 → FAN01
Cloud 断开时仍按最后有效策略运行。

Cloud Global Loop:
Dashboard → FastAPI → EDGE-SBC-01
用于策略、人工命令、状态汇聚与恢复同步。
```

Gate 2 已真实打通上行：

```text
TEMP01 → MCU → SBC → RealWSClient → FastAPI → Dashboard
```

Gate 3 当前目标是打通下行：

```text
Dashboard → FastAPI → SBC → policy_ack / command_ack → Dashboard
```

## Final Architecture v2 网络层次

```text
HQ Core --OSPF-- R-HQ --eBGP-- R-ISP --eBGP-- R-BRANCH --802.1Q-- SW-BRANCH
                         |
                   INTERNET-SERVER
```

业务角色：

- `BR-OFFICE-PC`：分部普通员工，Gate3 访问 HQ-SERVICE。
- `BR-ADMIN-PC`：异地运维，Gate4 经 IPv6 Overlay 访问 HQ MANAGEMENT。
- `ADMIN-PC`：总部 NOC，Gate4 管理 Branch 网络设备。
- `BACKEND-STUB`：Packet Tracer 中的 HQ-SERVICE / CONTROL-PLANE-STUB，不是真实 FastAPI。

## Public Contract — 完全冻结

- Protocol：`1.0`
- Edge WebSocket：`/ws/edge`
- Dashboard WebSocket：`/ws/dashboard`
- IDs：`EDGE-SBC-01`、`TEMP01`、`FAN01`
- 消息：Telemetry、Status、Command、Policy、Heartbeat、Hello、State Sync、ACK、Error
- 温度单位：`C`
- Policy：`policy_id`、`version`、`mode`、`threshold_c`、`hysteresis_c`
- FAN 传输状态：`ON/OFF`，不得使用 PT 物理值 `0/2`
- 权威定义：`docs/PROTOCOL.md`、`config/system.json`

Final Architecture v2 与 Gate 3 均不修改 Protocol v1.0。

## 网络冻结项

Gate 2 已实测并冻结：

- `SW-CORE Gi1/0/24 = 10.255.0.1/30 ↔ R-HQ G0/0 = 10.255.0.2/30`
- `R-HQ G0/1 = 203.0.113.1/30 ↔ R-ISP G0/0 = 203.0.113.2/30`
- `R-ISP G0/1 = 198.51.100.1/30 ↔ R-BRANCH G0/0 = 198.51.100.2/30`
- `R-ISP G0/2 = 192.0.2.1/24 ↔ INTERNET-SERVER = 192.0.2.10/24`
- Branch VLAN40 / VLAN50 + ROAS + DHCP/管理地址

Gate 3 冻结路由设计：

- OSPF 仅用于 HQ Core ↔ R-HQ Area0。
- eBGP：R-HQ AS65001、R-ISP AS65000、R-BRANCH AS65002。
- 优先发布明确业务前缀，禁止无解释的 broad redistribution。
- R-HQ 为 HQ Internet Edge，PAT 默认只覆盖 HQ OFFICE；IOT 不做通用 Internet NAT；站点间业务避免 NAT。

Gate 4 才进入 IPv6-over-IPv4 Tunnel、Port Security、中央管理。

## 真实性边界

Packet Tracer 的 VLAN / ACL / Routing / OSPF / BGP / NAT / Tunnel 是**模拟数据平面**。

真实控制通道：

```text
EDGE-SBC-01
  ↓ Packet Tracer External Network Access / RealWSClient
ws://127.0.0.1:8000/ws/edge
  ↓
Real FastAPI
```

它是带外通道。不得描述成真实 WebSocket 经过 VLAN20/30、R-HQ、R-ISP、BGP、NAT 或 IPv6 Tunnel。

## 当前 Gate 状态

- G0：COMPLETE。
- G1：`CLOSED-WITH-PENDING-STABILITY`。A/B/D PASS，A+B integration PASS；C Core PASS，但 malformed/offline/reconnect+state_sync 三项证据须 Gate5 前补齐。
- G2：COMPLETE。A 的 Branch/WAN Foundation 与 B/C/D 的真实 PT Telemetry 全链路均 PASS。
- 当前：**G3 — Policy Loop + WAN Business**。

当前唯一指挥文件：`docs/CURRENT_GATE.md`。

## Gate 3 Owner 边界

- **A Network**：`packet_tracer/`、network evidence、唯一 canonical `.pkt` Owner。顺序：OSPF → eBGP → Branch→HQ → PAT/DNS/HTTP → static mapping → ACL → regression。
- **B Edge**：`edge/`。先验证 RealWSClient 下行消息，再实现 Policy/Command/ACK；Local Loop 必须优先，callback 禁止阻塞。
- **C Control Plane**：`backend/`。转发 Policy/Command，处理 ACK/事件与 EDGE_OFFLINE；fake edge 仍须可用。
- **D UI & Integration**：`dashboard/`、`tests/`、集成 evidence。使用既有表单完成真实 Policy/Command 闭环，不创造新传输字段。

## Gate 3 核心验收

软件：

```text
threshold 30 → 33
version 1 → 2
policy_ack = APPLIED
真实 32 C → FAN OFF
真实 34 C → FAN ON
真实 command → command_ack
```

网络：

```text
OSPF FULL + HQ route learning
eBGP established + route propagation
BR-OFFICE → HQ-SERVICE PASS
HQ OFFICE → PAT → DNS/HTTP PASS
static TCP/80 + business ACL PASS
```

## 实现约束

1. 已验证 Core 只允许增量扩展。
2. 不引入 Kubernetes、MQ、数据库、多租户等非必要架构。
3. 软件字段、ID、WS/API 路径不得变。
4. 网络逐层配置、逐层验收；不要一次叠加 OSPF/BGP/NAT/ACL。
5. A 是 canonical `.pkt` 唯一 Owner。
6. 软件功能尽量保留 fake 对端可独立验证。
7. 未实测 PT 命令/API 必须标待验证。
8. Cloud 异常不得成为 Local Loop 的前置条件。
9. 新增网络不得改变 RealWSClient 带外事实。
10. 跨公共契约变更必须先 RFC。

## 每次交付格式

```text
完成内容：
修改文件：
公共接口影响：无 / 有（有则暂停并走 RFC）
运行命令：
测试结果：
待联调项：
建议截图证据：
```
