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

**完成（待补证据） / COMPLETE — EVIDENCE PENDING**，更新于 2026-09-18。

G4 后 NOC 开发收尾，真实 NC 接入已由用户确认。Network Health 使用真实清单，Managed→ONLINE；OSPF/BGP/Tunnel NOT COLLECTED。Security/Branch 为模拟，Campus Network/Security 为展示层，Network Failure 模拟已禁用。G3/G4 缺证及最终包复核、G5 三轮彩排仍待完成，不宣称已通过全部最终验收。

- [最终完成报告](docs/final/PROJECT_COMPLETION_REPORT.md)
- [全部待补证据：28 组](docs/final/EVIDENCE_PENDING.md)
- [软件验证](docs/final/VALIDATION.md)与[NOC 最终说明](docs/NOC_UPGRADE.md)
- [真实 NC 启动/配置](docs/PT_CONTROLLER_SETUP.md)与[现场演示](docs/DEMO_SCRIPT.md)

当前指挥文件：[CURRENT_GATE](docs/CURRENT_GATE.md)。分支继续 `feat/edge`，本次本地归档，不推送。

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

## G4 及之后收尾

G4 用户确认实测，9 张真实图已归档；网络 N12–N15、离线 OFF/物理输出、恢复 Dashboard 与最终回归待补。NOC 已增加中文五板块及真实 NC 只读采集。最新用户包 144326 bytes 原样归档，最终打开/源码一致性与三轮彩排仍待执行。详情见最终完成报告和补证清单。

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
