# Gate 与验收标准 — Final Architecture v2

## 总原则

Final Architecture v2 保留原 Gate 主线：

```text
G0 Contract Freeze
→ G1 四模块独立运行
→ G2 单向真实数据链路
→ G3 双向策略闭环
→ G4 断云自治与恢复
→ G5 Freeze 与三轮彩排
```

新增的多园区网络不是额外开一个“实验 Gate”，而是由 A 在 G2–G4 与 B/C/D 主线并行建设。

软件 Public Contract v1.0 不变；HQ Gate 1 Core 不重构。

---

## Gate 0：Contract Freeze — COMPLETE

已完成并继续有效：

- 项目定位、双控制环、状态所有权；
- Protocol v1.0、设备 ID、WS 路径、默认 Policy；
- HQ VLAN10/20/30、IPv4 地址和 Gate 1 ACL 放置原则；
- SW-CORE / SW-ACCESS 型号与 HQ 物理接口；
- Packet Tracer External Network Access / RealWSClient → 真实 FastAPI 实机连通；
- 保存、关闭、重开 `.pkt` 后 RealWSClient 连接可重复。

Final Architecture v2 是后续经项目级决策批准的网络范围扩展，不修改上述软件契约和已验证 HQ Core。

---

## Gate 1：四模块独立运行 — CLOSED-WITH-PLACEHOLDER

### A — Network Owner：PASS

已完成：

- VLAN10/20/30；
- Access 端口；
- LACP EtherChannel / Trunk；
- 三个 SVI + `ip routing`；
- OFFICE DHCP；
- VLAN10/VLAN20 inbound ACL；
- N1/N2/N3 网络验收与证据。

### B — Edge Owner：PASS

已完成真实 PT Local Loop：

```text
TEMP01 A0 → IO-MCU-01 A0
IO-MCU-01 USB0 → EDGE-SBC-01 USB0
EDGE-SBC-01 D0 → FAN01 D0
```

已验证：

```text
30.2 C → TURN_ON  → FAN ON
29.4 C → HOLD     → FAN ON
28.6 C → TURN_OFF → FAN OFF
```

以及 Backend 端口不可达时本地循环仍继续工作。

### D — UI & Integration Owner：PASS

已归档 Dashboard Gate 1 报告和证据，覆盖：

- NORMAL；
- WARNING；
- Edge Offline；
- Reconnect / State Sync 视图。

### A+B Integration：PASS

在 canonical 网络基线中合入 Edge 接线和 Local Loop 后，已回归验证：

- Po1 / Trunk / VLAN10/20/30 正常；
- HQ SVI / routing / ACL 正常；
- OFFICE→ADMIN 允许；
- OFFICE→IOT 仍拒绝；
- ADMIN→EDGE-SBC-01 允许；
- Edge 迟滞控制和 Backend-off autonomy 不受网络整合影响。

### C — Control Plane Owner：PLACEHOLDER

C 的 Owner 专属 Gate 1 证据未在项目进入 Gate 2 前提交。项目不再因此阻塞 G2，但不得把它写成 PASS。

占位报告：`docs/gate1/C_BACKEND_REPORT.md`  
证据占位：`evidence/backend/gate1/README.md`

C 必须在 Gate 5 Freeze 前补齐：

- `/healthz`；
- fake edge → `/ws/edge`；
- `/api/state` 状态更新；
- malformed/unsupported/wrong-version 消息安全拒绝；
- edge disconnect → offline；
- reconnect + state_sync；
- 正式报告和证据。

### Gate 1 管理结论

```text
A PASS
B PASS
C OWNER EVIDENCE PENDING
D PASS
A+B Integration PASS

Scheduling status: CLOSED-WITH-PLACEHOLDER
```

Gate 2 可以开始；**Gate 5 COMPLETE 的前置条件之一是 C placeholder 已清零。**

---

# Gate 2：真实单向数据链路 + Branch/WAN 基础层

## B/C/D 主线验收

目标：

```text
Packet Tracer TEMP01
→ IO-MCU-01
→ EDGE-SBC-01
→ RealWSClient
→ FastAPI
→ Dashboard
```

主验收动作：

1. 保持默认 Policy：AUTO / 30.0 C / hysteresis 1.0 C。
2. PT 温度从约 28 C 调到约 32 C。
3. SBC 本地 FAN 状态按迟滞逻辑变化。
4. SBC 通过 Protocol v1.0 发送真实 `telemetry`；必要时发送 `status`。
5. Backend `/api/state` 更新真实 temperature / fan state。
6. Dashboard 显示约 32 C、WARNING、Fan 状态。
7. Event Stream 出现可解释的 SENSOR / EDGE-AUTO 事件。

**G2 B/C/D PASS：** Dashboard 展示的温度来自真实 Packet Tracer TEMP01，而非 fake edge。

## A 并行网络验收

A 本 Gate 不等待 B/C/D，按 `NETWORK_PLAN.md` 建立 Final Architecture v2 的基础网络：

1. 核对新增物理接口和设备型号。
2. 建立 Branch VLAN40 / VLAN50。
3. 建立 `R-BRANCH G0/1` Router-on-a-Stick。
4. BR-OFFICE 获得 IPv4 DHCP；BR-ADMIN 和 SW-BRANCH 使用冻结管理地址。
5. 配置 HQ Transit、HQ↔ISP、ISP↔Branch、Internet Service LAN 的 IPv4 地址。
6. 只验证相邻节点和 Branch LAN，不急于一次性叠加 OSPF/BGP/NAT/IPv6。
7. 每一步后复测 HQ Gate 1 Core 未被破坏。

**G2 A PASS：** Branch LAN 与 IPv4 WAN Underlay 基础层独立成立，HQ Gate 1 网络回归仍 PASS。

---

# Gate 3：双向策略闭环 + 企业 WAN 业务层

## B/C/D 主线验收

目标：

```text
Dashboard threshold 30→33
→ Backend
→ Edge
→ policy_ack
```

主验收：

1. Dashboard 将阈值从 30 C 改为 33 C，version 严格递增。
2. Backend 只转发合法 Protocol v1.0 Policy。
3. Edge 应用新 Policy 并回 `policy_ack`。
4. 32 C 时 Fan 保持 OFF；34 C 时 Fan ON。
5. Event Stream 区分 `CLOUD-POLICY` 与 `EDGE-AUTO`。

增强验收：Dashboard 手动下发 FAN01 ON/OFF，Edge 返回 `command_ack`，事件源为 `REMOTE-MANUAL`。

## A 并行网络验收

A 本 Gate 完成主要企业互联：

- HQ SW-CORE ↔ R-HQ：OSPF Area 0；
- R-HQ / R-ISP / R-BRANCH：eBGP AS65001 / 65000 / 65002；
- R-HQ 向 HQ OSPF 提供默认出口，不把完整 BGP 表灌入 Core；
- BR-OFFICE → HQ-SERVICE HTTP；
- HQ ADMIN → Branch 管理网可达；
- R-HQ PAT：HQ OFFICE → INTERNET-SERVER；
- INTERNET-SERVER DNS + HTTP；
- `203.0.113.1:80 → 192.168.30.10:80` 静态 TCP/80 映射；
- 业务 ACL 保证 Branch Office 不能获得 HQ IoT / 网络管理权限。

**G3 A PASS：** OSPF/BGP 邻居与路由正确，Branch→HQ 业务、HQ→Internet PAT/DNS/HTTP、静态 HTTP 映射均可解释且可重复。

---

# Gate 4：断云不断控 + IPv6 Overlay / 接入安全

## B/C/D 主线验收

1. 正常连接，确认 Cloud / Edge ONLINE。
2. 停止 Backend；Dashboard 进入失联状态。
3. PT 将温度调到阈值之上，Fan 仍由 SBC 本地开启。
4. 将温度降到 `threshold - hysteresis` 以下，Fan 正确关闭。
5. 恢复 Backend。
6. Edge 自动重连并发送 `hello` + `state_sync`。
7. Dashboard 恢复真实 temperature、fan_state、Policy Version。

这是项目核心创新证据，必须保留连续录屏或顺序明确的截图。

## A 并行网络验收

完成课程网络能力收口：

- HQ OFFICE：IPv6 SLAAC；
- BR-OFFICE：DHCPv6；
- 管理域：Static IPv6；
- ISP 保持 IPv4-only；
- R-HQ ↔ R-BRANCH IPv6-over-IPv4 Tunnel；
- IPv6 静态路由实现 BR-ADMIN → HQ MANAGEMENT；
- HQ ADMIN 远程管理 R-BRANCH / SW-BRANCH，普通 Office 被拒绝；
- SW-ACCESS Fa0/1 sticky MAC / Port Security，非法终端触发 Violation；
- 对 HQ / Branch / Internet 权限矩阵进行最终 ACL 回归。

**G4 A PASS：** IPv6 Overlay、远程管理、Port Security 和全部关键业务流均通过，同时 Gate 1 HQ Core 回归无退化。

---

# Gate 5：Final Freeze 与三轮彩排

Gate 5 只允许：

- 修 Bug；
- 改善必要 UI 可读性；
- 补日志 / 错误处理；
- 补报告、截图、AI 协作记录；
- 修复 canonical `.pkt` 中已经识别的问题。

不得再新增协议、设备或业务场景。

## Freeze 前硬条件

- [ ] C Gate 1 placeholder 已由真实 C Owner 报告和证据替换。
- [ ] Final canonical `.pkt` 已包含 Final Architecture v2 的最终网络配置。
- [ ] Protocol v1.0 无未记录漂移。
- [ ] HQ Gate 1 回归仍 PASS。
- [ ] G2 Telemetry 真链路 PASS。
- [ ] G3 Policy 真闭环 PASS。
- [ ] G4 Cloud-off autonomy + reconnect PASS。
- [ ] A 的 OSPF/BGP/NAT/DNS/HTTP/IPv6 Tunnel/Port Security 验收 PASS。
- [ ] 完整流程连续三轮成功。

---

# 最终功能测试矩阵

| ID | 功能 | 操作 | 预期 | Owner |
|---|---|---|---|---|
| N1 | HQ VLAN / SVI | 允许域跨 VLAN 访问 | 可达 | A |
| N2 | HQ ACL | OFFICE → IOT | 拒绝 | A |
| N3 | EtherChannel | 查看 Po1 / Trunk / members | SU / bundled / VLAN 10,20,30 | A |
| N4 | Branch VLSM / ROAS | BR-OFFICE、BR-ADMIN 到各自网关 | 正确 | A |
| N5 | OSPF | SW-CORE ↔ R-HQ | FULL / HQ routes 正确 | A |
| N6 | eBGP | R-HQ ↔ R-ISP ↔ R-BRANCH | Established / prefixes 正确 | A |
| N7 | Branch Business | BR-OFFICE → HQ-SERVICE HTTP | 允许 | A |
| N8 | Branch Isolation | BR-OFFICE → HQ IOT / 管理设备 | 拒绝 | A |
| N9 | PAT | HQ OFFICE → Internet | 成功且有 NAT translation | A |
| N10 | DNS/HTTP | HQ OFFICE 访问 `www.edgecampus.net` | DNS + HTTP 成功 | A |
| N11 | Static Port Map | 外部节点 → `203.0.113.1:80` | 映射到 HQ-SERVICE | A |
| N12 | IPv6 modes | SLAAC / DHCPv6 / Static | 各模式按规划获得地址 | A |
| N13 | IPv6 Tunnel | BR-ADMIN → HQ-SERVICE IPv6 | 通过 IPv4-only ISP 可达 | A |
| N14 | Remote Admin | HQ ADMIN → Branch devices | 允许；普通 Office 拒绝 | A |
| N15 | Port Security | 替换非法 MAC | violation 增长/阻断 | A |
| E1 | Edge Local Loop | 调温跨阈值 | Fan 正确动作 | B |
| C1 | Real Telemetry | PT 温度变化 | Backend state 更新 | B+C |
| D1 | Dashboard | 温度跨阈值 | 页面 WARNING / Fan / event 正确 | C+D |
| P1 | Policy | 30→33 | Edge APPLIED + ACK | B+C+D |
| P2 | Manual Command | FAN ON/OFF | command_ack / status 正确 | B+C+D |
| R1 | Cloud Failure | 停 Backend 后调温 | Local Loop 不停止 | B |
| R2 | Reconnect | 恢复 Backend | hello + state_sync / UI 恢复 | B+C+D |

---

# 课程五次实验覆盖核对

| 实验 | Final Architecture v2 对应功能 |
|---|---|
| 实验1 | VLSM、DHCP、SLAAC、DHCPv6、Static IPv6、IPv6 static route、远程管理 |
| 实验2 | VLAN、Trunk、EtherChannel、SVI、Router-on-a-Stick |
| 实验3 | ACL、NAT/PAT、TCP/80 映射、DNS、HTTP |
| 实验4 | OSPF、eBGP、路由传播 |
| 实验5 | Sticky MAC / Port Security、IPv6-over-IPv4 Tunnel |

报告主体按业务架构写，上表只用于证明课程覆盖，避免五个实验机械拼接。

---

# 证据命名

继续使用：

```text
G<Gate>-<Owner>-<序号>-<内容>-<结果>.png
```

示例：

```text
G2-B-01-real-telemetry-pass.png
G2-A-01-branch-roas-pass.png
G3-A-03-bgp-branch-hq-pass.png
G3-B-02-policy-ack-pass.png
G4-A-02-ipv6-tunnel-pass.png
G4-B-03-cloud-offline-edge-auto-pass.png
```
