# 最终待补证据索引

基准日期：2026-09-19。项目状态：**完成（待补证据）**；正式分支：`feat/edge`。

## 1. 已有证据

[最终报告素材总清单](../FINAL_REPORT_SCREENSHOT_CHECKLIST.md)已经逐项登记73张可直接复用的原图，全部位于当前分支：

- G1–G3网络、Edge、Backend和Dashboard历史证据；
- 21张G4网络原图，来源提交 `4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8`；
- 9张G4 Edge/Backend/Dashboard恢复与鲁棒性证据；
- NC-HQ设备清单原图，其中SW-CORE、SW-BRANCH为Managed。

已有证据直接按总清单给出的本地路径引用，不重复截图。

## 2. 明确待拍范围

待拍范围固定为**25组、70张PNG**。执行入口为[四人逐张截图操作清单](../FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)：

| 人员 | 图号 | 张数 | 内容 |
|---|---|---:|---|
| A | A01–A30 | 30 | 最终拓扑、DNS/HTTP、VTY/ACL、终端地址、DHCP/SLAAC、IPv4/IPv6通信、真实Telnet、保存重开 |
| B | B01–B12 | 12 | 包内MCU/SBC程序、Policy ACK、Command ACK、真停Backend自治、重启同步 |
| C | C01–C15 | 15 | NC接口/地址/外部访问、Backend端口、真实设备/API、拓扑返回、NC失联恢复 |
| D | D01–D13 | 13 | 中文Dashboard、Branch检查、Campus策略、安全事件、Cloud故障恢复、Network Failure禁用/409 |

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

## 4. 最终彩排记录

A在自己的完整项目中使用当前正式PT包和当前提交，连续完成三轮演示。每轮记录日期、包哈希、软件提交、策略版本、预期、实际结果及证据路径。演示流程见[DEMO_SCRIPT](../DEMO_SCRIPT.md)。

未取得的PNG、配置附件和三轮记录保持待补；取得后按实际文件路径更新总清单。
