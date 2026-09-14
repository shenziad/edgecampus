# Packet Tracer Edge 适配说明

此目录由 B（Edge Owner）维护。不要把 `fake_edge.py` 原样复制进 Packet Tracer；PT 的 SBC Python API、网络能力和版本支持需要在目标实验环境中确认。

## 固定输入输出

输入设备：

- 温度传感器：`TEMP01`
- 边缘节点：`EDGE-SBC-01`
- 风扇：`FAN01`

必须保留的本地状态：

```text
mode = AUTO
threshold_c = 30.0
hysteresis_c = 1.0
policy_version = 1
fan_state = OFF
```

## 实现顺序

1. 只在 PT 内完成 `TEMP01 → SBC → FAN01`，断网也能运行。
2. 记录本机 PT 版本及 SBC 可用的网络 API。
3. 将传感器读数映射到 `telemetry`，将风扇状态映射到 `status`。
4. 接收 `policy` 与 `command`，分别返回 `policy_ack` 与 `command_ack`。
5. WebSocket 断开时继续执行本地 AUTO 策略；恢复后发送 `hello + state_sync`。

核心判断必须与 `edge/controller.py` 一致：

```python
if mode == "AUTO":
    if temperature_c >= threshold_c:
        fan_state = "ON"
    elif temperature_c <= threshold_c - hysteresis_c:
        fan_state = "OFF"
```

迟滞区间用于避免温度在阈值附近波动时风扇频繁开关。

## PT 接口验证记录

在写适配代码前，把以下信息补到本文件末尾：

- Packet Tracer 版本：`TODO`
- SBC 编程语言/运行模式：`TODO`
- 传感器读取 API：`TODO`
- 风扇控制 API：`TODO`
- 可用网络协议：`TODO`
- PT 与真实主机互通方式：`TODO（最高风险项，Gate 2 前验证）`
