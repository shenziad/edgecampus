# Packet Tracer Edge 适配说明

此目录由 B（Edge Owner）维护。这里记录 Packet Tracer 9.0.1 中已经验证的 API、接线、Gate 1 本地自治，以及 Gate 2 的增量联调边界。

> 环境：Cisco Packet Tracer **9.0.1**

## 1. 固定设备与公共状态

- 温度传感器：`TEMP01`
- 边缘节点：`EDGE-SBC-01`
- 风扇：`FAN01`
- `mode = AUTO`
- `threshold_c = 30.0`
- `hysteresis_c = 1.0`
- `policy_version = 1`
- 协议 Fan 状态：`OFF / ON`

Gate 1 正式 AUTO 语义与 `edge/controller.py` 一致：

```python
if temperature_c >= threshold_c:
    fan_state = "ON"
elif temperature_c <= threshold_c - hysteresis_c:
    fan_state = "OFF"
# 迟滞区间内保持原状态
```

Final Architecture v2 **不修改**以上 Edge 语义。

## 2. Packet Tracer 9.0.1 实测接线

```text
TEMP01 A0
    |
    | analog signal
    v
IO-MCU-01 A0
    |
    | USB0
    v
EDGE-SBC-01 USB0
    |
    | D0 / Custom Cable
    v
FAN01 D0
```

| 链路 | 端口/API | 状态 |
|---|---|---|
| TEMP01 → MCU | `TEMP01 A0 → MCU A0` | VERIFIED |
| MCU 温度采集 | `analogRead(A0)` | VERIFIED |
| MCU → SBC | `MCU USB0 → SBC USB0`，`USB(0, 9600)` | VERIFIED |
| SBC → FAN | `SBC D0 → FAN01 D0`，Custom Cable | VERIFIED |
| FAN 控制 | `customWrite(0, "0")` / `customWrite(0, "2")` | VERIFIED |

FAN01 PT 设备状态值：

```text
0 = OFF
1 = LOW
2 = HIGH
```

EdgeCampus 公共协议只使用 `ON/OFF`。PT 适配映射：

```text
OFF → physical state 0
ON  → physical state 2 (HIGH)
```

**禁止把 PT 物理值 `2` 直接发送为 Protocol v1.0 Fan 状态。**

## 3. MCU 温度采集与 USB 发送

实现：`mcu_temperature_sender.py`

```text
analogRead(A0)
→ 0~1023 映射到 -100~100 C
→ 保留 1 位小数
→ USB0.write()
→ SBC USB0 readLine()
```

温度换算：

```python
temp_c = raw * 200.0 / 1023.0 - 100.0
```

发送数据使用换行符作为帧结束标记。

## 4. SBC Gate 1 Local Loop

实现：`sbc_local_controller.py`

```text
TEMP >= 30.0 C       → FAN ON
TEMP <= 29.0 C       → FAN OFF
29.0 C < TEMP < 30 C → HOLD previous FAN state
```

本控制循环只依赖本地 USB 温度输入和本地 `customWrite()`，不依赖 Backend 才能作出 AUTO 决策。

## 5. Gate 1 实测结果 — PASS

已观察：

```text
27.x C          → TURN_OFF → FAN OFF
31.0 / 30.2 C   → TURN_ON  → FAN ON
29.4 C          → HOLD     → FAN ON
28.6 C          → TURN_OFF → FAN OFF
```

证据：

- `evidence/B1_hysteresis_console.png`
- `evidence/B2_fan_state_topology.png`
- `evidence/B3_backend_off_local_autonomy.png`

B3 证明 Backend 端口不可达时，本地循环仍可完成 ON / HOLD / OFF。

A+B 合入 canonical 网络后也已完成回归，见 `docs/gate1/AB_INTEGRATION_REPORT.md`。

## 6. RealWSClient 真实性边界

Gate 0 已实测：

```text
EDGE-SBC-01
  ↓ Packet Tracer External Network Access / RealWSClient
ws://127.0.0.1:8000/ws/edge
  ↓
Real FastAPI Backend
```

该通道是**带外 Edge–Cloud 控制通道**。Final Architecture v2 新增的 R-HQ / R-ISP / R-BRANCH / BGP / NAT / IPv6 Tunnel 不承载真实 WebSocket。

不得在报告中写成“Telemetry 经过 Packet Tracer WAN”。正确表述是：真实 PT 传感器产生数据，SBC 通过 RealWSClient 带外送入真实 Backend；模拟 WAN 负责验证企业网络对 HQ/Branch/Internet 业务的承载。

## 7. Gate 2 实测结果 — B Edge-side PASS

正式实现：`sbc_gate2_controller.py`

在**不重写 Gate 1 Local Loop**的基础上，真实 PT 状态已成功映射到 Protocol v1.0：

| Gate 2 能力 | 状态 |
|---|---|
| RealWSClient | VERIFIED |
| Protocol hello | VERIFIED |
| Fixed telemetry | VERIFIED |
| Real TEMP telemetry | VERIFIED |
| FAN status | VERIFIED |
| Heartbeat | VERIFIED |
| Physical FAN ON | VERIFIED |

最终程序执行顺序：

```text
USB real temperature
→ Local AUTO + hysteresis
→ physical FAN write
→ Cloud connected check
→ telemetry / status / heartbeat
```

因此 Local Loop 的执行优先级高于 Cloud 通信。WebSocket 不可用时，连接状态不会成为温度读取、本地决策或 FAN 执行的前置条件。

证据索引与完整实验过程见 `docs/gate2/B_EDGE_REPORT.md`；截图位于 `evidence/gate2/`。

Policy / Command 的真实 PT 应用属于 Gate 3，不要在 Gate 2 为了“多做一点”破坏 Local Loop。

## 8. Gate 2 RealWSClient callback 限制

Packet Tracer 9.0.1 实测中，若在 `onConnectionChange` callback 内调用 `delay()`，会出现：

```text
SuspensionError:
Cannot call a function that blocks or suspends here
```

因此 callback 只记录连接状态。hello、telemetry、status、heartbeat 以及所有 `delay()` 均在主循环中执行。

## 9. Gate 3 — B Edge-side PASS LOCALLY

实测源码：`sbc_gate3_controller.py`；报告：`../../docs/gate3/B_EDGE_REPORT.md`；证据：`evidence/gate3/`。

- Policy runtime apply 更新 AUTO/MANUAL、threshold、hysteresis 与 policy version；version 必须严格递增，旧版本不覆盖当前策略，成功应用后发送 `policy_ack / APPLIED`。
- AUTO 使用动态 threshold + hysteresis；MANUAL 保持远程 FAN ON/OFF，写入真实 FAN 后发送 `REMOTE-MANUAL` status 与 `command_ack / APPLIED`。
- callback 只入队和记录状态，不阻塞；本地循环不依赖 Cloud。Telemetry / Status / Heartbeat 保留，切回 AUTO 后 Gate 2 regression PASS。
- 保留已实测 PT 兼容实现：固定 ISO-8601 timestamp、UUID-shaped counter message_id、平坦消息字段提取，不引入新的 datetime/uuid/json 依赖。
- B 状态：**PASS LOCALLY / READY FOR B+C+D INTEGRATION**；B+C+D formal integration **PENDING**，Global Gate 3 **IN PROGRESS**。正式 Cloud-off/reconnect/state_sync 验收留 Gate 4。

## 10. 调试经验

### 温度初始接近 -0.5 C

通过改变 TEMP01 的环境温度后，`analogRead(A0)` 和换算结果同步变化，确认采集 API 与映射逻辑有效。

### SBC Console 有输出但 FAN state 不变

最初程序可打印，但 FAN01 `Attributes -> state` 始终为 `0`。将链路拆成独立的 `SBC → FAN` 测试后，重新核对 Custom Cable、D0 和 `customWrite()`，最终状态可正确切换。

### 分段测试方法

```text
TEMP → MCU
MCU → SBC
SBC → FAN
Local Loop
Local Loop + RealWSClient
```

始终逐段验证后再合并，避免传感器、串口、执行器和网络问题互相干扰。

## Gate4 断云恢复归档（2026-09-17）

实测源码 `sbc_gate4_controller.py`：本地优先、保留内存最后策略、2000 ms 重连调度、fresh connection hello + 有真实温度后 state_sync。Cloud outage 不等于 Edge process restart。报告与真实证据见 `../../docs/gate4/B_EDGE_REPORT.md`；当前完整验收 EVIDENCE PENDING。固定 ISO timestamp 与 counter message_id 的 PT 兼容实现不改。
