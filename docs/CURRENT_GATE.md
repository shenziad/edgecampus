# 项目收尾 — 验收完成，报告准备中

> 项目总状态：**ACCEPTANCE COMPLETE — REPORT PREPARATION / 验收完成，报告准备中**
> 更新：2026-09-19；正式分支：`feat/edge`。

## 当前交付事实

- 五大NOC板块已完成：Edge Control、Network Operation、Security Operation、Policy Management、Failure Simulation。
- PT Network Controller真实只读接入已完成，Managed设备映射ONLINE；OSPF/BGP/Tunnel显示NOT COLLECTED。
- Security/Branch使用演示适配器；Campus Network/Security为上层展示；Cloud按钮实际断开Edge WebSocket；Network Failure禁用并返回409。
- G4的21张网络原图已纳入当前分支；另有9张G4 Edge/Backend/Dashboard证据和1张NC Managed清单图。
- 最终配置和五次实验落点已经整理成独立文档。
- B01–B12 已完成（12/12），D01–D13 已完成（13/13）；D 最终证据位于 `evidence/final_report/D/`。

## 当前权威入口

- [最终配置总览](FINAL_CONFIGURATION.md)
- [五次实验映射](EXPERIMENT_MAPPING.md)
- [最终素材总清单](FINAL_REPORT_SCREENSHOT_CHECKLIST.md)
- [四人逐张截图操作清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)：A30张、B12张、C15张、D13张
- [前五次实验报告补拍的5张图](EXPERIMENT_EVIDENCE_COVERAGE.md)
- [最终完成报告](final/PROJECT_COMPLETION_REPORT.md)
- [最终软件验证](final/VALIDATION.md)

## 报告素材准备

原计划补拍25组、70张PNG；当前 B 12/12、D 13/13 已完成，其余 Owner 按四人清单继续整理。另整理CFG01–CFG08完整配置附件，并可在同一最终软件和PT包上完成三轮展示彩排记录。这些工作服务于实验报告和答辩材料，不影响已经完成的项目验收结论。

## 正式PT包

`packet_tracer/EdgeCampus.pkt` 是唯一正式包：

- 大小：147803 bytes
- SHA-256：`6d6c154415700ff750cabe41272b0f1f5aa46f2d8ee341c3336625175fa7a4ba`

包已纳入本次发布；保存重开、包内程序和展示流程按截图与附件清单复现，作为报告素材。

## 启动

```powershell
Set-Location 'D:\Develop\sommerom\bighomework\edgecampus-g3'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_pt_backend.ps1 -ControllerPort 58000 -BackendPort 8000
```

先在PT开启NC Real World Access和58000端口，运行MCU/SBC程序；随后输入NC Web/API账户并打开 `http://127.0.0.1:8000`。
