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

## Gate 4：IPv6 / Tunnel / Port Security / Central Admin — ✅ 已实施并验证通过

实施记录（2026-09-16，**已实测**）：按 `NETWORK_PLAN.md` §13 第 8–12 步推进。

### 第 8 层：Central Administration（N14）

```text
! R-BRANCH 与 SW-BRANCH 各配一份
ip access-list standard MGMT-ALLOW
 permit 192.168.30.20
exit
line vty 0 4
 access-class MGMT-ALLOW in
 transport input telnet
 password cisco
 login
exit
```

验证：ADMIN-PC(`192.168.30.20`) Telnet `172.16.40.65` / `.66` **成功**；OFFICE-PC Telnet `172.16.40.65` **被拒**（`Connection refused`）；两台 `show access-lists` 均显示 `MGMT-ALLOW` 且有命中。

### 第 9 层：IPv6 地址（N12）

```text
! 三台路由器（SW-CORE / R-HQ / R-BRANCH）
ipv6 unicast-routing

! SW-CORE
interface gigabitEthernet 1/0/24  ipv6 address 2001:db8:100::1/64
interface vlan 10                 ipv6 address 2001:db8:10::1/64
interface vlan 30                 ipv6 address 2001:db8:30::1/64

! R-HQ
interface gigabitEthernet 0/0     ipv6 address 2001:db8:100::2/64

! R-BRANCH
interface gigabitEthernet 0/1.40  ipv6 address 2001:db8:40::1/64
interface gigabitEthernet 0/1.50  ipv6 address 2001:db8:50::1/64

! DHCPv6 服务端（BR-OFFICE VLAN40）
ipv6 dhcp pool BR-V6
 address prefix 2001:db8:40::/64
exit
interface gigabitEthernet 0/1.40
 ipv6 dhcp server BR-V6
 ipv6 nd managed-config-flag
exit
```

终端：HQ-SERVICE `2001:db8:30::10/64`、ADMIN-PC `2001:db8:30::20/64`、BR-ADMIN-PC `2001:db8:50::70/64`（网关均为各自 `::1`）；OFFICE-PC 用 **SLAAC**、BR-OFFICE-PC 用 **DHCPv6**。

验证：OFFICE-PC 经 SLAAC 获得 `2001:DB8:10:0:2E0:F9FF:FEB0:77EE`；BR-OFFICE-PC 经 DHCPv6 获得 `2001:DB8:40:0:1990:FD7C:D148:C4A6`，与 R-BRANCH `show ipv6 dhcp binding` 的绑定**完全一致**（且**非 EUI-64**，证明来自地址池）。

### 第 10 层：IPv6-over-IPv4 Tunnel（N13）

```text
! R-HQ
interface tunnel 0
 tunnel source gigabitEthernet 0/1
 tunnel destination 198.51.100.2
 tunnel mode ipv6ip
 ipv6 address 2001:db8:ff::1/64

! R-BRANCH
interface tunnel 0
 tunnel source gigabitEthernet 0/0
 tunnel destination 203.0.113.1
 tunnel mode ipv6ip
 ipv6 address 2001:db8:ff::2/64

! 四条 IPv6 静态路由（不引入 OSPFv3）
R-BRANCH: ipv6 route 2001:db8:30::/64 2001:db8:ff::1
R-HQ:     ipv6 route 2001:db8:50::/64 2001:db8:ff::2
R-HQ:     ipv6 route 2001:db8:30::/64 2001:db8:100::1
SW-CORE:  ipv6 route 2001:db8:50::/64 2001:db8:100::2
```

验证：两端 `show interfaces tunnel 0` 均 `up/up` 且 `Tunnel protocol/transport IPv6/IP`；隧道端点互 ping **5/5**；**BR-ADMIN-PC → `2001:db8:30::10` 4/4 通**（N13 核心）。

### 第 11 层：Port Security（N15）

```text
interface fastEthernet 0/1
 switchport mode access
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation restrict
exit
```

验证：初始 `Secure-up` / `Max 1` / `Sticky 1` / `Violation 0`；替换为非法 MAC `0000.1111.2222` 触发 `%PORT_SECURITY-2-PSECURE_VIOLATION`，**Violation Count = 5**，非法流量 100% 丢包，合法 sticky MAC `00E0.F9B0.77EE` 仍在表；恢复原 MAC 后通信恢复正常。

### 第 12 层：Full Regression + 跨层问题修复

**全量回归（N1–N11 + Edge）**：EtherChannel / VLAN / ACL / SVI / DHCP、OSPF、eBGP、PAT / DNS / 静态映射、全部行为测试 —— 均通过。

**发现并修复：静态 NAT 误抓穿越流量（N7）**

- **现象**：BR-OFFICE-PC 浏览器打不开 `http://192.168.30.10`（N7）。
- **定位**：`show ip nat translations` 出现 `Outside global = 172.16.40.2:`**`0`**（端口 0）的坏会话；临时移除静态映射后 N7 立刻恢复正常。
- **根因**：**Packet Tracer** 的静态映射在反向查找时按 **inside-local（地址 + 端口）** 匹配，导致"**目的地 = 内网服务地址**"的**穿越流量**也被抓去翻译。真实 IOS 按 inside-global 匹配，无此问题。
- **处置**：引入**遮蔽条目**（置于配置前部），使穿越流量被"翻译成自身"（无害），公网流量仍走真正的映射：

```text
ip nat inside source static tcp 192.168.30.10 80 192.168.30.10 80     ! 遮蔽：身份翻译，必须在前面
ip nat inside source static tcp 192.168.30.10 80 203.0.113.1 80       ! 真正的公网端口映射
```

- **验证**：**N7 与 N11 同时成立** —— BR-OFFICE `http://192.168.30.10` 与 INTERNET-SERVER `http://203.0.113.1` 均正常打开；穿越流量的会话端口一致（如 `172.16.40.2:1039 ↔ 172.16.40.2:1039`），**不再出现端口 0**。**地址、端口、NAT 位置全部零偏离设计**。

### Gate 4 验证结果

| 日期 | 测试 | 预期 | 实际 | 证据 |
|---|---|---|---|---|
| 2026-09-16 | **N12** IPv6 modes | SLAAC / DHCPv6 / Static 正确 | 三种模式全部实测成立 | `G4-A-03/03b/03c/03d` |
| 2026-09-16 | **N13** IPv6 Tunnel | BR-ADMIN → HQ MANAGEMENT | IPv6 ping 4/4 通 | `G4-A-04*` |
| 2026-09-16 | **N14** Remote Admin | HQ ADMIN 允许，普通 Office 拒绝 | 两台登录成功；OFFICE 被拒 | `G4-A-01*` |
| 2026-09-16 | **N15** Port Security | 非法 MAC violation / 阻断 | Violation Count 5 + 100% 丢包 | `G4-A-02*` |
| 2026-09-16 | Full Regression | N1–N11 无退化 | 全部通过 | `G4-A-05*` |
| 2026-09-16 | N7 与 N11 共存 | 两条需求同时成立 | 遮蔽方案修复，均 PASS | `G4-A-06/07/07b` |

### Gate 4 实施中的问题与说明

1. **PT 静态 NAT 的 inside-local 反向匹配**：见第 12 层，已用遮蔽条目解决；属**平台实现差异**，非配置错误。**逐层回归必须覆盖完整验收矩阵**——Gate 3 第 4 层未回头重测 N7 才漏掉了它。
2. **DHCPv6 客户端不发起请求**：只配 `ipv6 dhcp pool` + `ipv6 dhcp server` 不够，RA 缺 **M 标志**时主机会自行 SLAAC。补 `ipv6 nd managed-config-flag` 后 `show ipv6 dhcp binding` 才出现绑定。**先记录实测再调整，未删除 DHCPv6 验收项**（符合 `NETWORK_PLAN.md` §9.2）。
3. **`tunnel source <IP>` PT 不支持**：改用接口形式 `tunnel source gigabitEthernet 0/1`。
4. **IPv6 静态路由不能用 `tunnel 0` 作下一跳**：必须写对端隧道 IPv6 地址（如 `2001:db8:ff::1`）。
5. **`show ipv6 route static` PT 不认 `static` 关键字**：改用 `show ipv6 route` 或 `show running-config | include ipv6 route`。
6. **Gate 3 的 N7 结论说明**：Gate 3 的 N7 验证发生在静态映射加入**之前**；在 Gate 3 最终配置下曾因上述 NAT 问题失效。本 Gate 已定位并修复，N7 在最终配置下**重新成立**。

权威逻辑规划始终以 `docs/NETWORK_PLAN.md` 为准。
