# EdgeCampus

面向智慧园区的边缘—云协同网络控制平台。项目把 Packet Tracer 园区网络、SBC 边缘自治、FastAPI 控制平面与实时 Dashboard 组合成一个可现场验收的闭环系统。

## 当前基线

- 已冻结设备 ID、消息字段、WebSocket 路径和默认策略。
- 后端可接收 Edge 遥测/心跳并向 Dashboard 广播。
- `fake_edge.py` 可在没有 Packet Tracer 时完成端到端联调。
- Dashboard 支持温度、风扇、在线状态、事件流、策略下发和手动控制。
- Packet Tracer 拓扑与 SBC 适配器保留了明确的实现入口。
- 测试证据、验收脚本、团队分工和 AI 协作红线已统一。

## 5 分钟启动（Windows / Linux）

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

另开一个终端：

```powershell
.venv\Scripts\Activate.ps1
python -m edge.fake_edge
```

浏览器打开 <http://127.0.0.1:8000>。拖动模拟温度、修改阈值或控制风扇即可验证闭环。

## 团队入口

| Owner | 工作目录 | 首要文档 |
|---|---|---|
| A Network | `packet_tracer/`、`docs/NETWORK_PLAN.md` | 网络地址、VLAN、ACL 与拓扑 |
| B Edge | `edge/` | 本地自治、PT 适配、断线重连 |
| C Control Plane | `backend/` | WebSocket、状态、策略和日志 |
| D UI & Integration | `dashboard/`、`tests/` | 页面、联调、验收证据 |

开始工作前必须先读：

1. `docs/AI_CONTEXT.md`
2. `docs/PROTOCOL.md`
3. `docs/CONTRIBUTING.md`
4. 自己负责模块的文档

## 最小验收闭环

```text
温度变化 → Edge 自动判断 → Fan 动作 → Backend 汇聚 → Dashboard 实时显示
Dashboard 下发阈值 → Edge 更新策略 → 返回 ACK → 使用新阈值控制
Backend 停止 → Edge 保持本地自治 → Backend 恢复 → Edge 重连并同步状态
```

完整 Gate 和现场演示顺序见 `docs/ACCEPTANCE.md` 与 `docs/DEMO_SCRIPT.md`。

## 常用检查

```bash
python -m compileall backend edge tests
python -m unittest discover -s tests -v
```

## 范围边界

首版只承诺 3 个安全域、1 个温度传感器、1 个风扇、AUTO/MANUAL、阈值策略、心跳和断线重连。烟雾、门禁、MQTT、数据库和多节点调度均属于 Gate 5 之后的增强项。
