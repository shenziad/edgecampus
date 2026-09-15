# Gate 1 — C Control Plane Validation Report

> 状态：**CORE PASS / STABILITY PENDING**  
> Owner：C Control Plane  
> 分支：`feat/backend`  
> 架构基线：Final Architecture v2 / Protocol v1.0  
> 公共接口影响：**无**

本文件替换原 PLACEHOLDER。  
Gate 1 验收句（`fake_edge` → `/api/state` 可见遥测）已举证。  
官方额外三项（malformed / offline / reconnect）仍待补，Gate 5 前清零。  
Gate 2 真 PT 遥测见同目录说明与 `evidence/backend/G2-C-*.png`，不能自动替代上述三项。

---

## 1. 完成内容

- 未修改 `backend/` 业务代码，未修改 Protocol v1.0。
- 本机完成 Backend 启动、fake_edge 接入、`/healthz`、`/api/state`。
- 向 `feat/backend` 提交 Gate 1 运行证据 `G1-01`～`G1-07`。
- 后续在同一 Backend 上完成真实 PT Telemetry 接入（见第 10 节）。

## 2. 环境

| 项 | 值 |
|---|---|
| 仓库 | `https://github.com/shenziad/edgecampus.git` |
| 本地 | `C:\Users\33621\edgecampus` |
| 分支 | `feat/backend` |
| Python | `.venv\Scripts\python.exe`（不可使用 MSYS2 的 `python`） |
| Backend | `http://127.0.0.1:8000` |
| Edge WS | `ws://127.0.0.1:8000/ws/edge` |
| 默认策略 | AUTO / 30.0 C / hysteresis 1.0 C / version 1 |

## 3. 运行命令

```bat
cd C:\Users\33621\edgecampus
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
.venv\Scripts\python.exe -m edge.fake_edge --temperatures 27,29,30,32,34,31,28,26 --interval 3
curl.exe -s http://127.0.0.1:8000/healthz
curl.exe -s http://127.0.0.1:8000/api/state
```

Gate 2 联调期间不要同时运行 fake_edge。

## 4. Gate 1 验收对照

| 要求 | 结果 | 证据 |
|---|---|---|
| `/healthz` | PASS | `evidence/backend/G1-04-healthz-pass.png` |
| fake_edge → `/ws/edge` | PASS | `G1-02`、`G1-03` |
| `/api/state` 反映 online/温度/风扇/策略 | PASS | `G1-05`、`G1-06` |
| 9 项单元测试 | PASS | `G1-01-unittest-pass.png` |
| AUTO 风扇事件入库 | PASS | `G1-07` |
| malformed 拒绝且不崩溃 | PENDING | — |
| 停止 Edge → offline | PENDING | — |
| 重连 + state_sync | PENDING | — |

## 5. Gate 1 截图说明

| 文件 | 证明 |
|---|---|
| G1-01 | `Ran 9 tests` / `OK` |
| G1-02 | `/ws/edge` accepted + `edge connected` |
| G1-03 | Fake Edge `Cloud connected`，AUTO ON/OFF |
| G1-04 | `healthz` + `edge_online:true` |
| G1-05 | snapshot 含温度与 SENSOR 事件 |
| G1-06 | 第二帧温度/心跳变化 |
| G1-07 | `FAN` / `EDGE-AUTO` ON 与 OFF |

官方预留名映射：`G1-C-01`←G1-04，`G1-C-02`←G1-03+G1-05+G1-06；`G1-C-03/04/05` 仍缺。

## 6. 排错

- 仅 socket accept 不等于遥测入库。
- CMD 中 `Activate.ps1` 不会切换解释器；必须用 `.venv\Scripts\python.exe`。
- 远程 `feat/backend` 有更新时先 `git pull --rebase`，禁止 force push。

## 7. Git

```text
origin: https://github.com/shenziad/edgecampus.git
branch: feat/backend
Gate1 evidence commit: b8b681d
未合入 main
无 backend 业务代码变更
```

## 8. Gate 1 结论

```text
C Gate 1 核心验收句：PASS
C Gate 1 稳定性三项：PENDING
不阻塞 Gate 2
Gate 5 前必须清零 PENDING 项
```

## 9. 下一动作

- 补 `G1-C-03` / `G1-C-04` / `G1-C-05`。
- 保持 Backend 给 D 做 Dashboard 真温度展示。
- 不在本阶段做 Policy/Command（G3）或正式断云（G4）。

## 10. Gate 2 进展（记录，不替代第 8 节）

已验证：

```text
PT TEMP01 环境温度 ≈32 C
→ EDGE-SBC-01 RealWSClient ws://127.0.0.1:8000/ws/edge
→ FastAPI /api/state 事件出现 31.8 C SENSOR
→ SBC：TX TELEMETRY TEMP=31.8 C，FAN=ON
```

环境曲线回落后快照可为 26.3 C / FAN OFF，属于迟滞关风扇，不是链路失败。

证据：`evidence/backend/G2-C-01`～`G2-C-04`。  
详细过程见 `evidence/backend/GATE2_C_REPORT.md`。
