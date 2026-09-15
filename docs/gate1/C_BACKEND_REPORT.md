# Gate 1 — C Control Plane Validation Placeholder

> 状态：**PLACEHOLDER / OWNER EVIDENCE PENDING**  
> 说明：项目已决定不再等待 C 的 Gate 1 专属证据后才启动 Gate 2。本文件不是 PASS 证明，也不得在报告中写成“C 已完成验收”。

## 1. 已存在的软件基线

仓库 `main` 已包含可启动的 FastAPI Backend、Protocol v1.0、`fake_edge.py`、内存状态、JSONL 事件日志以及自动化测试基线。历史基线验证已经覆盖 fake Edge 的状态更新、Policy/Command、断线自治与 State Sync。

这些事实说明 **Backend 基础实现已经存在**，但不能替代 C Owner 对 Gate 1 的正式独立验收与证据提交。

## 2. C 必须补交的 Gate 1 验收

在 Gate 5 Freeze 前，C 必须完成并把本文件改成正式报告：

1. 启动 Backend，验证 `/healthz`。
2. 启动 `python -m edge.fake_edge`，验证 `/ws/edge` 成功建立连接。
3. 验证 `/api/state` 能反映 Edge online、temperature、fan state、policy 等当前状态。
4. 验证 Telemetry / Status / Heartbeat / State Sync 按 Protocol v1.0 被接受并记录。
5. 发送 malformed / unsupported / wrong-version 消息，确认 Backend 返回错误或拒绝消息但服务不崩溃。
6. 停止 fake edge，确认 `edge_online=false`、Cloud/Edge 状态进入预期离线状态。
7. 重启 fake edge，确认 reconnect + `state_sync` 后状态恢复。
8. 记录启动命令、环境、结果、问题与结论。

## 3. 预留证据文件名

证据目录：`evidence/backend/gate1/`

```text
G1-C-01-backend-healthz-pass.png
G1-C-02-fake-edge-api-state-pass.png
G1-C-03-invalid-message-rejected-pass.png
G1-C-04-edge-offline-pass.png
G1-C-05-reconnect-state-sync-pass.png
```

若使用日志文本而非截图，应在正式报告中给出等价证据路径和说明。

## 4. Gate 2 期间的处理规则

- C 可以直接参加 Gate 2 的真实 PT Telemetry 联调，不需要等待本占位符补齐后才能开发。
- 但 Gate 2 的真实链路成功 **不能自动替代** Gate 1 的 malformed-message、offline、reconnect 等独立稳定性验证。
- 最迟 Gate 5 Freeze 前，本文件必须由 C 更新为真实的 `C_BACKEND_REPORT.md`，并删除 PLACEHOLDER 标记。
- 不得为了补证据修改 `docs/PROTOCOL.md`、设备 ID、WS 路径或消息字段。

## 5. 当前结论

```text
C Gate 1 owner-specific validation: PENDING
Backend software baseline: AVAILABLE
Project scheduling decision: Gate 2 may proceed
Final freeze requirement: placeholder MUST be resolved before Gate 5 COMPLETE
```
