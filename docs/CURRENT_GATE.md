# 项目收尾 — 完成（待补证据）

> 项目总状态：**COMPLETE — EVIDENCE PENDING / 完成（待补证据）**
> 更新：2026-09-18；用户指定分支：`feat/edge`。

本轮 G4 后 NOC 功能开发完成，转入补证与最终复核。此状态按用户最新要求更新；不等同于 G3/G4 全证据齐全或 G5 三轮彩排通过。

当前权威入口：

- [最终完成报告](final/PROJECT_COMPLETION_REPORT.md)：最终能力、真实性、配置依据、交付包哈希。
- [全部待补证据](final/EVIDENCE_PENDING.md)：28 组，含已测试待截图与尚待执行的彩排/最终复核。
- [本次软件验证](final/VALIDATION.md)：46 Python、3 Node、compileall、Protocol contract PASS。
- [NOC 最终实现](NOC_UPGRADE.md)、[真实控制器配置](PT_CONTROLLER_SETUP.md)、[现场脚本](DEMO_SCRIPT.md)。

## 已完成范围

Edge 真实温控、Policy/Command/ACK、自治与同步；中文 NOC 五板块；NC 设备清单/物理拓扑的真实只读采集；Managed→ONLINE；OSPF/BGP/Tunnel NOT COLLECTED。Security/Branch 为模拟，Campus Network/Security 为配置展示。Cloud 按钮实际中断 Edge WS，Network 故障模拟已禁用并返回 409。Protocol 1.0 与已有 Edge Policy 机制保持。

用户报告确认 NC-HQ `.30.30`/VLAN30/SW-CORE Gi1/0/10、R-HQ Loopback0 `10.255.255.1/32` 与 VTY 准入；用户确认 Dashboard 已显示。实际设备配置导出、成功 Dashboard/API 和现场恢复证据仍待归档。

## 阶段与后续动作

| 阶段 | 当前结论 | 剩余工作 |
|---|---|---|
| G0–G2 | 既有完成/关闭基线 | 保留历史证据 |
| G3 | 功能整合、实测确认，证据待补 | 修复后 Policy/Command ACK、完整 events |
| G4 | 已实现/用户测试，证据待补 | N12–N15、离线 OFF/物理输出、恢复 UI、最新 N1–N11 回归 |
| G4 后 NOC | 开发完成，真实 NC 接入确认 | 真实 API/卡片/断连恢复与中文页面操作归档 |
| G5 | 最终包候选已归档；正式验收未通过 | 打开复核、包内源码核验、连续 3 轮彩排待执行 |

只做补证、最终复核、必要修复；如需扩展真实 CLI 协议遥测或网络写配置，应另行确定范围。既有 G4 报告是历史阶段记录，不因项目总状态更新而改写历史验收事实。

## 分支与包

继续 `feat/edge`，不创建 g3/edge-gate3、不覆盖当前工作树、不推送。`packet_tracer/EdgeCampus.pkt` 是用户最新包，144326 bytes，SHA-256 `1c390fd766e6cb3c108f4e69853f61f614ca5a1a790cbed92e4cbd3f37e505dd`；本次未改二进制。PT 打开核验尚待执行，不能保证包内程序与外部代码一致。

## 启动

```powershell
Set-Location 'D:\Develop\sommerom\bighomework\edgecampus-g3'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_pt_backend.ps1 -ControllerPort 58000 -BackendPort 8000
```

先启用 PT NC Real World Access，输入 NC Web/API 账户；真实 SBC 使用 `ws://127.0.0.1:8000/ws/edge`。真实留证不用 Fake Edge。
