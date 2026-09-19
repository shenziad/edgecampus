# 最终报告素材准备索引

基准日期：2026-09-20。项目状态：**验收完成，报告准备中**；正式分支：`main`。

## 1. 已有证据

[最终报告素材总清单](../FINAL_REPORT_SCREENSHOT_CHECKLIST.md)已经逐项登记当前证据；仓库`evidence/`现有195张图片，全部位于当前分支：

- G1–G3网络、Edge、Backend和Dashboard历史证据；
- 21张G4网络原图，来源提交 `4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8`；
- 9张G4 Edge/Backend/Dashboard恢复与鲁棒性证据；
- NC-HQ设备清单原图，其中SW-CORE、SW-BRANCH为Managed。
- A/B/C/D最终报告证据共70张，A01–A30、B01–B12、C01–C15、D01–D13已经全部完成；
- 图47–54课程重点补强证据，包括静态EtherChannel、Branch PAT/ACL、双DROTHER、隔离重分发及双端口Port Security。

已有证据直接按总清单给出的本地路径引用，不重复截图。

## 2. 报告截图完成状态

原计划范围为**25组、70张PNG**，现已全部归档。复现入口为[四人逐张截图操作清单](../FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)：

| 人员 | 图号 | 张数 | 内容 |
|---|---|---:|---|
| A | A01–A30 | 30/30 | 最终拓扑、DNS/HTTP、VTY/ACL、终端地址、DHCP/SLAAC、IPv4/IPv6通信、真实Telnet、保存重开 |
| B | B01–B12 | 12/12 | 包内MCU/SBC程序、Policy ACK、Command ACK、真停Backend自治、重启同步 |
| C | C01–C15 | 15/15 | NC接口/地址/外部访问、Backend端口、真实设备/API、拓扑返回、NC失联恢复 |
| D | D01–D13 | 13/13 | 中文Dashboard、Branch检查、Campus策略、安全事件、Cloud故障恢复、Network Failure禁用/409 |

每张图的文件名、点击路径、输入命令和预期现象均在四人清单中固定。五次实验需要额外补强的5张图另见[实验功能补图清单](../EXPERIMENT_EVIDENCE_COVERAGE.md)。

## 3. 配置附件

除PNG外，还需保存以下附件：

- CFG01：SW-CORE完整配置及VLAN/Trunk/Po1状态；
- CFG02：SW-ACCESS完整配置及VLAN/Po1/Port Security状态；
- CFG03：R-HQ完整配置及OSPF/BGP/NAT/Tunnel/VTY状态；
- CFG04：R-ISP完整配置及BGP状态；
- CFG05：R-BRANCH完整配置及ROAS/DHCPv6/BGP/Tunnel/VTY状态；
- CFG06：SW-BRANCH完整配置及VLAN/Trunk/管理状态；
- CFG07：所有主机、服务器、NC和SBC地址/服务表；
- CFG08：PT包内实际运行的MCU/SBC源码导出；
- CFG09：Backend、Dashboard、NC适配器、协议和启动脚本，已在仓库。

配置导出的具体命令见[四人清单](../FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)和[配置总览](../FINAL_CONFIGURATION.md)。

## 4. 报告展示彩排记录

A可在自己的完整项目中使用当前正式PT包和当前提交，连续完成三轮展示演练。每轮记录日期、包哈希、软件提交、策略版本、预期、实际结果及素材路径。演示流程见[DEMO_SCRIPT](../DEMO_SCRIPT.md)。

70张PNG已经整理完成。尚未整理的CFG01–CFG08配置附件和三轮记录仍属于报告素材，不改变“验收完成”的项目状态；取得后按实际文件路径更新总清单。

### A 组证据完成状态

**A01–A30 已完成（30/30）**。正式报告证据已保存至 `evidence/final_report/A/`。

2026-09-20补齐：

1. `evidence/final_report/A/C17-management-final-swcore-acl.png`
2. `evidence/final_report/A/C17-management-final-swcore-vty.png`
3. `evidence/final_report/A/C17-management-final-swbranch-acl.png`

三张图确认SW-CORE/SW-BRANCH使用`VTY-HQ-ADMIN`；允许ADMIN-PC `192.168.30.20`与NC-HQ `192.168.30.30`，显式`deny any`；SW-CORE VTY 0–4已绑定该ACL并采用`login local`与Telnet。

### C 组证据完成状态

**C01–C15 已完成（15/15）**。正式报告证据已保存至 `evidence/final_report/C/`。

已覆盖NC-HQ的VLAN30接入、`.30.30/24`与网关、REST External Access、58000监听、Discovery结果、Backend/Edge WS启动、8000/58000运行状态、真实设备表/API、物理拓扑返回，以及NC关闭后的UNAVAILABLE与恢复后的CONNECTED对照。拓扑真实返回`links=[]`，未伪造链路。

### B 组证据完成状态

**B01–B12 已完成（12/12）**。正式报告证据已保存至 `evidence/final_report/B/`。

已覆盖：

- B01–B05：MCU/SBC 程序配置、AUTO 本地控制、重连状态同步代码与实际运行日志；
- B06：AUTO/33/1 策略下发，Policy ACK `APPLIED`；
- B07–B08：MANUAL 模式 FAN OFF/ON，Command ACK `APPLIED`，物理 FAN `state=0/2`；
- B09–B10：Backend 8000 端口监听数量为 0 时，SBC 保留最后有效 AUTO/33/1 策略并离线执行 `TURN_ON` / `TURN_OFF`，物理 FAN `state=2/0`；
- B11：Backend 重启后自动重连并通过 `STATE_SYNC` 恢复断云前策略状态；
- B12：恢复后 Dashboard 显示 Edge `ONLINE`、Cloud `CONNECTED`，实时温度/FAN 与 SBC Console 一致。

最终证据文件：

1. `evidence/final_report/B/C20-pt-program-config-mcu.png`
2. `evidence/final_report/B/C20-pt-program-config-sbc-params.png`
3. `evidence/final_report/B/C20-pt-program-config-sbc-loop.png`
4. `evidence/final_report/B/C20-pt-program-config-sbc-sync.png`
5. `evidence/final_report/B/C20-pt-program-running.png`
6. `evidence/final_report/B/F06-policy-ack.png`
7. `evidence/final_report/B/F07-command-ack-off.png`
8. `evidence/final_report/B/F07-command-ack-on.png`
9. `evidence/final_report/B/F09-offline-fan-on-attributes.png`
10. `evidence/final_report/B/F09-offline-fan-off.png`
11. `evidence/final_report/B/F11-dashboard-recovered.png`
12. `evidence/final_report/B/F11-edge-recovered.png`


### D 组证据完成状态

**D01–D13 已完成（13/13）**。正式报告证据已保存至 `evidence/final_report/D/`。

已覆盖：

- D01：最终中文 Dashboard 首屏，Edge `ONLINE`、Cloud `CONNECTED`、实时温度/FAN 与真实 NC 数据同屏；
- D02–D04：Branch Router/Switch 运维检查及非管理员来源 `DENIED / DENY / SIMULATED`；
- D05：Campus 三类策略展示，Edge thermal-01 v2 / 33 C / AUTO 与 Policy ACK `APPLIED`；
- D06–D08：Port Security 模拟攻击/恢复与 ACL_BLOCK_EVENT，保留模拟来源标签；
- D09–D11：Cloud Failure 实际断开 Edge WebSocket、离线本地 AUTO 触发 FAN ON，以及恢复后的 `CLOUD RECONNECTED + STATE_SYNC + SUCCESS`；
- D12–D13：真实 NC 模式下 Network Failure 控件禁用，并由 `POST /api/simulation/network` 返回 409 证明不混用模拟网络状态。

最终证据文件：

1. `evidence/final_report/D/U02-noc-overview-01.png`
2. `evidence/final_report/D/U08-branch-check-router.png`
3. `evidence/final_report/D/U08-branch-check-switch.png`
4. `evidence/final_report/D/U08-branch-check-denied-api.png`
5. `evidence/final_report/D/U09-campus-policy.png`
6. `evidence/final_report/D/U06-security-attack.png`
7. `evidence/final_report/D/U06-security-restored.png`
8. `evidence/final_report/D/U07-acl-block-event.png`
9. `evidence/final_report/D/U10-cloud-ws-failure.png`
10. `evidence/final_report/D/U10-cloud-ws-local-fan.png`
11. `evidence/final_report/D/U10-cloud-ws-restored.png`
12. `evidence/final_report/D/U11-network-simulation-disabled.png`
13. `evidence/final_report/D/U11-network-disabled-api.png`
