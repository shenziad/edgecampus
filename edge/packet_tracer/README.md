# Packet Tracer Edge 适配说明

此目录由 B（Edge Owner）维护。这里记录真实 Packet Tracer 环境中已经验证过的 API、接线和 Gate 1 本地自治实现。

> 环境：Cisco Packet Tracer **9.0.1**

## 1. 固定设备与项目状态

- 温度传感器：`TEMP01`
- 边缘节点：`EDGE-SBC-01`
- 风扇：`FAN01`
- `mode = AUTO`
- `threshold_c = 30.0`
- `hysteresis_c = 1.0`
- `policy_version = 1`
- `fan_state = OFF / ON`

Gate 1 的正式 AUTO 语义与 `edge/controller.py` 一致：

```python
if temperature_c >= threshold_c:
    fan_state = "ON"
elif temperature_c <= threshold_c - hysteresis_c:
    fan_state = "OFF"
# 迟滞区间内保持原状态
```

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

实际验证映射：

| 链路 | 端口/API | 状态 |
|---|---|---|
| TEMP01 -> MCU | `TEMP01 A0 -> MCU A0` | VERIFIED |
| MCU 温度采集 | `analogRead(A0)` | VERIFIED |
| MCU -> SBC | `MCU USB0 -> SBC USB0`, `USB(0, 9600)` | VERIFIED |
| SBC -> FAN | `SBC D0 -> FAN01 D0`, Custom Cable | VERIFIED |
| FAN 控制 | `customWrite(0, "0")` / `customWrite(0, "2")` | VERIFIED |

FAN01 的设备状态值：

```text
0 = OFF
1 = LOW
2 = HIGH
```

EdgeCampus 公共语义只使用 `ON/OFF`。当前 PT 适配层将：

```text
OFF -> FAN state 0
ON  -> FAN state 2 (HIGH)
```

## 3. MCU 温度采集与 USB 发送

实现文件：`mcu_temperature_sender.py`

核心流程：

```text
analogRead(A0)
    ->
0~1023 映射到 -100~100 C
    ->
保留 1 位小数
    ->
USB0.write()
    ->
SBC USB0
```

温度换算：

```python
temp_c = raw * 200.0 / 1023.0 - 100.0
```

发送数据使用换行符作为帧结束标记，SBC 端使用 `readLine()` 接收。

## 4. SBC 本地自治控制

实现文件：`sbc_local_controller.py`

AUTO 策略：

```text
TEMP >= 30.0 C       -> FAN ON
TEMP <= 29.0 C       -> FAN OFF
29.0 C < TEMP < 30 C -> HOLD previous FAN state
```

迟滞用于避免温度在 30 C 附近轻微波动时风扇反复开关。

本控制循环只依赖本地 USB 温度输入和本地 `customWrite()` 执行器调用，不依赖 Backend 才能作出 AUTO 决策。

## 5. Gate 1 实测结果

已观察到以下完整序列：

```text
27.x C -> TURN_OFF -> FAN OFF
31.0 / 30.2 C -> TURN_ON -> FAN ON
29.4 C -> HOLD -> FAN ON
28.6 C -> TURN_OFF -> FAN OFF
```

这证明：

1. 低温关闭正常；
2. 越过上阈值后开启正常；
3. 回落到迟滞区间时不会立即关闭；
4. 下降到关闭阈值以下后正确关闭。

证据：

- `evidence/B1_hysteresis_console.png`
- `evidence/B2_fan_state_topology.png`

## 6. Gate 0 已验证的真实 Backend 能力

Gate 0 已验证 `RealWSClient` 可通过 Packet Tracer External Network Access 连接同一物理主机上的 FastAPI：

```text
ws://127.0.0.1:8000/ws/edge
```

该通道属于 PT 的带外 Edge-Cloud 控制通道，不等价于 WebSocket 报文真实经过 PT 内 VLAN 20/30。

Gate 1 当前实现优先保证本地自治。后续 Gate 再把本地状态映射到协议 `telemetry/status/state_sync` 并接入真实 Backend。

## 7. 调试经验

### 温度初始接近 -0.5 C

最初 MCU 输出长期接近 -0.5 C。通过改变 TEMP01 的环境温度后，`analogRead(A0)` 和换算结果同步变化，确认采集 API 与映射逻辑有效。

### SBC Console 有输出但 FAN state 不变

最初控制程序可以正常打印，但 FAN01 `Attributes -> state` 始终为 `0`。将链路拆成独立的 `SBC -> FAN` 测试后，重新核对 Custom Cable、D0 pin 和 `customWrite()` 调用，最终 FAN state 可正确切换。

### 分段测试方法

本次采用：

```text
TEMP -> MCU
MCU -> SBC
SBC -> FAN
```

逐段验证后再合并闭环，避免传感器、通信和执行器问题互相干扰。
