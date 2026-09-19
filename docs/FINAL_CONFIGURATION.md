# EdgeCampus 最终配置总览

更新日期：2026-09-19。项目状态：**验收完成，报告准备中**。组织方式为“功能技术模块 → 拓扑区域 → 设备 → 配置、作用、验证”。本文汇总当前项目的网络、终端、IoT、Backend、Dashboard 与 NC 配置。用户本轮确认 G4/network 原则上与当前网络配置一致，因此以其已实施配置和证据为网络基线，再叠加后续 NC 改动；本文是配置总览，不冒充本次直接导出的完整 running-config。

## 1. 版本依据与阅读方法

### 1.1 本次实际核对的版本

配置核对使用当前 `feat/edge` 工作树、历史分支提交与已归档证据；最终交付以当前分支中的文件为准。

| 来源 | 核对版本 | 本文用途 |
|---|---|---|
| 当前 `feat/edge` | 工作树发布版本 | NOC、NC、最终文档和正式PT包 |
| G4网络来源提交 | `4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8` | 21张原图已原样纳入当前 `evidence/network/` |
| 历史集成基线 | `1a5beca755c63a3d57917491de5c1cef81c4060e` | 当前分支祖先；仅用于追溯 |
| 本地 `feat/edge` | `ac3f6c0bf58a75c4bb846ad790d7c19827147bd3` | 最新 G4 Edge、中文 NOC、NC 只读采集与收尾归档 |
| 用户 NOC 配置报告 | [原始报告](final/source/EdgeCampus_NOC功能升级过程与配置报告.docx) / [文本](final/source/REPORT_TEXT.md) | NC-HQ 接入、R-HQ Loopback、本地认证及 VTY 准入增量 |
| 课程重点补强 | [详细配置与证据](COURSE_COVERAGE_PATCH.md) | 当前正式包中的静态EtherChannel、Branch PAT/ACL、双DROTHER、隔离重分发、双端口Port Security |

网络 G4 的主要远程依据为 [CONFIG_LOG](https://github.com/shenziad/edgecampus/blob/4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8/packet_tracer/CONFIG_LOG.md) 与 [A_NETWORK_REPORT](https://github.com/shenziad/edgecampus/blob/4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8/docs/gate4/A_NETWORK_REPORT.md)。本地 [CONFIG_LOG](../packet_tracer/CONFIG_LOG.md) 包含更晚 NC 实施记录。按用户本轮确认，G4/network 为当前网络配置参考，不作为第二套并行配置；旧输入中的池名、路由语法及修复前 HTTP 结论以 G4 实施与证据更正。

### 1.2 配置来源标记

- **网络基线**：G1–G3 配置记录与 G4来源提交及当前分支已归档实施记录；用户确认与当前网络原则上一致；实时计数、动态地址和现场运行状态仍按采集时刻读取。
- **NC 增量**：用户后续报告的实际实施内容；设备覆盖、最终 ACL 绑定等仍需当前 running-config 核验。
- **源码确定**：本地程序或 JSON 中直接读取的参数与行为；包内实际部署一致性仍需核验。
- **未启用 / 未登记 / 待核验**：不补造命令、地址、密码、MAC、计数或在线状态。

下文 CLI 为分模块配置摘录，省略 `configure terminal/end` 等外层导航。它们用于阅读与对照，不应整篇粘贴执行；尤其 VTY 的 NC 增量、DHCPv6 池名与 NAT 条目顺序见 [§12 配置沿革与证据](#differences)。

### 1.3 内容导航

1. [拓扑、设备与地址总表](#inventory)
2. [VLAN、Trunk、EtherChannel](#layer2)
3. [IPv4 网关、ROAS、DHCP 与 Underlay](#ipv4)
4. [OSPF、默认出口与 eBGP](#routing)
5. [ACL、管理认证与 Port Security](#security)
6. [PAT、端口映射、DNS 与 HTTP](#services)
7. [IPv6 地址、SLAAC 与 DHCPv6](#ipv6)
8. [IPv6 Tunnel 与静态路由](#tunnel)
9. [TEMP/MCU/SBC/FAN 与 Edge Policy](#edge)
10. [Backend、Dashboard、NC 与 NOC](#noc)
11. [配置沿革、设备反向索引与核验](#differences)

<a id="inventory"></a>

## 2. 拓扑、设备与地址总表

### 2.1 系统分层

```text
HQ：OFFICE / IOT / MANAGEMENT
              SW-ACCESS == Po1(mode on) == SW-CORE -- OSPF -- R-HQ
                                                          |
                                          AS65001 -- eBGP -- R-ISP AS65000
                                                          |          |
                                                    eBGP       INTERNET-SERVER
                                                          |
                                                   R-BRANCH AS65002
                                                          |
                                                    802.1Q ROAS
                                                          |
                                                     SW-BRANCH
                                                  BR-OFFICE / BR-MGMT

IPv6 管理 Overlay：SW-CORE -- R-HQ == Tunnel0/IPv4 Underlay == R-BRANCH
IoT：TEMP01 A0 → MCU A0 → USB0/9600 → SBC → D0 → FAN01
带外通道1：SBC RealWSClient ↔ 宿主机 FastAPI :8000 ↔ Dashboard
带外通道2：NC-HQ Real World Access :58000 → 宿主机 NC 适配器 → Dashboard
课程隔离验证：SW-CORE -- VLAN100/OSPF1 -- R-COURSE -- OSPF44/eBGP -- R-TEST
```

R-ISP 转发 Tunnel 外层 IPv4，不是企业 Tunnel 终结点。HQ-SERVICE/BACKEND-STUB 是 PT 内部测试服务器，不是宿主机 FastAPI。

### 2.2 全部设备清单

| 区域 | 设备 | 地址 / 连接 | 配置职责 |
|---|---|---|---|
| HQ Core | SW-CORE，3650-24PS | VLAN10/20/30 `.1`；Vlan100 `10.255.0.1/29` | SVI、DHCP、HQ ACL、静态EtherChannel、OSPF、IPv6、NC 接入 |
| HQ Access | SW-ACCESS，2960-24TT | 上联 Gi0/1–2；独立管理 IP 未登记 | Access/Trunk/静态EtherChannel、Fa0/1与Fa0/3 Port Security；不能假定有管理 SVI |
| HQ Border | R-HQ，2911 | G0/0 `10.255.0.2/29`；G0/1 `203.0.113.1/30` | OSPF/eBGP、默认路由、WAN ACL、PAT、映射、Tunnel；NC 增量 Loopback0 `10.255.255.1/32` |
| Course Router | R-COURSE，2911 | G0/0 `10.255.0.3/29`；G0/1 `10.254.44.1/30` | OSPF1/44、BGP65144、隔离重分发与默认路由发布 |
| Test Router | R-TEST，2911 | G0/0 `10.254.44.2/30`；Lo0 `10.44.44.1/24`；Lo1 `10.54.54.1/32` | OSPF44、BGP65154、测试前缀与回程验证 |
| ISP | R-ISP，2911 | G0/0 `203.0.113.2/30`；G0/1 `198.51.100.1/30`；G0/2 `192.0.2.1/24` | AS65000、IPv4-only Transit、Internet LAN |
| Branch Border | R-BRANCH，2911 | G0/0 `198.51.100.2/30`；G0/1.40 `172.16.40.1/26`；G0/1.50 `172.16.40.65/27` | ROAS、DHCP/DHCPv6、AS65002、Tunnel、VTY |
| Branch Access | SW-BRANCH，2960-24TT | VLAN50 `172.16.40.66/27` | VLAN40/50、Trunk、管理 SVI、默认网关、VTY |
| HQ OFFICE | OFFICE-PC | DHCP，历史租约 `192.168.10.10/24`，GW `.10.1` | 办公业务、SLAAC、隔离/Port Security 测试；动态租约不是固定地址 |
| HQ IOT | EDGE-SBC-01 | `192.168.20.10/24`，GW `.20.1`；USB0/D0 | 实际 Edge 程序、策略执行与 RealWSClient |
| HQ IOT | TEMP01 | A0→MCU A0 | 温度输入，无需为该模拟量链路配置 IP |
| HQ IOT | IO-MCU-01 | A0、USB0 | 采样、换算和 USB 温度帧，无已登记网络地址 |
| HQ IOT | FAN01 | D0←SBC D0 | 执行器状态 0/1/2；项目使用 0/2 |
| HQ MANAGEMENT | ADMIN-PC | `192.168.30.20/24`，GW `.30.1` | 真实中央运维、访问 NC、IPv6 Static |
| HQ MANAGEMENT | HQ-SERVICE / BACKEND-STUB | `192.168.30.10/24`，GW `.30.1` | PT HTTP、IPv6 管理业务目标、静态映射内部端点 |
| HQ MANAGEMENT | NC-HQ | `192.168.30.30/24`，GW `.30.1`，GE0→Core Gi1/0/10 | 实际设备 Discovery/管理采集、Northbound API |
| Branch OFFICE | BR-OFFICE-PC | DHCP，历史租约 `172.16.40.2/26`，GW `.40.1` | 分部业务/隔离、DHCPv6；当前租约按实际读取 |
| Branch MGMT | BR-ADMIN-PC | `172.16.40.70/27`，GW `.40.65` | 异地管理与 IPv6 Overlay 验证 |
| Internet | INTERNET-SERVER | `192.0.2.10/24`，GW `192.0.2.1` | DNS/HTTP、外部映射测试 |
| 宿主机 | FastAPI Backend | 当前启动脚本 `127.0.0.1:8000` | WS、状态、ACK、NOC REST 与 NC 只读适配 |
| 宿主机浏览器 | Dashboard | `http://127.0.0.1:8000` | 中文 Edge/NOC 管理入口；不是 PT PC 的内部业务网页 |

### 2.3 全部物理接口

| 区域 | 本端 | 对端 | 类型 |
|---|---|---|---|
| HQ | SW-CORE Gi1/0/1、Gi1/0/2 | SW-ACCESS Gi0/1、Gi0/2 | Po1 两成员，802.1Q Trunk |
| HQ | SW-ACCESS Fa0/1 | OFFICE-PC Fa0 | access VLAN10，Port Security |
| HQ | SW-ACCESS Fa0/2 | EDGE-SBC-01 FastEthernet0 | access VLAN20 |
| HQ | SW-ACCESS Fa0/3 | ADMIN-PC Fa0 | access VLAN30 |
| HQ | SW-ACCESS Fa0/4 | HQ-SERVICE Fa0 | access VLAN30 |
| HQ NC | SW-CORE Gi1/0/10 | NC-HQ GigabitEthernet0 | access VLAN30，NC 增量 |
| HQ Transit | SW-CORE Gi1/0/24 | R-HQ G0/0 | access VLAN100，共享OSPF广播网段 |
| Course Transit | SW-CORE Gi1/0/23 | R-COURSE G0/0 | access VLAN100，共享OSPF广播网段 |
| Course Test | R-COURSE G0/1 | R-TEST G0/0 | IPv4 /30，隔离OSPF44/eBGP测试链路 |
| WAN | R-HQ G0/1 | R-ISP G0/0 | IPv4 /30 |
| WAN | R-ISP G0/1 | R-BRANCH G0/0 | IPv4 /30 |
| Internet | R-ISP G0/2 | INTERNET-SERVER Fa0 | Internet LAN |
| Branch | R-BRANCH G0/1 | SW-BRANCH Gi0/1 | Trunk，子接口 .40/.50 |
| Branch | SW-BRANCH Fa0/1 | BR-OFFICE-PC Fa0 | access VLAN40 |
| Branch | SW-BRANCH Fa0/2 | BR-ADMIN-PC Fa0 | access VLAN50 |
| IoT | TEMP01 A0→MCU A0；MCU USB0→SBC USB0；SBC D0→FAN D0 | 本地传感/执行链路 | 模拟量、USB、Custom Cable |

R-HQ/R-BRANCH G0/2 为预留，未登记业务配置；其他空闲端口不推定已配置 shutdown、PortFast 或其他增强参数。

<a id="layer2"></a>

## 3. 二层：VLAN、Trunk 与 EtherChannel

来源：网络基线 [本地配置日志](../packet_tracer/CONFIG_LOG.md)；NC 接入口来自用户报告。

### 3.1 HQ / SW-CORE

```text
hostname SW-CORE
vlan 10
 name OFFICE
vlan 20
 name IOT
vlan 30
 name MANAGEMENT
interface range gigabitEthernet 1/0/1 - 2
 channel-group 1 mode on
interface port-channel 1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
```

Gi1/0/1–2 由静态 `mode on` 合为Po1，承担HQ三个VLAN的交换机互联。当前3650的Packet Tracer CLI不接受`switchport trunk encapsulation dot1q`，因为封装固定为802.1Q；该行无需执行。最终`show etherchannel summary`应显示Po1(SU)、两个成员(P)，Protocol列为`-`。

NC 增量单独使用 Gi1/0/10，不改变 Po1 或 Transit：

```text
interface gigabitEthernet 1/0/10
 switchport mode access
 switchport access vlan 30
 no shutdown
```

### 3.2 HQ / SW-ACCESS

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
 channel-group 1 mode on
interface port-channel 1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
```

### 3.3 Branch / SW-BRANCH

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
```

Branch 不部署第二套 EtherChannel。现有 [Core Po1 证据](../evidence/network/G1-04-swcore-trunk-etherchannel-pass.png)、[Access Po1 证据](../evidence/network/G1-05-swaccess-trunk-etherchannel-pass.png) 与 [Branch Gi0/1 证据](../evidence/network/G2-A-02-branch-vlan-trunk-pass.png) 均显示 **Native VLAN 为默认 VLAN1**。HQ Trunk 只允许 VLAN10/20/30，Branch 只允许 VLAN40/50；这些业务 VLAN 使用 802.1Q 标签，VLAN1 不在上述允许列表中。未登记自定义 `switchport trunk native vlan` 命令，不把管理 VLAN30/50 说成 Native VLAN。没有登记专门的 STP 调优、PortFast 或 BPDU Guard 配置。

### 3.4 验证

`show vlan brief`、`show interfaces trunk`、`show etherchannel summary`。HQ 历史已归档 Po1(SU)、两个成员(P)、allowed VLAN10/20/30；Branch 为40/50。VLAN 隔离广播域，跨 VLAN 权限还需 §5 ACL。

<a id="ipv4"></a>

## 4. IPv4：网关、Underlay、ROAS 与 DHCP

### 4.1 HQ / SW-CORE：三层 SVI 与 Transit

```text
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
vlan 100
 name OSPF-TRANSIT
interface range gigabitEthernet 1/0/23 - 24
 switchport mode access
 switchport access vlan 100
 no shutdown
interface vlan 100
 ip address 10.255.0.1 255.255.255.248
 no shutdown
```

Vlan10/20/30 SVI提供HQ三个业务网关；Vlan100 SVI提供OSPF广播网段三层地址。Gi1/0/24接R-HQ、Gi1/0/23接R-COURSE，两者均为access VLAN100。

OFFICE IPv4 DHCP，G3 增加 Internet DNS 选项：

```text
ip dhcp excluded-address 192.168.10.1 192.168.10.9
ip dhcp pool OFFICE
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 192.0.2.10
```

### 4.2 HQ/WAN / R-HQ

| 接口 | 配置 | 作用 |
|---|---|---|
| G0/0 | `ip address 10.255.0.2 255.255.255.248`；`ip ospf priority 0`；`no shutdown` | HQ Transit，OSPF，NAT inside |
| G0/1 | `ip address 203.0.113.1 255.255.255.252`；`no shutdown` | HQ 外网、eBGP、NAT outside、Tunnel source |
| Loopback0 | `ip address 10.255.255.1 255.255.255.255`；`description MANAGEMENT_LOOPBACK` | 用户 NC 报告新增管理地址；其可达路由/协议发布未登记 |

### 4.3 ISP / R-ISP

| 接口 | 配置 | 作用 |
|---|---|---|
| G0/0 | `ip address 203.0.113.2 255.255.255.252`；`no shutdown` | HQ 互联 |
| G0/1 | `ip address 198.51.100.1 255.255.255.252`；`no shutdown` | Branch 互联 |
| G0/2 | `ip address 192.0.2.1 255.255.255.0`；`no shutdown` | INTERNET-SERVER 网关 |

ISP 保持 IPv4-only。未登记 ISP NAT、IPv6、DHCP 或用户管理认证配置。

### 4.4 Branch / R-BRANCH：VLSM 与 ROAS

```text
hostname R-BRANCH
interface gigabitEthernet 0/0
 ip address 198.51.100.2 255.255.255.252
 no shutdown
interface gigabitEthernet 0/1
 no shutdown
interface gigabitEthernet 0/1.40
 encapsulation dot1Q 40
 ip address 172.16.40.1 255.255.255.192
interface gigabitEthernet 0/1.50
 encapsulation dot1Q 50
 ip address 172.16.40.65 255.255.255.224
ip dhcp excluded-address 172.16.40.1
ip dhcp pool BR-OFFICE
 network 172.16.40.0 255.255.255.192
 default-router 172.16.40.1
```

VLAN40 使用 `172.16.40.0/26`，VLAN50 使用 `.64/27`，不是两个 `/24`。只有办公区登记 IPv4 DHCP；Branch DHCP 池未登记 `dns-server`，不能声称该池已下发 DNS。

### 4.5 Branch / SW-BRANCH 与终端

```text
interface vlan 50
 ip address 172.16.40.66 255.255.255.224
 no shutdown
ip default-gateway 172.16.40.65
```

SW-BRANCH 为二层交换机，SVI 用于本机管理，没有启用 `ip routing`。固定终端 IP/掩码/网关见 §2.2；IPv4 DHCP 客户端分别选 DHCP，其他终端选 Static。HQ-SERVICE、ADMIN-PC、NC-HQ 使用 `/24`，BR-ADMIN 与 SW-BRANCH 使用 `/27`。

### 4.6 验证

`show ip interface brief`、`show ip route`、`show ip dhcp binding`，配合各网关和四段 Underlay 相邻 ping。历史动态租约 `.10.10`、`.40.2` 只作实施例子；修改 DNS 后 PT 客户端可能需要重新申请租约。

<a id="routing"></a>

## 5. IPv4 路由：HQ OSPF、默认出口与 WAN eBGP

来源：G3 网络配置；G4归档报告记录了后续回归。新增 NC Loopback 是否进入路由发布仍待核验。

### 5.1 HQ / SW-CORE

```text
router ospf 1
 router-id 10.255.0.1
 network 10.255.0.0 0.0.0.7 area 0
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
 network 192.168.30.0 0.0.0.255 area 0
```

### 5.2 HQ Border / R-HQ

```text
ip route 0.0.0.0 0.0.0.0 203.0.113.2
router ospf 1
 router-id 10.255.0.2
 network 10.255.0.0 0.0.0.7 area 0
 default-information originate
router bgp 65001
 bgp log-neighbor-changes
 neighbor 203.0.113.2 remote-as 65000
 network 192.168.30.0 mask 255.255.255.0
```

HQ VLAN 路由由 Core 的 OSPF 学入 R-HQ；R-HQ 将已有默认出口发布给 Core，Core 历史为 `O*E2 0.0.0.0/0`。BGP 仅显式发布管理/业务网 `192.168.30.0/24`，没有发布 HQ IoT/Office 全部网段。Loopback 增量不自动意味着 Router ID 改成 `10.255.255.1`。

### 5.3 ISP / R-ISP

```text
router bgp 65000
 bgp log-neighbor-changes
 neighbor 203.0.113.1 remote-as 65001
 neighbor 198.51.100.2 remote-as 65002
 network 192.0.2.0 mask 255.255.255.0
 network 203.0.113.0 mask 255.255.255.252
 network 198.51.100.0 mask 255.255.255.252
```

ISP 发布 Internet LAN 与两条 WAN 前缀，支持业务及 Tunnel IPv4 端点互通。

### 5.4 Branch / R-BRANCH

```text
router bgp 65002
 bgp log-neighbor-changes
 neighbor 198.51.100.1 remote-as 65000
 network 172.16.40.0 mask 255.255.255.192
 network 172.16.40.64 mask 255.255.255.224
```

### 5.5 路由融合与验证

生产WAN的OSPF与BGP仍在R-HQ分工交汇，**没有配置生产域的广泛`redistribute`**，没有将完整AS65001/65000/65002 BGP表导入OSPF，也没有新增OSPFv3。课程补强的R-COURSE/R-TEST使用独立OSPF44与BGP65144/65154，只把测试前缀`10.54.54.0/24`以E2注入OSPF1，并向R-TEST发布缺省路由；见下一节。

`show ip ospf neighbor`、`show ip route`、`show ip bgp summary`、`show ip bgp`。两条 eBGP 连接在三个路由器上的邻居条目合计四条；R-ISP 有两个邻居，不能把设备数直接当会话数。BGP summary 的数字 PfxRcd 表示已建立，不要求显示字符串 ESTABLISHED。

### 5.6 课程隔离路由验证 / R-COURSE、R-TEST

VLAN100现为`10.255.0.0/29`。SW-CORE设置OSPF priority 255，R-HQ与R-COURSE均为priority 0，因此Core侧邻居表出现两个`FULL/DROTHER`。R-COURSE与R-TEST在`10.254.44.0/30`上运行独立OSPF44和eBGP 65144/65154；R-TEST用Null0汇总路由发布`10.54.54.0/24`，并以Lo1 `10.54.54.1/32`提供ping目标。

Packet Tracer 2911不支持本方案原计划使用的prefix-list、route-map及distribute-list，因此没有伪造这些命令；通过隔离协议域控制影响范围。验收以SW-CORE的`O E2 10.54.54.0/24`、Type-5 LSA `Metric Type: 2`、R-TEST的`O*E2 0.0.0.0/0`和ADMIN-PC到`10.54.54.1`四次成功ping为准。完整命令见[课程重点补强](COURSE_COVERAGE_PATCH.md)。

<a id="security"></a>

## 6. 安全：数据 ACL、管理 VTY 与 Port Security

### 6.1 HQ / SW-CORE：SVI 数据 ACL

```text
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

VLAN30 未登记限制性 SVI ACL。末尾 `permit ip any any` 意味着这是针对特定隔离目标的 ACL，不能声称只允许前两条业务；TCP8000 是 PT 模拟服务规则，不证明带外 FastAPI 流量经过该 SVI。

### 6.2 HQ Border / R-HQ：WAN-IN

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

Branch Office 对 `.30.10` 有 HTTP/ICMP 例外，随后拒绝其他 HQ 管理目标；Branch 管理网可访问 HQ 管理域，仍禁止 IoT。IoT 跨站点不通还包含 BGP 未发布该前缀的因素，丢包不能单独证明 ACL 命中。

WAN-IN 最后仍允许其他流量，不把它夸大为完整的 Internet 默认拒绝防火墙。这里的 IPv4 ACL 不自动过滤 IPv6 Overlay；未登记 IPv6 ACL，不能声称双栈权限完全相同。

### 6.3 Branch / R-BRANCH、SW-BRANCH：G4归档管理基线

以下两台设备各配置一份，来自已归档G4实测记录：

```text
ip access-list standard MGMT-ALLOW
 permit 192.168.30.20
line vty 0 4
 access-class MGMT-ALLOW in
 transport input telnet
 password <G4设备VTY实验密码>
 login
```

允许 ADMIN-PC `.30.20`，其他来源隐含 deny。这里是 line password + login，与后续 NC 的 login local 是两个阶段，不是同时生效的两种认证。SW-BRANCH 回程依赖 §4.5 默认网关。

### 6.4 HQ/Branch 管理平面：用户后续 NC 增量

用户报告记录了以下变更，但未逐台导出当前配置：

```text
username admin privilege 15 secret <设备CLI实验密码>
ip access-list standard VTY-HQ-ADMIN
 permit host 192.168.30.20
 permit host 192.168.30.30
 deny any
line vty 0 4
 login local
 transport input telnet
```

NC-HQ 以设备 CLI 凭据/Telnet 进行 Discovery，Web/API 登录账户为另一套账户。当前实际应用设备范围、原 MGMT-ALLOW 是否改名/替换、`access-class VTY-HQ-ADMIN in` 是否已绑定、VTY 5–15 是否存在及其设置均待当前运行配置确认。不能只创建新 ACL 就声称旧绑定自动迁移。没有登记 SSH 密钥、SSH 服务或 AAA 服务器配置。

### 6.5 HQ / SW-ACCESS：端口与 MAC 安全

```text
interface fastEthernet 0/1
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation restrict
interface fastEthernet 0/3
 switchport mode access
 switchport access vlan 30
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation restrict
```

当前两条合法sticky记录为Fa0/1/VLAN10的`00E0.F9B0.77EE`和Fa0/3/VLAN30的`00D0.97E2.907A`。课程违规测试在临时副本中把非法PC接入Fa0/3，违规计数达到5；恢复ADMIN-PC后ping恢复。计数属于该次测试，不是永久保证。

**restrict** 丢弃非法 MAC 流量、计数并可产生日志，合法终端仍可使用端口；没有选择 shutdown/err-disable 模式。sticky 为自动学习绑定，不伪称执行过手工静态 MAC 命令。是否将学习项保存入 startup-config 需保存重开核验。

### 6.6 权限与验证总表

| 源 | 目标 | 基线预期 / 注意事项 |
|---|---|---|
| HQ OFFICE | HQ IoT | OFFICE-IN 拒绝 |
| HQ IoT | HQ OFFICE | IOT-IN 拒绝 |
| HQ ADMIN | Branch `.65` / `.66` | 真实 Telnet 允许；应以登录提示符验收 |
| HQ OFFICE / BR-OFFICE | Branch 设备管理 | VTY 拒绝；NC 增量后需再回归 |
| NC-HQ | 被采集设备 | 用户增量允许准确来源 `.30.30`，不是放开整个 `/24` |
| BR-OFFICE | HQ-SERVICE | HTTP/ICMP 业务例外；NAT 共存差异见 §7 |
| BR-OFFICE | HQ 其他管理节点 / IoT | WAN ACL/路由隔离 |
| BR-ADMIN IPv6 | HQ-SERVICE IPv6 | 经 Overlay 可达，不据此声称已有 IPv6 ACL |

`show access-lists`、`show running-config`、实际 Telnet 允许/拒绝、`show port-security interface fa0/1`、`show port-security interface fa0/3`、`show port-security address`，配合正常→非法→恢复对照。NOC 模拟安全事件不替代这些输出。

<a id="services"></a>

## 7. 出口与应用：PAT、静态端口映射、DNS、HTTP

### 7.1 HQ Border / R-HQ：PAT

```text
interface gigabitEthernet 0/0
 ip nat inside
interface gigabitEthernet 0/1
 ip nat outside
ip access-list standard NAT-INSIDE
 permit 192.168.10.0 0.0.0.255
ip nat inside source list NAT-INSIDE interface gigabitEthernet 0/1 overload
```

HQ Office `/24`登记通用PAT，复用`203.0.113.1`的不同端口/标识。HQ IoT未登记通用PAT；不将NAT-INSIDE说成接口业务ACL。课程补强还在R-BRANCH配置VLAN40来源PAT，inside为G0/1.40、outside为G0/0，ACL `BR-NAT-INSIDE`只匹配`172.16.40.0/26`到Internet网段`192.0.2.0/24`。

R-BRANCH同时在G0/1.40入方向应用`BR-INTERNET-POLICY`：先拒绝到`192.0.2.10`的ICMP，再允许到同一主机的TCP/80，最后`permit ip any any`。因此HTTP成功与NAT TCP翻译、ping失败与deny计数共同构成协议级策略证据。

### 7.2 HQ Border / R-HQ：公网 TCP80 映射与G4归档修复

冻结映射为 `203.0.113.1:80 → 192.168.30.10:80`。G4归档实施记录为兼顾私网 HTTP 与公网映射，在真正映射之前增加身份翻译条目：

```text
ip nat inside source static tcp 192.168.30.10 80 192.168.30.10 80
ip nat inside source static tcp 192.168.30.10 80 203.0.113.1 80
```

第一条为 A 报告针对 PT 行为的修复，第二条才是公网端口映射；不将其说成一般生产网络必须配置的规则。没有登记一对一全协议 Static NAT，也没有把最终服务改成8080；8080仅曾用于定位实验。

已目视核对 G4 的 [最终共存图](https://github.com/shenziad/edgecampus/blob/4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8/evidence/network/G4-A-07b-n7-n11-coexist-confirm-pass.png)：running-config 中身份条目位于公网映射前，BR-OFFICE 私网 HTTP 与 INTERNET-SERVER 公网 HTTP 同时打开，穿越会话两侧源端口一致。按用户本轮确认，此修复纳入当前网络配置基线，两个入口都应保留；此前私网 HTTP FAIL 的记录属于修复前/历史状态，不作为最终预期。当前现场演示仍应刷新两个页面检查结果。报告对 NAT 误匹配的解释是该次 PT 排查结论，没有在真实 IOS 上复核。

### 7.3 HQ / HQ-SERVICE（BACKEND-STUB）

GUI 配置：Fa0 `192.168.30.10/24`，GW `.30.1`；IPv6 地址见 §8；HTTP 服务用于测试页面与映射，端口80。它不运行仓库 FastAPI，不把 `http://192.168.30.10` 当宿主机 Dashboard。TCP8000 ACL 规则与实际 HTTP80 是不同验证对象。

### 7.4 Internet / INTERNET-SERVER

GUI 配置：Fa0 `192.0.2.10/24`、GW `.2.1`；Services→DNS On、HTTP On。

| DNS A 记录 | IPv4 | 用途 |
|---|---|---|
| `www.edgecampus.net` | `192.0.2.10` | HQ OFFICE 经 PAT 访问 Internet DNS/HTTP |
| `status.edgecampus.net` | `203.0.113.1` | 公网服务映射名称 |

无已登记的 AAAA、IPv6 DNS 服务器、HTTPS 或其他应用服务。HQ DHCP 为 OFFICE 下发 IPv4 DNS；Branch IPv4/DHCPv6 DNS 下发未登记。

### 7.5 用户终端与验证

OFFICE-PC 浏览器 `http://www.edgecampus.net`；INTERNET-SERVER 或已确认 Branch 路径访问 `http://203.0.113.1`。BR-OFFICE 同时使用 `http://192.168.30.10` 验证私网业务，保留身份条目与公网映射共存。配合 `show ip nat translations`、`show ip nat statistics`、DNS 参数/解析与实际 HTTP 页面；ping 成功不能代替 HTTP。

<a id="ipv6"></a>

## 8. IPv6：地址、SLAAC、DHCPv6 与固定管理节点

来源：G4网络归档实施记录；具体动态地址仅为该阶段实测。IPv4 与 IPv6 共存，ISP 未开启原生 IPv6。

### 8.1 地址总表

| 区域 | 前缀 | 网关/设备 | 模式与状态 |
|---|---|---|---|
| HQ OFFICE VLAN10 | `2001:db8:10::/64` | SW-CORE Vlan10 `::1` | OFFICE-PC SLAAC |
| HQ IoT VLAN20 | `2001:db8:20::/64` | 规划值 | G4归档明确未启用；不能声称 SBC 已有该 IPv6 地址 |
| HQ MGMT VLAN30 | `2001:db8:30::/64` | SW-CORE `::1`；HQ-SERVICE `::10`；ADMIN-PC `::20` | Static；NC IPv6 未登记 |
| HQ Transit | `2001:db8:100::/64` | Core `::1`；R-HQ `::2` | Static |
| Branch OFFICE VLAN40 | `2001:db8:40::/64` | R-BRANCH `.40` 子接口 `::1` | BR-OFFICE DHCPv6 |
| Branch MGMT VLAN50 | `2001:db8:50::/64` | R-BRANCH `::1`；BR-ADMIN `::70` | Static；SW-BRANCH IPv6 未登记 |
| Tunnel | `2001:db8:ff::/64` | R-HQ `::1`；R-BRANCH `::2` | Static Overlay |

### 8.2 HQ / SW-CORE

```text
ipv6 unicast-routing
interface vlan 10
 ipv6 address 2001:db8:10::1/64
interface vlan 30
 ipv6 address 2001:db8:30::1/64
interface vlan 100
 ipv6 address 2001:db8:100::1/64
```

VLAN10 为 SLAAC 网络，OFFICE-PC 选择 Auto Config，依赖 RA 前缀与地址自动配置。没有登记手工指定 Link-local 地址，实际 FE80:: 地址由设备生成/观察，不虚构统一 `fe80::1`。

### 8.3 HQ Border / R-HQ

```text
ipv6 unicast-routing
interface gigabitEthernet 0/0
 ipv6 address 2001:db8:100::2/64
```

其 IPv6 默认出口、VLAN10跨站点路由、Loopback IPv6 均未登记；核心跨站点要求只覆盖管理域，不能推断所有 IPv6 网段都互通。

### 8.4 Branch / R-BRANCH

G4原图实测池名为 **BR-V6**，不是本地早期输入记录 BR-OFFICE-V6：

```text
ipv6 unicast-routing
ipv6 dhcp pool BR-V6
 address prefix 2001:db8:40::/64
interface gigabitEthernet 0/1.40
 ipv6 address 2001:db8:40::1/64
 ipv6 dhcp server BR-V6
 ipv6 nd managed-config-flag
interface gigabitEthernet 0/1.50
 ipv6 address 2001:db8:50::1/64
```

池 + 接口绑定 + RA M 标志构成记录中的有状态地址分配。M 标志通知客户端使用 DHCPv6 获取地址，不单独证明禁止 SLAAC；没有登记 `no-autoconfig`。该池未记录 `dns-server`/`domain-name`，不能声称已完成 IPv6 DNS 参数下发。DHCPv6 不负责提供默认路由，该信息依赖 RA/实际主机配置。

### 8.5 HQ/Branch / PC 与服务器

| 设备 | GUI 参数 / 历史结果 |
|---|---|
| OFFICE-PC | Auto Config；G4原图为 `2001:db8:10:0:2e0:f9ff:feb0:77ee`，不是固定地址承诺 |
| BR-OFFICE-PC | DHCP；G4原图为 `2001:db8:40:0:1990:fd7c:d148:c4a6`，与服务端 IA_NA 地址绑定一致 |
| ADMIN-PC | Static `2001:db8:30::20/64`，GW `2001:db8:30::1` |
| HQ-SERVICE | Static `2001:db8:30::10/64`，GW `2001:db8:30::1` |
| BR-ADMIN-PC | Static `2001:db8:50::70/64`，GW `2001:db8:50::1` |

Global Unicast 形式的实验地址使用文档前缀 `2001:db8::/32`，不声称是可在真实 Internet 公网路由的生产地址。远程 DHCPv6 输出还记录客户端 Link-local `FE80::2E0:B0FF:FE02:9A86`，这是历史采集值，不是手工固定配置。

### 8.6 验证

`show ipv6 interface brief`、`show ipv6 interface`、`show ipv6 dhcp binding` 与 PC `ipconfig`，将客户端地址与服务端绑定交叉核对。非 EUI-64 外观不是单独充分证据；服务器绑定与客户端结果对应才形成该次分配证据。具体 G4证据在远程 A 报告 §8，可复用其历史范围，加入 NC后的当前包仍需回归。

<a id="tunnel"></a>

## 9. IPv6 Overlay：Tunnel 与四条静态路由

### 9.1 HQ Border / R-HQ

```text
interface tunnel 0
 tunnel source gigabitEthernet 0/1
 tunnel destination 198.51.100.2
 tunnel mode ipv6ip
 ipv6 address 2001:db8:ff::1/64
ipv6 route 2001:db8:30::/64 2001:db8:100::1
ipv6 route 2001:db8:50::/64 2001:db8:ff::2
```

### 9.2 Branch / R-BRANCH

```text
interface tunnel 0
 tunnel source gigabitEthernet 0/0
 tunnel destination 203.0.113.1
 tunnel mode ipv6ip
 ipv6 address 2001:db8:ff::2/64
ipv6 route 2001:db8:30::/64 2001:db8:ff::1
```

### 9.3 HQ / SW-CORE：回程

```text
ipv6 route 2001:db8:50::/64 2001:db8:100::2
```

### 9.4 ISP / R-ISP 与端到端路径

ISP 无企业 Tunnel0、无原生 IPv6配置，只转发外层 IPv4。路径为 BR-ADMIN `50::70`→R-BRANCH→Tunnel→R-HQ→Core→HQ-SERVICE `30::10`，返回依靠 Core→R-HQ→Branch 的静态路由。未登记 Branch40与HQ10 的跨站点路由，不声称所有 IPv6 子网均跨站点互通。

远程实测使用接口名作为 `tunnel source`，静态路由用对端 Tunnel IPv6 **地址**，不是本地早期记录中被 PT 拒绝的 `tunnel 0` 下一跳写法。上述是 IPv6/IP，未使用 GRE、IPsec 或 OSPFv3。

先验证 IPv4 `203.0.113.1↔198.51.100.2`，再 `show interfaces tunnel 0`、`show ipv6 route`、两端 `ff::1/ff::2` ping、BR-ADMIN→`30::10` ping。G4原图记录两端 up/up、端点5/5、业务4/4；不作为当前实时数值显示。PT记录不支持 `show ipv6 route static`，使用完整路由表观察 S 路由。

<a id="edge"></a>

## 10. IoT 与 Edge：TEMP、MCU、SBC、FAN、Policy/ACK

### 10.1 HQ IoT / TEMP01、IO-MCU-01

实现：[mcu_temperature_sender.py](../edge/packet_tracer/mcu_temperature_sender.py)。TEMP01 A0接MCU A0，MCU通过 `analogRead(A0)` 读取0–1023：

```python
temp_c = raw * 200.0 / 1023.0 - 100.0
```

映射为−100～100℃，保留一位小数。MCU `USB(0,9600)`，每1000ms发送 `temp_str + "\n"`，SBC USB0同速率 `readLine()`。TEMP01环境温度是验收操作输入，不是另一份固定网络配置。

### 10.2 HQ IoT / EDGE-SBC-01：实际 Gate4 程序参数

正式源码：[sbc_gate4_controller.py](../edge/packet_tracer/sbc_gate4_controller.py)。程序与包内部署一致性按B01–B05截图和CFG08源码导出核对。

| 参数 | 源码值 | 作用 |
|---|---|---|
| EDGE_ID / TEMP_ID / FAN_ID | EDGE-SBC-01 / TEMP01 / FAN01 | 冻结设备标识 |
| POLICY_ID / PROTOCOL_VERSION | thermal-01 / 1.0 | 既有策略与消息契约 |
| WS_URL | `ws://127.0.0.1:8000/ws/edge` | External Network Access 带外连接 |
| 启动策略 | AUTO、v1、threshold30℃、hysteresis1℃ | 仅启动默认，不能当当前已应用策略 |
| LOOP_DELAY_MS | 100 | 主循环延时 |
| TELEMETRY_INTERVAL_MS | 1000 | 上报真实温度 |
| HEARTBEAT_INTERVAL_MS | 5000 | 心跳 |
| RECONNECT_INTERVAL_MS | 2000 | 重连调度 |
| TEMP_PRINT_DELTA_C | 0.5 | 温度打印变化门限 |
| USB | USB0，9600 | 实际 MCU 输入 |
| 初始 FAN | OFF | 程序启动时写入物理关闭 |

回调只记录连接/将消息入队，不在回调 `delay()`；本地温控优先于云端通信。有效策略存于当前进程内存，Cloud断连不丢失；**SBC程序重启不等同于Cloud断连**，没有实现跨程序重启的策略持久化。

AUTO：温度≥threshold→ON；温度≤threshold−hysteresis→OFF；区间内保留状态。MANUAL：保持远程命令指定状态，确认实际 FAN 写入后返回 ACK；测试后切回AUTO。新策略版本必须严格递增，阈值0–80、迟滞0–10；旧版本不能覆盖最新有效策略。

每次连接发送hello，取得实际温度后发送state_sync，包含temperature、fan_state与最后策略。恢复不能固定假设v2/v3；连续操作按实际版本递增。PT兼容timestamp使用源码固定ISO字符串，message_id为计数生成的UUID形状；日志留证应另记宿主机真实操作时间，不把固定消息时间当每次测量时钟。

### 10.3 HQ IoT / FAN01

SBC D0经Custom Cable连接FAN D0；`customWrite(0,"0")`=OFF，`customWrite(0,"2")`=HIGH，对外协议为ON。物理1=LOW未被本项目ON/OFF策略选用。状态2不能直接替代Protocol中的字符串ON。

### 10.4 Policy/Command、Backend 与 Dashboard

[PROTOCOL](PROTOCOL.md)规定hello/heartbeat/telemetry/status/state_sync、policy/command及policy_ack/command_ack，含type/protocol_version/message_id/timestamp。策略保留policy_id/version/mode/threshold_c/hysteresis_c；命令使用command_id、FAN01、ON/OFF。

Backend期望策略更新不等于物理执行成功；需要Edge ACK和实际状态。Dashboard区分待ACK、已确认与失联；真实温度/FAN来源SBC回报，离线值只表示最后观测。验证链路为温度→物理FAN→Telemetry→UI、Policy→APPLIED→新阈值动作、Command→物理动作→ACK、真停Backend→本地ON/OFF→恢复同步。

### 10.5 开发替身与默认参数差异

[config/system.json](../config/system.json)包含telemetry2s、heartbeat3s、offline_after8s以及transport0.0.0.0:8000；Fake Edge读取其部分配置。**真实PT Gate4当前为telemetry1s、heartbeat5s**，不是自动按JSON运行；当前Backend源码也没有按offline_after8s定时扫描的实现，offline主要由WS断开标记。不得把配置项存在说成全部已被实时执行。

Fake Edge/[edge/controller.py](../edge/controller.py)用于独立软件验证；真实PT验收时不与SBC争用同一Backend单Edge会话槽位。

<a id="noc"></a>

## 11. 宿主机与 NOC：Backend、Dashboard、Network Controller

### 11.1 宿主机 / Backend

[main.py](../backend/app/main.py)提供FastAPI、`/static`静态资源、Dashboard首页、单Edge WS与多个Dashboard WS。状态在内存；收到消息追加到 `runtime/events.jsonl`，事件列表上限100并优先移除高频温度事件以保留控制ACK。启动没有从该日志重放完整状态；重启后由真实Edge state_sync恢复，不是数据库持久化。

| 入口 | 用途 |
|---|---|
| GET `/`、GET `/healthz`、GET `/api/state` | UI、服务健康与Edge状态；healthz的ok不是整个PT网络PASS |
| WS `/ws/edge`、WS `/ws/dashboard` | 冻结Protocol1.0；Edge遥测/恢复、Policy/Command转发与ACK |
| GET `/api/controller/state`、`/api/network/state` | 真实NC快照与协议未采集说明 |
| GET `/api/noc/state`、`/api/network/events` | NOC聚合与独立事件流；事件API使用SIMULATED标签，不能当IOS日志 |
| GET `/api/security/state` | 模拟端口/ACL安全视图 |
| GET `/api/branch/state`、POST `/api/branch/check` | 模拟来源规则；device为R-BRANCH/SW-BRANCH，source_ip默认`.30.20` |
| GET `/api/campus-policy` | thermal现有策略与Network/Security上层展示 |
| GET `/api/simulation/state` | 演练状态、同步状态、FAN观测范围 |
| POST `/api/simulation/cloud`、`/cloud/restore` | 实际关闭/放开Edge WS；HTTP仍可用 |
| POST `/api/simulation/security`、`/security/restore` | 模拟PORT_SECURITY_VIOLATION/ACL_BLOCK_EVENT及恢复 |
| POST `/api/simulation/network`、`/network/restore` | 409，真实Health不混入网络模拟 |

原有Policy/Command走WS，不伪称另有网络设备写配置API。Protocol校验拒绝malformed/unsupported/wrong-version；Dashboard只允许下行policy/command，Edge离线时拒绝转发。依赖范围：[requirements.txt](../requirements.txt)，FastAPI>=0.115<1、Uvicorn>=0.30<1、websockets>=13<17。

### 11.2 宿主机浏览器 / Dashboard

中文界面保留协议、设备名、必要状态码。Edge使用同站点`/ws/dashboard`，WS失败约1800ms后重连，禁用控制直到snapshot确认Edge在线；NOC REST约1500ms刷新。页面在线不等于SBC在线；NC连接也不证明SBC连接。

页面同时展示Edge Control、Network Health、Security、Branch、Campus Policy、Simulation。NetworkHealth无UNKNOWN，只根据真实NC CONNECTED清单渲染卡片；Managed精确映射ONLINE，缺字段NOT COLLECTED，其他collectionStatus保留原值。OSPF/BGP/Tunnel及APIbranch_status始终NOT COLLECTED，不以Managed推断FULL/UP或分部业务通。

### 11.3 HQ MANAGEMENT / NC-HQ

用户报告：NC-HQ `192.168.30.30/24`、GW`.30.1`、GE0→Core Gi1/0/10 VLAN30；ADMIN-PC浏览器访问其内部Web配置Discovery。CLI设备账户、本地认证/Telnet和VTY来源增量见§6.4。报告称发现SW-CORE、SW-BRANCH与R-HQ Loopback；已有 [清单原图](../evidence/noc/NOC-NC-01-controller-managed-inventory.png)只直接证明：

| 设备/地址 | 原图状态 | 最终页面语义 |
|---|---|---|
| SW-CORE /192.168.30.1 | Managed | ONLINE，控制器管理状态 |
| SW-BRANCH /172.16.40.66 | Managed | ONLINE，控制器管理状态 |
| 203.0.113.1、192.0.2.1、198.51.100.2 | Unsupported，名称空缺 | 不改写为Managed/ONLINE |
| R-HQ Loopback 10.255.255.1 | 报告称发现，原图未展示 | 待实际清单核验，不声明Managed |

Preferences启用Network Controller REST External Access；Real World Access启用Access Enabled、HTTP58000并实际监听。内部192.168.30.30与宿主机127.0.0.1:58000为两个访问上下文，不可互换。

### 11.4 宿主机 / NC只读适配器

源码：[pt_controller.py](../backend/app/pt_controller.py)、[noc.py](../backend/app/noc.py)。

| 参数/请求 | 当前实现 |
|---|---|
| `PT_CONTROLLER_URL` | 默认启动脚本设`http://127.0.0.1:58000`；适配器补`/api/v1`，只接受localhost HTTP |
| `PT_CONTROLLER_USERNAME/PASSWORD` | 启动交互提供NC Web/API账户；不混用Discovery设备CLI凭据 |
| POST `/api/v1/ticket` | 获取serviceTicket，后续GET使用X-Auth-Token；这是API认证，不是写设备配置 |
| GET `/api/v1/network-device` | 白名单设备id/name/IP/type/family/reachabilityStatus/collectionStatus等字段 |
| GET `/api/v1/topology/physical-topology` | nodes/links；失败可保留成功清单并显示降级 |
| timeout / cache | 1.5s / 5s；按请求触发、缓存共享，不是独立定时采集进程 |
| 认证重试 | 401重登录后重试一次；不跟随重定向、不使用系统代理 |
| 失败结果 | NOT_CONFIGURED/UNAVAILABLE/AUTH_FAILED等，清单/旧健康失效；不回退Mock |

Frontend/API不返回密码或ticket。请求与聚合在线程池执行，避免控制器HTTP阻塞Edge WS；实际设备更新还需NC自己的采集周期，不保证拔线后5秒内必然改变Managed。

### 11.5 本地配置 / Security、Branch、Campus与Simulation

来源：[network_baseline.json](../config/network_baseline.json)、[network_agent.py](../backend/app/network_agent.py)。该JSON仍有历史mock FULL/ESTABLISHED/UP字段，但**真实NetworkHealth不读取这些字段展示路由正常**；其管理/安全/策略部分继续服务模拟与展示。

| 板块 | 配置/行为 | 真实范围 |
|---|---|---|
| Security | 初始SECURE/0/ACL ACTIVE，模拟MAC/ACL事件累计；restore保留次数和最后事件 | 不读真实PortSecurity计数，不实际封禁PT端口 |
| Branch | allowed_source`.30.20`，R-BRANCH`.65`/SW-BRANCH`.66`，配置ONLINE | Check为模拟；source_ip是请求参数，不是身份认证；未真实Telnet/SSH |
| Campus | campus version1；branch_access ALLOW、iot_isolation true、port_security STRICT；thermal为Backend现有策略 | campus-1/thermal-vN上层版本；Network/Security不下发IOS，Edge执行以ACK为准 |
| Cloud | 实际WS关闭/拒绝重连1013；restore后WAITING_FOR_STATE_SYNC→合法state_sync才SUCCESS | Uvicorn HTTP仍运行；离线FAN为LAST KNOWN，自治需PT物理观察；真停Backend另验收 |
| Network | 按钮禁用，POST409 | 不能用模拟BGP DOWN/隧道DOWN声称真实故障 |
| NOC事件 | 独立最多100条，内存保存 | 重启复位；统一事件source标签不能单独证明真实IOS作用 |

### 11.6 真实PT+NC启动

先打开当前 `.pkt`、开启PT External Network Access与NC外部API/58000、运行MCU/SBC程序，再在PowerShell：

```powershell
Set-Location 'D:\Develop\sommerom\bighomework\edgecampus-g3'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_pt_backend.ps1 -ControllerPort 58000 -BackendPort 8000
```

脚本使用`runtime/noc-venv/Scripts/python.exe`，Backend绑定127.0.0.1；交互输入NC账户，临时设置环境变量，退出恢复。旧`start_backend.ps1`使用system python/0.0.0.0且不主动设置NC参数；不是本机当前推荐入口。`.env.example`只是模板，当前main并未自动加载其中全部环境选项。

8000为Backend/SBC，58000为NC，8017曾用于独立软件演示，不自动替代SBC的8000。服务占用先处理现有进程，不重复启动。浏览器打开`http://127.0.0.1:8000`；`/healthz`检查服务，`/api/state`检查Edge，`/api/controller/state`检查NC，三者分别判断。

<a id="differences"></a>

## 12. 配置沿革、证据与设备反向索引

### 12.1 当前配置的取值与沿革

| 项目 | 本文当前取值 / 说明 |
|---|---|
| 网络基线 | 以用户确认一致且已纳入当前分支的G4/network配置为准，后续叠加 NC-HQ 管理增量 |
| 课程补强 | 静态EtherChannel、VLAN100 `/29`双DROTHER、R-COURSE/R-TEST隔离重分发、Branch PAT/ACL与双端口Port Security覆盖旧课程基线 |
| DHCPv6 | BR-V6 池绑定 G0/1.40，RA M标志；旧输入BR-OFFICE-V6不作为第二套配置 |
| IPv6路由 | 四条地址下一跳静态路由；旧`tunnel 0`输入错误不作为最终命令 |
| NAT共存 | 身份翻译条目在前、公网TCP80映射在后；私网/公网HTTP同时可用为当前预期 |
| VTY | G4图中为MGMT-ALLOW/line password；后续NC报告为本地用户认证、允许`.30.20`/`.30.30`。当前完整ACL名称/绑定范围仍需逐设备导出，不同时假定两套认证生效 |
| IPv6 IoT | 20::/64保留规划，G4证据Vlan20 IPv6 unassigned；不写成已启用 |
| 运行时序 | PT Gate4真实源码telemetry1s/heartbeat5s，不把JSON的2s/3s/8s全当实际生效 |

### 12.2 本次直接查看的关键 G4 图片

以下证据均来自固定版本 `4e0d314` 的 `evidence/network/`，原文件只读复制到被忽略的runtime参考目录，没有导入/覆盖当前正式包。下表记录实际查看过的图中内容，其他证据可从 [远程完整目录](https://github.com/shenziad/edgecampus/tree/4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8/evidence/network) 查阅。

| 图片 | 核对内容 |
|---|---|
| G4-A-01 | 两台Branch设备MGMT-ALLOW permit host .30.20与VTY access-class绑定 |
| G4-A-02 /02b | restrict/maximum1，初始计数0；非法MAC 0000.1111.2222、计数5、合法00E0.F9B0.77EE保留 |
| G4-A-03 | Core/R-HQ/Branch IPv6接口地址；G0/1.40绑定BR-V6；Vlan20 IPv6未启用 |
| G4-A-03b | ADMIN-PC .30.20及30::20，HQ内IPv6连通与静态网关 |
| G4-A-03d | M标志配置；服务端DHCPv6地址与客户端一致；客户端默认IPv6网关为路由器Link-local |
| G4-A-04 /04b | 两端Tunnel0 up/up，IPv6/IP，source/destination，端点ping5/5 |
| G4-A-04c | Core回程、R-HQ两条路由、Branch到HQ管理域路由，四条静态路由逐项核对 |
| G4-A-05c | OSPF FULL、三条HQ学习路由、三个路由器BGP摘要及NAT映射 |
| G4-A-07b | 两条静态NAT顺序、私网与公网HTTP同时打开、正常端口会话 |

G4图片提供已有网络配置参考，不替代后续NC准入和当前运行状态采集。此前收尾清单中“本地A图缺失”应理解为当时本地未归档；21张G4原图现已在当前分支，可直接引用，避免重复拍摄。

### 12.3 设备反向索引

| 设备 | 查阅配置模块 |
|---|---|
| SW-CORE | §3.1二层/NC端口；§4.1 SVI/DHCP/Transit；§5.1 OSPF；§6.1 ACL；§8.2 IPv6；§9.3回程；§6.4管理增量覆盖待核验 |
| SW-ACCESS | §3.2 VLAN/Access/静态EtherChannel；§6.5双端口PortSecurity；独立管理地址未登记 |
| R-HQ | §4.2接口/Loopback；§5.2 OSPF/默认/BGP；§6.2 WAN ACL；§6.4 NC管理；§7.1–2 NAT；§8.3/9.1 IPv6/Tunnel |
| R-ISP | §4.3 IPv4接口；§5.3 BGP；§9.4 IPv4 Underlay |
| R-BRANCH | §4.4 ROAS/DHCP；§5.4 BGP；§6.3–4 VTY；§8.4 DHCPv6；§9.2 Tunnel/静态路由 |
| R-COURSE / R-TEST | §5.6隔离OSPF/BGP重分发、双DROTHER、E2/Type-5与回程验证 |
| SW-BRANCH | §3.3二层；§4.5管理SVI/GW；§6.3–4 VTY |
| OFFICE-PC / BR-OFFICE-PC | §2.2 IPv4客户端；§7.5应用；§8.5 IPv6自动配置；§6测试角色 |
| ADMIN-PC / BR-ADMIN-PC | §2.2静态IPv4；§8.5静态IPv6；§6/9管理验证 |
| HQ-SERVICE | §2.2静态IPv4；§7.3 HTTP；§8.5静态IPv6 |
| INTERNET-SERVER | §2.2静态IPv4；§7.4 DNS/HTTP |
| NC-HQ | §3.1交换接入；§6.4设备准入；§11.3–4控制器/API |
| TEMP01 / IO-MCU-01 | §10.1采样/换算/USB |
| EDGE-SBC-01 / FAN01 | §2.2网络；§10.2–4程序/策略/执行/恢复 |
| Backend / Dashboard | §11.1–2/4–6服务、接口、轮询与启动 |

### 12.4 当前包与核验入口

当前正式 `.pkt`：156539 bytes，SHA-256 `4f53c07e45ea66ea96bd83b42b751cb3cfb41c354c9f9489ae4358f4cdf1634c`。21张G4网络原图、A/B/D最终证据和课程补强图47–54已经纳入当前分支；来源网络包与当前整合包是不同历史版本，不用于覆盖当前正式包。课程临时违规副本仅作为图54复现附件，不是正式包。最终包的保存重开、包内程序和现场行为按逐图清单、课程补强清单及CFG附件核验。

为完整实验报告，保存重开后整理：六台网络设备SW-CORE/SW-ACCESS/R-HQ/R-ISP/R-BRANCH/SW-BRANCH的完整配置；各PC/Server/NC地址和GUI服务；实际MCU/SBC程序；NC清单/API与Dashboard；N1–N15、Edge、Policy、Command、Outage、Recovery演示和展示彩排记录。报告素材计划见 [EVIDENCE_PENDING](final/EVIDENCE_PENDING.md)，软件回归见 [VALIDATION](final/VALIDATION.md)。

五次课程实验逐项落点见 [EXPERIMENT_MAPPING](EXPERIMENT_MAPPING.md)。配置字段、ID和URL仍以 [PROTOCOL](PROTOCOL.md) 与当前实现为准。
