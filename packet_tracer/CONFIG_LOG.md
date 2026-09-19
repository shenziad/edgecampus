# Packet Tracer 配置与验证日志

> 每条关键配置记录“目的—命令—结果”；不要把整份 running-config 无解释地堆入报告。  
> 本文件区分 **已验证配置** 与 **Final Architecture v2 待实施配置**，未实测内容不得写成 PASS。

## 环境信息

- Packet Tracer 版本：`9.0.1.0858`
- SW-CORE 型号：`Cisco 3650-24PS`
- SW-ACCESS 型号：`Cisco 2960-24TT`
- 真实主机控制方式：Packet Tracer External Network Access / `RealWSClient` → `ws://127.0.0.1:8000/ws/edge`
- RealWSClient 已在 Gate 0 实机验证，并在保存、关闭、重开 `.pkt` 后再次连接成功。
- 真实性边界：该 RealWSClient 是带外 Edge–Cloud 控制通道，**不经过 Packet Tracer VLAN/WAN 数据平面**。

## 当前正式包增量（2026-09-19）

本日志前面的Gate 1–Gate 4段落保留当时的实施历史，其中`LACP mode active`、Gi1/0/24三层口`10.255.0.0/30`和单Fa0/1 Port Security均是历史基线，不再代表当前正式包。当前配置由[课程重点补强详细配置](../docs/COURSE_COVERAGE_PATCH.md)覆盖：

- Core–Access两端改为`channel-group 1 mode on`，Po1(SU)、Protocol `-`、两成员(P)；
- SW-CORE Gi1/0/23–24改为access VLAN100，Vlan100 `10.255.0.1/29`；R-HQ `.2/29`、R-COURSE `.3/29`；
- R-BRANCH新增VLAN40来源PAT和“ICMP拒绝、TCP/80允许”的协议ACL；
- R-COURSE/R-TEST用独立OSPF44与BGP65144/65154完成E2/Type-5及默认路由验证；
- SW-ACCESS Fa0/1与Fa0/3均启用sticky、maximum1、restrict。

当前命令、验证结果和图47–54的文件映射以补强文档为准；以下旧段落用于解释设计演进，不应直接复制覆盖最终包。

---

# Gate 1 — HQ Core 已验证配置

## 端口映射

权威规划见 `docs/NETWORK_PLAN.md`。Gate 1 HQ 摘要：

| 链路/端口 | 对端 | VLAN | 模式 |
|---|---|---|---|
| SW-ACCESS Fa0/1 | OFFICE-PC | 10 | access |
| SW-ACCESS Fa0/2 | EDGE-SBC-01 | 20 | access |
| SW-ACCESS Fa0/3 | ADMIN-PC | 30 | access |
| SW-ACCESS Fa0/4 | BACKEND-STUB | 30 | access |
| SW-ACCESS Gi0/1 ↔ SW-CORE Gi1/0/1 | — | trunk | LACP |
| SW-ACCESS Gi0/2 ↔ SW-CORE Gi1/0/2 | — | trunk | LACP |

## SW-CORE

```text
hostname SW-CORE
vlan 10
 name OFFICE
vlan 20
 name IOT
vlan 30
 name MANAGEMENT
interface range gigabitEthernet 1/0/1 - 2
 channel-group 1 mode active
interface port-channel 1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
ip routing
interface vlan 10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
interface vlan 20
 ip address 192.168.20.1 255.255.255.0
 no shutdown
interface vlan 30
 ip address 192.168.30.1 255.255.255.0
 no shutdown
ip dhcp excluded-address 192.168.10.1 192.168.10.9
ip dhcp pool OFFICE
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
ip access-list extended OFFICE-IN
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.30.10 eq 8000
 permit icmp 192.168.10.0 0.0.0.255 192.168.30.0 0.0.0.255
 deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255
 permit ip any any
ip access-list extended IOT-IN
 permit tcp 192.168.20.0 0.0.0.255 host 192.168.30.10 eq 8000
 permit icmp 192.168.20.0 0.0.0.255 192.168.30.0 0.0.0.255
 deny ip 192.168.20.0 0.0.0.255 192.168.10.0 0.0.0.255
 permit ip any any
interface vlan 10
 ip access-group OFFICE-IN in
interface vlan 20
 ip access-group IOT-IN in
```

已完成验证：

```text
show vlan brief
show etherchannel summary
show interfaces trunk
show ip interface brief
show ip route
show ip dhcp binding
show access-lists
```

结果：

- VLAN 10 `OFFICE`、VLAN 20 `IOT`、VLAN 30 `MANAGEMENT` active；
- EtherChannel：`Po1(SU)` LACP，成员 `Gig1/0/1(P)`、`Gig1/0/2(P)`；
- Trunk：Po1 802.1Q / trunking，allowed `10,20,30`；
- SVI：Vlan10/20/30 均 up/up；
- 路由：三条 HQ `/24` 直连路由存在；
- DHCP：OFFICE-PC 获取 `192.168.10.10/24`、GW `192.168.10.1`；
- ACL：`OFFICE-IN` / `IOT-IN` 挂对应 SVI inbound。

证据位于 `evidence/network/` 的 Gate 1 文件。

## SW-ACCESS

```text
hostname SW-ACCESS
vlan 10
 name OFFICE
vlan 20
 name IOT
vlan 30
 name MANAGEMENT
interface fastEthernet 0/1
 switchport mode access
 switchport access vlan 10
interface fastEthernet 0/2
 switchport mode access
 switchport access vlan 20
interface fastEthernet 0/3
 switchport mode access
 switchport access vlan 30
interface fastEthernet 0/4
 switchport mode access
 switchport access vlan 30
interface range gigabitEthernet 0/1 - 2
 channel-group 1 mode active
interface port-channel 1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
```

验证结果：

- VLAN10：Fa0/1；VLAN20：Fa0/2；VLAN30：Fa0/3、Fa0/4；
- `Po1(SU)`，Gi0/1、Gi0/2 均 bundled；
- Po1 trunk 允许 VLAN10/20/30。

## HQ 终端地址

| 设备 | IPv4 | 掩码 | 网关 | 方式 |
|---|---|---|---|---|
| OFFICE-PC | 192.168.10.10 | 255.255.255.0 | 192.168.10.1 | DHCP 实测租约 |
| EDGE-SBC-01 | 192.168.20.10 | 255.255.255.0 | 192.168.20.1 | 静态 |
| ADMIN-PC | 192.168.30.20 | 255.255.255.0 | 192.168.30.1 | 静态 |
| BACKEND-STUB / HQ-SERVICE | 192.168.30.10 | 255.255.255.0 | 192.168.30.1 | 静态 |

## Gate 1 功能验证结果

| 日期 | 测试 | 预期 | 实际 | 证据 |
|---|---|---|---|---|
| 2026-09-15 | EtherChannel | Up / In use | Po1(SU)，两端 members bundled | `G1-04-*` / `G1-05-*` |
| 2026-09-15 | N1 VLAN/路由 | 允许域可达 | OFFICE→ADMIN 4/4 | `G1-09-n1-crossvlan-ping-pass.png` |
| 2026-09-15 | N2 ACL 隔离 | OFFICE→IOT 拒绝 | deny 命中，ping 被拦截 | `G1-10-n2-office-to-iot-deny.png` |
| 2026-09-15 | N3 管理节点访问 | OFFICE→BACKEND-STUB 允许 | 可达 | `G1-11-n3-mgmt-access-pass.png` |
| 2026-09-15 | A+B Integration | 合入 Edge 后 HQ 不退化 | PASS | `docs/gate1/AB_INTEGRATION_REPORT.md` |

> 旧日志中的“IOT → Backend:8000 待 B 侧 ping 验证”不再作为 RealWSClient 的真实性证明。真实 Edge→Cloud 通道已经在 Gate 0 通过 External Network Access 验证；PT VLAN20 到 `BACKEND-STUB` 的网络测试仅代表模拟数据平面。

---

# Final Architecture v2 — 逐层实施区

> **Gate 2 已实施并验证通过；Gate 3 / Gate 4 仍待实施。**  
> 本节按 Gate 逐层填充；**未实测内容不得写成 PASS**。

## Gate 2：Branch LAN + IPv4 Underlay — ✅ 已实施并验证通过

计划接口 / 地址：

```text
SW-CORE Gi1/0/24  10.255.0.1/30
  ↔ R-HQ G0/0      10.255.0.2/30

R-HQ G0/1          203.0.113.1/30
  ↔ R-ISP G0/0     203.0.113.2/30

R-ISP G0/1         198.51.100.1/30
  ↔ R-BRANCH G0/0  198.51.100.2/30

R-ISP G0/2         192.0.2.1/24
  ↔ INTERNET-SERVER 192.0.2.10/24

R-BRANCH G0/1 ↔ SW-BRANCH Gi0/1 (802.1Q trunk)
VLAN40 BR-OFFICE 172.16.40.0/26 GW .1
VLAN50 BR-MGMT   172.16.40.64/27 GW .65
SW-BRANCH VLAN50 172.16.40.66/27
BR-ADMIN-PC       172.16.40.70/27
```

实施记录（2026-09-15，**已实测**）：

**基线**：本 Gate 在 A 维护的 canonical `packet_tracer/EdgeCampus.pkt` 上实施；起点为队长提供的 **87,390 字节**版本，其 HQ Gate 1 配置经本次回归验证**完整保留**，**未修改 HQ Core 任何既有配置**。

### SW-BRANCH（2960-24TT）

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

验证：VLAN40 `BR-OFFICE`（Fa0/1）、VLAN50 `BR-MGMT`（Fa0/2）均 active；`Gi0/1` trunk，allowed / active / forwarding 均为 `40,50`；`Vlan50 = 172.16.40.66` up/up。
说明：2960 为**二层**设备，管理出口使用 `ip default-gateway`，**未启用** `ip routing`。

### R-BRANCH（2911）

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
interface gigabitEthernet 0/0
 ip address 198.51.100.2 255.255.255.252
 no shutdown
ip dhcp excluded-address 172.16.40.1
ip dhcp pool BR-OFFICE
 network 172.16.40.0 255.255.255.192
 default-router 172.16.40.1
```

验证：`G0/1.40 = 172.16.40.1`、`G0/1.50 = 172.16.40.65` 均 up/up；`show ip route` 出现 `C 172.16.40.0/26`、`C 172.16.40.64/27` 两条直连路由；`show ip dhcp binding` 出现 `172.16.40.2 / 00E0.B002.9A06 / Automatic`。

### IPv4 Underlay（四段新增链路）

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

说明：3650 的 `Gi1/0/24` 通过 **`no switchport`** 转为**路由口**承载 HQ Transit，Packet Tracer 9.0.1 **实测通过**。

### 新增终端地址

| 设备 | IPv4 | 掩码 | 网关 | 方式 |
|---|---|---|---|---|
| BR-OFFICE-PC | 172.16.40.2（实测租约） | 255.255.255.192 | 172.16.40.1 | DHCP |
| BR-ADMIN-PC | 172.16.40.70 | 255.255.255.224 | 172.16.40.65 | 静态 |
| SW-BRANCH（VLAN50） | 172.16.40.66 | 255.255.255.224 | 172.16.40.65 | 静态 |

### Gate 2 验证结果

| 日期 | 测试 | 预期 | 实际 | 证据 |
|---|---|---|---|---|
| 2026-09-15 | Topology Check（7 条新增链路） | 与冻结表一致 | CDP 双向确认 4 条；主机链路 3 条 up/connected | `G2-A-01…01d` |
| 2026-09-15 | Branch VLAN / Trunk | VLAN40/50 + trunk 40,50 | PASS | `G2-A-02-branch-vlan-trunk-pass.png` |
| 2026-09-15 | Router-on-a-Stick | 两个子接口 up/up + 两条直连路由 | PASS | `G2-A-03-branch-roas-pass.png` |
| 2026-09-15 | Branch DHCP / 管理地址 | 终端获址、管理地址可达 | BR-OFFICE-PC `172.16.40.2`；BR-ADMIN → `.65`/`.66` 通 | `G2-A-04-branch-dhcp-ping-pass.png` |
| 2026-09-15 | IPv4 Underlay 地址 | 四个网段地址正确 | PASS（含 `no switchport` 实测） | `G2-A-05…05e` |
| 2026-09-15 | 相邻三层可达 | 四段链路相邻 ping 通 | Server→ISP 4/4；三个 WAN 段各 4/5（首包 ARP） | `G2-A-06…06d` |
| 2026-09-15 | HQ Gate 1 Regression | Core 无退化 | 五条 show 全部正常 + 三个行为测试符合预期 | `G2-A-07…07f` |

### Gate 2 实施中的问题与说明

1. **SW-ACCESS `show access-lists` 无输出**：属**正常现象**——ACL 仅配置在三层核心 `SW-CORE` 的 SVI 上，2960 为二层设备本就不承载 ACL。
2. **ACL deny 命中计数与实际包数不完全对应**：本次回归中 deny 规则计数为 `2 match(es)`，而测试发送了 4 个 ICMP 请求。判定以**实际拦截效果**（100% 丢包 + `Destination host unreachable`）为准，**不虚报命中次数**。
3. **相邻 ping 首包超时**：四段链路首次 ping 均出现 1 个包超时（成功率 80%），原因为 ARP 解析期，**非故障**。
4. **本 Gate 不涉及路由协议**：OSPF / eBGP / NAT / IPv6 均留给 Gate 3 / Gate 4，当前只完成地址与相邻可达。

## Gate 3：OSPF / eBGP / NAT / DNS / HTTP — ✅ 已实施并验证通过

实施记录（2026-09-16，**已实测**）：

**基线**：在 Gate 2 基线上继续逐层叠加。HQ Gate 1 Core 与 Gate 2 成果均未修改，仅有一处**增量配置**（DHCP 池新增 DNS 选项，见第 4 层说明）。

### 第 1 层：HQ OSPF Area 0

```text
! SW-CORE
router ospf 1
 router-id 10.255.0.1
 network 10.255.0.0 0.0.0.3 area 0
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
 network 192.168.30.0 0.0.0.255 area 0

! R-HQ
router ospf 1
 router-id 10.255.0.2
 network 10.255.0.0 0.0.0.3 area 0
```

验证：两端 `show ip ospf neighbor` 均为 **FULL**；R-HQ `show ip route ospf` 出现三条 O 路由（`192.168.10.0/24`、`192.168.20.0/24`、`192.168.30.0/24`），下一跳 `10.255.0.1`。

说明：只发布 HQ Transit 段与 HQ 三个 `/24`，**不发布** `203.0.113.0/30`；**不把 BGP 表重分发进 OSPF**。SW-CORE 为 DR、R-HQ 为 BDR（DR 选举不抢占，先启动者当选），两端 FULL 即正常。

### 第 2 层：HQ 默认出口 + WAN eBGP

```text
! R-HQ：默认出口 + 向 OSPF 发布默认路由
ip route 0.0.0.0 0.0.0.0 203.0.113.2
router ospf 1
 default-information originate

! R-HQ（AS 65001）
router bgp 65001
 bgp log-neighbor-changes
 neighbor 203.0.113.2 remote-as 65000
 network 192.168.30.0 mask 255.255.255.0

! R-ISP（AS 65000）
router bgp 65000
 bgp log-neighbor-changes
 neighbor 203.0.113.1 remote-as 65001
 neighbor 198.51.100.2 remote-as 65002
 network 192.0.2.0 mask 255.255.255.0
 network 203.0.113.0 mask 255.255.255.252
 network 198.51.100.0 mask 255.255.255.252

! R-BRANCH（AS 65002）
router bgp 65002
 bgp log-neighbor-changes
 neighbor 198.51.100.1 remote-as 65000
 network 172.16.40.0 mask 255.255.255.192
 network 172.16.40.64 mask 255.255.255.224
```

验证：

- 三个 eBGP 会话全部 **Established**（`show ip bgp summary` 的 `State/PfxRcd` 显示前缀数）；
- R-HQ 学到 `B 172.16.40.0/26`、`B 172.16.40.64/27`、`B 192.0.2.0/24`、`B 198.51.100.0/30`；
- R-BRANCH 学到 `B 192.168.30.0/24`、`B 192.0.2.0/24`、`B 203.0.113.0/30`；
- SW-CORE 通过 OSPF 学到 **`O*E2 0.0.0.0/0`**（默认出口，via `10.255.0.2`）；
- `BR-OFFICE-PC ping 192.168.30.10` **通** —— 跨站点业务首次打通。

### 第 3 层：WAN-IN 业务与隔离 ACL（R-HQ G0/1 inbound）

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

interface gigabitEthernet 0/1
 ip access-group WAN-IN in
```

验证（6 项行为测试）：

| 测试 | 结果 | 对应验收 |
|---|---|---|
| BR-OFFICE → `192.168.30.10` | 4/4 通 | 业务服务允许 |
| BR-OFFICE → `http://192.168.30.10` | 页面打开 | **N7** |
| BR-OFFICE → `192.168.20.10` | 100% 丢包 | **N8** |
| BR-OFFICE → `192.168.30.20` | 100% 丢包 | **N8** |
| BR-ADMIN → `192.168.30.20` | 4/4 通 | 运维允许 |
| BR-ADMIN → `192.168.20.10` | 100% 丢包 | IOT 拒绝 |

> **隔离机制说明**：HQ IOT 的隔离由**双重保障**实现——① BGP 层面 R-HQ **不对外发布 IOT 前缀**，Branch 无路由可达；② `WAN-IN` 的 deny 规则作为**纵深防御**。由 ping 的 `unreachable` **来源地址**可分辨：来自 `172.16.40.1` / `.65`（R-BRANCH）= 无路由；来自 `203.0.113.1`（R-HQ）= ACL 主动拒绝。

### 第 4 层：NAT/PAT + 静态映射 + DNS/HTTP

```text
! R-HQ
interface gigabitEthernet 0/0
 ip nat inside
interface gigabitEthernet 0/1
 ip nat outside
ip access-list standard NAT-INSIDE
 permit 192.168.10.0 0.0.0.255
ip nat inside source list NAT-INSIDE interface gigabitEthernet 0/1 overload
ip nat inside source static tcp 192.168.30.10 80 203.0.113.1 80

! SW-CORE：为使 HQ OFFICE 能使用 Internet DNS（NETWORK_PLAN §7.2）而新增
ip dhcp pool OFFICE
 dns-server 192.0.2.10
```

INTERNET-SERVER（GUI）：HTTP Service = **On**；DNS Service = **On**，记录 `www.edgecampus.net → 192.0.2.10`、`status.edgecampus.net → 203.0.113.1`。

验证：

- **N9**：OFFICE-PC `ping 192.0.2.10` 通；`show ip nat translations` 出现静态表项 `203.0.113.1:80 ↔ 192.168.30.10:80` 与 PAT 会话；
- **N10**：OFFICE-PC 浏览器打开 `http://www.edgecampus.net`（DNS 解析 + PAT + HTTP 全链路）；
- **N11**：INTERNET-SERVER 浏览器打开 `http://203.0.113.1`，命中 HQ-SERVICE 页面；NAT 表出现 `192.0.2.10:1025` 活动会话。

> **增量说明**：`dns-server 192.0.2.10` 是既有 `ip dhcp pool OFFICE` 中的**新增选项**，未改变 VLAN / IPv4 网段 / 端口映射 / Trunk / EtherChannel / ACL / 路由等任何冻结项，地址分配范围不变。仅在 OSPF 范围内标注为增量配置。

### Gate 3 验证结果

| 日期 | 测试 | 预期 | 实际 | 证据 |
|---|---|---|---|---|
| 2026-09-16 | **N5** OSPF | FULL / HQ routes 正确 | 双向 FULL；R-HQ 学到三条 O 路由 | `G3-A-01` / `01b` |
| 2026-09-16 | **N6** eBGP | Established / prefixes 正确 | 三会话 Established，路由双向交换 | `G3-A-02` / `02b` |
| 2026-09-16 | **N7** Branch Business | BR-OFFICE → HQ-SERVICE HTTP 允许 | HTTP 页面打开 | `G3-A-03c` |
| 2026-09-16 | **N8** Branch Isolation | → HQ IOT / 管理设备 拒绝 | 均 100% 丢包 | `G3-A-03b` / `03d` |
| 2026-09-16 | **N9** PAT | 成功且有 NAT translation | 通 + NAT 转换表有记录 | `G3-A-04b` |
| 2026-09-16 | **N10** DNS/HTTP | `www.edgecampus.net` 解析并访问成功 | 页面打开 | `G3-A-04c` |
| 2026-09-16 | **N11** Static Port Map | 外部节点 → `203.0.113.1:80` → HQ-SERVICE | 页面打开 + NAT 会话 | `G3-A-04d` / `04d2` |
| 2026-09-16 | HQ ADMIN → Branch 管理 | 可达 | `.65` 4/4；`.66` 2/4（跨 4 跳 ARP） | `G3-A-05` |
| 2026-09-16 | 四层回归 | HQ Gate1 Core 无退化 | 每层后均通过 | `G3-A-01c/02d/02e/03e/04e/04f` |

### Gate 3 实施中的问题与说明

1. **Packet Tracer 不会自动续租**：SW-CORE 的 DHCP 池新增 `dns-server` 后，OFFICE-PC 仍持旧租约、`DNS Server` 为空，导致 `www.edgecampus.net` 无法解析。**解法**：在 PC 的 IP Configuration 中先切 Static、再切回 DHCP 触发重新请求。**非配置错误**。
2. **配置模式层级导致的 `Invalid input`**：在特权模式（`R-HQ#`）下直接输入 `router bgp 65001` 会报错；必须先 `configure terminal` 进入 `(config)`。属操作规范问题，已记录以避免复现。
3. **IOT 隔离的双重机制**：见第 3 层说明——BGP 不发布前缀（无路由）+ ACL deny（纵深防御）。报告与答辩中应如实说明，不宜简化为"配了 ACL 所以不通"。
4. **跨跳 ARP 首包超时**：ADMIN-PC → SW-BRANCH（跨 4 跳）首次 ping 出现 50% 丢包，后两个包 TTL=251 正常返回；属 ARP 解析期，**非故障**。

## Gate 4：IPv6 / Tunnel / Port Security / Central Admin

原发布范围（用户于 2026-09-17 确认已实测，截图后补；下方归档记录为当前结论）：

- HQ OFFICE SLAAC；
- BR-OFFICE DHCPv6；
- 管理域 Static IPv6；
- R-HQ ↔ R-BRANCH IPv6-over-IPv4 Tunnel；
- IPv6 static route；
- BR-ADMIN → HQ MANAGEMENT；
- HQ ADMIN → R-BRANCH / SW-BRANCH remote management；
- SW-ACCESS Fa0/1 sticky MAC / Port Security。

权威逻辑规划始终以 `docs/NETWORK_PLAN.md` 为准。

## 2026-09-17 Gate4 现场成果归档与更正

本次 feat/edge 为用户指定归档分支，不从旧 main 覆盖工作树。详细配置输入与解释见 `docs/gate4/A_NETWORK_REPORT.md`。配置来自用户现场记录，未把提示中的建议冒充本次读取的 running-config；二进制未直接打开核验。A N12-N15 用户确认已实测，截图本次跳过后补，见 `evidence/network/gate4/README.md`；G4 N1-N11 全量回归需新记录。

IPv6：SW-CORE VLAN10/30/Transit 为 2001:db8:10::1、30::1、100::1 /64；R-HQ Transit 100::2；Tunnel0 HQ ff::1 / Branch ff::2（IPv4 endpoints 203.0.113.1 / 198.51.100.2，ipv6ip）。Static routes 保证 Branch50↔HQ30，ISP IPv4-only、无 OSPFv3。BR-OFFICE DHCPv6 40::/64、BR-ADMIN Static 50::70、HQ-SERVICE 30::10。实际 DHCPv6 IOS 输出后补。

Remote Admin：R-BRANCH/SW-BRANCH VTY-HQ-ADMIN 只 permit 192.168.30.20、deny any，VTY telnet/login/access-class；ADMIN Telnet .65/.66 与 OFFICE deny 用户报告已测。Port Security：SW-ACCESS Fa0/1 access VLAN10、sticky、maximum 1、restrict；正常 Secure-up 与非法 MAC violation/恢复用户报告已测，计数不编造。

**N7 当前更正（取代历史最终 PASS 解读）**：用户最新实测 Branch 私网 ping 192.168.30.10 PASS，但 BR-OFFICE/BR-ADMIN http://192.168.30.10 FAIL；BR-OFFICE http://203.0.113.1 PASS。static TCP/80 让 192.168.30.10:80 同时承担 inside-local 与内部端点，导致 TCP/NAT 非对称。最终入口 203.0.113.1:80→192.168.30.10:80；G3-A-03c 只证明 static mapping 共存前历史阶段，不证明当前私网直连。未改变冻结地址或映射。

B/C/D：G4-B-01 v2/33 策略基线；G4-B-02 离线 33.3 C ON；G4-B-03 与 G4-C-05 自动 reconnect/hello/state_sync 恢复 31.8/OFF/v2/33/1；G4-D-01 控制平面失联；G4-C-01/02/03/04/05 清零 C 三项 stability debt。离线 OFF/Attributes 与恢复 Dashboard 待补图；图的真实路径/改名 SHA-256 见 `docs/gate4/EVIDENCE_INDEX.md`。

当前用户包 EdgeCampus.pkt：136138 bytes，SHA-256 74bfa6067dc8570b88c96c941101235d1cac4127c81fe5678483277767d6eb35；AI 未改动包内容。当前 Gate4 IMPLEMENTED / USER-TESTED / EVIDENCE PENDING，Gate5 NOT STARTED。

## 2026-09-18：G4 后 NOC 管理配置与最终归档

总状态：**完成（待补证据）**。配置来源为用户提交的《EdgeCampus NOC功能升级过程与配置报告》，原文件与完整文字见 `docs/final/source/`。本次没有登录PT、修改IOS或执行Discovery；以下按用户报告重排为可读配置记录，不代表本次运行输出。

### NC-HQ / SW-CORE

NC-HQ GigabitEthernet0接入SW-CORE Gi1/0/10；地址192.168.30.30/24，GW192.168.30.1，ADMIN-PC192.168.30.20。用户报告配置：

```text
interface gigabitEthernet 1/0/10
 switchport mode access
 switchport access vlan 30
 no shutdown
```

### R-HQ 管理地址

报告保留G0/0 OSPF业务链路，新增稳定管理Loopback：

```text
interface loopback0
 ip address 10.255.255.1 255.255.255.255
 description MANAGEMENT_LOOPBACK
```

报告称Discovery发现该地址，但没有直接截图证明其Managed。需导出接口/实际管理路由；不自动推定Loopback已被OSPF或BGP发布。

### CLI / VTY 管理增量

报告使用本地设备用户名认证、`line vty 0 4`、`login local`、`transport input telnet`，Discovery协议为Telnet。设备CLI实验凭据详见用户源报告，不与NC Web/API账户混用。

```text
ip access-list standard VTY-HQ-ADMIN
 permit host 192.168.30.20
 permit host 192.168.30.30
 deny any
```

此段更新旧G4‘只permit .30.20’的管理准入事实。应用设备、原ACL合并顺序、VTY `access-class VTY-HQ-ADMIN in` 绑定需以完整running-config核对；报告没有逐设备输出，不补造绑定已执行。必须验证普通HQ OFFICE/BR-OFFICE仍被拒绝。

### NC与Dashboard

用户确认真实NC接入，原图直接证明SW-CORE192.168.30.1/MultiLayerSwitch与SW-BRANCH172.16.40.66/Switch Managed，另三项Unsupported。原图`evidence/noc/NOC-NC-01-controller-managed-inventory.png`。Dashboard只对collectionStatus=Managed映射ONLINE；协议级OSPF/BGP/Tunnel为NOT COLLECTED。

Backend只读ticket/设备清单/物理拓扑，不写IOS。Security/Branch仍模拟，Campus Network/Security仍配置展示。Cloud演练中断Edge WS；网络模拟禁用/409。

### 最新用户包与待核验

`packet_tracer/EdgeCampus.pkt`：156539 bytes，SHA-256 `4f53c07e45ea66ea96bd83b42b751cb3cfb41c354c9f9489ae4358f4cdf1634c`。这是当前发布采用的最新正式文件；此前147803、136138和144326 bytes版本保留为历史。图47–54的详细配置、Packet Tracer限制和复现步骤见`docs/COURSE_COVERAGE_PATCH.md`；最终运行配置、SBC程序嵌入、保存重开及连续三轮彩排按`docs/FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md`留证。
