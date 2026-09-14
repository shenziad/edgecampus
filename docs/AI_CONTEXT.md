# AI 共享上下文（每次新对话首先粘贴）

## 项目定义

EdgeCampus 是“面向智慧园区的边缘—云协同网络控制平台”。Packet Tracer 承载园区网络和 IoT 物理世界，SBC 是 Edge Controller，真实主机上的 FastAPI 是 Cloud Controller，网页是 Management Plane。

## 固定架构

```text
TEMP01 / FAN01 ↔ EDGE-SBC-01 ↔ WebSocket ↔ FastAPI ↔ Dashboard
                         └─ 断云时继续执行最后有效 AUTO 策略
```

网络固定为三个安全域：

- VLAN 10 / OFFICE
- VLAN 20 / IOT
- VLAN 30 / MANAGEMENT

## Public Contract

- 协议版本：`1.0`
- Edge WebSocket：`/ws/edge`
- Dashboard WebSocket：`/ws/dashboard`
- 设备 ID：`EDGE-SBC-01`、`TEMP01`、`FAN01`
- 核心消息：Telemetry、Status、Command、Policy、Heartbeat
- 恢复消息：Hello、State Sync、ACK、Error
- 权威定义：`docs/PROTOCOL.md` 和 `config/system.json`

## 实现约束

1. 三天内形成可现场验收的最小闭环。
2. 优先最小可运行实现，不引入 Kubernetes、微服务、MQ、数据库。
3. 不得自行修改设备 ID、JSON 字段、URL、VLAN/IP 或目录结构。
4. 已联调代码只允许增量修改；不要“顺便重构”其他模块。
5. 修改前先说明文件、原因、公共接口影响和验证方式。
6. 每个功能必须能够使用 fake 组件独立测试。
7. 给出的代码必须实际运行或明确标记为未在 PT 环境验证的适配模板。
8. 错误处理优先保证：云端失联不影响 Edge 本地控制。

## 你的角色

只负责用户指定的 Owner 模块。需要跨模块变更时，先生成 RFC，不直接改公共契约。

## 每次交付格式

```text
完成内容：
修改文件：
公共接口影响：无 / 有（若有必须暂停）
运行命令：
测试结果：
待联调项：
建议截图证据：
```
