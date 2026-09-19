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

**验收完成，报告准备中 / ACCEPTANCE COMPLETE — REPORT PREPARATION**，更新于 2026-09-19。

当前 `feat/edge` 已整合五大NOC板块、真实Packet Tracer Network Controller只读采集、中文Dashboard、真实Edge Policy/Command/ACK、断云自治与恢复，以及五次实验的最终网络配置说明。Network Health以NC真实清单为准：Managed→ONLINE，OSPF/BGP/Tunnel显示NOT COLLECTED；Security/Branch是演示适配器，Campus Network/Security是上层策略展示，Network Failure已禁用。

- [最终配置总览](docs/FINAL_CONFIGURATION.md)
- [五次实验技术映射](docs/EXPERIMENT_MAPPING.md)
- [最终功能演示设计](docs/FINAL_FUNCTION_DEMO.md)
- [最终报告素材总清单](docs/FINAL_REPORT_SCREENSHOT_CHECKLIST.md)
- [四人逐张截图操作清单](docs/FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)
- [前五次实验报告补拍的5张图](docs/EXPERIMENT_EVIDENCE_COVERAGE.md)
- [最终完成报告](docs/final/PROJECT_COMPLETION_REPORT.md)与[软件验证](docs/final/VALIDATION.md)

当前仓库已正式收录21张G4网络原图、既有Edge/Backend/Dashboard证据和NC Managed清单原图。项目功能已经完成验收；后续25组、70张PNG、CFG01–CFG08配置附件和展示彩排记录均用于撰写报告、制作图表和准备答辩，不再作为项目验收门槛。

当前正式分支为 `feat/edge`，远程同名分支作为交付分支。`packet_tracer/EdgeCampus.pkt` 是唯一正式PT包，当前大小147803 bytes，SHA-256 `6d6c154415700ff750cabe41272b0f1f5aa46f2d8ee341c3336625175fa7a4ba`。

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

## Gate 3 已整合能力（补证待完成）

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

实际 Policy 核心证据为 v3/33 C，最终 Backend 图为 v5；连续联调版本正常递增。B 已验证 31.8 C FAN OFF、34.9 C FAN ON。Dashboard ACK 修复后证据待补。

## G4及NOC最终状态

G4的21张网络验证原图和9张Edge/Backend/Dashboard原图已经归档到当前分支。它们覆盖远程管理、Port Security、IPv6地址分配、Tunnel、路由表、N1–N11回归及NAT共存修复。G4后增加的真实NC采集和中文NOC软件已经完成；当前只剩最终报告要求的明确截图、完整配置导出和连续彩排记录。

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

## 真实 PT + NC 启动

先在 PT 启用 NC External Access/Real World Access（58000），运行真实 SBC 程序（WS 8000）；在仓库根目录：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_pt_backend.ps1 -ControllerPort 58000 -BackendPort 8000
```

输入 NC Web/API 账户，打开 `http://127.0.0.1:8000`。当前本机已有 `runtime/noc-venv`；其他机器环境安装见 PT_CONTROLLER_SETUP。Fake Edge 是独立开发替身，不与真实 PT 同时连接同一 Backend，也不用于现场真实证据。

## 常用检查

```bash
python -m compileall backend edge tests
python -m unittest discover -s tests -v
```

## 范围边界

Final Architecture v2 不引入 Kubernetes、MQ、数据库、多租户、复杂认证、第二套 IoT 场景或多 Edge 调度。新增能力必须服务于课程网络能力或双控制环验收，不做无关功能堆叠。

## Gate4 当前归档索引（2026-09-17）

报告见 `docs/gate4/`：A/B/C/D/BCD 报告、EVIDENCE_INDEX、VALIDATION_REPORT。Protocol 1.0 与冻结网络规划未改变。
