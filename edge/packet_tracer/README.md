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
2. 记录本机 PT 版本及 SBC 可用的传感器/执行器 API。
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

## Gate 0 已验证环境

- SBC 编程语言/运行模式：`Python 3 Project`
- Edge 项目：空白 Python 项目（开发时命名为 `EdgeCampusEdgect`）
- 网络接入：SBC-PT 已安装 FastEthernet 模块，并接入 `SW-ACCESS Fa0/2`
- External Network Access：已开启
- 可用真实网络协议：`RealWSClient / WebSocket`
- Edge WebSocket：`ws://127.0.0.1:8000/ws/edge`
- 真实 Backend：与 Packet Tracer 运行在同一台物理主机上的 FastAPI/Uvicorn

### PT → Real Host 实机验证

Gate 0 使用最小 `RealWSClient` 探针完成了真实联通测试，结果：

```text
Starting EdgeCampusEdgect (Python3)...
Connecting...
WS state: 2
WS state: 3
CONNECTED
Remote: 127.0.0.1 8000
```

同时真实 Backend 侧出现：

```text
WebSocket /ws/edge [accepted]
connection open
edge connected
```

访问 `/api/state` 可观察到：

```text
edge_online = true
cloud_state = CONNECTED
edge_id = EDGE-SBC-01
```

保存并关闭 Packet Tracer、重新打开 `.pkt` 后再次运行探针，WebSocket 仍可稳定连接。因此 Gate 0 中原“PT 与真实主机互通方式”的最高风险项已验证通过。

> 架构说明：该 `RealWSClient` 通道属于 Packet Tracer External Network Access 提供的带外 Edge–Cloud 控制通道，并不表示真实 WebSocket 报文实际经过 PT 内的 VLAN 20/30。PT 以 VLAN/ACL/路由等承担园区模拟数据平面。

## Gate 1 待完成的 PT API 适配

以下内容不属于 Gate 0，交由 B 在 Gate 1 实机确认：

- Packet Tracer 具体版本号：`TODO（记录环境信息）`
- `TEMP01` 传感器读取 API：`TODO`
- `FAN01` 风扇控制 API：`TODO`
- TEMP01 / FAN01 与 SBC 的实际连接方式和 pin/API 映射：`TODO`
- 无 Cloud 条件下 `TEMP01 → SBC → FAN01` 本地自治验证：`TODO`

Gate 1 的通过重点是**本地自治**，而不是继续证明 WebSocket 可连接。
