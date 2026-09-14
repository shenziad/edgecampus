# Gate 与验收标准

## Gate 0：Contract Freeze — COMPLETE

| 验收项 | 状态 |
|---|---|
| 项目定位、三平面与双控制环 | DONE |
| 设备 ID、消息协议、WS 路径 | DONE |
| VLAN/IP 逻辑规划 | DONE |
| 物理设备型号、接口映射 | DONE |
| PT 与真实主机互通方式 | VERIFIED |
| ACL 放置原则 | DONE |
| 重开 Packet Tracer 后连接可重复 | VERIFIED |
| 最终 6 分钟 Demo | DONE |

Gate 0 结束后，公共契约只通过 RFC 改动。

### Gate 0 已冻结事实

- `SW-CORE`：Cisco 3650-24PS。
- `SW-ACCESS`：Cisco 2960-24TT。
- `SW-CORE Gi1/0/1 ↔ SW-ACCESS Gi0/1`。
- `SW-CORE Gi1/0/2 ↔ SW-ACCESS Gi0/2`。
- `SW-ACCESS Fa0/1 → OFFICE-PC`。
- `SW-ACCESS Fa0/2 → EDGE-SBC-01`。
- `SW-ACCESS Fa0/3 → ADMIN-PC`。
- `SW-ACCESS Fa0/4 → BACKEND-STUB`。
- Edge 控制通道：`ws://127.0.0.1:8000/ws/edge`，通过 Packet Tracer `RealWSClient` / External Network Access 连接真实 FastAPI Backend。
- 首次连接与保存、关闭、重新打开 `.pkt` 后的再次连接均验证成功。
- VLAN 10、20 的 ACL 首版部署在对应 SVI inbound；VLAN 30 作为管理域首版不配置限制性 ACL。

### Gate 0 证据建议

```text
G0-02-minimal-topology-pass.png
G0-03-external-network-access-enabled.png
G0-04-pt-realhost-websocket-pass.png
```

其中 `G0-04` 应能体现 SBC `CONNECTED`、Backend `edge connected` 以及 `/api/state` 中 `edge_online=true`、`cloud_state=CONNECTED`。

## Gate 1：四模块独立运行（四路并行）

Gate 1 的目标不是端到端联调，而是让四个 Owner 在冻结的 Public Contract 下各自获得一个可独立验收的模块。除 canonical `.pkt` 外，四路工作可以并行进行。

### A — Network Owner

- 在 canonical `.pkt` 中完成 VLAN 10/20/30。
- 配置 Access 端口、两条 Core–Access 链路的 LACP EtherChannel 与 trunk。
- 在 3650 上完成三个 SVI、三层转发、OFFICE DHCP。
- 按 Gate 0 冻结原则部署 VLAN 10 / VLAN 20 inbound ACL。
- 独立完成允许通信、OFFICE→IOT 隔离、MANAGEMENT 运维访问等网络测试。
- A 是 canonical `.pkt` 的唯一 Owner；其他人不得并行覆盖正式 `.pkt`。

**Gate 1 A 通过标志：** 纯 Packet Tracer 园区网络可以独立验收，且配置与 `docs/NETWORK_PLAN.md` 一致。

### B — Edge Owner

- 使用 PT 开发副本确认 `TEMP01` 读取 API、`FAN01` 控制 API 及实际连接/pin 映射。
- 在不依赖 Cloud 的条件下完成 `TEMP01 → EDGE-SBC-01 → FAN01` 本地 AUTO 控制。
- 保持冻结状态：`threshold_c=30.0`、`hysteresis_c=1.0`、`policy_version=1`。
- 验证迟滞逻辑，避免阈值附近风扇频繁抖动。
- 保留已验证的 `RealWSClient` 连接方式，但 Gate 1 不要求真实 Telemetry 已进入 Dashboard。
- 将可复用的 Edge 代码和 PT API 验证结果提交到 `edge/`，不要用开发 `.pkt` 覆盖 canonical `.pkt`。

**Gate 1 B 通过标志：** Backend 完全关闭时，在 PT 内改变温度，FAN01 仍按照本地策略正确动作。

### C — Control Plane Owner

- 使用 `fake_edge.py` 独立验证 `/ws/edge`、`/ws/dashboard`、`/api/state`、`/healthz`。
- 确保 Telemetry / Status / Heartbeat 能更新内存状态并形成事件记录。
- 确保非法消息按 Protocol v1.0 被拒绝，而不是导致 Backend 崩溃。
- 验证 Edge 断开后 `edge_online=false`，并保持服务可用。
- 保留 Policy / Command 转发和 ACK 所需状态，为 Gate 3 做准备，但 Gate 1 不新增数据库、MQ、微服务等非必要组件。

**Gate 1 C 通过标志：** 不依赖真实 PT，仅使用 fake edge 就能稳定驱动 Backend 状态、断连和日志行为。

### D — UI & Integration Owner

- 使用 fake/Backend snapshot 独立完成 Dashboard 状态展示。
- 至少展示 Cloud/Edge 状态、当前温度、Fan 状态、控制模式、当前 Policy 和事件流。
- 对温度跨阈值、Edge offline 等状态提供明确视觉反馈。
- 准备 Gate 3 所需的 Policy 表单，但 Gate 1 不要求真实 PT 已接入。
- 维护 `tests/` 中与页面/集成相关的验证入口，并开始整理验收证据。

**Gate 1 D 通过标志：** 不依赖真实 PT，Dashboard 可根据 fake/Backend 状态正确更新并可独立演示。

### Gate 1 Integration Check

四个 Owner 各自通过独立测试后进行一次短集成：

1. B 将已验证的 SBC 接线/API/代码方案合入 A 维护的 canonical `.pkt`；
2. 不要求此时完整打通 `TEMP01 → Dashboard`；
3. 确认 Public Contract 未被任何 AI 或个人擅自修改；
4. 更新 `docs/PROJECT_BOARD.md` 与证据目录。

达到以上条件后，Gate 1 COMPLETE，进入 Gate 2。

## Gate 2：单向数据链路

```text
Packet Tracer TEMP01 → SBC → Backend → Dashboard
```

验收动作：PT 温度从 28℃ 改到 32℃；Dashboard 在可接受延迟内显示 32℃ 与 WARNING，事件流出现 SENSOR 记录。

## Gate 3：双向策略闭环

```text
Dashboard threshold 30→33 → Backend → Edge → policy_ack
```

验收动作：下发 33℃，温度 32℃ 时风扇保持 OFF，温度 34℃ 时风扇 ON；事件流能区分 CLOUD-POLICY 与 EDGE-AUTO。

增强验收：Dashboard 手动下发 FAN01 ON/OFF，收到 `command_ack`。

## Gate 4：断云不断控

1. 正常连接，确认 Cloud/Edge ONLINE。
2. 停止 Backend，Dashboard 显示失联。
3. 在 PT 内将温度改到阈值之上，Fan 仍由 SBC 开启。
4. 再改到阈值减迟滞区间之下，Fan 关闭。
5. 恢复 Backend；Edge 自动重连并发送当前温度、风扇和 Policy Version。

这是项目的核心创新性证据，必须保留连续录屏或按时间顺序的截图。

## Gate 5：Freeze 与三轮彩排

第三天只允许修 Bug、改善 UI、补日志和异常处理。完整流程连续演示三轮都成功后冻结版本。

## 最终功能测试矩阵

| ID | 测试 | 操作 | 预期 | Owner |
|---|---|---|---|---|
| N1 | VLAN/路由 | 跨允许域 ping/访问 | 可达 | A |
| N2 | ACL 隔离 | OFFICE 直连 IOT | 拒绝 | A |
| N3 | 控制面访问 | OFFICE 访问逻辑管理服务 | 按设计允许 | A+C |
| E1 | 本地自治 | 断开 Cloud 后跨阈值调温 | Fan 正确动作 | B |
| C1 | 遥测 | fake/PT 发送温度 | Backend 状态更新 | B+C |
| D1 | 可视化 | 温度跨阈值 | 页面状态与告警更新 | C+D |
| P1 | 策略下发 | 阈值 30→33 | Edge 应用并 ACK | B+C+D |
| R1 | 状态恢复 | Cloud 重启 | Edge 重连并同步 | B+C+D |

## 截图命名

`G<Gate>-<序号>-<内容>-<结果>.png`，例如：

```text
G1-01-vlan-trunk-pass.png
G2-01-temperature-dashboard-pass.png
G3-02-policy-ack-pass.png
G4-03-cloud-offline-edge-auto-pass.png
G4-04-reconnect-state-sync-pass.png
```
