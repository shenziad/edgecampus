# Gate 1 — D UI & Integration Report



## 1. Owner



- Module: D — UI & Integration

- Branch: `feat/dashboard`

- Scope: `dashboard/`, UI / integration validation, Dashboard evidence

- Gate: Gate 1 — 四模块独立运行



本阶段未修改 A Network、B Edge、C Control Plane 的实现，也未修改 Public Contract。



---



## 2. Gate 1 Goal



D 模块在 Gate 1 的目标是：



> 不依赖真实 Packet Tracer，使用 Backend + fake edge 即可独立展示

> EdgeCampus 当前状态、温度、风扇、告警、事件及策略界面。



本阶段不要求真实 `TEMP01 → SBC → Backend → Dashboard`

端到端链路，也不要求 Dashboard 策略实际作用于 Packet Tracer Edge。



---



## 3. Validation Environment



Dashboard 使用现有 FastAPI Backend 提供页面和 WebSocket 服务。



启动 Backend：



```powershell

python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

