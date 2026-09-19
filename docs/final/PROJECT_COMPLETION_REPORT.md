# EdgeCampus 最终完成报告

项目状态：**验收完成，报告准备中 / ACCEPTANCE COMPLETE — REPORT PREPARATION**。归档日期：2026-09-20；分支：`main`。

此状态表示功能开发、仓库整合和项目验收均已完成。21张G4网络原图、9张G4 Edge/Backend/Dashboard原图、NC Managed清单图、A/B/C/D最终证据及课程补强图47–54已经归入当前分支；A01–A30、B01–B12、C01–C15与D01–D13共70张最终截图全部完成。后续完整配置附件和展示彩排记录用于撰写实验报告与准备答辩。

## 本次归档依据

- 用户提供的 [NOC 升级配置报告](source/EdgeCampus_NOC功能升级过程与配置报告.docx)及[原文提取](source/REPORT_TEXT.md)。原始报告没有内嵌截图。
- G4历史报告、[9张Edge/Backend/Dashboard证据索引](../gate4/EVIDENCE_INDEX.md)，以及现已纳入当前分支的21张G4网络原图。
- G4 后本地开发提交：`260192d` Network Agent；`b791bd5` Security Center；`1a54005` Branch/Policy/Simulation；`2069e38` 中文界面与端口说明；`9181ea5` NC 真实读取；`1aaa81d` 真实设备健康与 NOT COLLECTED。
- 用户确认 NC 已连通且 Dashboard 已显示。现归档的 [NC 清单截图](../../evidence/noc/NOC-NC-01-controller-managed-inventory.png)与`evidence/final_report/C/`的C10–C15直接证明 SW-CORE、SW-BRANCH 为 Managed，并记录同次Dashboard/API、NC断连与恢复。
- 本次重新执行的[软件验证](VALIDATION.md)。HTTP fixture/Fake Edge 回归与真实 PT 现场证据分开记录。
- 本次用户提供的正式PT包、最终拓扑和图47–54；逐命令说明、兼容限制及证据映射见[课程重点补强](../COURSE_COVERAGE_PATCH.md)。

## 最终能力与真实作用范围

| 板块 | 最终行为 | 对 PT 的真实作用 |
|---|---|---|
| Edge Control | 温度/FAN 实时展示、AUTO/MANUAL、阈值/迟滞、Policy/Command ACK、断云自治与恢复 | 连接真实 SBC 时可下发已有 Edge Policy/Command，控制 PT FAN；使用 Fake Edge 时只证明软件链路 |
| Network Health / Network Controller | NC 认证、读取设备清单与物理拓扑；名称、管理 IP、类型、collectionStatus；Managed 精确映射 ONLINE | 读取真实 NC API；不写交换机/路由器配置。ONLINE 仅为控制器管理状态 |
| Security Center | 非法 MAC / ACL 阻断模拟、红色事件、次数与恢复审计 | SIMULATED；不注入 PT MAC，不实际关闭端口。真实 Port Security 另按 N15 验收 |
| Branch Operations | R-BRANCH `.65` / SW-BRANCH `.66`，模拟 ADMIN-PC 来源的 VTY ALLOW/DENY | SIMULATED；未发起真实 Telnet/SSH，PASS 不替代 N14 |
| Campus Policy | thermal 来自已有 Backend 策略；保留 thermal-01、严格递增 version 与 ACK；Campus 版本上层展示 | thermal 执行通过真实 Edge ACK 确认；branch_access / iot_isolation / port_security 为配置展示，不下发 IOS |
| Failure Simulation | Cloud 控制通道中断与恢复、安全攻击模拟 | Cloud 按钮实际断开 Edge WS，HTTP 仍运行；自治与 FAN 动作须在 PT 观察。Security 为模拟；Network Failure 禁用，接口 409 |

**OSPF/BGP/Tunnel 均为 NOT COLLECTED**。本版 NC inventory/topology 不提供协议级验收结果，不能从 Managed 推断邻居 FULL、BGP Established、Tunnel UP。真实网络协议采用 IOS 与端到端测试留证。最初 Mock Network 故障演示已被用户要求的真实 NC-only 行为替代，不作为最终功能宣称。

PT 企业 WAN 为模拟数据平面。RealWSClient→FastAPI 与宿主机→NC Real World Access 是不同的带外通道；不声称 WebSocket 经过 PT BGP/NAT。HQ-SERVICE/BACKEND-STUB 不是宿主机 FastAPI。

## 当前G4后网络与NC配置

| 项目 | 用户报告的实际配置 | 证据状态 |
|---|---|---|
| NC-HQ | `192.168.30.30/24`，网关 `192.168.30.1`；GigabitEthernet0→SW-CORE Gi1/0/10，access VLAN30 | C01–C07已归档，含端口、地址、外部访问与Discovery |
| ADMIN-PC | `192.168.30.20`，可访问 NC-HQ | 配置记录已整理；页面/地址按A项清单补拍 |
| R-HQ 管理 | Loopback0 `10.255.255.1/32`，description MANAGEMENT_LOOPBACK；G0/0 保留 OSPF 链路 | G4配置与NC报告均已整理；最终管理路由和running-config按CFG附件导出 |
| 设备 CLI | 本地用户名认证、VTY 0–4 `login local`、`transport input telnet` | SW-CORE与SW-BRANCH最终ACL/VTY截图已归档；完整运行配置仍按CFG01–CFG06导出 |
| VTY-HQ-ADMIN | SW-CORE/SW-BRANCH permit host `.30.20` 与 `.30.30`，deny any | C17最终截图及V01正负向回归已归档 |
| 已有直接截图 | SW-CORE `192.168.30.1` / MultiLayerSwitch；SW-BRANCH `172.16.40.66` / Switch；均 Managed | 原图与C10–C15已入库；其余设备Unsupported，未改写为在线 |

## 课程重点补强增量

| 能力 | 当前最终实现 | 证据 |
|---|---|---|
| EtherChannel | Core/Access两端静态`mode on`，Po1(SU)、Protocol `-`、成员(P) | 图47 |
| Branch出口策略 | VLAN40来源PAT；到Internet Server的ICMP拒绝、TCP/80允许 | 图48、49a、49b |
| OSPF广播网段 | VLAN100 `10.255.0.0/29`；Core为DR，R-HQ/R-COURSE为两个FULL/DROTHER | 图50a、50b |
| 路由重分发实验 | R-COURSE/R-TEST隔离OSPF44/BGP65144/65154；Core学习O E2/Type-5，R-TEST获O*E2默认路由 | 图51、52a、52b |
| Port Security | Fa0/1与Fa0/3双端口sticky/maximum1/restrict；非法接入计数与恢复 | 图53、54拓扑、54a、54b |

Packet Tracer 2911不支持prefix-list、route-map和distribute-list，因此课程重分发没有伪造这些命令，而是通过独立协议域限制影响范围。生产WAN AS65001/65000/65002仍不做完整BGP表到OSPF的广泛重分发。

报告中 CLI 段落被压平，不自动作为脚本执行。本次未操作 PT、未写 IOS、未自动运行 Discovery。用户名/VTY ACL 的真实设备覆盖范围、Loopback 路由与 `access-class … in` 绑定，以最终 running-config 为准。

## 阶段结论

| 阶段 | 收尾状态 |
|---|---|
| G0–G2 | 既有完成基线和历史证据保留 |
| G3 | 功能整合完成，历史网络与Edge证据保留 |
| G4 | 功能完成；21张网络图和9张软件侧图已纳入当前分支 |
| G4后NOC | 五大板块完成；真实NC Managed清单原图已归档 |
| 最终报告 | 仓库现有195张证据图片；A/B/C/D共70张最终截图已完成；继续整理CFG01–CFG08和展示彩排记录 |
| 项目总状态 | **验收完成，报告准备中** |

## 最新交付包

`packet_tracer/EdgeCampus.pkt` 是本次发布采用的唯一正式PT包。

- 大小：156,539 bytes。
- SHA-256：`4f53c07e45ea66ea96bd83b42b751cb3cfb41c354c9f9489ae4358f4cdf1634c`。
- 当前包已纳入 `main`；现场保存重开和包内程序一致性已按A29/A30、B01–B05留证。
- 原始 DOCX SHA-256：`ce6f10931e090d52e9e004fc191a46d8084e1c1976da7901e6709fb185b50e6b`。
- 147,803 bytes及更早的136,138 bytes包均为历史版本；不再当作当前包。
- 哈希用于锁定发布二进制；现场可运行性和最终行为以逐张截图及配置附件为准。
- 2026-09-20新增截图未修改该二进制包；SW-CORE/SW-BRANCH的本次CLI画面证明当次运行配置，不单独证明这些命令已持久化到上述哈希对应的正式包。

## 启动与收尾入口

先打开最新 `.pkt`，启用 NC REST External Access 与 Real World Access（58000），运行真实 SBC Gate4 程序（`ws://127.0.0.1:8000/ws/edge`），再在 PowerShell 启动：

```powershell
Set-Location 'D:\Develop\sommerom\bighomework\edgecampus-g3'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_pt_backend.ps1 -ControllerPort 58000 -BackendPort 8000
```

输入 NC 的 Web/API 管理员账户，不混用设备 Discovery CLI 凭据。打开 `http://127.0.0.1:8000`。真实 PT 留证时不启动 Fake Edge。本次没有启动长期 Backend 服务。

完整报告素材要求见 [逐张操作清单](../FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)和[报告素材准备索引](EVIDENCE_PENDING.md)；展示流程见 [DEMO_SCRIPT.md](../DEMO_SCRIPT.md)。整理后更新素材索引，不重命名未拍摄图片为 PASS，也不混淆真实能力与模拟/展示能力。
