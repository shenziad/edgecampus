# EdgeCampus 当前阶段指挥文件

> 当前 Gate：**Gate 1 — 四模块独立运行**  
> 状态：**IN PROGRESS**  
> 发布日期：2026-09-14  
> 总原则：**先独立跑通，再进入 Gate 2 真实端到端联调。**

---

## 0. 所有人 / 所有 AI 开工前必须先读

在开始修改任何内容前，按顺序检查：

1. `docs/AI_CONTEXT.md` —— 项目目标、固定架构、Public Contract、AI 红线。
2. `docs/CONTRIBUTING.md` —— Owner 边界、分支、提交规范、RFC、Definition of Done。
3. `docs/ARCHITECTURE.md` —— 三平面架构、双控制环、状态所有权、断云降级行为。
4. `docs/PROTOCOL.md` —— B/C/D 联调唯一消息契约。
5. `docs/NETWORK_PLAN.md` —— A 的网络地址、设备、端口、ACL 与 PT/真实主机边界。
6. `docs/ACCEPTANCE.md` —— Gate 1 通过标准及后续 Gate 的验收主线。

### 开工前必须核对的冻结项

- VLAN 10 / OFFICE：`192.168.10.0/24`，网关 `192.168.10.1`。
- VLAN 20 / IOT：`192.168.20.0/24`，网关 `192.168.20.1`。
- VLAN 30 / MANAGEMENT：`192.168.30.0/24`，网关 `192.168.30.1`。
- `EDGE-SBC-01 = 192.168.20.10`。
- `BACKEND-STUB = 192.168.30.10`，`ADMIN-PC = 192.168.30.20`。
- Edge WS：`ws://<backend>:8000/ws/edge`；本机 PT → Real Host 已实测 `ws://127.0.0.1:8000/ws/edge` 可用。
- Dashboard WS：`/ws/dashboard`。
- 设备 ID：`EDGE-SBC-01`、`TEMP01`、`FAN01`。
- 协议版本：`1.0`。
- 公共 JSON 字段、URL、VLAN/IP、设备 ID、目录结构不得由个人或 AI 擅自修改；确需修改先走 RFC。

> **特别注意**：Packet Tracer 的 VLAN/ACL/路由属于模拟数据平面；`RealWSClient` 连接真实 FastAPI 属于 Edge–Cloud 带外控制通道。不要在代码、报告或答辩中把两者混写成“WebSocket 流量经过 VLAN 20/30”。

---

## 1. Gate 1 的共同目标

Gate 1 不要求四个模块已经端到端联通。目标是让 A/B/C/D **分别拥有一个可独立运行、可独立验收、可被 fake 对端替代的稳定模块**。

Gate 1 通过时应达到：

```text
A：Packet Tracer 网络底座独立可验收
B：Edge 在无 Cloud 时可完成 TEMP01 → SBC → FAN01 本地自治
C：Backend 使用 fake_edge 可稳定接收、校验、维护状态
D：Dashboard 使用 fake/Backend 状态可稳定展示状态、告警、事件与策略表单
```

### Gate 1 暂时不追求

- 不要求真实 `TEMP01 → SBC → Backend → Dashboard` 全链路完成（这是 Gate 2）。
- 不要求 Dashboard 策略真正下发到 PT Edge（这是 Gate 3）。
- 不要求正式演示“断云不断控 + 云恢复同步”（这是 Gate 4）。
- 不新增烟雾、门禁、Guest VLAN、数据库、MQ、Kubernetes、微服务、账号系统等非核心功能。
- 不为了“看起来高级”擅自扩大范围。

---

## 2. A — Network Owner

### 本阶段主要任务

把 Gate 0 已冻结的网络规划真正实现为一个稳定的 **canonical Packet Tracer 网络底座**。

需要完成：

- VLAN 10 / 20 / 30 创建与命名。
- `Fa0/1`、`Fa0/2`、`Fa0/3`、`Fa0/4` 分别接入 OFFICE / IOT / MANAGEMENT。
- `SW-CORE Gi1/0/1 ↔ SW-ACCESS Gi0/1` 与 `Gi1/0/2 ↔ Gi0/2` 配置 LACP EtherChannel。
- Port-Channel 配置 Trunk，仅允许 VLAN 10/20/30。
- 3650 上创建三个 SVI，开启三层转发。
- OFFICE 使用 DHCP。
- IOT / MANAGEMENT 核心节点使用冻结的静态地址。
- 按 `NETWORK_PLAN.md` 的源安全域原则配置 VLAN10 / VLAN20 inbound ACL。
- MANAGEMENT 保持最高信任运维域。
- 完成 N1 / N2 类独立网络验证并记录配置。

### 开工前先检查

- 只使用 Gate 0 已确认的设备型号和端口。
- 不改 VLAN/IP。
- 不擅自把真实 FastAPI 伪装成 PT 内 VLAN30 节点；`BACKEND-STUB` 只用于 PT 网络验收。
- 确认自己持有**唯一 canonical `.pkt` 修改权**。

### 交付物

- 正式可继续集成的 canonical `.pkt`。
- `packet_tracer/CONFIG_LOG.md` 或等价配置记录，包含关键命令和验证结果。
- 至少一份可复现的网络验收说明：VLAN/Trunk/EtherChannel/SVI/DHCP/ACL。
- Gate 1 网络证据截图，重点证明：允许流量可达、OFFICE → IOT 被拒绝、EtherChannel 正常。

### Gate 1 通过标准

> 不依赖 B/C/D 的代码，A 单独打开正式 `.pkt` 就能完成本阶段所有网络验收。

---

## 3. B — Edge Owner

### 本阶段主要任务

完成 Packet Tracer 内真正的 **Edge Local Loop**，证明 Edge 不依赖 Cloud 也能工作。

需要完成：

- 在自己的 PT 开发副本中确认 `TEMP01` 读取方式。
- 确认 `FAN01` 控制方式。
- 实现本地状态：`mode`、`threshold_c`、`hysteresis_c`、`policy_version`、`fan_state`。
- AUTO 模式下实现迟滞控制：

```text
温度 >= threshold       → FAN ON
温度 <= threshold-hyst  → FAN OFF
迟滞区间内              → 保持原状态
```

- Cloud / WebSocket 不可用时，本地传感器循环和风扇控制不得停止。
- 保留 Gate 0 已验证的 `RealWSClient` 能力，但本 Gate **不以完整遥测上传为通过条件**。
- 将真实 PT API / pin / 接线方式记录到 `edge/packet_tracer/README.md`。

### 开工前先检查

- 不把 `fake_edge.py` 原样复制到 PT。
- `edge/controller.py` 中的核心控制语义是参考基线，不允许随意改变迟滞规则。
- 不修改 `docs/PROTOCOL.md` 的字段。
- B 使用自己的 `.pkt` 开发副本；**不要覆盖或提交替换 A 的 canonical `.pkt`**。

### 交付物

- 可放入 SBC 的 PT Python Edge 程序。
- `TEMP01` 读取 API、`FAN01` 控制 API、接线/pin 映射的实际验证记录。
- 本地自治测试结果：至少覆盖低于阈值、跨阈值开启、迟滞区间保持、降到关闭阈值以下四种情况。
- 一份“关闭真实 Backend 后仍可自治”的证据。
- 可由 A 后续并入 canonical `.pkt` 的明确接线和导入说明。

### Gate 1 通过标准

> FastAPI 完全关闭时，在 PT 中改变 TEMP01，EDGE-SBC-01 仍能按最后有效 AUTO 策略正确控制 FAN01。

---

## 4. C — Control Plane Owner

### 本阶段主要任务

把现有 FastAPI Backend 做成一个**稳定、可被 fake edge 独立验证的控制平面基线**，不要继续扩架构。

需要完成/确认：

- `/healthz` 正常。
- `/api/state` 正常。
- `/ws/edge` 能接收并校验协议 v1 消息。
- `/ws/dashboard` 能向 Dashboard 广播 snapshot，并转发合法 `policy` / `command`。
- `fake_edge.py` 可以发送 hello / heartbeat / telemetry / status / state_sync 等已定义消息。
- malformed / unsupported 消息不会导致 Backend 崩溃，而是返回协议错误。
- Edge 断开时 `edge_online=false`、`cloud_state=DISCONNECTED`。
- fake edge 重连后状态恢复逻辑可重复测试。
- 事件日志与内存状态保持最小、清晰、可解释。

### 开工前先检查

- Backend 不是温控决策核心；真正 AUTO 判断属于 Edge。
- 不新增数据库、MQ、微服务、认证、容器编排等非目标。
- 不更改协议字段和 WS 路径。
- 优先稳定性和可测试性，而不是新增功能。

### 交付物

- 可直接启动的 FastAPI Backend。
- 可独立运行的 `fake_edge.py`。
- 运行命令与最小环境说明。
- 自动测试 / 手工验证结果，至少覆盖：正常遥测、非法消息、Edge 断开、重连恢复。
- `/api/state` 与日志证据。

### Gate 1 通过标准

> 不需要 Packet Tracer，单独运行 Backend + fake_edge 就能稳定复现 Edge ONLINE、温度/风扇状态更新、断线和重连。

---

## 5. D — UI & Integration Owner

### 本阶段主要任务

把 Dashboard 做成一个**不依赖真实 PT 也能独立验收的 Management Plane 基线**，并为后续 Gate 2/3/4 的真实联调预留稳定接口。

需要完成/确认：

- 展示系统 / Cloud / Edge 基本状态。
- 展示当前温度、风扇状态、控制模式、Policy Version / threshold / hysteresis。
- 温度越过告警阈值时有清晰 WARNING 状态。
- Edge Offline / Disconnected 时 UI 明确降级显示。
- Event Stream 可以持续追加并区分关键 source（如 SENSOR、EDGE-AUTO、CLOUD-POLICY、REMOTE-MANUAL、SYSTEM）。
- 策略表单具备 Gate 3 所需字段，但本 Gate 只要求与 fake/backend 基线联调，不要求真实 PT Edge 已应用。
- 前端不要自行重命名协议字段；展示层可以转换文案，传输层不能改契约。
- 维护 `tests/` 中与 UI / 集成有关的最小测试或验证脚本。

### 开工前先检查

- 不把主要时间花在动画、主题、登录页等视觉花活。
- 页面必须优先服务现场验收：状态是否正确、事件是否可解释、故障是否明显。
- Dashboard 不直接控制 PT 设备，所有正式控制必须走 Backend。

### 交付物

- 可打开并稳定显示状态的 Dashboard。
- fake/backend 驱动的状态切换演示：正常温度、WARNING、Edge Offline、事件追加。
- Policy 表单基线。
- UI / 集成验证说明与必要截图。

### Gate 1 通过标准

> 不需要 Packet Tracer，使用 Backend 或 fake snapshot 就能完整展示 EdgeCampus 当前状态、告警、事件和策略界面。

---

## 6. Gate 1 并行开发规则

四个角色**同时开工**。唯一特殊约束是 `.pkt`：

```text
A：唯一 canonical .pkt Owner
B：自己的 PT 开发副本 + edge/ 代码
C：backend/
D：dashboard/ + tests/
```

### 第一次 Integration Check

每位 Owner 独立开发最长约 4 小时后，无论完成度如何，进行一次短检查，只汇报：

```text
完成内容：
当前可独立演示什么：
测试结果：
阻塞项：
是否触碰 Public Contract：
下一动作：
```

### 提前完成后的支援原则

- C 先完成：优先帮助 B 调试 WebSocket / JSON，不加数据库。
- D 先完成：优先帮助 C 做集成测试，不继续堆 UI 花活。
- A 先完成：优先帮助 B 把已验证 Edge 配置并入 canonical `.pkt`。
- B 若被 PT API 卡住：尽早报告，A/C 可协助排错；不要一个人闷头重写架构。

---

## 7. Gate 1 Definition of Done

Gate 1 只有在以下四项**全部**满足后才可宣布 COMPLETE：

- [ ] A：正式 `.pkt` 的 VLAN / Trunk / EtherChannel / SVI / DHCP / ACL 独立通过。
- [ ] B：PT 内 `TEMP01 → EDGE-SBC-01 → FAN01` 本地自治独立通过，Cloud 关闭仍运行。
- [ ] C：`fake_edge.py → Backend → /api/state` 独立通过，断线 / 重连 / 错误消息行为稳定。
- [ ] D：Dashboard 使用 fake/backend 数据可展示状态、告警、事件和策略表单。

此外每位 Owner 都必须：

- 提供运行/操作方式；
- 提供至少一个可复现测试；
- 保留必要证据；
- 不擅自修改 Public Contract；
- 更新自己的交付记录或在 Integration Check 中说明现状。

**Gate 1 完成后，才进入 Gate 2：第一次真实 `Packet Tracer TEMP01 → SBC → Backend → Dashboard` 单向全链路联调。**

---

## 8. 给 AI 的固定提示

每个人把本文件与 `docs/AI_CONTEXT.md` 一并提供给自己的 AI，并追加：

> 你只负责我对应的 Gate 1 Owner 模块。先检查冻结契约和当前仓库实现，再提出最小可运行计划。只做增量修改；若需要改设备 ID、JSON 字段、URL、VLAN/IP、目录结构、最终 Demo 主线或 canonical `.pkt` 所有权，请立即停止并输出 RFC，不要直接修改。每次交付都要给出运行方式、测试结果、待联调项和建议证据。

---

## 9. 当前指挥结论

**G0 已完成，G1 已发布。**

本阶段团队的优先级不是“功能越多越好”，而是：

> **四个模块分别变得稳定、可测试、可替代、可合并。**

当四个 Owner 都达到本文件的 Gate 1 通过标准后，由项目总指挥统一复核仓库和证据，再更新本文件并发布 Gate 2。
