# EdgeCampus

**面向多园区智慧校园的边缘—云协同网络控制平台。**

EdgeCampus 将 Packet Tracer 中的总部园区、企业 WAN、Internet 与异地分部，和 SBC 边缘自治、真实主机 FastAPI 控制平面、实时 Dashboard 组合为一个可现场验收的系统。核心是“感知—边缘决策—云端管理—设备执行”的双控制环；Final Architecture v2 只向已验证 HQ Core 外扩，不破坏 Gate 1/2 基线。

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

最终系统覆盖总部安全分区、Edge 本地自治、真实 Edge→Cloud Telemetry、Cloud→Edge Policy/Command、断云不断控、总部互联网出口、总部—分部业务访问、OSPF/eBGP、NAT/PAT、DNS/HTTP、IPv6-over-IPv4 Overlay、Port Security 与集中管理。

## 当前项目状态

- Gate 0：**COMPLETE**。
- Gate 1：**CLOSED-WITH-PENDING-STABILITY**。A/B/D 与 A+B 集成通过；C 核心验收已补，仍有 malformed/offline/reconnect 三项稳定性证据须在 Gate 5 前清零。
- Gate 2：**COMPLETE**。Branch/WAN IPv4 基础层以及真实 `TEMP01 → Dashboard` 全链路均已通过。
- 当前 Gate：**Gate 3 — Policy Loop + WAN Business**。

当前唯一指挥文件：`docs/CURRENT_GATE.md`。

## Gate 2 已验证基线

网络线：

```text
HQ Core → R-HQ → R-ISP → R-BRANCH → SW-BRANCH
                    |
             INTERNET-SERVER
```

已完成 Branch VLAN40/50、ROAS、DHCP/管理地址、四段 IPv4 Underlay 相邻可达和 HQ Gate1 regression。

软件 / IoT 线：

```text
TEMP01 → MCU → EDGE-SBC-01
          ├→ Local AUTO → FAN01
          └→ RealWSClient → FastAPI → Dashboard
```

真实正常/告警温度、FAN OFF/ON、SENSOR/EDGE-AUTO 事件和 Heartbeat 已实测。

Gate 2 集成报告：`docs/gate2/INTEGRATION_REPORT.md`。

## Gate 3 主线

A Network：

```text
OSPF → eBGP → BR-OFFICE→HQ-SERVICE
     → HQ PAT → DNS/HTTP → Static TCP/80 → Business ACL
```

B/C/D：

```text
Dashboard Policy / Command
        ↓
Backend
        ↓
Real Edge
        ↓
policy_ack / command_ack
        ↓
Dashboard
```

核心 Policy 验收目标：threshold 30→33、version 1→2；真实 32 C 时 FAN OFF、34 C 时 FAN ON。

## 真实性边界

Packet Tracer 的 VLAN / ACL / Routing / OSPF / BGP / NAT / IPv6 Tunnel 是**模拟企业数据平面**。`EDGE-SBC-01` 通过 Packet Tracer External Network Access / `RealWSClient` 连接宿主机 FastAPI，属于**带外 Edge–Cloud 控制通道**。

不得声称真实 WebSocket 流量经过 R-HQ、R-ISP、BGP、NAT 或 PT VLAN20/30。

`BACKEND-STUB` 是 Packet Tracer 中用于验证总部业务/管理路径的 Server-PT（HQ-SERVICE / CONTROL-PLANE-STUB），不是真实 FastAPI Backend。

## Owner

| Owner | 负责范围 |
|---|---|
| A Network | `packet_tracer/`、网络 evidence、唯一 canonical `.pkt` Owner |
| B Edge | `edge/`、PT Edge 控制器与 Edge evidence |
| C Control Plane | `backend/`、Backend evidence |
| D UI & Integration | `dashboard/`、`tests/`、UI/集成 evidence |

开始工作前按顺序阅读：

1. `docs/AI_CONTEXT.md`
2. `docs/CURRENT_GATE.md`
3. `docs/CONTRIBUTING.md`
4. `docs/ARCHITECTURE.md`
5. `docs/PROTOCOL.md`
6. `docs/NETWORK_PLAN.md`
7. `docs/ACCEPTANCE.md`

## 软件基线启动

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

开发替身：

```powershell
python -m edge.fake_edge
```

Dashboard：`http://127.0.0.1:8000`

## 常用检查

```bash
python -m compileall backend edge tests
python -m unittest discover -s tests -v
```

## 范围边界

Final Architecture v2 不引入 Kubernetes、MQ、数据库、多租户、复杂认证、第二套 IoT 场景或多 Edge 调度。新增能力必须服务于课程网络能力或双控制环验收，不做无关功能堆叠。
