# Gate 2 — C Control Plane Real Telemetry

> 状态：**C 段 PASS（真温度已入 Backend）；整关待 D 页面确认**  
> Owner：C  
> 分支：`feat/backend`  
> 公共接口影响：**无**

## 目标

```text
TEMP01 → MCU → EDGE-SBC-01 → RealWSClient
      → ws://127.0.0.1:8000/ws/edge
      → FastAPI /api/state
```

C 通过标准：`/api/state` 反映真实 TEMP01，且 fake_edge 路径仍可用。

## 启动

```bat
cd C:\Users\33621\edgecampus
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

联调不加 `--reload`，不开 `fake_edge`。  
同一台电脑 PT 使用 `ws://127.0.0.1:8000/ws/edge`。  
Radmin VPN 对端使用 `ws://26.181.160.200:8000/ws/edge`。

## 操作

1. 启动 Backend。
2. Packet Tracer 打开 EdgeCampus 拓扑，EDGE-SBC-01 运行 Gate 2 SBC 脚本。
3. `/healthz` 出现 `edge_online:true`；初始温度约 9.1 C（未改环境）。
4. Shift+E 打开 Environment，Location 选 `Corporate Office`，Edit Ambient Temperature 至约 32 C。
5. SBC 控制台：`LOCAL TEMP: 31.8 C`，`FAN=ON`，`TX TELEMETRY: TEMP=31.8 C`。
6. `/api/state` 事件出现 `31.8 C` / `SENSOR`。
7. 环境曲线回落后温度可降到 26.3 C，事件出现 `FAN / EDGE-AUTO / OFF`（迟滞，预期）。

## 证据

| 文件 | 内容 |
|---|---|
| `G2-C-01-healthz-edge-online-pass.png` | `edge_online:true` |
| `G2-C-02-api-state-real-pt-temp-pass.png` | 真温度事件 31.8 C |
| `G2-C-03-pt-environment-32-pass.png` | 环境温度 keyframe 32 |
| `G2-C-04-sbc-tx-telemetry-pass.png` | SBC 发送 31.8 C 且 FAN ON |

目录：`evidence/backend/`。

## 结论

```text
C Gate 2：真 PT telemetry 进入 Backend = PASS
Dashboard 展示 = D Owner，C 保持 Backend 在线即可
未改 Protocol / 未改 backend 业务代码
```
