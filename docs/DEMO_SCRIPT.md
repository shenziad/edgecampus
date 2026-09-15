# 现场 6 分钟演示脚本 — Final Architecture v2

> 主演示仍控制在约 6 分钟。Final Architecture v2 新增的课程组网能力采用“业务路径 + 快速状态命令”展示，不把现场变成逐条配置演示。若老师单独验收网络协议，再使用本文末尾的扩展验收清单。

## 演示前检查

- 打开最终 canonical `.pkt`，确认 HQ / WAN / Branch 链路稳定。
- `show etherchannel summary`、OSPF/BGP 邻居、Tunnel、NAT 等关键状态已预检查。
- Backend 与 Dashboard 未残留旧进程。
- Event Stream 清理或从当前时间明确开始。
- 已准备停止/恢复 Backend 的确定命令。
- HQ-SERVICE、INTERNET-SERVER 的 HTTP/DNS 已开启。
- 主讲人和每次操作人固定，不现场临时换手。

## 0:00–0:45 架构与项目定位

展示完整拓扑：HQ、ISP/Internet、Branch，以及 HQ 内 OFFICE / IOT / MANAGEMENT。

话术重点：

> EdgeCampus 是一个多园区智慧校园网络。总部拥有 IoT Edge 与控制服务，分部承担异地业务和运维；企业 WAN 使用 OSPF/eBGP、NAT 和 IPv6 Overlay。系统核心不是远程开风扇，而是 Edge Local Loop 与 Cloud Global Loop 的协同，并在 Cloud 失联时保持本地自治。

必须主动说明：Packet Tracer WAN 是模拟 Data Plane；真实 FastAPI 由 RealWSClient 带外连接，不声称 WebSocket 经过 BGP/NAT。

## 0:45–1:30 HQ 网络安全与多站点业务

快速展示：

- `Po1(SU)` / Trunk / VLAN10/20/30；
- OFFICE → IOT 被 ACL 拒绝；
- BR-OFFICE → HQ-SERVICE HTTP 成功；
- HQ ADMIN 可管理 Branch 网络设备，普通 Office 不可。

只用一句话指出：HQ 使用 SVI，Branch 使用 Router-on-a-Stick，是根据站点规模采用不同设计。

## 1:30–2:25 真实温度闭环

- PT 将温度由约 28 C 调到约 32 C。
- SBC 本地自动开启 FAN01。
- 真实 Telemetry 经 RealWSClient 进入 FastAPI。
- Dashboard 显示约 32 C、WARNING、Fan ON。
- Event Stream 展示 `SENSOR` 与 `EDGE-AUTO`。

强调：Dashboard 数值来自真实 Packet Tracer TEMP01，不是 fake edge。

## 2:25–3:15 Cloud Policy 下发

- Dashboard 把阈值从 30 C 改为 33 C。
- 展示 `policy_ack` / Policy Version 更新。
- 证明 32 C 时不再触发 ON，34 C 时 FAN ON。

强调：这是 Policy Delivery，不是单纯“网页遥控开关”。

## 3:15–4:35 核心高潮：断云不断控

- 停止 Backend，Dashboard 明确显示连接丢失。
- PT 调温：高于阈值时 FAN ON；低于 `threshold-hysteresis` 时 FAN OFF。
- 说明 Edge 保留最后有效策略，本地闭环仍运行。
- 恢复 Backend。
- 展示 Edge 自动重连、`hello` / `state_sync`、温度/Fan/Policy 恢复。

这是创新性最重要的一段，不应被 WAN 演示挤掉。

## 4:35–5:20 WAN / Internet / IPv6 Overlay

用预先准备好的最短路径展示：

- HQ OFFICE → `www.edgecampus.net`：DNS + HTTP + PAT；
- 快速展示 `show ip nat translations`；
- BR-ADMIN 通过 IPv6-over-IPv4 Tunnel 到达 HQ-SERVICE / HQ MANAGEMENT；
- 快速展示 Tunnel up / IPv6 ping 成功。

话术：

> ISP 只提供 IPv4 Underlay，企业通过 IPv6 Overlay 保留跨站点管理网络；总部普通办公用户通过 R-HQ PAT 访问 Internet。

## 5:20–6:00 总结与课程覆盖

快速指出：

```text
HQ：VLAN / Trunk / EtherChannel / SVI / DHCP / ACL / Port Security
HQ→WAN：OSPF / NAT / DNS / HTTP / static port mapping
WAN：eBGP
Branch：VLSM / Router-on-a-Stick / DHCPv6 / remote management
跨站点：IPv6 static route + IPv6-over-IPv4 Tunnel
应用：Edge Local Loop + Cloud Global Loop + State Sync
```

收尾：

> 因此，本系统不是五次实验的拼接，而是一个统一的多园区业务系统：网络层负责安全承载总部、分部与 Internet，Edge 层负责现场自治，Cloud 层负责全局策略和可观测，故障时仍能按分层原则降级运行。

---

# 教师扩展网络验收清单（主演示后按需）

### HQ 二层/三层

```text
show vlan brief
show interfaces trunk
show etherchannel summary
show ip interface brief
show access-lists
```

### OSPF / BGP

```text
show ip ospf neighbor
show ip route
show ip bgp summary
show ip bgp
```

### NAT / Internet

```text
show ip nat translations
show ip nat statistics
```

配合 DNS / HTTP 页面验收。

### IPv6 / Tunnel

```text
show ipv6 interface brief
show ipv6 route
show interfaces tunnel 0
```

配合 BR-ADMIN → HQ-SERVICE IPv6 ping / 业务访问。

### Port Security

```text
show port-security interface fa0/1
show mac address-table interface fa0/1
```

先展示正常 OFFICE-PC，再用非法 MAC 触发 violation，观察 Violation Count 增长。

> 具体 Packet Tracer 9.0.1 支持的命令以 A 的最终 `CONFIG_LOG.md` 为准；如某条 show 命令语法有差异，使用等价命令，不改变验收意图。
