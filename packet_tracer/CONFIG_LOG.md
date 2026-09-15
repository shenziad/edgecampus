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

# Final Architecture v2 — 待实施配置区

> **当前状态：DESIGN FROZEN / NOT YET CONFIGURED。**  
> A 从 Gate 2 起逐层填充本节。不要在配置完成前把下面项目改成 PASS。

## Gate 2：Branch LAN + IPv4 Underlay

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

实施后在此追加真实命令、输出、问题与截图路径。

## Gate 3：OSPF / eBGP / NAT / DNS / HTTP

计划内容：

- SW-CORE ↔ R-HQ：OSPF Area 0；
- R-HQ/R-ISP/R-BRANCH：eBGP 65001/65000/65002；
- R-HQ IPv4 static default route → ISP，并向 HQ OSPF 发布默认出口；
- BR-OFFICE → HQ-SERVICE；
- HQ OFFICE → PAT → Internet；
- DNS / HTTP；
- `203.0.113.1:80 → 192.168.30.10:80` static TCP mapping；
- WAN/Branch ACL。

## Gate 4：IPv6 / Tunnel / Port Security / Central Admin

计划内容：

- HQ OFFICE SLAAC；
- BR-OFFICE DHCPv6；
- 管理域 Static IPv6；
- R-HQ ↔ R-BRANCH IPv6-over-IPv4 Tunnel；
- IPv6 static route；
- BR-ADMIN → HQ MANAGEMENT；
- HQ ADMIN → R-BRANCH / SW-BRANCH remote management；
- SW-ACCESS Fa0/1 sticky MAC / Port Security。

权威逻辑规划始终以 `docs/NETWORK_PLAN.md` 为准。
