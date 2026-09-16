# A — Network Owner 阶段报告（Gate 2）

| 项目 | 内容 |
|---|---|
| Owner | **A / Network** |
| 模块 | Final Architecture v2 — Branch LAN + IPv4 WAN Underlay |
| 分支 | `feat/network` |
| 依据文档 | `docs/CURRENT_GATE.md` §3、`docs/NETWORK_PLAN.md`、`docs/ACCEPTANCE.md` |
| 配置记录 | `packet_tracer/CONFIG_LOG.md`（「Final Architecture v2 — 逐层实施区」） |
| 证据目录 | `evidence/network/` |
| 截图命名依据 | `docs/ACCEPTANCE.md`：`G<Gate>-<Owner>-<序号>-<内容>-<结果>.png` |

---

## 1. 阶段目标

### 1.1 本阶段做什么

在不修改 HQ Gate 1 核心配置的前提下，为 Final Architecture v2 建立 **Branch LAN + IPv4 WAN Underlay**：

1. **Topology Check**：核对新增设备型号、物理接口与连线是否与冻结规划一致；
2. **Branch LAN**：SW-BRANCH 的 VLAN40 / VLAN50、Trunk、Access 端口与管理 SVI；R-BRANCH 的 Router-on-a-Stick 与 IPv4 DHCP；
3. **IPv4 Underlay**：为四段新增三层链路配置地址，验证**相邻节点可达**；
4. **HQ Gate 1 Regression**：确认 WAN 扩展未破坏 Gate 1 核心。

### 1.2 本阶段不做什么

- **不配置任何路由协议**（OSPF、eBGP 属 Gate 3）；
- 不做 NAT/PAT、DNS/HTTP、静态 TCP/80 映射（属 Gate 3）；
- 不做 IPv6、Tunnel、Port Security、中央远程管理（属 Gate 4）；
- 不修改 HQ VLAN10/20/30、地址、Trunk、EtherChannel、SVI、DHCP、ACL 与 `TEMP01→MCU→SBC→FAN01` 接线；
- 不为"用满接口"增加无关设备（`R-HQ G0/2`、`R-BRANCH G0/2` 保持预留）。

> 依据 `docs/NETWORK_PLAN.md` §13：必须**分层推进**，每一层验证通过后再叠加下一层，禁止一次性配置完再排错。

### 1.3 验收标准

对应 `docs/ACCEPTANCE.md`「Gate 2 → A 并行网络验收」：

> **Branch LAN 与 IPv4 WAN Underlay 基础层独立成立，HQ Gate 1 网络回归仍 PASS。**

---

## 2. 实验与开发环境

| 项目 | 内容 |
|---|---|
| 仿真平台 | **Cisco Packet Tracer 9.0.1.0858** |
| HQ 三层交换 | `SW-CORE` = Cisco **3650-24PS** |
| HQ 二层交换 | `SW-ACCESS` = Cisco **2960-24TT** |
| 新增 WAN 路由器 | `R-HQ`、`R-ISP`、`R-BRANCH` = Cisco **2911**（各 3 个板载 GE 口） |
| 新增分支交换 | `SW-BRANCH` = Cisco **2960-24TT** |
| 新增终端 | `BR-OFFICE-PC`、`BR-ADMIN-PC`（PC-PT）、`INTERNET-SERVER`（Server-PT） |
| 配置方式 | 路由器/交换使用 CLI（Cisco IOS）；主机使用 Packet Tracer GUI |
| 依赖 | 无 |
| Git 分支 | `feat/network` |
| 正式拓扑文件 | `packet_tracer/EdgeCampus.pkt`（canonical，A 唯一维护） |

### 2.1 新增设备清单（Gate 0/v2 冻结）

| 设备 | 型号 | 角色 |
|---|---|---|
| `R-HQ` | 2911 | 总部企业边界（本文档阶段：仅承担 IPv4 地址） |
| `R-ISP` | 2911 | IPv4-only ISP / Transit |
| `R-BRANCH` | 2911 | 分部边界 / Router-on-a-Stick |
| `SW-BRANCH` | 2960-24TT | 分部二层接入、VLAN40/50、Trunk、管理 SVI |
| `BR-OFFICE-PC` | PC-PT | 分部普通员工 |
| `BR-ADMIN-PC` | PC-PT | 分部异地运维人员 |
| `INTERNET-SERVER` | Server-PT | 模拟公网 DNS + HTTP 服务节点 |

### 2.2 新增物理接口映射（v2 冻结）

| 本端 | 本端接口 | 对端 | 对端接口 | 用途 |
|---|---|---|---|---|
| SW-CORE | `Gi1/0/24` | R-HQ | `G0/0` | HQ L3 Transit |
| R-HQ | `G0/1` | R-ISP | `G0/0` | HQ WAN |
| R-ISP | `G0/1` | R-BRANCH | `G0/0` | Branch WAN |
| R-ISP | `G0/2` | INTERNET-SERVER | `Fa0` | Internet Service LAN |
| R-BRANCH | `G0/1` | SW-BRANCH | `Gi0/1` | 802.1Q Router-on-a-Stick Trunk |
| SW-BRANCH | `Fa0/1` | BR-OFFICE-PC | — | access VLAN40 |
| SW-BRANCH | `Fa0/2` | BR-ADMIN-PC | — | access VLAN50 |

### 2.3 IPv4 地址规划（v2 冻结）

**新建点对点链路（/30，掩码 `255.255.255.252`）**

| 链路 | 本端 | 地址 | 对端 | 地址 |
|---|---|---|---|---|
| HQ Transit | SW-CORE Gi1/0/24 | `10.255.0.1` | R-HQ G0/0 | `10.255.0.2` |
| HQ ↔ ISP | R-HQ G0/1 | `203.0.113.1` | R-ISP G0/0 | `203.0.113.2` |
| ISP ↔ Branch | R-ISP G0/1 | `198.51.100.1` | R-BRANCH G0/0 | `198.51.100.2` |

**Internet Service LAN（/24）**

| 节点 | 地址 |
|---|---|
| R-ISP G0/2 | `192.0.2.1/24` |
| INTERNET-SERVER Fa0 | `192.0.2.10/24`，GW `192.0.2.1` |

**Branch VLSM（来自 `172.16.40.0/24`）**

| VLAN | 名称 | 网段 | 网关 | 用途 |
|---:|---|---|---|---|
| 40 | BR-OFFICE | `172.16.40.0/26` | `172.16.40.1` | 分部办公（DHCP） |
| 50 | BR-MGMT | `172.16.40.64/27` | `172.16.40.65` | 分部管理 / 运维 |

### 2.4 Branch 终端地址

| 设备 | IPv4 | 掩码 | 网关 | 方式 |
|---|---|---|---|---|
| BR-OFFICE-PC | `172.16.40.2`（实测租约） | `255.255.255.192` | `172.16.40.1` | DHCP |
| BR-ADMIN-PC | `172.16.40.70` | `255.255.255.224` | `172.16.40.65` | 静态 |
| SW-BRANCH（VLAN50 SVI） | `172.16.40.66` | `255.255.255.224` | `172.16.40.65` | 静态 |

---

## 3. 架构与连接关系

```text
                 INTERNET-SERVER (192.0.2.10/24)
                          |
                     R-ISP (AS 预留)
                G0/0 203.0.113.2/30 | G0/1 198.51.100.1/30
                          |                     |
        R-HQ G0/1 203.0.113.1/30        R-BRANCH G0/0 198.51.100.2/30
                 |                              |
        R-HQ G0/0 10.255.0.2/30         G0/1 ── 802.1Q Trunk ──> SW-BRANCH Gi0/1
                 |                              |                  |
        SW-CORE Gi1/0/24 10.255.0.1/30          |            Fa0/1 ── BR-OFFICE-PC (VLAN40)
        (HQ L3 Core，Gate 1 未改动)             |            Fa0/2 ── BR-ADMIN-PC  (VLAN50)
                 |                              |
        SW-ACCESS ══ LACP EtherChannel ══ SW-CORE
                 |
   OFFICE(VLAN10) / IOT(VLAN20, EDGE-SBC-01) / MANAGEMENT(VLAN30)
                 |
   TEMP01 → IO-MCU-01 → EDGE-SBC-01 → FAN01   （Gate 1 A+B 集成，本 Gate 未改动）
```

> `R-BRANCH G0/1.40 = 172.16.40.1/26`、`G0/1.50 = 172.16.40.65/27` 为两段 Branch 子网的网关。

### 3.1 真实性边界（沿用 ADR-012）

| 路径 | 组成 | 性质 |
|---|---|---|
| **PT 模拟数据平面** | VLAN / Trunk / EtherChannel / SVI / ACL / 路由 / WAN 链路 | 本 Gate 的配置对象 |
| **Edge–Cloud 带外控制通道** | `EDGE-SBC-01 → RealWSClient → ws://127.0.0.1:8000 → Real FastAPI` | 与 PT WAN **无关** |

**禁止表述**真实 WebSocket 经过 R-HQ / R-ISP / WAN / VLAN20/30。本 Gate 新增的 R-HQ / R-ISP / R-BRANCH 只模拟企业数据平面，**不承载真实控制通道**。

---

## 4. 实现过程

严格按 `docs/NETWORK_PLAN.md` §13 的分层顺序执行，每步验证后再进入下一步。

### 4.1 第 1 层：Topology Check

**目标**：确认新增设备型号、接口与连线与冻结表一致，避免"静默换口"。

**方法**：

| 对象 | 手段 |
|---|---|
| 路由器/交换机之间的链路 | `show cdp neighbors`（CDP 是 Cisco 私有协议，可在设备间互相确认两端接口） |
| 到主机的链路 | `show interfaces status`（交换机侧）/ `show ip interface brief`（路由器侧） |

> 说明：`INTERNET-SERVER`、`BR-OFFICE-PC`、`BR-ADMIN-PC` 是主机设备，**不运行 CDP**，因此不会出现在邻居列表中——这是正常现象，改用接口状态验证。

**结果**：7 条冻结链路全部核实（详见 7.1）。

**截图**：【G2-A-01】【G2-A-01b】【G2-A-01c】【G2-A-01d】

---

### 4.2 第 2 层：SW-BRANCH 二层配置

**目标**：建立分部两个 VLAN、上行 Trunk 与管理地址。

**配置**：

```text
hostname SW-BRANCH
vlan 40
 name BR-OFFICE
vlan 50
 name BR-MGMT
interface gigabitEthernet 0/1
 switchport mode trunk
 switchport trunk allowed vlan 40,50
interface fastEthernet 0/1
 switchport mode access
 switchport access vlan 40
interface fastEthernet 0/2
 switchport mode access
 switchport access vlan 50
interface vlan 50
 ip address 172.16.40.66 255.255.255.224
 no shutdown
ip default-gateway 172.16.40.65
```

**关键解释**：

- 分部 Trunk **只放行 `40,50`**（与 HQ 的 `10,20,30` 完全隔离）；
- 2960 是**二层**设备：管理地址用 SVI 承载，出口依赖 **`ip default-gateway`**，**不使用** `ip routing`；
- 管理地址放在 **VLAN50（管理域）**，而不是 VLAN40（业务域），与安全域划分意图一致。

**结果**：VLAN40（Fa0/1）、VLAN50（Fa0/2）均 active；`Gi0/1` trunk 的 allowed / active / forwarding 均为 `40,50`；`Vlan50 = 172.16.40.66` up/up。

**截图**：【G2-A-02】

---

### 4.3 第 3 层：R-BRANCH Router-on-a-Stick

**目标**：用单个物理接口承载两个 VLAN 的网关。

**配置**：

```text
hostname R-BRANCH
interface gigabitEthernet 0/1
 no shutdown
interface gigabitEthernet 0/1.40
 encapsulation dot1Q 40
 ip address 172.16.40.1 255.255.255.192
interface gigabitEthernet 0/1.50
 encapsulation dot1Q 50
 ip address 172.16.40.65 255.255.255.224
```

**关键解释**：

- 物理接口 `G0/1` **不配置 IP**，仅作为承载；
- 两个子接口分别用 `encapsulation dot1Q <VLAN>` 打标签，VLAN 号必须与 SW-BRANCH 一致；
- **HQ 用 SVI（3650 三层交换）、Branch 用 ROAS（2911 单臂路由）**——这是按站点规模选择架构（ADR-008），而非重复配置。

**结果**：`G0/1.40`、`G0/1.50` 均 up/up；`show ip route` 出现 `C 172.16.40.0/26`、`C 172.16.40.64/27` 两条直连路由。

**截图**：【G2-A-03】

---

### 4.4 第 4 层：Branch 地址与 DHCP

**目标**：BR-OFFICE 自动获址，BR-ADMIN 使用冻结静态地址，管理地址可达。

**配置（R-BRANCH）**：

```text
ip dhcp excluded-address 172.16.40.1
ip dhcp pool BR-OFFICE
 network 172.16.40.0 255.255.255.192
 default-router 172.16.40.1
```

**终端配置**：

| 设备 | 方式 | 位置（Packet Tracer） |
|---|---|---|
| BR-OFFICE-PC | DHCP | Desktop → IP Configuration → DHCP |
| BR-ADMIN-PC | 静态 `172.16.40.70/27`，GW `.65` | Desktop → IP Configuration → Static |

**关键解释**：`excluded-address` 排除网关 `.1`，可分配区间为 `.2–.62`（`.0` 网络号、`.63` 广播）；DHCP 服务**只覆盖 VLAN40**，管理域保持静态地址，符合"业务域动态、管理域静态"的常规做法。

**结果**：

- `show ip dhcp binding` → `172.16.40.2 / 00E0.B002.9A06 / Automatic`；
- BR-OFFICE-PC `ipconfig` → `172.16.40.2 / 255.255.255.192 / GW 172.16.40.1`；
- BR-OFFICE-PC → `172.16.40.1` 4/4 通；
- BR-ADMIN-PC → `172.16.40.65` 4/4 通、→ `172.16.40.66`（SW-BRANCH）3/4 通（首包 ARP）。

**截图**：【G2-A-04】

---

### 4.5 第 5 层：IPv4 Underlay（四段链路地址）

**目标**：为四段新增链路配置地址，**不叠加任何路由协议**。

**配置**：

```text
SW-CORE
interface gigabitEthernet 1/0/24
 no switchport
 ip address 10.255.0.1 255.255.255.252
 no shutdown

R-HQ      G0/0  10.255.0.2/30       G0/1  203.0.113.1/30
R-ISP     G0/0  203.0.113.2/30      G0/1  198.51.100.1/30    G0/2  192.0.2.1/24
R-BRANCH  G0/0  198.51.100.2/30
INTERNET-SERVER（GUI） Fa0 192.0.2.10/24  Gateway 192.0.2.1
```

**关键解释**：

- **`no switchport`**：3650 的 `Gi1/0/24` 需要从二层交换口切换为**三层路由口**才能承载 HQ Transit。**这是本 Gate 唯一的平台能力实测点**，Packet Tracer 9.0.1 实测支持。
- **点对点链路统一使用 `/30`**：仅 2 个可用地址，避免浪费，也是 WAN 互连的常规做法。
- **R-HQ G0/2、R-BRANCH G0/2 保持预留**，未为"用满接口"增加配置。

**结果**：四段链路各接口均 **up/up** 且地址正确（详见 7.2）；`INTERNET-SERVER` ping `192.0.2.1` 4/4 通。

**截图**：【G2-A-05】【G2-A-05b】【G2-A-05c】【G2-A-05d】【G2-A-05e】

---

### 4.6 第 6 层：相邻三层可达验证

**目标**：证明四段新增链路真的连通。

**方法**：**只测相邻节点**（尚无路由协议，跨段必然不通，属设计内行为）。

| 从 | ping | 结果 |
|---|---|---|
| INTERNET-SERVER | `192.0.2.1` | 4/4 ✅ |
| SW-CORE | `10.255.0.2` | 4/5（80%）✅ |
| R-HQ | `203.0.113.2` | 4/5（80%）✅ |
| R-ISP | `198.51.100.2` | 4/5（80%）✅ |
| R-BRANCH（反向补测） | `198.51.100.1` | 5/5 ✅ |

**关键解释**：首次 ping 出现 1 个包超时（成功率 80%）是 **ARP 解析期**造成的——第 1 个 ICMP 报文在 ARP 完成前即超时，后续全部正常，**非故障**。ping 成功本身已证明**双向**连通（请求发出、回复返回）。

**截图**：【G2-A-06】【G2-A-06b】【G2-A-06c】【G2-A-06d】

---

### 4.7 第 7 层：HQ Gate 1 Regression

**目标**：确认 WAN 扩展未破坏 Gate 1 核心。

**检查命令**：

```text
show etherchannel summary
show interfaces trunk
show vlan brief
show ip interface brief
show access-lists
```

**行为测试**：

| # | 从 | 操作 | 预期 | 实际 |
|---|---|---|---|---|
| 1 | OFFICE-PC | `ping 192.168.30.20` | 允许 | 3/4 通 ✅ |
| 2 | OFFICE-PC | `ping 192.168.20.10` | 拒绝 | 4 个 `Destination host unreachable`，100% 丢包 ✅ |
| 3 | ADMIN-PC | `ping 192.168.20.10` | 允许 | 3/4 通 ✅ |

**结果**：SW-CORE / SW-ACCESS 的全部基础项无退化（详见 7.3）；三个行为测试全部符合预期。

**截图**：【G2-A-07】【G2-A-07b】【G2-A-07c】【G2-A-07d】【G2-A-07e】【G2-A-07f】

---

## 5. 关键配置解释（要点归纳）

1. **`no switchport`（3650 路由口）**：三层交换机的物理口默认是交换口，必须显式切换为路由口才能直接配置 IP 承载 WAN 互连。本 Gate 已实测通过。
2. **L2 交换机管理出口用 `ip default-gateway`**：2960 不参与三层转发，自身产生的管理流量（如远程管理回包）需要一个默认出口，此时不能用 `ip routing`。
3. **Router-on-a-Stick 的 VLAN 号必须两端一致**：`encapsulation dot1Q 40/50` 与 SW-BRANCH 的 VLAN ID 一一对应，否则子接口无法收包。
4. **Trunk 放行列表按站点收敛**：HQ 侧 `10,20,30`，Branch 侧 `40,50`，互不携带对方 VLAN，从二层就切断跨站点广播域。
5. **点对点链路用 `/30`**：WAN 互连仅需 2 个地址，`/30` 是最省地址的常规选择。
6. **VLSM 按业务规模划分**：Branch 总块 `172.16.40.0/24` 按"业务域大、管理域小"拆成 `/26` + `/27`，管理域只用 30 个地址。
7. **分层实施、逐层验证**：每一层完成即验证并留存证据，避免一次性叠加多协议后难以定位故障（`docs/NETWORK_PLAN.md` §13 的强制要求）。

---

## 6. 问题与排查过程

### 6.1 SW-ACCESS 的 `show access-lists` 没有输出

**现象**：执行 Gate 2 regression 时，SW-CORE 的 `show access-lists` 正常输出两条 ACL，但 **SW-ACCESS 上该命令无任何输出**。

**初步判断**：怀疑 ACL 丢失或配置被 WAN 扩展破坏。

**排查步骤**：

1. 回到 `docs/CURRENT_GATE.md` §10.1 与 Gate 1 配置记录核对 ACL 的部署位置；
2. 确认 SW-ACCESS 的设备角色。

**根因**：**属于正常现象**。ACL 全部部署在**三层核心 SW-CORE 的 SVI（`interface Vlan10/20`）**上；SW-ACCESS 是**二层交换机**，本身不承载三层 ACL，因此 `show access-lists` 为空是正确的。

**结论**：`docs/CURRENT_GATE.md` §3.4 中列出的 `show access-lists` 指的是 **SW-CORE**；在 SW-ACCESS 上执行该命令没有意义。

---

### 6.2 ACL deny 命中计数与实际 ping 包数不完全对应

**现象**：回归测试中 OFFICE-PC 向 `192.168.20.10` 发送 4 个 ICMP 请求，全部被拦截（100% 丢包 + `Destination host unreachable`），但 `show access-lists` 中 deny 规则的命中计数显示为 `2 match(es)`。

**初步判断**：怀疑 ACL 只拦截了部分流量（是否漏放了一半？）。

**排查步骤**：

1. 核对 ping 的实际结果：4 个包**全部**返回 `Destination host unreachable`，收到 0 个回复；
2. 核对 ACL 规则顺序：请求的目标是 `192.168.20.10`，只会匹配第 30 条 `deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255`，不可能被第 10/20 条放行；
3. 交叉比对 ping 结果与计数。

**根因**：**Packet Tracer 的 ACL 计数本身存在偏差**（Gate 1 中同类测试曾出现 4 个包对应 4 次命中，本次为 4 个包对应 2 次命中）。计数与实际拦截效果不一致时，**应以实际拦截效果为准**。

**结论**：隔离功能**确实生效**。本报告与 `CONFIG_LOG.md` 中**只记录"deny 命中"这一事实，不虚报命中次数**。

---

### 6.3 四段新增链路首次 ping 出现 1 个包超时

**现象**：SW-CORE→R-HQ、R-HQ→R-ISP、R-ISP→R-BRANCH 三段均显示 `Success rate is 80 percent (4/5)`，首个包超时。

**根因**：首次通信需先完成 **ARP 解析**，第 1 个 ICMP 报文在 ARP 完成前即超时。

**结论**：**非故障**。判断相邻可达应看"是否收到回复"，而非单看成功率。反向补测（R-BRANCH→R-ISP）因 ARP 已学习，成功率为 100%，进一步印证该判断。

---

### 6.4 主机设备不出现在 CDP 邻居列表

**现象**：R-ISP 的 `show cdp neighbors` 只列出 `G0/0`、`G0/1` 两个邻居，**没有列出 G0/2 对端的 `INTERNET-SERVER`**。

**根因**：CDP 是 Cisco 私有链路层协议，`INTERNET-SERVER`（Server-PT）与两台 BR-PC 都是**通用主机，不运行 CDP**，因此不会出现在邻居列表中。

**解决**：改用接口状态验证——R-ISP `show ip interface brief` 中 `G0/2` 为 **up/up**，SW-BRANCH `show interfaces status` 中 `Fa0/1`、`Fa0/2` 为 **connected**。

**结论**：链路实际存在且已启用，CDP 无输出不代表链路缺失。

---

## 7. 验收结果

### 7.1 Topology Check（7 条新增链路）

| # | 冻结链路 | 验证方式 | 结果 |
|---|---|---|---|
| 1 | SW-CORE Gi1/0/24 ↔ R-HQ G0/0 | CDP 双向 | ✅ |
| 2 | R-HQ G0/1 ↔ R-ISP G0/0 | CDP 双向 | ✅ |
| 3 | R-ISP G0/1 ↔ R-BRANCH G0/0 | CDP 双向 | ✅ |
| 4 | R-ISP G0/2 ↔ INTERNET-SERVER Fa0 | G0/2 up/up | ✅ |
| 5 | R-BRANCH G0/1 ↔ SW-BRANCH Gi0/1 | CDP 双向 | ✅ |
| 6 | SW-BRANCH Fa0/1 ↔ BR-OFFICE-PC | connected | ✅ |
| 7 | SW-BRANCH Fa0/2 ↔ BR-ADMIN-PC | connected | ✅ |

设备型号与冻结规划一致（2911 ×3、2960-24TT ×2、Server-PT / PC-PT 若干），**无一处端口冲突或静默换口**。

### 7.2 IPv4 Underlay 地址

| 设备 | 接口 | 地址 | 状态 | 判定 |
|---|---|---|---|---|
| SW-CORE | Gi1/0/24 | `10.255.0.1/30` | up/up | ✅ |
| R-HQ | G0/0 / G0/1 | `10.255.0.2` / `203.0.113.1` | up/up | ✅ |
| R-ISP | G0/0 / G0/1 / G0/2 | `203.0.113.2` / `198.51.100.1` / `192.0.2.1` | up/up | ✅ |
| R-BRANCH | G0/0 | `198.51.100.2/30` | up/up | ✅ |
| INTERNET-SERVER | Fa0 | `192.0.2.10/24`，GW `192.0.2.1` | — | ✅ |

### 7.3 相邻三层可达

| 链路 | 从 → 到 | 结果 | 判定 |
|---|---|---|---|
| Internet Service LAN | INTERNET-SERVER → `192.0.2.1` | 4/4 | ✅ |
| HQ Transit | SW-CORE → `10.255.0.2` | 4/5（首包 ARP） | ✅ |
| HQ ↔ ISP | R-HQ → `203.0.113.2` | 4/5（首包 ARP） | ✅ |
| ISP ↔ Branch | R-ISP → `198.51.100.2` | 4/5（首包 ARP） | ✅ |
| 反向补测 | R-BRANCH → `198.51.100.1` | 5/5 | ✅ |

### 7.4 Branch LAN

| 检查项 | 预期 | 实际 | 判定 |
|---|---|---|---|
| VLAN40 / VLAN50 | active 且命名正确 | `BR-OFFICE`（Fa0/1）、`BR-MGMT`（Fa0/2） | ✅ |
| Branch Trunk | allowed `40,50` | allowed / active / forwarding 均 `40,50` | ✅ |
| Router-on-a-Stick | 两个子接口 up/up | `G0/1.40 = .1`、`G0/1.50 = .65` | ✅ |
| Branch 直连路由 | 两条 `/26`、`/27` | `C 172.16.40.0/26`、`C 172.16.40.64/27` | ✅ |
| DHCP | BR-OFFICE 自动获址 | `172.16.40.2`，GW `.1` | ✅ |
| 管理地址 | SW-BRANCH `.66` 可达 | BR-ADMIN → `.66` 3/4 通 | ✅ |

### 7.5 HQ Gate 1 Regression

| 检查项 | 实际 | 判定 |
|---|---|---|
| SW-CORE EtherChannel | `Po1(SU)`，`Gig1/0/1(P)`、`Gig1/0/2(P)` | ✅ |
| SW-CORE Trunk | allowed / active / forwarding 均 `10,20,30` | ✅ |
| SW-CORE VLAN | 10 / 20 / 30 全 active | ✅ |
| SW-CORE SVI | `Vlan10/20/30` 全 up/up | ✅ |
| SW-CORE ACL | `OFFICE-IN` / `IOT-IN` 规则完整，deny 有命中 | ✅ |
| SW-ACCESS EtherChannel | `Po1(SU)`，`Gig0/1(P)`、`Gig0/2(P)` | ✅ |
| SW-ACCESS Trunk | `10,20,30` | ✅ |
| SW-ACCESS VLAN | 10→Fa0/1、20→Fa0/2、30→Fa0/3,4（**划分未变**） | ✅ |
| 行为：OFFICE → ADMIN | 3/4 通 | ✅ 允许 |
| 行为：OFFICE → IOT | 100% 丢包，`Destination host unreachable` | ✅ 拒绝 |
| 行为：ADMIN → EDGE-SBC | 3/4 通 | ✅ 允许 |

> SW-CORE `Gi1/0/24 = 10.255.0.1` 为本 Gate **新增**，不属回归；VLAN 1 中不再包含 Gi1/0/24 亦为路由口的正常结果。

### 7.6 公共契约与冻结项检查

| 检查项 | 结果 |
|---|---|
| HQ VLAN10/20/30 与 IPv4 网段 | **未修改** |
| Gate 1 已验证 HQ 端口映射 | **未修改** |
| v2 新增物理接口映射 | **按冻结表实施，无换口** |
| Branch VLAN40/50、WAN 前缀、Internet LAN | **按冻结值实施** |
| AS 号（65001/65000/65002） | **本 Gate 未涉及**（G3 使用） |
| Protocol v1.0 / 设备 ID / WS 路径 | **未涉及** |
| `TEMP01 → MCU → SBC → FAN01` 接线 | **未改动** |

---

## 8. 截图索引

全部位于 `evidence/network/`，命名遵循 `docs/ACCEPTANCE.md` 的 `G<Gate>-<Owner>-<序号>-<内容>-<结果>.png`。

| 编号 | 文件 | 内容 | 证明什么 |
|---|---|---|---|
| G2-A-01 | `G2-A-01-topology-check-pass.png` | 新增 WAN/Branch 拓扑全景 | 设备与连线与冻结规划一致 |
| G2-A-01b | `G2-A-01b-cdp-neighbors-pass.png` | SW-CORE / SW-BRANCH 的 `show cdp neighbors` | `SW-CORE Gi1/0/24 ↔ R-HQ`、`SW-BRANCH Gi0/1 ↔ R-BRANCH` 端口正确 |
| G2-A-01c | `G2-A-01c-cdp-routers-pass.png` | R-HQ / R-ISP / R-BRANCH 的 `show cdp neighbors` | 三段 WAN 互连端口**双向**确认 |
| G2-A-01d | `G2-A-01d-host-links-pass.png` | R-ISP `show ip interface brief` + SW-BRANCH `show interfaces status` | 主机侧三条链路已连接并启用 |
| G2-A-02 | `G2-A-02-branch-vlan-trunk-pass.png` | SW-BRANCH `show vlan brief` + `show interfaces trunk` + `show ip interface brief` | Branch VLAN40/50、Trunk 40,50、管理地址 `.66` 正常 |
| G2-A-03 | `G2-A-03-branch-roas-pass.png` | R-BRANCH `show ip interface brief` + `show ip route` | ROAS 两个子接口 up/up 且生成两条直连路由 |
| G2-A-04 | `G2-A-04-branch-dhcp-ping-pass.png` | R-BRANCH `show ip dhcp binding` + 两台 BR-PC 的 `ipconfig`/`ping` | DHCP 与静态地址、管理地址可达 |
| G2-A-05 | `G2-A-05-wan-swcore-underlay-pass.png` | SW-CORE `show ip interface brief` | `Gi1/0/24 = 10.255.0.1` up/up（`no switchport` 实测通过） |
| G2-A-05b | `G2-A-05b-wan-rhq-underlay-pass.png` | R-HQ 配置命令 + `show ip interface brief` | R-HQ 两段地址正确 |
| G2-A-05c | `G2-A-05c-wan-risp-underlay-pass.png` | R-ISP `show ip interface brief` | R-ISP 三个接口地址正确 |
| G2-A-05d | `G2-A-05d-wan-rbranch-underlay-pass.png` | R-BRANCH `show ip interface brief` | `G0/0 = 198.51.100.2` up/up |
| G2-A-05e | `G2-A-05e-internet-server-underlay-pass.png` | INTERNET-SERVER `ipconfig` + `ping 192.0.2.1` | Internet LAN 地址与连通 |
| G2-A-06 | `G2-A-06-wan-transit-ping-pass.png` | SW-CORE → `10.255.0.2` | HQ Transit 相邻可达 |
| G2-A-06b | `G2-A-06b-wan-hq-isp-ping-pass.png` | R-HQ → `203.0.113.2` | HQ ↔ ISP 相邻可达 |
| G2-A-06c | `G2-A-06c-wan-isp-branch-ping-pass.png` | R-ISP → `198.51.100.2` | ISP ↔ Branch 相邻可达 |
| G2-A-06d | `G2-A-06d-wan-branch-reverse-ping-pass.png` | R-BRANCH → `198.51.100.1` | 反向 100% 成功，印证 80% 为首包 ARP |
| G2-A-07 | `G2-A-07-hq-regression-swcore-pass.png` | SW-CORE EtherChannel / Trunk / VLAN | HQ 核心二层无退化 |
| G2-A-07b | `G2-A-07b-hq-regression-swcore-acl-pass.png` | SW-CORE `show ip interface brief` + `show access-lists` | 三个 SVI up/up；两条 ACL 完整、deny 有命中 |
| G2-A-07c | `G2-A-07c-hq-regression-swaccess-pass.png` | SW-ACCESS EtherChannel / Trunk / VLAN | 接入层无退化，端口划分未变 |
| G2-A-07d | `G2-A-07d-hq-regression-swaccess-ios-pass.png` | SW-ACCESS `show ip interface brief` + `show access-lists` | 接口正常；`show access-lists` 为空属正常（二层设备） |
| G2-A-07e | `G2-A-07e-hq-behavior-office-pass.png` | OFFICE-PC → `.30.20`（通）+ → `.20.10`（拒） | Gate 1 允许/拒绝行为全部保持 |
| G2-A-07f | `G2-A-07f-hq-behavior-admin-pass.png` | ADMIN-PC → `192.168.20.10`（通） | 管理域对 IOT 的允许行为保持 |

**"一图多证据"示例**：`G2-A-02`（VLAN + Trunk + 管理地址同屏）、`G2-A-04`（交换机绑定表 + PC 地址 + ping 同屏）、`G2-A-07e`（拒绝与放行同屏对照）。

---

## 9. 本阶段交付物

| 交付物 | 位置 | 说明 |
|---|---|---|
| 正式拓扑文件 | `packet_tracer/EdgeCampus.pkt` | canonical `.pkt`，已包含 Gate 2 的 Branch/WAN 配置 |
| 配置与验证日志 | `packet_tracer/CONFIG_LOG.md` | 「Final Architecture v2 — 逐层实施区 → Gate 2」已填入真实命令、结果与问题 |
| 验收证据 | `evidence/network/G2-A-01 ~ G2-A-07f`（22 张） | 见第 8 节索引 |
| 集成看板更新 | `docs/PROJECT_BOARD.md` | Branch LAN/ROAS、IPv4 WAN Underlay、HQ Gate1 Regression 行 → PASS G2，并新增 Integration Check 记录 |
| 本阶段报告 | `docs/gate2/A_NETWORK_REPORT.md` | 本文档 |

> 本模块不产出代码（纯网络配置），交付物以拓扑文件、配置日志与证据为主。

---

## 10. 创新性支撑

> **归属说明**：Gate 2 本身不新增"创新点"，它的价值是**为 Gate 3 / Gate 4 的四条跨站点业务流提供可承载的分层网络底座**。相关业务流的正式验收在 G3/G4，本节只说明本阶段的设计取向。

### 10.1 向外扩展而非重构（ADR-006）

Gate 1 的 HQ Core 已经实测通过，本 Gate 采用**只向外延伸**的策略：

```text
新增网络只从 SW-CORE Gi1/0/24 向外扩展
HQ VLAN10/20/30、Trunk、EtherChannel、SVI、DHCP、ACL 全部不动
```

结果：在获得多园区组网能力的同时，**Gate 1 的回归测试零退化**。这体现的是工程上的风险控制取向——不为了覆盖课程能力去重写已经稳定的核心。

### 10.2 按站点规模选择架构（ADR-008）

| 站点 | 规模假设 | VLAN 间路由方式 | 理由 |
|---|---|---|---|
| HQ | 大型园区 | 3650 **SVI** 三层交换 | 高性能、集中核心 |
| Branch | 小型分部 | 2911 **Router-on-a-Stick** | 设备少、成本低、结构清晰 |

两种方案**同时存在不是重复配置**，而是"按规模选型"的设计表达，这一点在最终报告的架构章节中可作为设计合理性的论据。

### 10.3 分层可验证的实施顺序

`docs/NETWORK_PLAN.md` §13 强制要求逐层推进（Physical → Branch LAN → Underlay → OSPF → eBGP → NAT → IPv6 → Security → Regression）。本 Gate 严格按此执行，**每一层都有独立证据**，使故障定位范围始终局限于"当前这一层"。

### 10.4 在最终报告与现场演示中的位置

| 用途 | 位置 | 提供的素材 |
|---|---|---|
| 网络设计章节 | `docs/REPORT_OUTLINE.md` 网络设计 | 第 2–5 节 |
| 课程覆盖说明 | `docs/ACCEPTANCE.md` 五次实验覆盖核对 | 实验二（VLAN/Trunk/SVI/ROAS）、实验一（VLSM/DHCP） |
| 功能测试章节 | 最终功能测试矩阵 N4 | 第 7.4 节 |
| 现场演示 | `docs/DEMO_SCRIPT.md` | 分部拓扑与相邻可达演示 |

---

## 11. 分工与 AI 协作记录

### 11.1 本人角色与边界

| 项目 | 内容 |
|---|---|
| Owner | **A / Network** |
| 本阶段可修改范围 | `packet_tracer/`（含 canonical `EdgeCampus.pkt`、`CONFIG_LOG.md`）、网络证据 `evidence/network/`、本报告 |
| 明确不修改 | `backend/`（C）、`edge/`（B）、`dashboard/` 与 `tests/`（D） |
| 排他约定 | A 为 canonical `.pkt` 唯一 Owner；B 如需开发 PT Edge 应使用副本，由 A 合并回正式文件 |

### 11.2 本阶段承担明细

Topology Check（7 条新增链路）→ SW-BRANCH 二层（VLAN40/50、Trunk、Access、管理 SVI）→ R-BRANCH Router-on-a-Stick → Branch DHCP 与终端地址 → IPv4 Underlay 四段地址配置 → 相邻可达验证 → HQ Gate 1 Regression（五条 show + 三个行为测试）→ 证据采集 → `CONFIG_LOG.md` / `PROJECT_BOARD.md` / 本报告。

### 11.3 与各 Owner 的接口

| 对象 | 接口内容 |
|---|---|
| **B / Edge** | 本 Gate 未触及 Edge 侧；`TEMP01 → MCU → SBC → FAN01` 接线与 Gate 1 A+B 集成结果**保持不变**；B 的真实 Telemetry 属于 G2 软件主线，与 A 的网络扩展并行 |
| **C / Control Plane** | `BACKEND-STUB / HQ-SERVICE = 192.168.30.10` 未改动；G3 将由其承载 Branch 业务访问目标 |
| **D / UI & Integration** | A 提供网络侧证据；G2 的端到端联调由 B/C/D 主线负责 |
| **全组** | HQ Gate 1 Core、Protocol v1.0、设备 ID、WS 路径本阶段**均未修改** |

### 11.4 协作机制与流程遵守

| 机制 | 本阶段执行情况 |
|---|---|
| Owner 边界（`docs/CONTRIBUTING.md`） | 严格遵守，未跨模块修改 |
| 分层实施规则（`NETWORK_PLAN.md` §13） | 严格执行，逐层验证并留证 |
| 新增冻结项不得擅自变更 | 接口、VLAN、IPv4 前缀、Gateway 全部按冻结值实施 |
| 公共契约变更须走 RFC | **未触发** |
| HQ Core 不得破坏 | 通过 Gate 2 Regression 验证（7.5） |
| `.pkt` 所有权 | 全程由 A 在 canonical 文件上实施；起点采用队长提供的 87,390 字节版本并回归确认其 HQ 配置完整 |

### 11.5 AI 协作记录

| 项目 | 内容 |
|---|---|
| AI 承担的角色 | 分层实施指导、调试记录员、截图证据管理员、阶段报告整理者（依据 `EdgeCampus_AI阶段记录与提交规范.md`） |
| **红线遵守** | 未修改 HQ VLAN/IP、Gate 1 端口映射、v2 冻结接口、Protocol 字段、设备 ID、WS 路径 |
| **AI 参与的真实排查** | ① SW-ACCESS `show access-lists` 为空是否异常；② deny 计数（2）与 ping 包数（4）不一致的判定；③ 主机设备不出现于 CDP 邻居列表的原因 |
| **AI 被纠正的记录** | 在整理证据过程中，AI 曾口头声明"已完成某张截图改名"但**实际未执行**，经核对后被指出并立即补做。该过程如实保留，未做美化 |
| **AI 明确拒绝的做法** | 当回归测试一度被误读为"OFFICE→IOT 通了"时，AI **未直接改动 ACL**，而是先要求提供 `show access-lists` / `show running-config` / `show ip interface` 输出以定位，避免在未确认前修改冻结配置 |

### 11.6 真实性声明

- 本报告中的**全部命令与输出**均为实际执行所得，未编造；
- ACL 命中计数等存在平台偏差的数值，**如实记录并注明以实际效果为准，不虚报**；
- 跨站点业务路径（如 BR-OFFICE → HQ-SERVICE）当前**必然不通**（尚无路由协议），本报告**未将其写成已完成**，明确列为 Gate 3 范围；
- 归属于其他 Owner 范围的工作已在报告中单独标注，未计入本模块成果。

---

## 12. 未完成项与后续工作

### 12.1 本 Gate 明确不做、留给后续 Gate 的部分

| 项 | 目标 Gate | 说明 |
|---|---|---|
| HQ OSPF Area 0（SW-CORE ↔ R-HQ） | **G3** | 让 HQ 内部网段被 R-HQ 学习 |
| WAN eBGP（AS65001 / 65000 / 65002） | **G3** | 跨 AS 路由交换 |
| BR-OFFICE → HQ-SERVICE 业务访问 | **G3** | 依赖 eBGP 路由可达 |
| HQ OFFICE → PAT → Internet | **G3** | R-HQ 承担 HQ Internet Edge |
| DNS / HTTP / `203.0.113.1:80 → 192.168.30.10:80` | **G3** | 实验三服务发布验收 |
| WAN / Branch 业务 ACL | **G3** | 按 `NETWORK_PLAN.md` §10.2 权限矩阵 |
| IPv6（SLAAC / DHCPv6 / Static） | **G4** | — |
| IPv6-over-IPv4 Tunnel + 静态 IPv6 路由 | **G4** | BR-ADMIN → HQ MANAGEMENT |
| 中央远程管理、Port Security | **G4** | — |

> 当前跨站点 ping（例如 BR-OFFICE-PC → HQ 任一地址）**不通是设计内的预期结果**，因为本 Gate 只完成地址与相邻可达，尚未叠加任何路由协议。

### 12.2 其他 Owner 任务范围（非 A 职责）

| 项 | Owner | 说明 |
|---|---|---|
| 真实 PT Telemetry（TEMP01 → Dashboard） | **B+C+D** | G2 的主 Critical Path，与 A 并行 |
| C 的 Gate 1 Owner 证据补齐 | **C** | `docs/gate1/C_BACKEND_REPORT.md` 目前为 **PLACEHOLDER**，Gate 5 Freeze 前必须清零 |
| Dashboard 接真 PT Telemetry | **D** | — |

### 12.3 后续网络层工作（A）

1. 按 `docs/NETWORK_PLAN.md` §13 继续叠加 **HQ OSPF**，每层后重复本报告第 4.7 节的 Regression；
2. Gate 3 起 OSPF/eBGP 生效后，需重新验证 HQ Core 与 Branch 的端到端业务流；
3. 持续维护 canonical `.pkt`，并在每次网络层变更后更新 `CONFIG_LOG.md` 与 `PROJECT_BOARD.md`。

---

## 13. Gate 2 状态小结

```text
Gate 状态：A（Network）侧 Gate 2 网络基础层完成（Branch LAN + IPv4 WAN Underlay）

已完成：
  - Topology Check：7 条新增冻结链路全部核实（CDP 双向 + 接口状态）
  - Branch LAN：SW-BRANCH VLAN40/50 + Trunk 40,50 + Access + 管理 SVI .66
  - R-BRANCH Router-on-a-Stick：G0/1.40 = .1、G0/1.50 = .65，两条直连路由
  - Branch 地址与 DHCP：BR-OFFICE-PC 获 172.16.40.2；BR-ADMIN 静态 .70
  - IPv4 Underlay：四段链路地址正确（含 3650 no switchport 实测通过）
  - 相邻三层可达：四段链路全部连通
  - HQ Gate 1 Regression：五条 show + 三个行为测试全部符合预期
  - 22 张验收证据 + CONFIG_LOG + PROJECT_BOARD 同步

未完成（设计内，属后续 Gate）：
  - OSPF / eBGP / NAT / DNS / HTTP / 静态 TCP 映射 / Branch 业务 ACL（G3）
  - IPv6 / Tunnel / 中央远程管理 / Port Security（G4）
  - 跨站点业务路径当前不通（无路由协议），符合本 Gate 分层设计

证据：evidence/network/G2-A-01 ~ G2-A-07f（22 张，见第 8 节截图索引）

阻塞项：无

建议是否提交 PR：建议提交（feat/network → main），
  由项目总指挥复核后合入；合入前不修改任何公共契约或冻结网络项。
```

---

**报告结论**

A 侧 Gate 2 的网络基础层已在**不修改 HQ Gate 1 核心**的前提下建立完成：Branch 站点具备独立的 VLAN/ROAS/DHCP 与管理地址体系，四段新增 IPv4 链路相邻可达，且 HQ Gate 1 的全部回归项（EtherChannel / Trunk / VLAN / SVI / ACL / 三个安全行为）均无退化。本阶段严格按分层顺序实施，未叠加任何路由协议，未修改任何公共契约或 v2 冻结项。
