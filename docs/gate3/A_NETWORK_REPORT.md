# A — Network Owner 阶段报告（Gate 3）

| 项目 | 内容 |
|---|---|
| Owner | **A / Network** |
| 模块 | Final Architecture v2 — 企业 WAN 业务层（OSPF / eBGP / NAT / DNS / HTTP） |
| 分支 | `feat/network` |
| 依据文档 | **`docs/CURRENT_GATE.md` §4 Track A（Gate 3 正式任务书，2026-09-16 发布）**、`docs/CURRENT_GATE.md` §8 DoD、`docs/NETWORK_PLAN.md` §6–§8/§10/§13、`docs/ACCEPTANCE.md` Gate 3 |
| 配置记录 | `packet_tracer/CONFIG_LOG.md`（「Final Architecture v2 — 逐层实施区 → Gate 3」） |
| 证据目录 | `evidence/network/` |
| 截图命名依据 | `docs/ACCEPTANCE.md`：`G<Gate>-<Owner>-<序号>-<内容>-<结果>.png` |

---

## 1. 阶段目标

### 1.1 本阶段做什么

在 Gate 2 已建立的 Branch LAN + IPv4 Underlay 基础上，按 `docs/NETWORK_PLAN.md` §13 的第 4–7 层逐层叠加**企业 WAN 业务层**：

| 层 | 内容 | 验收 ID |
|---|---|---|
| 1 | **HQ OSPF Area 0**（SW-CORE ↔ R-HQ） | **N5** |
| 2 | **WAN eBGP**（AS65001 / 65000 / 65002）+ R-HQ 默认出口 | **N6** |
| 3 | **Branch 业务 + 隔离 ACL**（WAN-IN） | **N7 / N8** |
| 4 | **NAT/PAT + DNS/HTTP + 静态 TCP/80 映射** | **N9 / N10 / N11** |

附加验收（`docs/ACCEPTANCE.md` Gate 3 A 列表）：**HQ ADMIN → Branch 管理网可达**。

### 1.2 本阶段不做什么

- **不做 IPv6**（SLAAC / DHCPv6 / 静态 IPv6）——属 Gate 4；
- **不做 IPv6-over-IPv4 Tunnel** 与 IPv6 静态路由——属 Gate 4；
- **不做 Port Security / sticky MAC**——属 Gate 4；
- **不做正式的远程管理配置**（Telnet/SSH + VTY ACL）——属 Gate 4（本 Gate 只验证**可达性**）；
- 不改动 HQ Gate 1 Core 与 Gate 2 成果（唯一例外为一处**增量** DHCP DNS 选项，见 4.4 与 7.6）；
- 不为"用满接口"增加设备（`R-HQ G0/2`、`R-BRANCH G0/2` 保持预留）。

### 1.3 验收标准

> **OSPF/BGP 邻居与路由正确，Branch→HQ 业务、HQ→Internet PAT/DNS/HTTP、静态 HTTP 映射均可解释且可重复。**（`docs/ACCEPTANCE.md` Gate 3 A）

Gate 3 正式任务书（`docs/CURRENT_GATE.md`，2026-09-16 发布）将 A 侧工作定义为 **§4 Track A** 的 8 个层级条目，并在 **§8 DoD** 中列出 5 条 A 侧验收项。本报告完成后已与其**逐条对照**，结果见 **§7.4**。

---

## 2. 实验与开发环境

| 项目 | 内容 |
|---|---|
| 仿真平台 | **Cisco Packet Tracer 9.0.1.0858** |
| HQ 三层交换 | `SW-CORE` = Cisco **3650-24PS** |
| HQ 二层交换 | `SW-ACCESS` = Cisco **2960-24TT** |
| 路由器 | `R-HQ` / `R-ISP` / `R-BRANCH` = Cisco **2911** |
| Branch 交换 | `SW-BRANCH` = Cisco **2960-24TT** |
| 主机 | `OFFICE-PC`、`ADMIN-PC`、`BR-OFFICE-PC`、`BR-ADMIN-PC`（PC-PT）；`BACKEND-STUB`（Server-PT，兼 **HQ-SERVICE**）；`INTERNET-SERVER`（Server-PT，DNS+HTTP） |
| Edge/IoT | `EDGE-SBC-01`（SBC-PT）、`IO-MCU-01`（MCU-PT）、`TEMP01`、`FAN01`（B 侧成果，本 Gate 未改动） |
| Git 分支 | `feat/network` |
| 正式拓扑文件 | `packet_tracer/EdgeCampus.pkt`（canonical，A 唯一维护） |

### 2.1 路由协议参数（v2 冻结值）

| 项 | 值 |
|---|---|
| HQ IGP | **OSPF Area 0**，仅运行于 `SW-CORE(10.255.0.1) ↔ R-HQ(10.255.0.2)` |
| WAN EGP | **eBGP**：`R-HQ = AS65001`、`R-ISP = AS65000`、`R-BRANCH = AS65002` |
| HQ 默认出口 | R-HQ 静态默认路由 → `203.0.113.2`，并以 `default-information originate` 发布进 HQ OSPF |
| 重分发原则 | **不把完整 BGP 表重分发进 HQ OSPF**；SW-CORE 只需要默认路由 |

### 2.2 各设备发布的前缀

| 设备 | 发布到 BGP 的前缀 | 说明 |
|---|---|---|
| R-HQ | `192.168.30.0/24` | HQ-SERVICE 所在管控域；**不对外发布 HQ IOT** |
| R-BRANCH | `172.16.40.0/26`、`172.16.40.64/27` | Branch 业务域 + 管理域 |
| R-ISP | `192.0.2.0/24`、`203.0.113.0/30`、`198.51.100.0/30` | Internet LAN + 两段 WAN Transit（保证两端 IPv4 endpoint 互相可达） |

### 2.3 关键地址（沿用 Gate 2 冻结值）

| 区域 | 地址 |
|---|---|
| HQ VLAN10 / 20 / 30 | `192.168.10.0/24` / `192.168.20.0/24` / `192.168.30.0/24`（GW `.1`） |
| HQ Transit | `10.255.0.0/30`（SW-CORE `.1` / R-HQ `.2`） |
| HQ ↔ ISP | `203.0.113.0/30`（R-HQ `.1` / R-ISP `.2`） |
| ISP ↔ Branch | `198.51.100.0/30`（R-ISP `.1` / R-BRANCH `.2`） |
| Internet LAN | `192.0.2.0/24`（R-ISP `.1` / INTERNET-SERVER `.10`） |
| Branch VLAN40 / 50 | `172.16.40.0/26`（GW `.1`）/ `172.16.40.64/27`（GW `.65`） |

### 2.4 业务节点地址

| 节点 | 地址 | 角色 |
|---|---|---|
| `BACKEND-STUB / HQ-SERVICE` | `192.168.30.10` | 模拟业务/状态页服务端（HTTP 80） |
| `ADMIN-PC` | `192.168.30.20` | HQ NOC 管理终端 |
| `INTERNET-SERVER` | `192.0.2.10` | 模拟公网 DNS + HTTP |
| `BR-OFFICE-PC` | DHCP（实测 `172.16.40.2`） | 分部普通员工 |
| `BR-ADMIN-PC` | `172.16.40.70` | 分部异地运维 |
| `SW-BRANCH`（VLAN50 SVI） | `172.16.40.66` | 分部交换管理地址 |

---

## 3. 架构与连接关系

```text
        INTERNET-SERVER (192.0.2.10)   ← DNS + HTTP 服务，并作外部测试节点
                 |
   AS65000  R-ISP ────────────────────────────────┐
      G0/0 203.0.113.2/30        G0/1 198.51.100.1/30
             |                                      |
   AS65001  R-HQ G0/1 203.0.113.1/30      R-BRANCH G0/0 198.51.100.2/30  AS65002
             |  （NAT outside / WAN-IN inbound）   |
      G0/0 10.255.0.2/30                     G0/1 ── 802.1Q Trunk ──> SW-BRANCH
             |  （NAT inside）                                      ├─ Fa0/1 → BR-OFFICE-PC (VLAN40)
   SW-CORE Gi1/0/24 10.255.0.1/30                                 └─ Fa0/2 → BR-ADMIN-PC  (VLAN50)
   （OSPF Area 0 边界，HQ L3 Core）
             |
   SW-ACCESS ══ LACP EtherChannel ══ SW-CORE
             |
   OFFICE(VLAN10) / IOT(VLAN20: EDGE-SBC-01) / MANAGEMENT(VLAN30: HQ-SERVICE, ADMIN-PC)
```

### 3.1 路由分层（本 Gate 的核心设计）

```text
HQ VLAN10/20/30
      ↓  OSPF Area 0（IGP，管企业内部）
   SW-CORE ── 10.255.0.0/30 ── R-HQ AS65001
                                  │  eBGP（EGP，管自治系统边界）
                                  ├── R-ISP AS65000
                                  │        └── R-BRANCH AS65002
                                  └── 静态默认路由 → ISP
```

**职责分离**：IGP 负责 HQ 内部可达性；EGP 负责 AS 之间的前缀交换；R-HQ 向 HQ OSPF **只注入一条默认路由**，SW-CORE 不承载完整 BGP 表，Core 保持简洁稳定。

### 3.2 真实性与边界（ADR-012）

| 路径 | 组成 | 性质 |
|---|---|---|
| **PT 模拟企业数据平面** | VLAN / Trunk / EtherChannel / ACL / OSPF / eBGP / NAT / WAN | 本 Gate 的配置对象 |
| **Edge–Cloud 带外控制通道** | `EDGE-SBC-01 → RealWSClient → ws://127.0.0.1:8000 → Real FastAPI` | 与 PT WAN **无关** |

**禁止表述**：真实 FastAPI WebSocket 经过 `R-HQ` / `R-ISP` / BGP / NAT / VLAN20-30。
`HQ-SERVICE` 与 `INTERNET-SERVER` 只用于验证**模拟网络能够承载相应类型的业务访问**，不代表真实 FastAPI 对公网发布。

---

## 4. 实现过程

严格按 `docs/NETWORK_PLAN.md` §13 分层顺序执行：**每一层完成后立即验证并留存证据，再进入下一层**。

> **输出呈现说明**：本节引用的命令输出做了必要的**摘录与排版整理**（省略与结论无关的冗余行），**所有数值、状态与字段均与原始输出一致**；完整原始输出见第 8 节对应截图。

### 4.1 第 1 层：HQ OSPF Area 0

**目标**：让 R-HQ 学到 HQ 内部三个网段，并为后续 eBGP 提供 HQ 路由来源。

**配置**：

```text
SW-CORE
router ospf 1
 router-id 10.255.0.1
 network 10.255.0.0 0.0.0.3 area 0
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
 network 192.168.30.0 0.0.0.255 area 0

R-HQ
router ospf 1
 router-id 10.255.0.2
 network 10.255.0.0 0.0.0.3 area 0
```

**关键解释**：

- OSPF **只运行在 HQ 内部这一段**（`10.255.0.0/30`），`203.0.113.0/30` 属外部段，**不发布进 OSPF**；
- `router-id` 显式指定，避免依赖接口地址自动选举；
- VLAN20（IOT）与 VLAN30（MANAGEMENT）也发布进 OSPF——它们是 HQ 内部可达域，**是否对外开放由 BGP 发布策略控制**（见 4.2）。

**结果**：

| 命令 | 实际 |
|---|---|
| `show ip ospf neighbor`（两端） | 双向 **FULL**（SW-CORE 为 DR、R-HQ 为 BDR） |
| `R-HQ# show ip route ospf` | `O 192.168.10.0/24`、`O 192.168.20.0/24`、`O 192.168.30.0/24`，via `10.255.0.1`，`[110/2]` |

> DR/BDR 说明：DR 选举**不抢占**，先启动的一方当选；两端均为 FULL 即邻接完全正常，不代表配置差异。

**截图**：【G3-A-01】【G3-A-01b】

---

### 4.2 第 2 层：HQ 默认出口 + WAN eBGP

**目标**：建立 AS 之间的前缀交换，让 Branch 能到达 HQ、HQ 能到达 Internet。

**配置**：

```text
R-HQ：默认出口 + 向 OSPF 发布
ip route 0.0.0.0 0.0.0.0 203.0.113.2
router ospf 1
 default-information originate

R-HQ（AS65001）
router bgp 65001
 bgp log-neighbor-changes
 neighbor 203.0.113.2 remote-as 65000
 network 192.168.30.0 mask 255.255.255.0

R-ISP（AS65000）
router bgp 65000
 bgp log-neighbor-changes
 neighbor 203.0.113.1 remote-as 65001
 neighbor 198.51.100.2 remote-as 65002
 network 192.0.2.0 mask 255.255.255.0
 network 203.0.113.0 mask 255.255.255.252
 network 198.51.100.0 mask 255.255.255.252

R-BRANCH（AS65002）
router bgp 65002
 bgp log-neighbor-changes
 neighbor 198.51.100.1 remote-as 65000
 network 172.16.40.0 mask 255.255.255.192
 network 172.16.40.64 mask 255.255.255.224
```

**关键解释**：

- **`network` 语句而非重分发**：BGP 只发布**明确指定的前缀**，发布面可控；R-HQ 只发布 `192.168.30.0/24`，**不发布 HQ IOT**，从路由层面就把 IOT 排除在对外可达域之外；
- **`default-information originate`**：R-HQ 已有静态默认路由，OSPF 才会向 HQ 核心发布默认出口（SW-CORE 因此得到 `O*E2 0.0.0.0/0`）；**没有**这条默认路由，该命令不会产生任何效果；
- **ISP 发布两段 WAN Transit**：为后续 Gate 4 的 IPv6-over-IPv4 Tunnel 提供两端 IPv4 endpoint 互达；
- 不使用 `redistribute ospf` / `redistribute bgp`，避免路由泄漏与环路风险。

**结果**：

| 检查项 | 实际 |
|---|---|
| `show ip bgp summary`（三台） | 三个会话全部 **Established**（`State/PfxRcd` 显示前缀数） |
| `R-HQ# show ip route bgp` | `B 172.16.40.0/26`、`B 172.16.40.64/27`、`B 192.0.2.0/24`、`B 198.51.100.0/30` |
| `R-BRANCH# show ip route bgp` | `B 192.168.30.0/24`、`B 192.0.2.0/24`、`B 203.0.113.0/30` |
| `SW-CORE# show ip route` | **`O*E2 0.0.0.0/0 [110/1] via 10.255.0.2`**（默认出口） |
| `BR-OFFICE-PC ping 192.168.30.10` | **通**（跨站点业务首次打通） |

**截图**：【G3-A-02】【G3-A-02b】【G3-A-02c】

---

### 4.3 第 3 层：Branch 业务 + 隔离 ACL（WAN-IN）

**目标**：实现 N7（BR-OFFICE 能访问 HQ-SERVICE 业务）与 N8（BR-OFFICE 进不了 HQ IOT 与管理设备）。

**放置位置**：**R-HQ `G0/1`（朝 ISP 的 WAN 口）inbound** —— 所有来自 Branch / Internet 的流量在进入 HQ 之前统一过滤，一处定义、单点判定。

**配置**：

```text
ip access-list extended WAN-IN
 permit ip 172.16.40.64 0.0.0.31 192.168.30.0 0.0.0.255
 permit tcp 172.16.40.0 0.0.0.63 host 192.168.30.10 eq 80
 permit icmp 172.16.40.0 0.0.0.63 host 192.168.30.10
 deny ip 172.16.40.0 0.0.0.63 192.168.20.0 0.0.0.255
 deny ip 172.16.40.64 0.0.0.31 192.168.20.0 0.0.0.255
 deny ip 172.16.40.0 0.0.0.63 192.168.30.0 0.0.0.255
 deny tcp 172.16.40.0 0.0.0.63 any eq 23
 deny tcp 172.16.40.0 0.0.0.63 any eq 22
 permit ip any any
exit

interface gigabitEthernet 0/1
 ip access-group WAN-IN in
exit
```

**规则与冻结意图的对应（`docs/NETWORK_PLAN.md` §10.2 / §8.1）**：

| 规则 | 意图 |
|---|---|
| 1 | BR-ADMIN（`172.16.40.64/27`）→ HQ MANAGEMENT：**运维访问允许** |
| 2 / 3 | BR-OFFICE（`172.16.40.0/26`）→ HQ-SERVICE 的 **HTTP 与必要 ICMP** 允许 |
| 4 / 5 | **整个 Branch → HQ IOT 拒绝** |
| 6 | BR-OFFICE → HQ 管理域（含 ADMIN-PC 等管理设备）**拒绝** |
| 7 / 8 | BR-OFFICE 对任意目标的 **Telnet / SSH 拒绝**（不获得网络设备管理权限） |
| 9 | 其余放行（Internet 流量等） |

**关键解释**：

- **顺序即语义**：第 2/3 条的服务放行必须排在第 6 条的管理域拒绝**之前**；
- **IPv4 通配符**：`172.16.40.0/26 → 0.0.0.63`，`172.16.40.64/27 → 0.0.0.31`；
- ACL 挂在 **WAN 口 inbound**，不影响 HQ 内部流量，也不过滤 HQ→Branch 的**回程**（回程从该口出向）。

**结果（6 项行为测试）**：

| # | 测试 | 结果 |
|---|---|---|
| 1 | BR-OFFICE → `192.168.30.10` | 4/4 通 |
| 2 | BR-OFFICE → `http://192.168.30.10` | **页面打开（N7）** |
| 3 | BR-OFFICE → `192.168.20.10` | 100% 丢包（N8） |
| 4 | BR-OFFICE → `192.168.30.20` | 100% 丢包（N8） |
| 5 | BR-ADMIN → `192.168.30.20` | 4/4 通 |
| 6 | BR-ADMIN → `192.168.20.10` | 100% 丢包 |

**截图**：【G3-A-03】【G3-A-03b】【G3-A-03c】【G3-A-03d】

---

### 4.4 第 4 层：NAT/PAT + 静态映射 + DNS/HTTP

**目标**：实现 N9（HQ OFFICE 上公网）、N10（DNS 访问）、N11（外网访问 HQ 状态页）。

**配置（R-HQ）**：

```text
interface gigabitEthernet 0/0
 ip nat inside
interface gigabitEthernet 0/1
 ip nat outside
ip access-list standard NAT-INSIDE
 permit 192.168.10.0 0.0.0.255
ip nat inside source list NAT-INSIDE interface gigabitEthernet 0/1 overload
ip nat inside source static tcp 192.168.30.10 80 203.0.113.1 80
```

**配置（SW-CORE，增量）**：

```text
ip dhcp pool OFFICE
 dns-server 192.0.2.10
```

**配置（GUI）**：

- `INTERNET-SERVER`：HTTP Service = **On**；DNS Service = **On**，记录
  `www.edgecampus.net → 192.0.2.10`、`status.edgecampus.net → 203.0.113.1`；
- `BACKEND-STUB / HQ-SERVICE`：HTTP Service = **On**（第 3 层已开启）。

**关键解释**：

- **NAT 边界**：`G0/0`（朝 HQ 内部）为 `inside`，`G0/1`（朝 ISP）为 `outside`；
- **PAT 只放行 `192.168.10.0/24`（HQ OFFICE）**：HQ IOT 默认**不获得**公网 NAT 权限，符合冻结规划；
- **静态映射只开 TCP/80**：不把整个 MANAGEMENT 域暴露出去；
- **`overload`**：多台内部主机共享 `203.0.113.1` 出口，用端口区分会话。

**结果**：

| 验收项 | 实际 |
|---|---|
| **N9** | OFFICE-PC `ping 192.0.2.10` 通；`show ip nat translations` 出现静态表项与 PAT 会话 |
| **N10** | OFFICE-PC 浏览器打开 `http://www.edgecampus.net`（DNS 解析 + PAT + HTTP） |
| **N11** | INTERNET-SERVER 浏览器打开 `http://203.0.113.1` → 命中 HQ-SERVICE 页面；NAT 表出现 `192.0.2.10:1025` 活动会话 |

**截图**：【G3-A-04】【G3-A-04b】【G3-A-04c】【G3-A-04d】【G3-A-04d2】

---

### 4.5 附加验收：HQ ADMIN → Branch 管理网可达

**目标**：满足 `docs/ACCEPTANCE.md` Gate 3 A 列表中的「HQ ADMIN → Branch 管理网可达」（正式远程管理配置属 Gate 4）。

**操作**：在 `ADMIN-PC` 上：

```
ping 172.16.40.65      ← R-BRANCH G0/1.50（分部管理网关）
ping 172.16.40.66      ← SW-BRANCH 管理 SVI
```

**结果**：`.65` **4/4 通**（TTL=252）；`.66` **2/4 通**（后两个包 TTL=251，前两个为跨 4 跳的 ARP 解析期）。

**路径说明**：去程 `ADMIN-PC → SW-CORE(VLAN30 无 ACL) → R-HQ（有到 Branch 的 BGP 路由）→ R-ISP → R-BRANCH`；回程由 R-BRANCH 经 BGP 学到的 `192.168.30.0/24` 返回。

**截图**：【G3-A-05】

---

## 5. 关键配置解释（要点归纳）

1. **IGP 与 EGP 职责分离**：OSPF 管 HQ 企业内部，eBGP 管自治系统边界；R-HQ 只向 HQ OSPF 注入**一条默认路由**，Core 不承载完整 BGP 表。
2. **用 `network` 而非 `redistribute` 发布 BGP 前缀**：发布面显式可控——R-HQ 只发 `192.168.30.0/24`，HQ IOT 天然不在对外可达域内。
3. **`default-information originate` 需要一条已存在的默认路由**：否则命令无效；两者必须配套。
4. **ACL 挂在最靠近边界的入口（R-HQ G0/1 inbound）**：一处定义、单点判定，且不影响 HQ 内部与出向回程流量。
5. **NAT inside/outside 标记决定转换方向**：`G0/0` inside、`G0/1` outside；PAT 的源地址 ACL 决定**谁能获得公网出口**（只给 HQ OFFICE）。
6. **静态端口映射只开业务端口**：`203.0.113.1:80 → 192.168.30.10:80`，避免整段 MANAGEMENT 暴露。
7. **分层实施、逐层验证**：每层完成即验证并留存证据，故障定位范围始终局限于当前层（`NETWORK_PLAN.md` §13 的强制要求）。

---

## 6. 问题与排查过程

### 6.1 `www.edgecampus.net` 无法打开（Packet Tracer 不会自动续租）

**现象**：PAT、静态映射均已验证成功（`ping 192.0.2.10` 通、`http://203.0.113.1` 页面可打开），但 OFFICE-PC 的 Web Browser 访问 `http://www.edgecampus.net` **打不开**。

**初步判断**：怀疑 DNS 记录未配、或 DNS 报文被 ACL/PAT 阻断。

**排查步骤**（按"先隔离、后定位"）：

1. OFFICE-PC → Desktop → IP Configuration：检查 **DNS Server** 字段；
2. INTERNET-SERVER → Services → DNS：检查服务开关与 A 记录；
3. OFFICE-PC `ping www.edgecampus.net`：判断是解析失败还是访问失败；
4. OFFICE-PC 浏览器访问 `http://192.0.2.10`：隔离"DNS 问题"与"HTTP/PAT 问题"。

**根因**：第 1 步发现 **OFFICE-PC 的 `DNS Server` 为空**。原因是：`dns-server` 选项是在 PC 已持有租约之后才加入 DHCP 池的，而 **Packet Tracer 的 PC 不会自动续租**，因此一直沿用旧租约（无 DNS）。

**修复**：在 OFFICE-PC 的 IP Configuration 中**先切 Static、再切回 DHCP**，触发重新请求；随后 `DNS Server` 正确显示 `192.0.2.10`，域名访问成功。

**验证**：`http://www.edgecampus.net` 页面成功打开（DNS + PAT + HTTP 全链路）。

**结论**：**非配置错误**，属仿真平台的租约行为。`Packet Tracer 不会自动续租`这一经验已记入 `CONFIG_LOG.md`。

---

### 6.2 配置命令报 `Invalid input`（配置模式层级）

**现象**：在 `R-HQ#`（特权模式）下输入 `router bgp 65001`，报错：

```text
R-HQ#router bgp 65001
                       ^
% Invalid input detected at '^' marker.
```

**根因**：`router bgp` 是**全局配置命令**，必须在 `R-HQ(config)#` 下输入。此前已用 `end` 退出过配置模式，提示符回到 `#`，但仍按配置命令继续输入。

**修复**：先 `configure terminal` 进入 `(config)` 再执行；每次 `end` 退出后如需继续配置，必须重新进入。

**结论**：属**操作规范**问题，不涉及配置正确性。已记录以便团队避免复现：**凡见到 `^` 与 `Invalid input`，先确认提示符中是否含 `(config)`**。

---

### 6.3 一条 ACL 规则是否真的生效？（IOT 隔离的双重机制）

**现象**：BR-OFFICE → `192.168.20.10`（HQ IOT）被拒绝，但被拒绝时的 `Destination host unreachable` **来自 `172.16.40.1`（R-BRANCH）**，而不是 R-HQ——那么 `WAN-IN` 里的 deny 规则（第 4/5 条）到底有没有起作用？

**排查思路**：对比不同目标的 `unreachable` **来源地址**：

| 测试 | unreachable 来源 | 含义 |
|---|---|---|
| BR-OFFICE → `192.168.30.20`（管理设备） | **`203.0.113.1`（R-HQ）** | **是 R-HQ 的 ACL 主动拒绝**（第 6 条命中） |
| BR-OFFICE → `192.168.20.10`（IOT） | `172.16.40.1`（R-BRANCH） | R-BRANCH **没有到 HQ IOT 的路由** |

**根因/结论**：HQ IOT 的隔离实际上是**双重保障**：

1. **路由层面（主）**：R-HQ 依冻结规划**不对外发布 IOT 前缀**，Branch 侧根本没有到 `192.168.20.0/24` 的路由 → 报文在 R-BRANCH 即被丢弃；
2. **ACL 层面（纵深防御）**：`WAN-IN` 的 deny 规则在流量真的到达 R-HQ 时兜底。

**记录要求**：报告与答辩中应**如实说明该双重机制**，不宜简化为"配了 ACL 所以不通"——前者体现的是分层防御设计，后者则掩盖了路由发布策略的作用。

---

### 6.4 跨跳 ping 出现 25% / 50% 丢包

**现象**：

- `BR-OFFICE-PC → 192.168.30.10`：`Sent=4, Received=3 (25% loss)`；
- `ADMIN-PC → 172.16.40.66`（跨 4 跳）：`Sent=4, Received=2 (50% loss)`。

**根因**：首次通信需先完成 **ARP 解析**，在 ARP 完成前发出的 ICMP 报文超时。跳数越多、路径上需要解析的下一跳越多，首个可用回包出现得越晚。

**结论**：**非故障**。判断连通性应看"**是否收到回复**"以及后续包的 TTL 是否合理（如 `.66` 的 TTL=251 恰好对应跨 4 台路由器），而不是单看丢包率。

---

## 7. 验收结果

### 7.1 Gate 3 A 侧验收（N5–N11）

| ID | 验收项 | 预期 | 实际 | 结果 | 证据 |
|---|---|---|---|---|---|
| **N5** | OSPF | `SW-CORE ↔ R-HQ` FULL / HQ routes 正确 | 双向 FULL；R-HQ 学到三条 O 路由 | **PASS** | G3-A-01 / 01b |
| **N6** | eBGP | Established / prefixes 正确 | 三会话 Established；双向路由交换 | **PASS** | G3-A-02 / 02b |
| **N7** | Branch Business | BR-OFFICE → HQ-SERVICE HTTP 允许 | HTTP 页面成功打开 | **PASS** | G3-A-03c |
| **N8** | Branch Isolation | BR-OFFICE → HQ IOT / 管理设备 拒绝 | 两项均 100% 丢包 | **PASS** | G3-A-03b / 03d |
| **N9** | PAT | HQ OFFICE → Internet 成功且有 NAT translation | 通 + NAT 转换表有记录 | **PASS** | G3-A-04b |
| **N10** | DNS/HTTP | `www.edgecampus.net` 解析并访问成功 | 页面成功打开 | **PASS** | G3-A-04c |
| **N11** | Static Port Map | 外部节点 → `203.0.113.1:80` 映射到 HQ-SERVICE | 页面打开 + NAT 活动会话 | **PASS** | G3-A-04d / 04d2 |
| — | HQ ADMIN → Branch 管理 | 可达 | `.65` 4/4；`.66` 2/4（跨 4 跳 ARP） | **PASS** | G3-A-05 |

### 7.2 逐层 HQ Gate 1 Regression

| 层 | 回归内容 | 结果 | 证据 |
|---|---|---|---|
| 第 1 层 OSPF | 五条 show + 三行为 | PASS | G3-A-01c |
| 第 2 层 eBGP | 五条 show + 三行为 | PASS | G3-A-02d / 02e |
| 第 3 层 WAN-IN ACL | 轻量回归（ACL + 三行为） | PASS | G3-A-03e |
| 第 4 层 NAT/DNS | 四条 show（含 DHCP 绑定）+ 三行为 | PASS | G3-A-04e / 04f |

**行为测试恒定结论**：`OFFICE → ADMIN` 允许、`OFFICE → IOT` 拒绝、`ADMIN → EDGE-SBC` 允许 —— 四层叠加后**全部保持不变**。

> 第 3 层采用轻量回归的依据：该层只在 **R-HQ 的 WAN 接口**上新增 ACL，HQ 内部（VLAN10/20/30）流量不经过该接口，故 Layer 2 的五条 show 结论继续有效；第 4 层改动了 DHCP 池，因此恢复完整回归。

### 7.3 公共契约与冻结项检查

| 检查项 | 结果 |
|---|---|
| HQ VLAN10/20/30 与 IPv4 网段 | **未修改** |
| Gate 1 已验证 HQ 端口映射 | **未修改** |
| v2 冻结物理接口（含 G2 新增段） | **未修改** |
| Branch VLAN40/50、WAN 前缀、Internet LAN | **未修改** |
| **AS 号 65001 / 65000 / 65002** | **按冻结值实施** |
| Protocol v1.0 / 设备 ID / WS 路径 | **未涉及** |
| `TEMP01 → MCU → SBC → FAN01` 接线 | **未改动** |
| **增量修改**：`ip dhcp pool OFFICE` 新增 `dns-server 192.0.2.10` | **已声明**：为满足 `NETWORK_PLAN.md` §7.2 的 DNS 验收要求；不改变地址分配范围与任何其余冻结项 |

> 该增量是唯一一处对 Gate 1 既有配置的补充。若团队认为需要走 RFC 流程追认，可据此条目发起；本报告不将其表述为"零改动"。

### 7.4 与 Gate 3 正式任务书的逐条对照

依据 `docs/CURRENT_GATE.md`（2026-09-16 发布的 Gate 3 正式任务书）**§4 Track A** 与 **§8 DoD**：

| 任务书条目（§4 Track A） | 要求要点 | 本报告对应 | 结果 |
|---|---|---|---|
| ① HQ OSPF Area 0 | 邻居 FULL；R-HQ 学到 HQ VLAN10/20/30；SW-CORE 获得所需出口路由 | 4.1 / 7.1 N5 | ✅ |
| ② WAN eBGP | AS65001 ↔ 65000 ↔ 65002；发布冻结前缀；**禁止无解释的全量 redistribution** | 4.2 / 7.1 N6 | ✅ 全部使用显式 `network` 语句，**无任何 redistribute** |
| ③ Branch Business | `BR-OFFICE-PC → HQ-SERVICE / BACKEND-STUB` 业务流 | 4.2 结果 / 4.3 | ✅ |
| ④ HQ Internet PAT | G0/0 inside、G0/1 outside；**默认只为 HQ OFFICE 提供 PAT**；**IOT 不做通用 Internet NAT**；**站点间业务必须避免被 NAT** | 4.4 | ✅ PAT 源 ACL 仅含 `192.168.10.0/24`，故 IOT 不获 NAT；Branch↔HQ 与 HQ→Branch 流量均不被转换 |
| ⑤ DNS / HTTP | INTERNET-SERVER 提供 DNS + HTTP；HQ OFFICE 经 PAT 访问 | 4.4 / 7.1 N10 | ✅ |
| ⑥ Static TCP/80 Mapping | `203.0.113.1:80 → 192.168.30.10:80`，**若 PT 行为与模板不同必须实测记录** | 4.4 / 7.1 N11 | ✅ PT 行为与设计一致，已实测并留存 NAT 活动会话证据 |
| ⑦ WAN / Branch ACL | **路由先通再施加业务权限，不能用 ACL 掩盖路由错误** | 4.2（先验证路由）→ 4.3（后施加 ACL） | ✅ 第 2 层先证明 `BR-OFFICE → HQ-SERVICE` 可达，第 3 层才部署 `WAN-IN` |
| ⑧ Regression | 每层后复查 HQ（EtherChannel/Trunk/VLAN/SVI/ACL）、**Branch（VLAN/ROAS/DHCP）** 与新增业务流 | 7.2 + 下方说明 | 🟡 HQ 与业务流逐层完成；Branch 基础见下 |

**Gate 3 DoD（§8）中 A 侧条目**：

| DoD 条目 | 结果 | 证据 |
|---|---|---|
| A：OSPF 邻居与 HQ 路由学习 PASS | ✅ | G3-A-01 / 01b |
| A：eBGP 两段邻接与路由传播 PASS | ✅ | G3-A-02 / 02b |
| A：`BR-OFFICE → HQ-SERVICE` PASS | ✅ | G3-A-02c / 03c |
| A：HQ OFFICE → PAT → Internet DNS/HTTP PASS | ✅ | G3-A-04b / 04c |
| A：Static TCP/80 mapping 与业务 ACL 按设计完成并留证 | ✅ | G3-A-03* / 04d / 04d2 |

**关于第 ⑧ 条中「Branch VLAN/ROAS/DHCP」回归的说明（如实记录）**：

本 Gate 未对 Branch 基础单独截图，理由如下（均可在配置记录中核对）：

1. **变更面分析**：Gate 3 的全部配置变更集中在 `SW-CORE`（新增 OSPF；DHCP 池新增 DNS 选项）、`R-HQ` / `R-ISP` / `R-BRANCH`（动态路由、NAT、WAN ACL）。**`SW-BRANCH` 的二层配置未做任何修改**，**`R-BRANCH` 的 `G0/1.40` / `G0/1.50` 子接口与 `BR-OFFICE` DHCP 池亦未修改**。
2. **隐含验证**：本 Gate 期间三条跨站点业务流多次实测通过 —— `BR-OFFICE-PC → HQ-SERVICE`（4/4）、`BR-ADMIN-PC → HQ 管理域`（4/4）、`ADMIN-PC → Branch 管理网`（4/4、2/4）——**这些路径成立的前提正是 Branch VLAN / ROAS / DHCP 工作正常**。
3. **历史证据继续有效**：Gate 2 的 Branch 基础证据（`G2-A-02-branch-vlan-trunk-pass.png`、`G2-A-03-branch-roas-pass.png`、`G2-A-04-branch-dhcp-ping-pass.png`）未被任何后续变更作废。

因此本条按「**未单独留证，但已由变更面分析与业务流隐含覆盖**」记录，**未标为 PASS**。

---

## 8. 截图索引

全部位于 `evidence/network/`，命名遵循 `docs/ACCEPTANCE.md` 的 `G<Gate>-<Owner>-<序号>-<内容>-<结果>.png`（Gate 3 共 **21 张**）。

| 编号 | 文件 | 内容 | 证明什么 |
|---|---|---|---|
| G3-A-01 | `G3-A-01-ospf-swcore-neighbor-regression-pass.png` | SW-CORE `show ip ospf neighbor` + EtherChannel/VLAN/ACL | OSPF 邻接建立，且 HQ 核心无退化 |
| G3-A-01b | `G3-A-01b-ospf-rhq-neighbor-routes-pass.png` | R-HQ `show ip ospf neighbor` + `show ip route ospf` + `show ip protocols` | 邻接 FULL；R-HQ 学到 HQ 三个 /24；只发布 Transit 段 |
| G3-A-01c | `G3-A-01c-hq-behavior-regression-pass.png` | OFFICE / ADMIN 三个 ping | 第 1 层后 HQ 行为无退化 |
| G3-A-02 | `G3-A-02-bgp-neighbors-pass.png` | 三台 `show ip bgp summary` | 三个 eBGP 会话全部 Established |
| G3-A-02b | `G3-A-02b-bgp-routes-ospf-default-pass.png` | SW-CORE `show ip route` + R-HQ / R-BRANCH `show ip route bgp` | OSPF 默认出口 + 双向 BGP 前缀交换 |
| G3-A-02c | `G3-A-02c-branch-to-hq-service-pass.png` | BR-OFFICE-PC → `192.168.30.10` | 跨站点业务路径首次打通 |
| G3-A-02d | `G3-A-02d-hq-regression-swcore-pass.png` | SW-CORE 回归三件套 | 第 2 层后 HQ 核心无退化 |
| G3-A-02e | `G3-A-02e-hq-behavior-regression-pass.png` | OFFICE / ADMIN 三个 ping | 第 2 层后 HQ 行为无退化 |
| G3-A-03 | `G3-A-03-wan-in-acl-pass.png` | `show ip interface g0/1` + `show access-lists` | `WAN-IN` 已挂载，九条规则顺序正确 |
| G3-A-03b | `G3-A-03b-br-office-ping-pass.png` | BR-OFFICE → HQ-SERVICE 通 / → HQ IOT 拒绝 / → 管理设备拒绝 | N8 隔离成立 |
| G3-A-03c | `G3-A-03c-br-office-http-pass.png` | BR-OFFICE 浏览器打开 `http://192.168.30.10` | **N7 达成** |
| G3-A-03d | `G3-A-03d-br-admin-ping-pass.png` | BR-ADMIN → 管理设备通 / → IOT 拒绝 | BR-ADMIN 运维路径正确 |
| G3-A-03e | `G3-A-03e-hq-regression-pass.png` | SW-CORE `show access-lists` + 三个 ping | 第 3 层后 HQ 无退化 |
| G3-A-04 | `G3-A-04-pat-config-pass.png` | R-HQ `show running-config \| include ip nat` | PAT overload 与静态映射配置正确 |
| G3-A-04b | `G3-A-04b-office-internet-pat-pass.png` | OFFICE-PC → `192.0.2.10` + NAT 转换表 | **N9 达成** |
| G3-A-04c | `G3-A-04c-office-dns-http-pass.png` | OFFICE-PC 浏览器打开 `http://www.edgecampus.net` | **N10 达成**（DNS + PAT + HTTP） |
| G3-A-04d | `G3-A-04d-static-tcp80-map-pass.png` | INTERNET-SERVER 浏览器打开 `http://203.0.113.1` | **N11 达成** |
| G3-A-04d2 | `G3-A-04d2-nat-translations-session-pass.png` | R-HQ NAT 表含活动会话 `192.0.2.10:1025` | 静态映射确实转发了 HTTP 连接 |
| G3-A-04e | `G3-A-04e-hq-regression-swcore-pass.png` | SW-CORE 四条 show（含 `dns-server` 与 DHCP 绑定） | 第 4 层后 HQ 无退化，DNS 选项生效 |
| G3-A-04f | `G3-A-04f-hq-behavior-regression-pass.png` | OFFICE / ADMIN 三个 ping | 第 4 层后 HQ 行为无退化 |
| G3-A-05 | `G3-A-05-admin-to-branch-mgmt-pass.png` | ADMIN-PC → `172.16.40.65` / `.66` | HQ ADMIN → Branch 管理网可达 |

**"一图多证据"示例**：`G3-A-01b`（邻接 + 路由 + 协议参数同屏）、`G3-A-02b`（OSPF 默认出口 + 两台风向 BGP 路由同屏）、`G3-A-04d2`（NAT 静态表项 + 活动会话同屏）。

---

## 9. 本阶段交付物

| 交付物 | 位置 | 说明 |
|---|---|---|
| 正式拓扑文件 | `packet_tracer/EdgeCampus.pkt` | canonical `.pkt`，已包含 Gate 3 的 OSPF/eBGP/ACL/NAT 配置 |
| 配置与验证日志 | `packet_tracer/CONFIG_LOG.md` | 「Final Architecture v2 → Gate 3」已填入四层真实命令、验证结果与问题记录 |
| 验收证据 | `evidence/network/G3-A-01 ~ G3-A-05`（21 张） | 见第 8 节索引 |
| 集成看板更新 | `docs/PROJECT_BOARD.md` | HQ OSPF / WAN eBGP / Branch 业务 / WAN-IN ACL / PAT+DNS+HTTP / 静态映射 / ADMIN→Branch 七行 → **PASS G3**，并新增 Integration Check 记录 |
| 本阶段报告 | `docs/gate3/A_NETWORK_REPORT.md` | 本文档 |

> 本模块不产出代码（纯网络配置），交付物以拓扑文件、配置日志与证据为主。

---

## 10. 创新性支撑

> **归属说明**：本项目级的核心创新（**双控制环**、**断云不断控**）属全组共有，其正式验收在 Gate 4。本 Gate 对创新的贡献在于**为这些能力提供可承载、可隔离、可审计的企业级网络底座**。

### 10.1 分层路由设计：IGP 与 EGP 职责分离

```text
HQ 内部可达性  → OSPF Area 0（只一条链路、面积最小化）
AS 间前缀交换  → eBGP（多 AS、显式 network 发布）
Core 复杂度    → 通过"只注入一条默认路由"保持恒定
```

**创新点**：不是"把 BGP 配通"，而是**让 Core 永远不感知外部路由规模**——R-HQ 承担全部外部路由，SW-CORE 只有一条 `O*E2 0.0.0.0/0`。这在真实企业网中是降低核心风险的常规做法，在本项目中同时保证了 Gate 1 已验证的 HQ Core **不被 WAN 的复杂度污染**。

### 10.2 业务与运维的"双路径"设计

| 角色 | 路径 | 权限 |
|---|---|---|
| BR-OFFICE（普通员工） | → HQ-SERVICE HTTP | **只允许业务服务**，禁 IOT、禁管理、禁 Telnet/SSH |
| BR-ADMIN（运维人员） | → HQ MANAGEMENT | **允许运维访问**，仍禁 IOT |
| HQ ADMIN（总部 NOC） | → Branch 管理网 | **允许集中管理** |

**创新点**：同一条 WAN 链路上，**按角色而非按网段**区分权限，用一条 `WAN-IN` ACL 表达完整业务意图；并且与"网络策略强制控制路径"（Gate 1 创新点）一脉相承——**用网络设备而不是用应用登录页来定义谁可以做什么**。

### 10.3 隔离的"双重保障"可解释性

HQ IOT 的不可达由 **路由层（不发布前缀）+ ACL 层（deny 兜底）** 共同保证，且可通过 `unreachable` 的**来源地址**区分是"无路由"还是"被 ACL 拒绝"（见 6.3）。这种**可解释性**本身就是设计质量的一部分：它让"隔离为什么生效"可以被验证，而不只是"结果不通"。

### 10.4 在最终报告与课程覆盖中的位置

| 用途 | 位置 | 素材 |
|---|---|---|
| 网络设计章节 | `docs/REPORT_OUTLINE.md` 网络设计 | 第 2–5 节 |
| 课程覆盖说明 | `docs/ACCEPTANCE.md` 五次实验覆盖核对 | **实验三**（ACL/NAT/PAT/TCP-80 映射/DNS/HTTP）、**实验四**（OSPF/eBGP/路由传播） |
| 功能测试章节 | 最终功能测试矩阵 **N5–N11** | 第 7.1 节 |
| 现场演示 | `docs/DEMO_SCRIPT.md` 企业互联段落 | G3 证据链 |

---

## 11. 分工与 AI 协作记录

### 11.1 本人角色与边界

| 项目 | 内容 |
|---|---|
| Owner | **A / Network** |
| 本阶段可修改范围 | `packet_tracer/`（含 canonical `EdgeCampus.pkt`、`CONFIG_LOG.md`）、网络证据 `evidence/network/`、本报告 |
| 明确不修改 | `backend/`（C）、`edge/`（B）、`dashboard/` 与 `tests/`（D） |
| 排他约定 | A 为 canonical `.pkt` 唯一 Owner；本 Gate 的 `.pkt` 起点为团队提供的 Gate 2 合并版 |

### 11.2 本阶段承担明细

HQ OSPF（Area 0）→ R-HQ 默认出口 + WAN eBGP（三个 AS）→ WAN-IN 业务与隔离 ACL → NAT/PAT + 静态 TCP/80 映射 + DNS/HTTP 服务 → HQ ADMIN → Branch 可达性验收 → 四层逐层回归 → 证据采集（21 张）→ `CONFIG_LOG.md` / `PROJECT_BOARD.md` / 本报告。

### 11.3 与各 Owner 的接口

| 对象 | 接口内容 |
|---|---|
| **B / Edge** | 本 Gate **未触及** Edge 侧；`TEMP01 → MCU → SBC → FAN01` 与 A+B 集成结果保持不变。B 的真实 Telemetry 属 G2/G3 软件主线，与 A 的网络扩展并行 |
| **C / Control Plane** | `HQ-SERVICE = 192.168.30.10` 未改动；G3 起该节点由 A 侧的 WAN-IN ACL 与静态映射承载"模拟业务服务"角色；**A 不实现服务本体** |
| **D / UI & Integration** | A 提供 WAN/业务侧证据；端到端联调由 B/C/D 主线负责 |
| **全组** | HQ Gate 1 Core、v2 冻结网络项、Protocol v1.0、设备 ID、WS 路径本阶段**均未修改**（唯一增量见 7.3） |

### 11.4 协作机制与流程遵守

| 机制 | 本阶段执行情况 |
|---|---|
| Owner 边界（`docs/CONTRIBUTING.md`） | 严格遵守，未跨模块修改 |
| 分层实施规则（`NETWORK_PLAN.md` §13） | 严格执行：每层配置 → 验证 → 回归 → 留证，再进入下一层 |
| 冻结项（AS 号、WAN 前缀、业务权限） | 全部按冻结值实施，未自行重编号 |
| 公共契约变更须走 RFC | **未触发**（唯一增量为 DHCP DNS 选项，已在 7.3 声明并说明理由） |
| HQ Core 不得破坏 | 四层回归全部 PASS |
| canonical `.pkt` 所有权 | 全程由 A 维护；起点采用团队 Gate 2 合并版，未覆盖他人成果 |

### 11.5 AI 协作记录

| 项目 | 内容 |
|---|---|
| AI 承担的角色 | 分层实施指导、调试记录员、截图证据管理员、阶段报告整理者（依据 `EdgeCampus_AI阶段记录与提交规范.md`） |
| **红线遵守** | 未修改 HQ VLAN/IP、Gate 1 端口映射、v2 冻结接口、AS 号、Protocol 字段、设备 ID、WS 路径 |
| **AI 参与的真实排查** | ① PAT/静态映射正常但域名打不开的分层定位（最终定性为"PT 不自动续租"）；② `router bgp` 报 `Invalid input` 的模式层级判定；③ IOT 隔离是否真由 ACL 生效的**来源地址对比法** |
| **AI 预估被实测修正的记录** | AI 曾预估"R-HQ 与 R-BRANCH 各学到 3 条 BGP 前缀"，实测 **R-HQ 为 4 条**（多出 R-BRANCH 侧的 WAN Transit `198.51.100.0/30`，符合 ISP 发布 Transit 的设计）。记录以**实测为准**，未沿用预估 |
| **AI 明确拒绝的做法** | 当回归结果一度被误读为"OFFICE → IOT 通了"时，AI **未直接修改 ACL**，而是先要求提供 `show access-lists` / `show running-config` / `show ip interface` 以定位；最终证实为读数误判，冻结配置全程未被改动 |
| **AI 的排查纪律** | DNS 故障时先给出"4 项隔离检查"，要求**先定位、后修改**，避免在未确认根因前改动 NAT/ACL/路由 |

### 11.6 真实性声明

- 本报告中的**全部命令与输出**均为实际执行所得，未编造；
- 四层验证中的**每一项结论均对应可追溯的截图**（第 8 节索引）；
- 存在平台偏差的数值（如 ACL 命中计数、跨跳丢包率）**如实记录并注明以实际效果为准**；
- 未完成内容（IPv6 / Tunnel / Port Security / 正式远程管理）**明确列为 Gate 4**，未以"理论可用"替代实测；
- **唯一一处对既有配置的增量**（DHCP `dns-server`）已在 4.4 与 7.3 显式声明，未表述为"零改动"。

---

## 12. 未完成项与后续工作

### 12.1 本 Gate 明确不做、留给 Gate 4 的部分

| 项 | Gate | 说明 |
|---|---|---|
| HQ OFFICE **SLAAC** | G4 | IPv6 地址自动配置 |
| BR-OFFICE **DHCPv6** | G4 | 需在 PT 9.0.1 实测具体支持情况后再调整，**不得因此删除该项验收** |
| 管理域 **静态 IPv6** | G4 | — |
| **IPv6-over-IPv4 Tunnel**（R-HQ ↔ R-BRANCH，`2001:db8:ff::/64`） | G4 | 跨 IPv4-only ISP 构建 IPv6 管理 Overlay |
| **IPv6 静态路由** | G4 | 实现 BR-ADMIN → HQ MANAGEMENT（IPv6） |
| **Central Administration** | G4 | HQ ADMIN 对 R-BRANCH / SW-BRANCH 的**正式远程管理**（含 VTY ACL，仅允许 `192.168.30.20`）——本 Gate 只验证了**可达性** |
| **Port Security / sticky MAC** | G4 | `SW-ACCESS Fa0/1`，含非法 MAC 触发 violation 与计数变化 |
| 全量 ACL / 业务回归 | G4 | 对 HQ / Branch / Internet 权限矩阵做最终回归 |

### 12.2 其他 Owner 的 Gate 3 范围（非 A 职责）

| 项 | Owner | 说明 |
|---|---|---|
| Dashboard Policy → Edge → `policy_ack` 真闭环 | **B+C+D** | G3 主 Critical Path |
| 手动 `command` / `command_ack`（`REMOTE-MANUAL`） | **B+C+D** | 增强验收 |
| C 的 Gate 1 owner 证据清零 | **C** | `docs/gate1/C_BACKEND_REPORT.md` 由占位符转正式报告（Gate 5 前） |
| Dashboard 接真 PT Telemetry 的现场验收 | **D** | — |

### 12.3 待团队确认事项

| 事项 | 说明 |
|---|---|
| **Gate 3 正式任务书** | ✅ **已解决**：`docs/CURRENT_GATE.md` 已于 **2026-09-16** 发布 Gate 3 正式任务书（§4 Track A / §8 DoD）。本报告完成后的逐条对照见 **§7.4**，结论为**条目全部吻合**，无新增缺口 |
| **canonical `.pkt` 版本归并** | `main` 上存在一份由项目总指挥上传的 `.pkt`，与 A 完成 Gate 3 后的版本**不同源**（大小与 SHA-256 均不同）。`.pkt` 为二进制、无法自动合并。A 为 canonical Owner，按团队看板指示「**由 A 本地替换 canonical 后 push**」，归并时应**以 A 的版本为准**；具体操作方式需与项目总指挥确认 |
| **DHCP `dns-server` 增量是否需 RFC 追认** | 见 7.3；若团队要求，A 可据该条目发起轻量 RFC |

### 12.4 后续网络层工作（A）

1. 按 `NETWORK_PLAN.md` §13 第 9–11 层推进 **IPv6 / Tunnel / Port Security**；
2. 每层完成后重复本报告 7.2 的**逐层回归**；
3. 持续维护 canonical `.pkt`，并在每次网络层变更后更新 `CONFIG_LOG.md` 与 `PROJECT_BOARD.md`；
4. Gate 5 前确保 HQ / Branch / Internet 权限矩阵的**最终 ACL 回归**。

---

## 13. Gate 3 状态小结

```text
Gate 状态：A（Network）侧 Gate 3 企业 WAN 业务层完成

已完成：
  - 第 1 层 HQ OSPF Area 0：SW-CORE ↔ R-HQ 双向 FULL，R-HQ 学到 HQ 三个 /24
  - 第 2 层 WAN eBGP：AS65001/65000/65002 三会话 Established，双向前缀交换，
    SW-CORE 经 OSPF 获得默认出口；跨站点业务首次打通
  - 第 3 层 WAN-IN ACL：BR-OFFICE 仅可访问 HQ-SERVICE 业务（HTTP），
    禁 HQ IOT、禁管理设备、禁 Telnet/SSH；BR-ADMIN 运维路径可用
  - 第 4 层 NAT/PAT + DNS/HTTP + 静态 TCP/80 映射：三项验收全部达成
  - 附加：HQ ADMIN → Branch 管理网可达
  - 四层逐层 HQ Gate 1 Regression 全部 PASS
  - 21 张验收证据 + CONFIG_LOG + PROJECT_BOARD 同步

未完成（设计内，属 Gate 4）：
  - IPv6（SLAAC / DHCPv6 / 静态）、IPv6-over-IPv4 Tunnel 与 IPv6 静态路由
  - Central Administration 的正式远程管理配置（本 Gate 仅验证可达性）
  - Port Security / sticky MAC
  - B/C/D 的 Gate 3 主 Critical Path（Policy/Command 真闭环）

证据：evidence/network/G3-A-01 ~ G3-A-05（21 张，见第 8 节截图索引）

阻塞项：无

建议是否提交 PR：建议提交（feat/network → main），
  由项目总指挥复核后合入；合入前不修改任何公共契约或 v2 冻结网络项。
```

---

**报告结论**

A 侧 Gate 3 的企业 WAN 业务层已在**不破坏 HQ Gate 1 Core 与 Gate 2 成果**的前提下完成：HQ 内部由 OSPF 保证可达性、AS 之间由 eBGP 交换前缀、Core 仅持有一条默认路由；业务侧实现了"分部办公只可访问总部业务服务、分部运维可访问管理域、总部 NOC 可管理分部"的差异化权限；总部出口侧完成 PAT、DNS/HTTP 与静态端口映射，并可用 `show ip nat translations` 复核。

验收矩阵 **N5 – N11 全部 PASS**，附加的「HQ ADMIN → Branch 管理网可达」亦通过；四层逐层回归证明 HQ Gate 1 Core 无退化。本阶段严格按分层顺序实施，未越界实现 Gate 4 内容，未修改任何公共契约（唯一增量 DHCP `dns-server` 已显式声明）。
