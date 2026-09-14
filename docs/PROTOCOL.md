# EdgeCampus Protocol v1.0

此文档是 B/C/D 联调的唯一消息契约。字段变更必须走 `docs/CONTRIBUTING.md` 中的 RFC。

## 传输与通用信封

- JSON 文本帧，UTF-8。
- Edge 连接 `ws://<backend>:8000/ws/edge`。
- Dashboard 连接 `ws://<backend>:8000/ws/dashboard`。
- 时间统一使用带时区的 ISO-8601 UTC 字符串。

所有消息必须包含：

```json
{
  "type": "telemetry",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:30:00.000+00:00"
}
```

## Edge → Backend

### hello

```json
{
  "type": "hello",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:30:00.000+00:00",
  "edge_id": "EDGE-SBC-01"
}
```

### heartbeat

```json
{
  "type": "heartbeat",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:30:03.000+00:00",
  "edge_id": "EDGE-SBC-01",
  "status": "ONLINE",
  "mode": "AUTO",
  "policy_version": 1
}
```

### telemetry

```json
{
  "type": "telemetry",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:30:04.000+00:00",
  "edge_id": "EDGE-SBC-01",
  "device_id": "TEMP01",
  "metric": "temperature",
  "value": 31.4,
  "unit": "C"
}
```

### status

`source` 只能由实现映射到可解释来源，首版使用 `EDGE-AUTO` 或 `REMOTE-MANUAL`。

```json
{
  "type": "status",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:30:04.010+00:00",
  "edge_id": "EDGE-SBC-01",
  "device_id": "FAN01",
  "value": "ON",
  "source": "EDGE-AUTO"
}
```

### state_sync

Edge 每次重连时上报实际状态，解决 Dashboard 使用旧状态的问题。

```json
{
  "type": "state_sync",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:31:00.000+00:00",
  "edge_id": "EDGE-SBC-01",
  "temperature_c": 34.0,
  "fan_state": "ON",
  "policy": {
    "policy_id": "thermal-01",
    "version": 2,
    "mode": "AUTO",
    "threshold_c": 33.0,
    "hysteresis_c": 1.0
  }
}
```

## Dashboard → Backend → Edge

### policy

新策略版本必须严格递增。`threshold_c` 允许 0–80，`hysteresis_c` 允许 0–10。

```json
{
  "type": "policy",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:32:00.000+00:00",
  "policy_id": "thermal-01",
  "version": 2,
  "mode": "AUTO",
  "threshold_c": 33.0,
  "hysteresis_c": 1.0
}
```

### command

```json
{
  "type": "command",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:32:05.000+00:00",
  "command_id": "uuid",
  "device_id": "FAN01",
  "action": "ON"
}
```

## Edge ACK

```json
{
  "type": "policy_ack",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:32:00.030+00:00",
  "policy_id": "thermal-01",
  "version": 2,
  "result": "APPLIED"
}
```

```json
{
  "type": "command_ack",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:32:05.030+00:00",
  "command_id": "uuid",
  "device_id": "FAN01",
  "action": "ON",
  "result": "APPLIED"
}
```

## 错误语义

```json
{
  "type": "error",
  "protocol_version": "1.0",
  "message_id": "uuid",
  "timestamp": "2026-09-14T08:32:10.000+00:00",
  "code": "EDGE_OFFLINE",
  "message": "edge is not connected"
}
```

首版错误码：`INVALID_MESSAGE`、`UNSUPPORTED_FROM_DASHBOARD`、`EDGE_OFFLINE`。

## 兼容性红线

以下都属于破坏性变更：重命名字段、修改 ID、把摄氏单位由 `C` 改为 `℃`、改变 URL、用数字代替 `ON/OFF`。展示层可以翻译，传输层不能自行变化。
