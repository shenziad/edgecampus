# Gate 4 — A Network 配置与验收归档

日期：2026-09-17。N12-N15：USER-REPORTED PASS / EVIDENCE PENDING。用户确认已测试，本次截图跳过后补。本报告区分用户提供的现场记录与 AI 未能直接核验的二进制内容。

## 目标与设计

在既有 HQ Core/Branch/WAN 上增量实现 IPv6 modes、IPv6-over-IPv4 Tunnel、Remote Administration 与 Port Security。ISP 保持 IPv4-only；不新增 OSPFv3，管理 Overlay 用 IPv6 static route。避免改动冻结 VLAN/IP/接口/AS/协议。RealWSClient 的真实 Edge–Cloud 流仍是带外，不经此 Tunnel。

## 用户提供的关键配置记录（待 show running-config / evidence 交叉核验）

SW-CORE 开启 ipv6 unicast-routing；VLAN10=2001:DB8:10::1/64（OFFICE SLAAC）、VLAN30=2001:DB8:30::1/64（Static），Gi1/0/24=2001:DB8:100::1/64；返回路由：

```text
ipv6 route 2001:DB8:50::/64 2001:DB8:100::2
```

R-HQ G0/0=2001:DB8:100::2/64；R-HQ 与 R-BRANCH 的 Tunnel0 分别为 2001:DB8:FF::1/64、::2/64，source 分别 G0/1、G0/0，destination 分别 198.51.100.2、203.0.113.1，tunnel mode ipv6ip，no shutdown。

```text
! R-HQ
ipv6 route 2001:DB8:30::/64 2001:DB8:100::1
ipv6 route 2001:DB8:50::/64 tunnel 0
! R-BRANCH
ipv6 route 2001:DB8:30::/64 tunnel 0
```

R-BRANCH 的 BR-OFFICE-V6 pool 记录 address prefix 2001:DB8:40::/64，G0/1.40 配 2001:DB8:40::1/64、managed-config-flag、ipv6 dhcp server BR-OFFICE-V6；G0/1.50=2001:DB8:50::1/64。BR-ADMIN=2001:DB8:50::70/64、GW ::1；HQ-SERVICE=2001:DB8:30::10/64、GW ::1。PT 9.0.1 的实际 DHCPv6 支持/获取结果待现场图核验，不将这些输入记录伪称本次已导出配置。

两台 Branch 设备的 VTY 配置只允许 ADMIN-PC 192.168.30.20：

```text
ip access-list standard VTY-HQ-ADMIN
 permit host 192.168.30.20
 deny any
line vty 0 4
 password edgecampus
 login
 transport input telnet
 access-class VTY-HQ-ADMIN in
```

Telnet 仅用于课程验收；生产环境优先 SSH。G3 的 ping 管理可达不能代替 G4 的 Telnet 成功与 OFFICE 拒绝。

```text
interface fastEthernet 0/1
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation restrict
```

sticky/maximum 1 绑定原 OFFICE MAC；restrict 阻断非法 MAC 并保留端口工作便于展示计数，测试后恢复原 OFFICE-PC。

## 实际测试记录与占位

用户确认 N12 SLAAC/DHCPv6/Static、N13 BR-ADMIN ping 2001:DB8:30::10、N14 ADMIN Telnet .65/.66/OFFICE 拒绝、N15 Secure-up/sticky/非法 MAC violation 已实测。当前未入库相应截图，不填写虚构地址后缀、MAC、violation 数值或 IOS 原始输出。逐项占位见 [EVIDENCE_INDEX](EVIDENCE_INDEX.md) 和 evidence/network/gate4/README.md。

N1-N11 本次全量回归没有新增截图/命令导出；历史 G1-G3 保留作基线，不能直接代替 G4 regression PASS。

## Gate3 NAT/HTTP 回归问题

用户最新实测：Branch ping 192.168.30.10 PASS，但 BR-OFFICE/BR-ADMIN 直连 http://192.168.30.10 FAIL；BR-OFFICE http://203.0.113.1 PASS。静态映射使私网 TCP/80 同时承担 inside-local 和内部业务端点，导致 TCP/NAT 非对称。最终业务入口为 203.0.113.1:80→192.168.30.10:80，私网三层用 ping 验证。历史 G3-A-03c 私网页面截图真实保留，但仅证明当时阶段，不能代表最终映射共存状态。

## canonical 包记录

当前用户修改的 packet_tracer/EdgeCampus.pkt：136138 bytes；SHA-256 74bfa6067dc8570b88c96c941101235d1cac4127c81fe5678483277767d6eb35。AI 未修改二进制、未从 main 覆盖，未在此环境打开 PT 验证内部配置。用户提供包本次作为待验收现场成果归档，不用文件大小/哈希证明 N12-N15 PASS。

归档期间外部更新了用户包：初读 124085 bytes / f5aa95c4…，最终 136138 bytes / 74bfa6067dc8570b88c96c941101235d1cac4127c81fe5678483277767d6eb35。AI 保留最新内容，未覆盖或编辑；此变化不当作新实测证据。
