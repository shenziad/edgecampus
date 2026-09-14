# Packet Tracer 配置与验证日志

> 每条关键配置记录“目的—命令—结果”；不要把整份 running-config 无解释地堆入报告。

## 环境信息

- Packet Tracer 版本：`9.0.1.0858`
- SW-CORE 型号：`Cisco 3650-24PS`
- SW-ACCESS 型号：`Cisco 2960-24TT`
- 真实主机网络方式：`TODO（待与 B/C 联调确认）`

## 端口映射

见 `docs/NETWORK_PLAN.md`，Gate 0 已冻结（摘要）：

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

已完成的验证：

```text
show vlan brief
show etherchannel summary
show interfaces trunk
show ip interface brief
show ip route
show ip dhcp binding
```

- VLAN 10 `OFFICE` active、VLAN 20 `IOT` active、VLAN 30 `MANAGEMENT` active
- EtherChannel：`Po1(SU)` LACP，成员 `Gig1/0/1(P)`、`Gig1/0/2(P)`
- Trunk：`Po1` on / 802.1q / trunking，allowed `10,20,30`，STP 转发态 `10,20,30`
- SVI：`Vlan10/20/30` 均 up/up，地址 `192.168.10.1 / .20.1 / .30.1`
- 路由：三条直连 `C 192.168.10.0/24`、`192.168.20.0/24`、`192.168.30.0/24`
- DHCP：OFFICE-PC 获取 `192.168.10.10`（掩码 255.255.255.0，网关 192.168.10.1）
- ACL：`OFFICE-IN` 挂 `Vlan10` inbound、`IOT-IN` 挂 `Vlan20` inbound（`show running-config` 确认）
- 证据：`evidence/network/G1-02-swcore-vlan-brief-pass.png`、`evidence/network/G1-04-swcore-trunk-etherchannel-pass.png`、`evidence/network/G1-06-swcore-svi-routing-pass.png`、`evidence/network/G1-07-dhcp-pass.png`、`evidence/network/G1-08-swcore-acl-config.png`

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

验证：

```text
show vlan brief
show etherchannel summary
show interfaces trunk
```

- VLAN 10 `OFFICE` active，Fa0/1 在其中
- VLAN 20 `IOT` active，Fa0/2 在其中
- VLAN 30 `MANAGEMENT` active，Fa0/3、Fa0/4 在其中
- EtherChannel：`Po1(SU)` LACP，成员 `Gig0/1(P)`、`Gig0/2(P)`
- Trunk：`Po1` on / 802.1q / trunking，allowed `10,20,30`，STP 转发态 `10,20,30`
- 证据：`evidence/network/G1-01-swaccess-vlan-brief-pass.png`、`evidence/network/G1-03-swaccess-access-ports-pass.png`、`evidence/network/G1-05-swaccess-trunk-etherchannel-pass.png`

## 终端地址

| 设备 | IP | 掩码 | 网关 | 方式 |
|---|---|---|---|---|
| OFFICE-PC | 192.168.10.10 | 255.255.255.0 | 192.168.10.1 | DHCP |
| EDGE-SBC-01 | 192.168.20.10 | 255.255.255.0 | 192.168.20.1 | 静态 |
| ADMIN-PC | 192.168.30.20 | 255.255.255.0 | 192.168.30.1 | 静态 |
| BACKEND-STUB | 192.168.30.10 | 255.255.255.0 | 192.168.30.1 | 静态 |

## 功能验证结果

| 日期/时间 | 测试 | 预期 | 实际 | 证据路径 |
|---|---|---|---|---|
| 2026-09-15 | EtherChannel 状态 | Up/In use | Po1(SU)，两台交换机均通过 | `evidence/network/G1-04-*.png`、`G1-05-*.png` |
| 2026-09-15 | N1 VLAN/路由 | 跨允许域可达 | OFFICE→ADMIN(192.168.30.20) 4/4 通 | `evidence/network/G1-09-n1-crossvlan-ping-pass.png` |
| 2026-09-15 | N2 ACL 隔离 | OFFICE→IOT 拒绝 | deny 命中 4 次，4 个 ping 全被拦截 | `evidence/network/G1-10-n2-office-to-iot-deny.png` |
| 2026-09-15 | N3 控制面访问 | OFFICE→管理节点 允许 | OFFICE→BACKEND-STUB(192.168.30.10) 通 | `evidence/network/G1-11-n3-mgmt-access-pass.png` |
| TODO | IOT → Backend:8000 | 允许 | 待 B 侧联调（SBC 不便于直接 ping 验证） | `evidence/network/` |
