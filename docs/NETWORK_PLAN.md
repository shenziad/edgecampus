# 网络规划 — Final Architecture v2（Network Owner）

> 本文是 A Network Owner 与所有 AI 的网络权威文档。Final Architecture v2 已批准将 Gate 1 的单园区网络向外扩展为 HQ + ISP/Internet + Branch，但**不允许破坏已验证 HQ Core**。

## 1. 总原则

1. Gate 1 HQ Core 保持不变；新增网络只从 `SW-CORE Gi1/0/24` 向外延伸。
2. A 是 canonical `packet_tracer/EdgeCampus.pkt` 的唯一 Owner。
3. 每一层网络功能必须先验证再叠加下一层：Branch LAN → IPv4 Underlay → OSPF → eBGP → NAT/DNS/HTTP → IPv6 Overlay → Port Security/管理验收。
4. Final Architecture v2 中的逻辑接口、VLAN、IPv4/IPv6 前缀和 AS Number 不得由 AI 自行重编号。
5. Packet Tracer WAN 是模拟数据平面；RealWSClient 到真实 FastAPI 始终是带外 Edge–Cloud 控制通道。

---

## 2. 已验证且不得破坏的 HQ Core

### 2.1 HQ 安全域

| 安全域 | VLAN | IPv4 网段 | 网关 | 关键节点 | Gate 1 状态 |
|---|---:|---|---|---|---|
| OFFICE | 10 | `192.168.10.0/24` | `192.168.10.1` | OFFICE-PC：DHCP | VERIFIED |
| IOT | 20 | `192.168.20.0/24` | `192.168.20.1` | `EDGE-SBC-01 = 192.168.20.10` | VERIFIED |
| MANAGEMENT | 30 | `192.168.30.0/24` | `192.168.30.1` | `BACKEND-STUB = 192.168.30.10`；`ADMIN-PC = 192.168.30.20` | VERIFIED |

`BACKEND-STUB` 在 Final Architecture v2 中同时承担 **HQ-SERVICE / CONTROL-PLANE-STUB** 的 Packet Tracer 网络验收角色，但仍不是真实 FastAPI Backend。

### 2.2 HQ 已验证物理接口

| 链路 | A 端接口 | B 端接口 | 模式 | 状态 |
|---|---|---|---|---|
| Core–Access #1 | `SW-CORE Gi1/0/1` | `SW-ACCESS Gi0/1` | LACP member / trunk | VERIFIED |
| Core–Access #2 | `SW-CORE Gi1/0/2` | `SW-ACCESS Gi0/2` | LACP member / trunk | VERIFIED |
| OFFICE-PC | `SW-ACCESS Fa0/1` | PC Fa0 | access VLAN10 | VERIFIED |
| EDGE-SBC-01 | `SW-ACCESS Fa0/2` | SBC FastEthernet0 | access VLAN20 | VERIFIED |
| ADMIN-PC | `SW-ACCESS Fa0/3` | PC Fa0 | access VLAN30 | VERIFIED |
| BACKEND-STUB | `SW-ACCESS Fa0/4` | Server Fa0 | access VLAN30 | VERIFIED |

Gate 1 已验证 VLAN10/20/30、Po1(LACP)、Trunk、SVI、`ip routing`、OFFICE DHCP 和 VLAN10/VLAN20 inbound ACL。Final Architecture v2 不重新设计这些内容。

### 2.3 HQ Edge 物理闭环

```text
TEMP01 A0 → IO-MCU-01 A0
IO-MCU-01 USB0 → EDGE-SBC-01 USB0
EDGE-SBC-01 D0 → FAN01 D0  (Custom Cable)
```

该接线已经完成 Gate 1 A+B 集成回归，新增 WAN 不得改变。

---

## 3. Final Architecture v2 新增设备

| 设备 | 建议型号 | 角色 |
|---|---|---|
| `R-HQ` | Cisco 2911 | 总部企业边界、OSPF 边界、eBGP、NAT/PAT、Tunnel endpoint |
| `R-ISP` | Cisco 2911 | IPv4-only ISP / Transit AS |
| `R-BRANCH` | Cisco 2911 | 分部边界、eBGP、Router-on-a-Stick、Tunnel endpoint |
| `SW-BRANCH` | Cisco 2960-24TT | 分部二层接入、VLAN40/50、Trunk、管理 SVI |
| `BR-OFFICE-PC` | PC-PT | 分部普通员工 |
| `BR-ADMIN-PC` | PC-PT | 分部异地运维人员 |
| `INTERNET-SERVER` | Server-PT | 模拟公网 DNS + HTTP 服务与外部访问测试节点 |

`R-HQ G0/2`、`R-BRANCH G0/2` 预留，不为了“用满接口”增加无关设备。

---

## 4. Final Architecture v2 冻结物理接口

| 本端 | 本端接口 | 对端 | 对端接口 | 用途 | 当前状态 |
|---|---|---|---|---|---|
| SW-CORE | `Gi1/0/24` | R-HQ | `G0/0` | HQ L3 Transit / OSPF | PLANNED V2 |
| R-HQ | `G0/1` | R-ISP | `G0/0` | HQ WAN / eBGP / NAT outside | PLANNED V2 |
| R-ISP | `G0/1` | R-BRANCH | `G0/0` | Branch WAN / eBGP | PLANNED V2 |
| R-ISP | `G0/2` | INTERNET-SERVER | `Fa0` | 模拟 Internet Service LAN | PLANNED V2 |
| R-BRANCH | `G0/1` | SW-BRANCH | `Gi0/1` | 802.1Q Router-on-a-Stick Trunk | PLANNED V2 |
| SW-BRANCH | `Fa0/1` | BR-OFFICE-PC | `Fa0` | access VLAN40 | PLANNED V2 |
| SW-BRANCH | `Fa0/2` | BR-ADMIN-PC | `Fa0` | access VLAN50 | PLANNED V2 |

若 Packet Tracer 实际接线与表格不一致，**先停止配置并修正拓扑/文档，不允许 AI 静默换端口。**

---

## 5. IPv4 地址规划

### 5.1 HQ Core ↔ R-HQ Transit

网络：`10.255.0.0/30`

| 节点 | 地址 |
|---|---|
| `SW-CORE Gi1/0/24` | `10.255.0.1/30` |
| `R-HQ G0/0` | `10.255.0.2/30` |

此链路运行 OSPF Area 0。

### 5.2 HQ ↔ ISP

网络：`203.0.113.0/30`

| 节点 | 地址 |
|---|---|
| `R-HQ G0/1` | `203.0.113.1/30` |
| `R-ISP G0/0` | `203.0.113.2/30` |

### 5.3 ISP ↔ Branch

网络：`198.51.100.0/30`

| 节点 | 地址 |
|---|---|
| `R-ISP G0/1` | `198.51.100.1/30` |
| `R-BRANCH G0/0` | `198.51.100.2/30` |

### 5.4 Internet Service LAN

网络：`192.0.2.0/24`

| 节点 | 地址 |
|---|---|
| `R-ISP G0/2` | `192.0.2.1/24` |
| `INTERNET-SERVER Fa0` | `192.0.2.10/24` |
| INTERNET-SERVER Gateway | `192.0.2.1` |

### 5.5 Branch VLSM

Branch 地址块：`172.16.40.0/24`，按业务规模拆分：

| VLAN | 名称 | IPv4 网络 | Gateway | 角色 |
|---:|---|---|---|---|
| 40 | BR-OFFICE | `172.16.40.0/26` | `172.16.40.1` | 普通分部办公 |
| 50 | BR-MGMT | `172.16.40.64/27` | `172.16.40.65` | 分部管理 / 运维 |

推荐固定管理地址：

- `SW-BRANCH VLAN50 = 172.16.40.66/27`
- `BR-ADMIN-PC = 172.16.40.70/27`，GW `172.16.40.65`
- BR-OFFICE-PC 使用 R-BRANCH 提供的 IPv4 DHCP，避免固定某一动态租约地址。

### 5.6 Branch Router-on-a-Stick

```text
R-BRANCH G0/1.40
  encapsulation dot1Q 40
  172.16.40.1/26

R-BRANCH G0/1.50
  encapsulation dot1Q 50
  172.16.40.65/27
```

`SW-BRANCH Gi0/1` 为 trunk；`Fa0/1` 为 VLAN40；`Fa0/2` 为 VLAN50。

---

## 6. IPv4 路由分层

### 6.1 HQ IGP — OSPF Area 0

OSPF 只运行在 HQ 内部：

```text
HQ VLAN10/20/30
       ↓
    SW-CORE
       ↕ 10.255.0.0/30
    R-HQ
```

设计意图：

- SW-CORE 将 HQ `192.168.10.0/24`、`192.168.20.0/24`、`192.168.30.0/24` 发布到 OSPF。
- R-HQ 使用静态默认路由指向 `203.0.113.2`。
- R-HQ 使用 `default-information originate` 向 HQ Core 发布默认出口。
- **不把完整 BGP 路由表重分发进 HQ OSPF**；SW-CORE 对外部网络只需要默认路由。

### 6.2 WAN EGP — eBGP

冻结 AS Number：

| Router | AS |
|---|---:|
| R-HQ | `65001` |
| R-ISP | `65000` |
| R-BRANCH | `65002` |

邻居：

```text
R-HQ AS65001     ↔     R-ISP AS65000     ↔     R-BRANCH AS65002
203.0.113.1             203.0.113.2
                         198.51.100.1             198.51.100.2
```

计划发布前缀：

- R-HQ：至少 `192.168.30.0/24`，用于 Branch 访问 HQ-SERVICE 和 HQ ADMIN 的返回路径；根据验收需求可发布 HQ OFFICE，但默认不要求将 IOT 作为 Branch 业务可达域。
- R-BRANCH：`172.16.40.0/26`、`172.16.40.64/27`。
- R-ISP：`192.0.2.0/24`，以及 WAN Transit `203.0.113.0/30`、`198.51.100.0/30`，保证 Tunnel 两端 IPv4 endpoint 互相可达。

若最终采用更严格的前缀过滤，必须保留“BR-OFFICE → HQ-SERVICE”和“HQ ADMIN → Branch 管理设备”两条业务路径。

---

## 7. NAT / DNS / HTTP 设计

### 7.1 HQ Office Internet PAT

NAT 位于 R-HQ：

- `G0/0`：`ip nat inside`
- `G0/1`：`ip nat outside`
- PAT 主要对象：`192.168.10.0/24` HQ OFFICE。
- HQ IOT 默认不直接获得公网 NAT 权限。

业务路径：

```text
OFFICE-PC → SW-CORE → R-HQ → PAT → R-ISP → INTERNET-SERVER
```

PAT 验收要同时保留 `show ip nat translations` / 等价证据，而不是只做 ping。

### 7.2 Internet DNS / HTTP

`INTERNET-SERVER = 192.0.2.10` 开启 DNS 与 HTTP。

推荐 DNS 记录：

```text
www.edgecampus.net    → 192.0.2.10
status.edgecampus.net → 203.0.113.1
```

HQ OFFICE 通过 DNS 访问 `www.edgecampus.net`，验证 DNS + PAT + HTTP。

### 7.3 静态 TCP/80 映射

为覆盖实验三端口映射并赋予业务意义，R-HQ 计划将：

```text
203.0.113.1:80  →  192.168.30.10:80
```

即外部测试节点访问 HQ-SERVICE 的**模拟公开状态页**。

安全要求：仅开放验收所需 HTTP/80，不把整个 MANAGEMENT 网段暴露给外部。该映射只发生在 Packet Tracer 中，不代表真实 FastAPI 公开到 Internet。

---

## 8. Branch 与 HQ 的业务关系

### 8.1 BR-OFFICE：异地业务访问

```text
BR-OFFICE-PC
 → VLAN40
 → R-BRANCH
 → R-ISP
 → R-HQ
 → 192.168.30.10 HQ-SERVICE
```

冻结业务意图：BR-OFFICE 可以访问 HQ-SERVICE 的允许业务（主要 HTTP），不能直接进入 HQ IOT，也不能获得网络设备管理权限。

### 8.2 BR-ADMIN：异地运维

BR-ADMIN 主要通过 IPv6 Overlay 访问 HQ MANAGEMENT，体现“异地运维人员访问总部控制/管理服务”。

### 8.3 HQ ADMIN：集中网络管理

`ADMIN-PC = 192.168.30.20` 作为 HQ NOC 管理员，应能通过企业 WAN 管理：

- `R-BRANCH`（可使用 VLAN50 gateway/subinterface 地址 `172.16.40.65`）；
- `SW-BRANCH VLAN50 = 172.16.40.66`。

为覆盖课程远程管理功能，可保留 Telnet 作为实验验收手段，并通过 VTY ACL 只允许 `192.168.30.20`。报告中注明真实生产网络应优先使用 SSH。

---

## 9. IPv6 规划

ISP 网络保持 **IPv4-only**，企业内部与跨站点管理平面使用 IPv6。

### 9.1 HQ IPv6

| 区域 | Prefix | 计划分配方式 |
|---|---|---|
| HQ OFFICE VLAN10 | `2001:db8:10::/64` | SLAAC |
| HQ IOT VLAN20 | `2001:db8:20::/64` | 静态/按设备需要 |
| HQ MANAGEMENT VLAN30 | `2001:db8:30::/64` | 静态 |
| HQ Transit | `2001:db8:100::/64` | 静态 |

推荐：

- `SW-CORE Gi1/0/24 = 2001:db8:100::1/64`
- `R-HQ G0/0 = 2001:db8:100::2/64`
- `HQ-SERVICE = 2001:db8:30::10/64`
- `ADMIN-PC = 2001:db8:30::20/64`

### 9.2 Branch IPv6

| 区域 | Prefix | 计划分配方式 |
|---|---|---|
| BR-OFFICE VLAN40 | `2001:db8:40::/64` | DHCPv6（A 需在 PT 9.0.1 实测具体 IOS 支持） |
| BR-MGMT VLAN50 | `2001:db8:50::/64` | 静态 |

推荐：

- `R-BRANCH G0/1.40 = 2001:db8:40::1/64`
- `R-BRANCH G0/1.50 = 2001:db8:50::1/64`
- `BR-ADMIN-PC = 2001:db8:50::70/64`

这样最终可以分别展示：SLAAC、DHCPv6、静态 IPv6 三种课程要求。若 PT 9.0.1 对 DHCPv6 的具体行为与实验手册存在差异，A 必须先记录实测再调整命令，但不得偷偷把 DHCPv6 验收删除。

### 9.3 IPv6-over-IPv4 Tunnel

Tunnel prefix：`2001:db8:ff::/64`

| 设备 | Tunnel0 IPv6 | IPv4 source | IPv4 destination |
|---|---|---|---|
| R-HQ | `2001:db8:ff::1/64` | `203.0.113.1` | `198.51.100.2` |
| R-BRANCH | `2001:db8:ff::2/64` | `198.51.100.2` | `203.0.113.1` |

使用 IPv6-over-IPv4 tunnel（PT IOS 中的确切 `tunnel mode` 命令由 A 实机确认）。

### 9.4 IPv6 静态路由意图

不引入 OSPFv3。计划通过静态 IPv6 路由完成：

```text
BR-MGMT 2001:db8:50::/64
    ↕ Tunnel0
HQ MANAGEMENT 2001:db8:30::/64
```

至少需要保证：

- R-BRANCH 将 `2001:db8:30::/64` 指向 Tunnel0；
- R-HQ 将 `2001:db8:50::/64` 指向 Tunnel0；
- R-HQ 可经 `2001:db8:100::1` 到达 HQ VLAN30；
- SW-CORE 有到 Branch IPv6 prefix 的返回路由，下一跳 `2001:db8:100::2`。

核心验收：`BR-ADMIN-PC` 能通过 IPv6 Overlay 到达 `HQ-SERVICE 2001:db8:30::10`。

---

## 10. ACL 与安全意图

### 10.1 Gate 1 已冻结 HQ SVI ACL

- VLAN10 inbound：OFFICE 可访问必要管理/业务服务，但不得直控 IOT。
- VLAN20 inbound：IOT 仅允许必要管理/控制流，拒绝主动访问 OFFICE。
- VLAN30：最高信任 HQ 管理域，Gate 1 不部署限制性 SVI ACL。

新增 WAN 不能破坏上述行为。

### 10.2 WAN / Branch 访问控制目标

| Source | 允许 | 拒绝/限制 |
|---|---|---|
| BR-OFFICE | HQ-SERVICE HTTP；必要 ICMP 验收 | HQ IOT、HQ 管理设备、Telnet/SSH |
| BR-ADMIN | HQ-SERVICE / HQ MANAGEMENT 的运维访问 | 默认不直接控制 HQ IoT |
| HQ ADMIN | R-BRANCH、SW-BRANCH 管理 | — |
| HQ OFFICE | Internet DNS/HTTP 经 PAT | Branch 管理设备、HQ IOT |
| HQ IOT | 必要控制服务 | Internet 默认无 PAT |
| Internet | R-HQ 映射的 TCP/80 验收服务 | 其他 HQ 内部网络 |

具体 ACL 放置与 IOS 命令由 A 在实施阶段验证，但不能降低上述最小隔离要求。

---

## 11. Port Security / MAC Binding

复用已存在的 HQ Office 接口：

```text
SW-ACCESS Fa0/1 → OFFICE-PC
```

最终计划：

- maximum 1；
- sticky MAC；
- 推荐 `violation restrict`，便于现场展示 Violation Count 且不让演示因端口 err-disable 中断；
- 临时使用 Rogue PC / 替换终端测试非法 MAC，不把攻击终端作为永久拓扑节点。

验收必须同时展示正常终端通过、非法 MAC 触发 violation，以及计数/状态变化。

---

## 12. Packet Tracer 数据平面与真实控制平面边界

### PT 模拟数据平面

```text
HQ / Branch / ISP / Internet
        ↓
VLAN + EtherChannel + ACL + Routing + OSPF + BGP + NAT + IPv6 Tunnel
```

### RealWSClient 带外控制通道

```text
EDGE-SBC-01
    ↓ Packet Tracer External Network Access / RealWSClient
ws://127.0.0.1:8000/ws/edge
    ↓
Real FastAPI Backend
```

Gate 0 已实测该通道；Final Architecture v2 不改变它。

**禁止表述：** “真实 FastAPI WebSocket 经过 VLAN20/30、R-HQ、R-ISP、BGP、NAT、Tunnel。”

**正确表述：** “Packet Tracer 模拟企业数据平面；RealWSClient 提供 Edge 到真实 Cloud Control Plane 的带外控制通道；HQ-SERVICE 用于验证模拟网络对业务/管理流的承载能力。”

---

## 13. A 的实施顺序（所有 AI 必须遵守）

1. **Topology Check**：核对新增设备型号、接口、连线；不先配高级协议。
2. **Branch LAN**：VLAN40/50、Trunk、Router-on-a-Stick、IPv4 DHCP/静态管理地址。
3. **IPv4 Underlay**：三个新增三层网段，先验证所有相邻节点 ping。
4. **HQ OSPF**：SW-CORE ↔ R-HQ；复测 Gate 1 HQ VLAN/ACL/EtherChannel。
5. **WAN eBGP**：65001 ↔ 65000 ↔ 65002；验证路由表和 BR-OFFICE → HQ-SERVICE。
6. **WAN ACL / Branch 业务权限**：只放行设计中的业务和管理路径。
7. **NAT/PAT + DNS/HTTP + TCP/80 static mapping**：完成实验三业务验收。
8. **Central Administration**：HQ ADMIN → R-BRANCH / SW-BRANCH；普通 Office 管理访问被拒绝。
9. **IPv6 Addressing**：HQ SLAAC、Branch DHCPv6、管理域静态 IPv6。
10. **IPv6-over-IPv4 Tunnel + IPv6 static routes**：BR-ADMIN → HQ MANAGEMENT。
11. **Port Security**：HQ Office sticky MAC + violation 验收。
12. **Full Regression**：重新验证 Gate 1 网络和 Edge Local Loop，确保扩展未破坏 Core。

每完成一步就提交阶段报告、关键命令、结果和建议截图点。不要一次性配置完再排错。

---

## 14. 前五次实验覆盖映射

| 课程实验能力 | Final Architecture v2 中的有机用途 |
|---|---|
| VLSM / DHCP / IPv6 / 静态路由 / 远程管理 | Branch VLSM；HQ DHCP；SLAAC + DHCPv6 + Static IPv6；IPv6 静态路由；HQ NOC 管理 Branch |
| VLAN / Trunk / EtherChannel / SVI / Router-on-a-Stick | HQ 大型园区与 Branch 小型站点采用不同合理设计 |
| ACL / NAT/PAT / 静态映射 / DNS / HTTP | 安全域控制、总部公网出口、状态页发布、业务访问 |
| OSPF / BGP / 路由传播 | HQ IGP + 多 AS WAN EGP |
| MAC Binding / Port Security / IPv6-over-IPv4 | HQ 接入安全 + 跨 IPv4 ISP 的 IPv6 管理 Overlay |

最终报告应按业务/架构组织，再用此表说明课程覆盖；不要把最终项目写成五个独立实验的机械拼接。
