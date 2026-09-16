# EdgeCampus 当前阶段指挥文件

> 当前 Gate：**Gate 3 — Policy Loop + WAN Business**  
> 状态：**IN PROGRESS**  
> 发布日期：2026-09-16  
> 架构基线：**Final Architecture v2 / Gate 2 Integrated Baseline**  
> 总原则：**A 推进 OSPF/eBGP/NAT/业务链；B/C/D 打通真实 Policy / Command 双向闭环；任何人不得破坏 Gate 2 已验证能力。**

---

## 0. 开工前必须先读

1. `docs/AI_CONTEXT.md`
2. `docs/CURRENT_GATE.md`
3. `docs/CONTRIBUTING.md`
4. `docs/ARCHITECTURE.md`
5. `docs/PROTOCOL.md`
6. `docs/NETWORK_PLAN.md`
7. `docs/ACCEPTANCE.md`

---

## 1. 已关闭阶段

### Gate 0 — COMPLETE

软件契约、HQ Core 规划、PT → Real Host RealWSClient 通道已冻结并实测。

### Gate 1 — CLOSED-WITH-PENDING-STABILITY

- A Network：PASS。
- B Edge：PASS。
- D UI：PASS。
- A+B canonical integration：PASS。
- C Control Plane：核心独立验收已提交，`/healthz`、fake edge、`/api/state`、AUTO event 已有证据；仍缺 malformed-message / offline / reconnect+state_sync 三项稳定性补证。

C 的三项遗留不阻塞 Gate 3，但必须在 Gate 5 Freeze 前清零。不得把 C Gate 1 写成完整 PASS。

### Gate 2 — COMPLETE

Gate 2 两条并行轨道均已通过：

```text
软件 / IoT：
TEMP01 → MCU → SBC → RealWSClient → Backend → Dashboard

网络：
HQ Core → R-HQ → R-ISP → R-BRANCH → SW-BRANCH
                    |
             INTERNET-SERVER
```

已验证：

- A：Branch VLAN40/50、ROAS、DHCP/管理地址、IPv4 WAN Underlay、HQ Gate1 regression。
- B：真实 TEMP01 Telemetry、Local AUTO、FAN Status、Heartbeat，Cloud 不作为本地控制前置条件。
- C：真实 PT Telemetry 更新 Backend `/api/state`，无协议漂移。
- D：真实 PT 正常/告警状态进入 Dashboard；约 27.9 C 为 NORMAL/FAN OFF，约 34.1 C 为 WARNING/FAN ON。
- B+C+D：真实 `TEMP01 → Dashboard` 端到端链路 PASS。

Gate 2 集成记录见 `docs/gate2/INTEGRATION_REPORT.md`。

---

## 2. 不可破坏基线

### 2.1 HQ Gate 1 Core

```text
VLAN10 OFFICE      192.168.10.0/24  GW 192.168.10.1
VLAN20 IOT         192.168.20.0/24  GW 192.168.20.1
VLAN30 MANAGEMENT  192.168.30.0/24  GW 192.168.30.1

EDGE-SBC-01 = 192.168.20.10
BACKEND-STUB = 192.168.30.10
ADMIN-PC = 192.168.30.20
```

HQ 既有 EtherChannel、Trunk、SVI、DHCP、ACL 和 IoT 接线不得为 Gate 3 重构。

### 2.2 Gate 2 Network Foundation

```text
SW-CORE Gi1/0/24  10.255.0.1/30  ↔ R-HQ G0/0 10.255.0.2/30
R-HQ G0/1          203.0.113.1/30 ↔ R-ISP G0/0 203.0.113.2/30
R-ISP G0/1         198.51.100.1/30↔ R-BRANCH G0/0 198.51.100.2/30
R-ISP G0/2         192.0.2.1/24    ↔ INTERNET-SERVER 192.0.2.10/24

VLAN40 BR-OFFICE   172.16.40.0/26  GW 172.16.40.1
VLAN50 BR-MGMT     172.16.40.64/27 GW 172.16.40.65
SW-BRANCH VLAN50   172.16.40.66/27
BR-ADMIN-PC        172.16.40.70/27
```

### 2.3 Gate 2 Edge Foundation

```text
TEMP01 A0 → IO-MCU-01 A0
IO-MCU-01 USB0 → EDGE-SBC-01 USB0
EDGE-SBC-01 D0 → FAN01 D0
```

真实 Telemetry、Status、Heartbeat 与 Local AUTO 已验证；Gate 3 只能增量加入下行 Policy/Command。

---

## 3. Public Contract 继续冻结

- Protocol `1.0`
- Edge WS `/ws/edge`
- Dashboard WS `/ws/dashboard`
- `EDGE-SBC-01` / `TEMP01` / `FAN01`
- 温度单位 `C`
- Policy：`policy_id` / `version` / `mode` / `threshold_c` / `hysteresis_c`
- 默认 Policy：AUTO / 30.0 C / hysteresis 1.0 C / version 1
- FAN 协议状态只用 `ON/OFF`

本 Gate 不修改 `docs/PROTOCOL.md`。

### 真实性边界

Packet Tracer 的 VLAN / ACL / Routing / OSPF / BGP / NAT / Tunnel 是模拟企业数据平面；真实 FastAPI 控制通道仍是：

```text
EDGE-SBC-01
  ↓ External Network Access / RealWSClient
ws://127.0.0.1:8000/ws/edge
  ↓
Real FastAPI
```

禁止表述真实 WebSocket 经过 R-HQ、R-ISP、BGP、NAT 或 PT VLAN20/30。

---

# 4. Gate 3 Track A — Network Owner

目标：在 Gate 2 Underlay 上建立企业动态路由、跨站业务与 Internet 出口。

按层实施，每层完成后先验证再进入下一层：

1. **HQ OSPF Area 0**：仅 SW-CORE ↔ R-HQ；确认邻居 FULL，R-HQ 学到 HQ VLAN10/20/30，SW-CORE 获得所需出口路由。
2. **WAN eBGP**：R-HQ AS65001 ↔ R-ISP AS65000 ↔ R-BRANCH AS65002；发布冻结前缀，禁止无解释的全量 redistribution。
3. **Branch Business**：验证 `BR-OFFICE-PC → HQ-SERVICE / BACKEND-STUB` 的 IPv4 企业 WAN 业务流。
4. **HQ Internet PAT**：R-HQ G0/0 inside、G0/1 outside；默认只为 HQ OFFICE 提供 PAT；IOT 不做通用 Internet NAT；站点间业务必须避免被 NAT。
5. **DNS / HTTP**：INTERNET-SERVER 提供 DNS + HTTP，验证 HQ OFFICE 通过 PAT 访问。
6. **Static TCP/80 Mapping**：按冻结设计验证 `203.0.113.1:80 → 192.168.30.10:80`，若 PT 行为与模板不同必须实测记录。
7. **WAN / Branch ACL**：路由先通再施加业务权限，不能用 ACL 掩盖路由错误。
8. **Regression**：每层后复查 HQ EtherChannel/Trunk/VLAN/SVI/ACL、Branch VLAN/ROAS/DHCP 和新增业务流。

Gate 3 不做 IPv6 Tunnel、Port Security、SLAAC/DHCPv6 或中央远程管理；这些属于 Gate 4。

---

# 5. Gate 3 Track B — Edge Owner

目标：在已验证的 Gate 2 控制器上加入真实 Cloud → Edge 下行。

优先顺序：

1. 单独验证 Packet Tracer 9.0.1 `RealWSClient` 能稳定接收服务器下发消息；callback 内禁止阻塞/`delay()`。
2. 接收并解析 Protocol v1 `policy`。
3. Policy `version` 必须严格递增；合法策略更新运行时 `mode/threshold_c/hysteresis_c/version`。
4. Local AUTO 必须使用当前运行时策略，不再只依赖硬编码默认值。
5. 返回合法 `policy_ack`。
6. 接收 `command` 控制 `FAN01`，保持 AUTO/MANUAL 语义清晰，返回 `command_ack`；远程手动状态来源使用 `REMOTE-MANUAL`。
7. Local Loop 仍优先于 Cloud，新增接收逻辑不得破坏 Gate 2 Telemetry/Status/Heartbeat。

核心 Policy 验收：

```text
Dashboard: threshold 30 → 33, version 1 → 2
Edge ACK: APPLIED
真实温度 32 C → FAN OFF
真实温度 34 C → FAN ON
```

正式 Cloud-off/reconnect/state_sync 故障恢复留 Gate 4。

---

# 6. Gate 3 Track C — Control Plane Owner

1. 保持 Protocol v1 不变。
2. 将 Dashboard 的合法 `policy` / `command` 转发给当前真实 Edge WebSocket。
3. 接收 `policy_ack` / `command_ack`，更新事件与 Dashboard snapshot。
4. Edge 不在线时维持 `EDGE_OFFLINE` 语义。
5. fake edge 仍可作为独立开发替身。
6. 可顺手补 Gate 1 三项稳定性欠账，但不得用 Gate 3 成功自动替代它们。

---

# 7. Gate 3 Track D — UI & Integration Owner

1. 使用既有 Policy 表单真实发送 Policy，不创造新协议字段。
2. 显示新 threshold、policy version、ACK/result 与可解释事件。
3. 配合 B/C 完成真实 Edge Policy 闭环。
4. 完成真实 FAN Command 演示与 ACK（若按本 Gate 全量验收）。
5. 不做主题、登录页、动画等非验收功能扩张。

---

# 8. Gate 3 Definition of Done

- [ ] A：OSPF 邻居与 HQ 路由学习 PASS。
- [ ] A：eBGP 两段邻接与路由传播 PASS。
- [ ] A：`BR-OFFICE → HQ-SERVICE` PASS。
- [ ] A：HQ OFFICE → PAT → Internet DNS/HTTP PASS。
- [ ] A：Static TCP/80 mapping 与业务 ACL 按设计完成并留证。
- [ ] B+C+D：Dashboard Policy → Backend → 真实 Edge → `policy_ack` → Dashboard PASS。
- [ ] Policy 由 30 C / v1 改为 33 C / v2 后，32 C FAN OFF、34 C FAN ON。
- [ ] B+C+D：真实 FAN Command → `command_ack` PASS。
- [ ] Gate 2 Telemetry、Local Loop、Dashboard 与网络基础回归无退化。
- [ ] 所有新增阶段报告与 evidence 完整。
- [ ] 无 Protocol drift；真实性边界保持。

满足后才正式关闭 Gate 3。
