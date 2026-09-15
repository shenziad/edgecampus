# EdgeCampus

**面向多园区智慧校园的边缘—云协同网络控制平台。**

EdgeCampus 将 Packet Tracer 中的总部园区、企业 WAN、Internet 与异地分部，和 SBC 边缘自治、真实主机 FastAPI 控制平面、实时 Dashboard 组合为一个可现场验收的系统。项目核心仍是“感知—边缘决策—云端管理—设备执行”的双控制环；Final Architecture v2 只向现有总部 Core 外扩，不破坏 Gate 1 已验证的 VLAN / Edge 基线。

## Final Architecture v2

```text
                                  INTERNET-SERVER
                                     DNS / HTTP
                                         |
                                      R-ISP
                                      AS65000
                                    /         \
                               eBGP             eBGP
                                /                 \
                           R-HQ                   R-BRANCH
                          AS65001                  AS65002
                             |                        |
                           OSPF                 802.1Q Trunk
                             |                        |
                          SW-CORE                 SW-BRANCH
                             ║                    /       \
                       LACP EtherChannel     BR-OFFICE   BR-ADMIN
                             ║
                          SW-ACCESS
                    /          |           \
                 OFFICE       IOT       MANAGEMENT
                               |
                     TEMP01 → MCU → SBC → FAN01
                               |
                     RealWSClient（带外）
                               |
                     FastAPI ↔ Dashboard
```

最终系统同时承载：总部网络安全分区、Edge 本地自治、真实 Edge→Cloud Telemetry、Cloud→Edge Policy、断云不断控、总部互联网出口、总部—分部业务访问、集中网络管理、OSPF/eBGP、NAT/PAT、DNS/HTTP、IPv6-over-IPv4 Overlay 与 Port Security。

## 关键真实性边界

Packet Tracer 的 VLAN / ACL / Routing / OSPF / BGP / NAT / IPv6 Tunnel 是**模拟企业数据平面**。`EDGE-SBC-01` 使用 Packet Tracer External Network Access / `RealWSClient` 连接宿主机 FastAPI，属于**带外 Edge–Cloud 控制通道**。

因此不得在代码、报告或答辩中声称真实 WebSocket 流量经过 R-HQ、R-ISP、BGP、NAT 或 VLAN 20/30。

`BACKEND-STUB` 是 Packet Tracer 中的 Server-PT，Final Architecture v2 中同时承担 **HQ-SERVICE / CONTROL-PLANE-STUB** 的网络验收角色；它不是真实 FastAPI Backend。

## 当前阶段

- Gate 0：COMPLETE。
- Gate 1：**CLOSED-WITH-PLACEHOLDER**。A、B、D 已有正式结果；A+B 已完成 canonical 集成与回归；C 的 Owner 专属验收证据暂以 `docs/gate1/C_BACKEND_REPORT.md` 占位，必须在 Gate 5 Freeze 前补齐。
- 当前 Gate：**Gate 2**。
- Final Architecture v2 已冻结设计；新增 Branch/WAN 的实际网络配置由 A 从 Gate 2 起按层实施。

当前指挥文件：`docs/CURRENT_GATE.md`。

## 5 分钟软件基线启动

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

浏览器打开 <http://127.0.0.1:8000>。

## Owner

| Owner | 工作目录 | Final Architecture v2 主责 |
|---|---|---|
| A Network | `packet_tracer/`、网络证据 | HQ Core 保持稳定；Branch/WAN、OSPF/BGP、NAT、IPv6 Tunnel、Port Security；唯一 canonical `.pkt` Owner |
| B Edge | `edge/` | TEMP/MCU/SBC/FAN 本地自治、PT Telemetry、Policy/Command、重连 |
| C Control Plane | `backend/` | WebSocket、协议校验、状态、事件、策略转发；补齐 Gate 1 占位验收 |
| D UI & Integration | `dashboard/`、`tests/` | Dashboard、集成测试、端到端证据与演示整合 |

开始任何工作前按顺序阅读：

1. `docs/AI_CONTEXT.md`
2. `docs/CURRENT_GATE.md`
3. `docs/CONTRIBUTING.md`
4. `docs/ARCHITECTURE.md`
5. `docs/PROTOCOL.md`
6. `docs/NETWORK_PLAN.md`
7. `docs/ACCEPTANCE.md`

## 核心业务流

```text
1. Edge Local Loop
   TEMP01 → MCU → SBC → FAN01

2. Cloud Control Loop
   Edge ↔ FastAPI ↔ Dashboard

3. Branch Business Flow
   BR-OFFICE → Enterprise WAN → HQ-SERVICE

4. Remote Operations Flow
   BR-ADMIN → IPv6-over-IPv4 Tunnel → HQ MANAGEMENT

5. Central Administration Flow
   HQ ADMIN → WAN → R-BRANCH / SW-BRANCH

6. Enterprise Internet Flow
   HQ OFFICE → R-HQ PAT → ISP → DNS/HTTP
```

## 常用软件检查

```bash
python -m compileall backend edge tests
python -m unittest discover -s tests -v
```

## 范围边界

Final Architecture v2 不引入 Kubernetes、MQ、数据库、多租户、复杂认证、第二套 IoT 场景或多 Edge 调度。网络扩展的目的，是把前五次组网实验能力有机承载到同一个多园区业务系统中，而不是增加与主线无关的功能。
