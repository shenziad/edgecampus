# Gate 与验收标准 — Final Architecture v2

## 最新项目收尾结论（2026-09-19）

总状态 **验收完成，报告准备中**。下方 N1–N15/E1/C1/D1/P1/P2/R1/R2 保留为已完成验收所依据的标准；历史 G5 NOT STARTED 和 EVIDENCE PENDING 是早期阶段记录，不代表当前项目仍待验收。21张G4网络原图已归档到当前分支；后续指定截图、配置导出和展示彩排均用于最终报告。

新增 NOC 验收：真实 NC 清单/IP/type/collectionStatus 与 Dashboard一致；Managed→ONLINE；OSPF/BGP/Tunnel NOT COLLECTED；失联不回退模拟/不保留陈旧在线；Network Failure禁用/409；Security与Branch明确SIMULATED；Campus thermal保留Edge ACK，Network/Security展示不写IOS；Cloud按钮实际中断WS并等待真实state_sync。完整证据范围见 [最终素材总清单](FINAL_REPORT_SCREENSHOT_CHECKLIST.md)和[四人逐张操作清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)。

## 总原则

```text
G0 Contract Freeze
→ G1 四模块独立运行
→ G2 单向真实数据链路 + WAN Foundation
→ G3 双向策略闭环 + WAN Business
→ G4 断云自治恢复 + IPv6/Security
→ G5 Freeze + 三轮彩排
```

多园区网络由 A 在 G2–G4 与 B/C/D 软件主线并行推进。Protocol v1.0 不变；HQ Gate1 Core 不重构。

---

## Gate 0 — COMPLETE

已完成：Protocol v1.0、设备 ID、WS 路径、默认 Policy、HQ VLAN/IP/端口、External Network Access / RealWSClient → 真实 FastAPI，并验证保存重开 `.pkt` 后仍可连接。

---

## Gate 1 — CLOSED（稳定性欠账于 Gate4 清零）

### A Network — PASS

VLAN10/20/30、Access、LACP EtherChannel/Trunk、SVI/IP routing、OFFICE DHCP、HQ ACL、N1/N2/N3 均有实测证据。

### B Edge — PASS

```text
TEMP01 → IO-MCU-01 → EDGE-SBC-01 → FAN01
```

迟滞与 Backend-off 本地自治已验证。

### D Dashboard — PASS

NORMAL、WARNING、Edge Offline、Reconnect/State Sync 视图和 Dashboard contract tests 已归档。

### A+B Integration — PASS

canonical Gate1 基线中网络与 Edge Local Loop 回归无退化。

### C Control Plane — PASS（稳定性证据见 Gate4 C 报告）

已举证：`/healthz`、fake edge `/ws/edge`、`/api/state`、telemetry/fan events、单元测试。

历史三项欠账已于 Gate4 补齐真实证据（见 `docs/gate4/C_CONTROL_PLANE_REPORT.md`）：

- malformed / unsupported / wrong-version 安全拒绝；
- Edge disconnect → offline；
- reconnect + `state_sync`。

三项对应 G4-C-01/02/03/04/05；清零不代表 Global Gate4 已关闭。

---

## Gate 2 — COMPLETE

### B/C/D：真实单向数据链路 — PASS

```text
Packet Tracer TEMP01
→ IO-MCU-01
→ EDGE-SBC-01
→ External Network Access / RealWSClient
→ FastAPI
→ Dashboard
```

通过标准已经满足：

- Telemetry 来自真实 PT TEMP01，而非 fake edge；
- Backend `/api/state` 反映真实温度/FAN；
- Dashboard 实测约 27.9 C NORMAL/FAN OFF、约 34.1 C WARNING/FAN ON；
- Event Stream 可见 SENSOR / EDGE-AUTO；
- Local Loop 不以 Cloud 为前置条件；
- Protocol v1.0 无漂移。

### A：Branch/WAN Foundation — PASS

已完成并验证：

- Branch VLAN40/50；
- R-BRANCH Router-on-a-Stick；
- BR-OFFICE DHCP；
- BR-ADMIN / SW-BRANCH 管理地址；
- HQ Transit、HQ↔ISP、ISP↔Branch、Internet LAN IPv4 地址；
- 四段相邻三层链路可达；
- HQ Gate1 Core regression PASS。

集成记录：`docs/gate2/INTEGRATION_REPORT.md`。

---

# Gate 3 — EVIDENCE PENDING

2026-09-17 当前审计：Gate4 已实现并有用户现场实测确认；B 离线 ON、真实 reconnect/hello/state_sync、Backend 恢复与 D 失联有截图，C 三项 Gate1 stability debt 清零。A N12-N15 用户确认已测，截图本次跳过后补；离线 OFF/Attributes、恢复后 Dashboard、G4 N1-N11 全量回归及 G3 修复后 ACK/完整 events 仍需归档。Gate4 为 IMPLEMENTED / USER-TESTED / EVIDENCE PENDING，未正式 COMPLETE；Gate5 NOT STARTED。

## B/C/D：真实双向 Policy / Command 闭环

### Policy 主验收

```text
Dashboard threshold 30 → 33, version 1 → 2
→ Backend
→ Real Edge
→ policy_ack = APPLIED
→ Dashboard
```

必须证明：

1. Dashboard 发出的 Policy 符合 Protocol v1.0。
2. Backend 只向在线真实 Edge 转发合法 Policy。
3. Edge 仅接受严格递增的 Policy version，并更新运行时 AUTO 参数。
4. `policy_ack` 返回并进入 Dashboard/Event Stream。
5. 新策略下真实 32 C → FAN OFF；真实 34 C → FAN ON。
6. 事件能区分 `CLOUD-POLICY` 与 `EDGE-AUTO`。

### Command 主验收

Dashboard 向 `FAN01` 发 ON/OFF → Backend → Real Edge → 物理 FAN → `command_ack`。手动状态来源使用 `REMOTE-MANUAL`，AUTO/MANUAL 语义必须明确。

### 软件 Gate3 PASS

> 真实 Policy 和 Command 都能从 Dashboard 到达真实 PT Edge，并有合法 ACK 与可解释状态回传；Gate2 Telemetry/Local Loop 不退化。

## A：企业 WAN 业务层

按层验收：

1. **OSPF Area0**：SW-CORE ↔ R-HQ 邻居 FULL；R-HQ 学到 HQ VLAN10/20/30；Core 获得设计要求的出口路由。
2. **eBGP**：R-HQ AS65001 ↔ R-ISP AS65000 ↔ R-BRANCH AS65002 邻居 Established；业务前缀传播正确。
3. **Branch Business**：最终 HTTP 入口为 `http://203.0.113.1` → static TCP/80 → HQ-SERVICE；私网 `ping 192.168.30.10` 验证三层。静态映射共存时私网直连 HTTP FAIL，历史直连页面不作为最终 PASS，详见 G4 A 报告。
4. **HQ PAT**：HQ OFFICE 经 R-HQ PAT 访问 INTERNET-SERVER；IOT 不获得通用 Internet NAT；站点间流量不被错误 NAT。
5. **DNS/HTTP**：INTERNET-SERVER 提供 DNS/HTTP，HQ OFFICE 域名访问 PASS。
6. **Static TCP/80**：`203.0.113.1:80 → 192.168.30.10:80` 按 PT 实测行为完成并留证。
7. **Business ACL**：Branch Office 不得取得 HQ IoT / 网络管理权限；ACL 必须在基础路由已通后叠加。
8. 每层后做 HQ/Branch regression。

### A Gate3 PASS

> OSPF/eBGP 邻居与路由正确，Branch→HQ 业务、HQ→Internet PAT/DNS/HTTP、Static TCP/80 与业务隔离均可重复验证，且 G2 Foundation 无退化。

---

# Gate 4 — IMPLEMENTED / USER-TESTED / EVIDENCE PENDING

## B/C/D：断云不断控 + 恢复同步

1. 正常连接并记录真实状态。
2. 停止 Backend。
3. Dashboard 显示失联；Edge 本地温控仍按最后有效 Policy 工作。
4. 温度上升/下降跨迟滞阈值时 FAN 仍正确动作。
5. 恢复 Backend。
6. Edge 自动重连并发送 `hello` + `state_sync`。
7. Dashboard 恢复真实 temperature、fan_state、Policy Version。

## A：IPv6 Overlay + Access Security

- HQ OFFICE：SLAAC；
- BR-OFFICE：DHCPv6；
- 管理域：Static IPv6；
- ISP 保持 IPv4-only；
- R-HQ ↔ R-BRANCH IPv6-over-IPv4 Tunnel；
- IPv6 静态路由：BR-ADMIN → HQ MANAGEMENT；
- HQ ADMIN → Branch devices 中央远程管理；普通 Office 被拒绝；
- SW-ACCESS Fa0/1 sticky MAC / Port Security；
- 最终 ACL / 业务矩阵回归。

---

# Gate 5 — NOT STARTED

只允许修 Bug、必要 UI 可读性、日志/错误处理、报告/证据与 final canonical `.pkt` 修正，不再增加协议、设备或业务场景。

Freeze 前硬条件：

- [x] C Gate1 三项稳定性欠账清零（G4 C 报告与真实截图）。
- [ ] Final canonical `.pkt` 完成。
- [ ] Protocol v1.0 无漂移。
- [ ] HQ Core regression PASS。
- [x] G2 真实 Telemetry + WAN Foundation PASS。
- [ ] G3 Policy/Command + WAN Business PASS。
- [ ] G4 Outage Recovery + IPv6/Security PASS。
- [ ] 完整流程连续三轮成功。

---

# 最终功能测试矩阵

| ID | 功能 | 预期 | Owner |
|---|---|---|---|
| N1 | HQ VLAN / SVI | 允许域可达 | A |
| N2 | HQ ACL OFFICE→IOT | 拒绝 | A |
| N3 | EtherChannel | Po1 SU / members bundled | A |
| N4 | Branch VLSM / ROAS | 两 VLAN 网关正确 | A |
| N5 | OSPF | FULL / HQ routes 正确 | A |
| N6 | eBGP | Established / prefixes 正确 | A |
| N7 | Branch→HQ Business | HTTP 成功 | A |
| N8 | Branch Isolation | HQ IOT/MGMT 被拒绝 | A |
| N9 | PAT | HQ OFFICE → Internet 成功 | A |
| N10 | DNS/HTTP | 域名访问成功 | A |
| N11 | Static Port Map | 公网 TCP/80 映射 HQ-SERVICE | A |
| N12 | IPv6 modes | SLAAC/DHCPv6/Static 正确 | A |
| N13 | IPv6 Tunnel | BR-ADMIN → HQ MANAGEMENT | A |
| N14 | Remote Admin | HQ ADMIN 允许，普通 Office 拒绝 | A |
| N15 | Port Security | 非法 MAC violation / 阻断 | A |
| E1 | Local Loop | 跨阈值 FAN 正确 | B |
| C1 | Real Telemetry | Backend state 更新 | B+C |
| D1 | Dashboard | NORMAL/WARNING/FAN/Event 正确 | C+D |
| P1 | Policy | 30→33、ACK、32 OFF/34 ON | B+C+D |
| P2 | Command | FAN ON/OFF + ACK | B+C+D |
| R1 | Cloud Failure | Local Loop 继续 | B |
| R2 | Reconnect | hello + state_sync + UI 恢复 | B+C+D |

---

# 五次实验覆盖

| 实验 | Final Architecture v2 对应 |
|---|---|
| 实验1 | VLSM、DHCP、SLAAC、DHCPv6、Static IPv6、IPv6 route、远程管理 |
| 实验2 | VLAN、Trunk、EtherChannel、SVI、ROAS |
| 实验3 | ACL、NAT/PAT、TCP/80、DNS、HTTP |
| 实验4 | OSPF、eBGP、路由传播 |
| 实验5 | Sticky MAC / Port Security、IPv6-over-IPv4 Tunnel |

证据命名继续使用：`G<Gate>-<Owner>-<序号>-<内容>-<结果>.png`。

## Gate4 当前归档索引（2026-09-17）

报告见 `gate4/`：A/B/C/D/BCD 报告、EVIDENCE_INDEX、VALIDATION_REPORT。Protocol 1.0 与冻结网络规划未改变。
