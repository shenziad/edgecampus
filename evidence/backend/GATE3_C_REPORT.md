# Gate 3 — C Control Plane Policy / Command

> 状态：**C 段 Policy 写入 + Command 转发 PASS；真 PT policy_ack / 32℃-OFF / 34℃-ON 待 B 闭环**  
> Owner：C  
> 分支：`feat/backend`  
> 公共接口影响：**无**（未改 Protocol v1.0，未改业务代码）

## 证明范围

C 本 Gate 负责：

```text
Dashboard policy/command
  → /ws/dashboard
  → Backend 校验并仅在 Edge 在线时转发
  → /ws/edge
  → 更新 SystemState / events
  → /api/state 与 Dashboard snapshot
```

不负责改 SBC 脚本，不负责宣布整关 B+C+D PASS。

## 实测

环境：本机 FastAPI `0.0.0.0:8000`，Edge 在线（`healthz.edge_online=true`）。

| 项 | 结果 |
|---|---|
| 启动阈值 30 → 33，「下发新策略」 | `/api/state`：`threshold_c=33`，`version=3`（多次下发导致 version>2，合法递增） |
| Dashboard | 启动阈值 33，Policy Version v3，AUTO |
| 手动开启 FAN01 | 事件 `COMMAND_SENT` / `REMOTE-MANUAL` / `FAN01 ON`；`FAN` / `REMOTE-MANUAL` / `ON` |
| `/api/state` | `fan_state=ON`，`edge_online=true`，策略仍为 33 / v3 |

未改 `backend/` 源码。页面输入框在 Edge 离线或未点击「下发新策略」时会回到旧阈值，这是 snapshot 回写，不是表单损坏。

## 证据

目录：`evidence/backend/`

| 文件 | 内容 |
|---|---|
| `G3-C-01-healthz-edge-online-pass.png` | `edge_online:true` |
| `G3-C-02-dashboard-policy-v3-33-pass.png` | 页面阈值 33、v3 |
| `G3-C-03-api-state-policy-v3-33-pass.png` | snapshot policy 33 / version 3 |
| `G3-C-04-command-fan-on-remote-manual-pass.png` | `fan_state=ON` |
| `G3-C-04b-events-remote-manual-on-pass.png` | `REMOTE-MANUAL` 事件（若已归档） |

未交：`EDGE_OFFLINE` 拒发策略（可选，Gate 5 前可与 G1 稳定性一并补）。

## 结论

```text
C Gate 3：Dashboard Policy 已写入 Backend state = PASS
C Gate 3：Dashboard FAN Command 已写入 Backend state / events = PASS
整关软件 PASS 仍需真实 Edge policy_ack，以及 32 C OFF / 34 C ON
```
