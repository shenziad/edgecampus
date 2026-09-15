# EdgeCampus 当前阶段指挥文件

> 当前 Gate：**Gate 2 — 真实单向 Telemetry + 多园区网络基础层**  
> 状态：**IN PROGRESS**  
> 发布日期：2026-09-15  
> 架构基线：**Final Architecture v2**  
> 总原则：**B/C/D 打通真实 TEMP→Dashboard；A 并行搭建 Branch LAN + IPv4 WAN Underlay；任何人不得破坏 Gate 1 HQ Core。**

---

## 0. 所有人 / 所有 AI 开工前必须先读

按顺序：

1. `docs/AI_CONTEXT.md`
2. `docs/CURRENT_GATE.md`
3. `docs/CONTRIBUTING.md`
4. `docs/ARCHITECTURE.md`
5. `docs/PROTOCOL.md`
6. `docs/NETWORK_PLAN.md`
7. `docs/ACCEPTANCE.md`

### Gate 1 状态

Gate 1 已按项目管理决策进入：

```text
CLOSED-WITH-PLACEHOLDER
```

- A：PASS。
- B：PASS。
- D：PASS。
- A+B canonical 集成与回归：PASS。
- C：核心验收句已举证（见 `docs/gate1/C_BACKEND_REPORT.md` 与 `evidence/backend/G1-01`–`G1-07`）。invalid-message / offline / reconnect 仍 PENDING，**不得写成完整 PASS**，Gate 5 前必须补齐。Gate 2 真 PT 遥测已进入 Backend（`evidence/backend/G2-C-01`–`G2-C-04`）。

因此 Gate 2 可以推进。不得把 C 稳定性三项未完成写成“C Gate 1 完整 PASS”。

---

## 1. Final Architecture v2 冻结原则

### 1.1 HQ Gate 1 Core 不得破坏

```text
VLAN10 OFFICE      192.168.10.0/24  GW 192.168.10.1
VLAN20 IOT         192.168.20.0/24  GW 192.168.20.1
VLAN30 MANAGEMENT  192.168.30.0/24  GW 192.168.30.1

EDGE-SBC-01 = 192.168.20.10
BACKEND-STUB = 192.168.30.10
ADMIN-PC = 192.168.30.20
```

HQ 已验证接口：

```text
SW-CORE Gi1/0/1 ↔ SW-ACCESS Gi0/1
SW-CORE Gi1/0/2 ↔ SW-ACCESS Gi0/2
SW-ACCESS Fa0/1 → OFFICE-PC
SW-ACCESS Fa0/2 → EDGE-SBC-01
SW-ACCESS Fa0/3 → ADMIN-PC
SW-ACCESS Fa0/4 → BACKEND-STUB
```

Edge 已验证接线：

```text
TEMP01 A0 → IO-MCU-01 A0
IO-MCU-01 USB0 → EDGE-SBC-01 USB0
EDGE-SBC-01 D0 → FAN01 D0
```

### 1.2 软件 Public Contract 完全冻结

- Protocol：`1.0`
- Edge WS：`/ws/edge`
- Dashboard WS：`/ws/dashboard`
- IDs：`EDGE-SBC-01`、`TEMP01`、`FAN01`
- 温度单位：`C`
- Policy fields：`policy_id`、`version`、`mode`、`threshold_c`、`hysteresis_c`
- 默认 Policy：AUTO / threshold 30.0 C / hysteresis 1.0 C / version 1

本 Gate 不修改 `docs/PROTOCOL.md`。

### 1.3 真实性边界

```text
Packet Tracer Data Plane
VLAN / ACL / Routing / OSPF / BGP / NAT / Tunnel
```

与：

```text
EDGE-SBC-01
  ↓ External Network Access / RealWSClient
ws://127.0.0.1:8000/ws/edge
  ↓
Real FastAPI
```

是两条不同路径。

**禁止表述真实 WebSocket 经过 R-HQ、R-ISP、BGP、NAT 或 VLAN20/30。**

---

# 2. Gate 2 共同目标

Gate 2 完成时，同时得到两项独立成果：

```text
软件 / IoT 主线：
TEMP01 → MCU → SBC → RealWSClient → Backend → Dashboard

网络扩展线：
HQ Core → R-HQ → R-ISP → R-BRANCH → SW-BRANCH
                    |
             INTERNET-SERVER
```

本 Gate **不要求**：

- Dashboard Policy 已真实下发 PT Edge（Gate 3）；
- OSPF/BGP/NAT 已全部配完（A 在 Gate 3 完成）；
- IPv6 Tunnel / Port Security 最终验收（Gate 4）；
- Cloud-off + reconnect 正式整套演示（Gate 4）。

---

# 3. A — Network Owner

## 本 Gate 目标

在不修改 HQ Gate 1 核心配置的情况下，为 Final Architecture v2 建立 **Branch LAN + IPv4 WAN Underlay**。

### 3.1 先做 Physical Topology Check

新增接口必须与 `docs/NETWORK_PLAN.md` 一致：

```text
SW-CORE Gi1/0/24 ↔ R-HQ G0/0
R-HQ G0/1        ↔ R-ISP G0/0
R-ISP G0/1       ↔ R-BRANCH G0/0
R-ISP G0/2       ↔ INTERNET-SERVER Fa0
R-BRANCH G0/1    ↔ SW-BRANCH Gi0/1
SW-BRANCH Fa0/1  ↔ BR-OFFICE-PC Fa0
SW-BRANCH Fa0/2  ↔ BR-ADMIN-PC Fa0
```

设备建议：R-HQ / R-ISP / R-BRANCH 使用 2911；SW-BRANCH 使用 2960-24TT。

不要静默换口。如果当前 `.pkt` 接口与文档不同，先报告并修正再配置。

### 3.2 建立 Branch LAN

冻结：

```text
VLAN40 BR-OFFICE  172.16.40.0/26  GW 172.16.40.1
VLAN50 BR-MGMT    172.16.40.64/27 GW 172.16.40.65
```

完成：

- SW-BRANCH VLAN40 / VLAN50；
- `Gi0/1` trunk；
- `Fa0/1` access VLAN40；
- `Fa0/2` access VLAN50；
- R-BRANCH `G0/1.40` / `G0/1.50` Router-on-a-Stick；
- BR-OFFICE IPv4 DHCP；
- `SW-BRANCH VLAN50 = 172.16.40.66/27`；
- `BR-ADMIN-PC = 172.16.40.70/27`，GW `172.16.40.65`。

### 3.3 建立 IPv4 Underlay

```text
HQ Transit
SW-CORE Gi1/0/24  10.255.0.1/30
R-HQ G0/0          10.255.0.2/30

HQ ↔ ISP
R-HQ G0/1          203.0.113.1/30
R-ISP G0/0         203.0.113.2/30

ISP ↔ Branch
R-ISP G0/1         198.51.100.1/30
R-BRANCH G0/0      198.51.100.2/30

Internet LAN
R-ISP G0/2         192.0.2.1/24
INTERNET-SERVER    192.0.2.10/24 GW 192.0.2.1
```

本 Gate 先验证**相邻三层节点**，不要一上来叠加 BGP/NAT/IPv6。

### 3.4 Gate 1 Regression

每次新增网络阶段后至少复查：

```text
show etherchannel summary
show interfaces trunk
show vlan brief
show ip interface brief
show access-lists
```

并验证：

```text
OFFICE → ADMIN      PASS
OFFICE → IOT        DENY（预期）
ADMIN  → EDGE-SBC   PASS
```

### A Gate 2 通过标准

> Branch VLAN40/50 + Router-on-a-Stick + DHCP/管理地址正常；新增四个 IPv4 三层网段相邻可达；HQ Gate 1 Core 无回归。

### A 交付物

- 更新 canonical `.pkt`；
- 更新 `packet_tracer/CONFIG_LOG.md`；
- Gate 2 A 阶段报告；
- 关键截图：Branch VLAN/Trunk、ROAS、DHCP、相邻 WAN ping、HQ regression。

---

# 4. B — Edge Owner

## 本 Gate 目标

把 Gate 1 已经可靠运行的 PT Local Loop 增量升级为真实 Telemetry Source。

### 必须保留

```text
TEMP01 → MCU → SBC → FAN01
```

Cloud 连接、发送 JSON、重连等逻辑不得阻塞本地温控循环。

### 需要完成

1. SBC 从 USB 继续读取真实 MCU 温度。
2. 保留本地迟滞 AUTO 控制。
3. 使用 Gate 0 已验证的 `RealWSClient` 连接 `/ws/edge`。
4. 按 Protocol v1.0 发送真实 `telemetry`：

```text
type = telemetry
edge_id = EDGE-SBC-01
device_id = TEMP01
metric = temperature
unit = C
```

5. Fan 状态变化时发送合法 `status`，source 为 `EDGE-AUTO`。
6. 必要的 hello / heartbeat 可以复用已有协议语义。
7. Cloud 不可达时继续本地控制；连接失败不能让 SBC 主循环挂死。

### B Gate 2 通过标准

> Dashboard 最终看到的温度来自真实 PT TEMP01；停止/未启动 Backend 时，Local Loop 仍不受影响。

### B 禁止事项

- 不改温度单位为 `℃`；
- 不改 device ID；
- 不把 Fan PT 物理值 `2` 直接传成协议状态；协议仍用 `ON/OFF`；
- 不为了 WebSocket 重写 Gate 1 本地控制逻辑。

---

# 5. C — Control Plane Owner

## 本 Gate 两个任务

### 任务 A：不阻塞开发地补齐 Gate 1 占位符

参见：`docs/gate1/C_BACKEND_REPORT.md`。

核心句（healthz / fake edge / `/api/state` 遥测）已举证。仍须补：invalid message、offline、reconnect/state_sync。

### 任务 B：支持真实 PT Telemetry

现有 Backend 设计原则不变：

- `/ws/edge` 校验 Protocol v1.0；
- Telemetry 更新 SystemState；
- Status 更新 Fan 实际状态；
- `/api/state` 提供当前 snapshot；
- `/ws/dashboard` 广播状态；
- 事件日志来源清晰；
- malformed 数据不能使 Backend 崩溃。

本 Gate 不需要 C 新增数据库、MQ、认证或新 API。

2026-09-16 已验证：PT TEMP01 ≈32 C 经 RealWSClient 进入 `/api/state`（事件 31.8 C / SENSOR；SBC 同时 FAN ON）。证据：`evidence/backend/G2-C-01`–`G2-C-04`。

### C Gate 2 通过标准

> 收到真实 PT SBC Telemetry 后，`/api/state` 和 Dashboard snapshot 都反映真实 TEMP01 值，并且 fake edge 开发路径仍可继续使用。

C 段 `/api/state` 已满足；Dashboard 展示待 D。

---

# 6. D — UI & Integration Owner

## 本 Gate 目标

把 Gate 1 Dashboard 从 fake/Backend 驱动切换到**真实 PT Telemetry 验收**，但不修改传输协议。

需要确认：

- Edge Online/Offline；
- current temperature；
- Fan ON/OFF；
- AUTO mode；
- Policy Version / threshold / hysteresis；
- 32 C 左右出现 WARNING；
- Event Stream 有 SENSOR / EDGE-AUTO；
- fake edge 仍可作为开发替身。

### D Gate 2 通过标准

> PT 将真实温度从约 28 C 调到约 32 C 后，Dashboard 在可接受延迟内显示真实温度、WARNING、Fan 状态与事件。

D 本 Gate不要继续堆动画、主题、登录页等非验收功能。

---

# 7. Gate 2 Integration Check

建议按下面顺序联调 B/C/D：

```text
① Backend 启动
② Dashboard 打开
③ PT / SBC 启动 Local Loop
④ RealWSClient CONNECTED
⑤ 28 C：检查 Backend + Dashboard
⑥ 32 C：检查 Telemetry + WARNING + Fan ON + Events
⑦ 保持当前状态 10~20 秒，确认 Heartbeat / UI 稳定
⑧ 临时中断连接只做健壮性观察；正式 outage 验收留给 Gate 4
```

每位 Owner 汇报统一格式：

```text
完成内容：
当前可独立演示什么：
测试结果：
阻塞项：
是否触碰 Public Contract：
提交 SHA / 分支：
建议证据：
下一动作：
```

---

# 8. Gate 2 Definition of Done

- [ ] A：Branch VLAN40/50 + Router-on-a-Stick + IPv4 Underlay 基础层 PASS。
- [ ] A：HQ Gate 1 网络 regression PASS。
- [x] B：真实 TEMP01 数据进入合法 Protocol v1.0 Telemetry。（C 已在 Backend 侧观察到 31.8 C）
- [ ] B：Local Loop 仍独立于 Cloud。
- [x] C：真实 PT Telemetry 更新 Backend state；Backend 无协议漂移。
- [ ] D：Dashboard 展示真实温度 / WARNING / Fan / events。
- [ ] B+C+D：`TEMP01 → SBC → Backend → Dashboard` 真实链路 PASS。
- [ ] 所有新增证据、阶段报告、`PROJECT_BOARD.md` 更新完成。
- [ ] 无人把 RealWSClient 描述成经过 Packet Tracer WAN。

满足后才进入 Gate 3。

---

# 9. Gate 3 / G4 预告，禁止提前乱加

### Gate 3

B/C/D：Dashboard Policy / Command → Backend → Edge → ACK。  
A：OSPF + eBGP + BR-OFFICE→HQ-SERVICE + PAT/DNS/HTTP + static TCP/80 mapping。

### Gate 4

B/C/D：Cloud-off autonomy + reconnect + state_sync。  
A：SLAAC + DHCPv6 + static IPv6 + IPv6-over-IPv4 Tunnel + Port Security + HQ central administration + 完整 ACL/业务回归。

除非本 Gate 遇到明确阻塞，不要提前把 Gate 3/4 功能全部混入 Gate 2，避免排错复杂化。
