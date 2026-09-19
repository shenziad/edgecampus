# EdgeCampus 课程重点补强配置与证据

更新日期：2026-09-19。本文记录图47～图54对应的真实 Packet Tracer 增量配置、验证结果、兼容性限制与证据路径。历史 Gate 1～Gate 4 报告保留当时配置；当前最终状态以本文、[最终配置总览](FINAL_CONFIGURATION.md)和正式包 `packet_tracer/EdgeCampus.pkt` 为准。

## 1. 版本与真实性边界

| 项目 | 当前值 |
|---|---|
| 正式包 | `packet_tracer/EdgeCampus.pkt` |
| 大小 | `156539` bytes |
| SHA-256 | `4f53c07e45ea66ea96bd83b42b751cb3cfb41c354c9f9489ae4358f4cdf1634c` |
| 图54临时包 | `evidence/final_report/A/course_patch/EdgeCampus-course-e5-violation-temp.pkt` |
| 临时包 SHA-256 | `f1f3c8e2c281cdeaf5385a7bd2a4d60d49686a5e77a1396014998b7598e77747` |

正式包保留合法终端和最终拓扑；图54临时包只用于复现 Fa0/3 非法终端替换，不是 canonical 包。动态租约、MAC、计数和时间以截图当次实际值为准。

## 2. 增量拓扑

课程补强在原 HQ/ISP/Branch/NC/IoT 拓扑上增加 `R-COURSE`、`R-TEST` 和 VLAN100 广播型 OSPF 测试网段：

```text
R-HQ G0/0 10.255.0.2/29 ─ SW-CORE Gi1/0/24 access VLAN100
                                  |
                         Vlan100 10.255.0.1/29
                                  |
R-COURSE G0/0 10.255.0.3/29 ─ SW-CORE Gi1/0/23 access VLAN100
        |
        | 10.254.44.0/30；OSPF 44；eBGP 65144/65154
        |
R-TEST G0/0 10.254.44.2/30
```

原 SW-CORE Gi1/0/24 的 IPv4/IPv6 三层地址迁移到 `Vlan100`；R-HQ 地址保持 `.2`，掩码由 `/30` 扩为 `/29`。`R-COURSE` 和 `R-HQ` 的 OSPF Priority 均为 0，SW-CORE Vlan100 Priority 为 255，因此 SW-CORE 为 DR，两台路由器均显示 `FULL/DROTHER`。

## 3. 图47：手工 EtherChannel

### 3.1 SW-CORE

```text
interface range GigabitEthernet1/0/1 - 2
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 channel-group 1 mode on
 no shutdown
interface Port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
```

### 3.2 SW-ACCESS

```text
interface range GigabitEthernet0/1 - 2
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 channel-group 1 mode on
 no shutdown
interface Port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
```

验证结果：两端均为 `Po1(SU)`、两个成员均为 `(P)`、Protocol 为 `-`，Po1 trunk allowed/active/forwarding VLAN 均为 `10,20,30`。

Packet Tracer 3650 不接受 `switchport trunk encapsulation dot1q`，因为平台封装固定为 802.1Q；该报错不影响 trunk。旧 LACP 聚合器曾缓存协议状态，最终通过两端先移除 channel-group、删除并重建 Port-channel1 后消除。

## 4. 图48～49：Branch PAT 与协议正负对照

### 4.1 R-BRANCH PAT

```text
ip access-list extended BR-NAT-INSIDE
 permit ip 172.16.40.0 0.0.0.63 192.0.2.0 0.0.0.255
interface GigabitEthernet0/1.40
 ip nat inside
interface GigabitEthernet0/0
 ip nat outside
ip nat inside source list BR-NAT-INSIDE interface GigabitEthernet0/0 overload
```

最终使用扩展 ACL 限定目的为 Internet Service LAN，避免把 Branch→HQ 的内部业务流量也转换为 `198.51.100.2`。VLAN50 管理网未加入通用 PAT。

真实 TCP/80 会话示例：

```text
Inside local  172.16.40.2:1029
Inside global 198.51.100.2:1029
Outside       192.0.2.10:80
```

### 4.2 同源同目的协议策略

```text
ip access-list extended BR-INTERNET-POLICY
 deny icmp 172.16.40.0 0.0.0.63 host 192.0.2.10
 permit tcp 172.16.40.0 0.0.0.63 host 192.0.2.10 eq 80
 permit ip any any
interface GigabitEthernet0/1.40
 ip access-group BR-INTERNET-POLICY in
```

验证结果：BR-OFFICE-PC 到 `192.0.2.10` 的四次 ICMP 全部失败并命中 deny 4 次；同一客户端访问 `http://192.0.2.10` 成功，TCP/80 permit 命中并产生 PAT translation。末尾 `permit ip any any` 保留既有 Branch→HQ 业务。

## 5. 图50：两个 FULL/DROTHER

### 5.1 SW-CORE

```text
vlan 100
 name OSPF-COURSE
interface GigabitEthernet1/0/23
 switchport mode access
 switchport access vlan 100
interface GigabitEthernet1/0/24
 switchport mode access
 switchport access vlan 100
interface Vlan100
 ip address 10.255.0.1 255.255.255.248
 ipv6 address 2001:DB8:100::1/64
 ip ospf priority 255
 no shutdown
router ospf 1
 network 10.255.0.0 0.0.0.7 area 0
```

### 5.2 R-HQ

```text
interface GigabitEthernet0/0
 ip address 10.255.0.2 255.255.255.248
 ip ospf priority 0
router ospf 1
 network 10.255.0.0 0.0.0.7 area 0
```

### 5.3 R-COURSE生产侧

```text
interface GigabitEthernet0/0
 ip address 10.255.0.3 255.255.255.248
 ip ospf priority 0
 no shutdown
router ospf 1
 network 10.255.0.0 0.0.0.7 area 0
```

验证结果：SW-CORE同时看到 `10.255.0.2`、`10.255.0.3` 两条 `Pri 0 / FULL/DROTHER / Vlan100`；Vlan100 为 `State DR / Priority 255 / Neighbor Count 2 / Adjacent 2`。

## 6. 图51～52：隔离的跨协议重分发

### 6.1 Packet Tracer限制与安全替代

当前 2911 精简 IOS 不支持 `ip prefix-list`、`route-map`，也不支持 OSPF/BGP `distribute-list`。因此没有在生产 R-HQ/R-ISP 上执行无过滤的双向重分发，而是用独立 OSPF 进程44和测试 AS65144/65154实现等效隔离。生产 AS65000～65002 的显式 `network` 设计保持不变。

### 6.2 R-COURSE测试侧

```text
interface GigabitEthernet0/1
 ip address 10.254.44.1 255.255.255.252
 no shutdown
router ospf 44
 router-id 10.44.44.254
 network 10.254.44.0 0.0.0.3 area 0
 default-information originate
router bgp 65144
 bgp log-neighbor-changes
 neighbor 10.254.44.2 remote-as 65154
 redistribute ospf 44
router ospf 1
 redistribute bgp 65144 subnets
```

### 6.3 R-TEST

```text
interface GigabitEthernet0/0
 ip address 10.254.44.2 255.255.255.252
 no shutdown
interface Loopback0
 ip address 10.44.44.1 255.255.255.0
 ip ospf network point-to-point
interface Loopback1
 ip address 10.54.54.1 255.255.255.255
ip route 10.54.54.0 255.255.255.0 Null0
router ospf 44
 router-id 10.44.44.1
 network 10.254.44.0 0.0.0.3 area 0
 network 10.44.44.0 0.0.0.255 area 0
router bgp 65154
 bgp log-neighbor-changes
 neighbor 10.254.44.1 remote-as 65144
 redistribute static
```

R-TEST只有课程测试聚合静态路由进入 `redistribute static`；R-COURSE的测试BGP表只承载课程测试/测试Transit前缀。R-COURSE通过OSPF 44发布默认路由，供R-TEST返回HQ网段，不在R-TEST添加会被 `redistribute static` 误导入BGP的静态回程。

验证结果：

- R-COURSE BGP表出现 `10.54.54.0/24`，下一跳 `10.254.44.2`，AS Path `65154`；
- SW-CORE完整OSPF路由表出现 `O E2 10.54.54.0/24 [110/20] via 10.255.0.3, Vlan100`；
- SW-CORE OSPF数据库存在 `10.54.54.0/24` Type-5 LSA、Metric Type 2；
- R-TEST获得 `O*E2 0.0.0.0/0 via 10.254.44.1`；
- ADMIN-PC到 `10.54.54.1` 4/4成功，TTL 253。

Packet Tracer 的 `show ip route 10.54.54.0` 曾错误显示 `type intra area`；完整 `show ip route ospf` 的 `O E2` 和Type-5/Metric Type 2数据库为一致的协议证据，报告不使用错误的单前缀显示。

## 7. 图53～54：双端口Port Security

### 7.1 正式配置

```text
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 1
 switchport port-security violation restrict
 switchport port-security mac-address sticky
interface FastEthernet0/3
 switchport mode access
 switchport access vlan 30
 switchport port-security
 switchport port-security maximum 1
 switchport port-security violation restrict
 switchport port-security mac-address sticky
```

当次合法地址：

| 接口 | VLAN | 合法SecureSticky MAC |
|---|---:|---|
| Fa0/1 | 10 | `00E0.F9B0.77EE` |
| Fa0/3 | 30 | `00D0.97E2.907A` |

两端均为 `Secure-up`、maximum 1、restrict、Total/Sticky MAC 1。

### 7.2 临时违规与恢复

图54临时包将 `ILLEGAL-PC` 接到Fa0/3并Ping `192.168.30.1`，结果4/4超时；Fa0/3保持 `Secure-up`，violation count增至5，原合法Sticky地址未被替换。恢复ADMIN-PC后，Ping网关4/4成功且合法MAC保持。临时拓扑和包不覆盖正式交付包。

## 8. 证据索引

| 图号 | 文件 |
|---:|---|
| 1 | `evidence/final_report/A/T02-final-topology.png` |
| 47 | `evidence/final_report/A/course_patch/COURSE-E2-01-manual-etherchannel.png` |
| 48 | `evidence/final_report/A/course_patch/COURSE-E3-01-rbranch-pat.png` |
| 49 | `COURSE-E3-02-http-permit-acl-nat.png` + `COURSE-E3-03-icmp-deny.png` |
| 50 | `COURSE-E4-01-two-drother-neighbors.png` + `COURSE-E4-02-vlan100-dr-state.png` |
| 51 | `COURSE-E4-03-isolated-redistribution-config.png` |
| 52 | `COURSE-E4-04-oe2-type5.png` + `COURSE-E4-05-bgp-ping.png` |
| 53 | `COURSE-E5-01-two-port-security.png` |
| 54 | `COURSE-E5-02-violation-topology.png` + `COURSE-E5-03-fa03-violation.png` + `COURSE-E5-04-fa03-restored.png` |

除图1外，表中相对文件均位于 `evidence/final_report/A/course_patch/`。

## 9. 强制回归

课程补强后必须复核：Po1手工聚合与VLAN10/20/30；HQ DHCP/SLAAC；Branch DHCP/DHCPv6/ROAS；生产OSPF/eBGP；BR-OFFICE→HQ业务；HQ和Branch PAT；公网TCP/80映射；IPv6 Tunnel；VTY正负向；Fa0/1/Fa0/3 Port Security；TEMP→MCU→SBC→FAN；Backend断开/恢复；NC Managed清单与真实/模拟数据边界。课程测试重分发不得成为正常业务依赖。
