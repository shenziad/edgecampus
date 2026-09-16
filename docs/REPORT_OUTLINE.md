# 设计文档 / 实验报告建议结构 — Final Architecture v2

评分中功能正常实现占 60%，创新性占 20%，现场验收占 5%，问题回答占 5%，设计文档占 10%。报告应围绕**统一业务系统 + 可验证证据**组织，而不是按五次实验机械罗列命令。

## 1. 实验目的与任务要求

- 组建多园区智慧校园网络；
- 综合覆盖前五次实验的关键技术；
- 构建“感知—边缘决策—云端管理—设备执行”的应用闭环；
- 证明 Cloud 失联时 Edge 仍可自治。

## 2. 场景与需求分析

说明三个业务区域：

- HQ 总部智慧园区；
- ISP / Internet；
- Branch 异地业务与运维站点。

说明角色：HQ OFFICE、HQ ADMIN、IoT Edge、BR-OFFICE、BR-ADMIN、HQ-SERVICE、INTERNET-SERVER。

## 3. 总体架构设计

- Final Architecture v2 总拓扑；
- Physical / Edge / Campus & WAN / Cloud 四层；
- Edge Local Loop + Cloud Global Loop；
- Packet Tracer Data Plane 与 RealWSClient 带外 Control Channel 的真实性边界；
- 模块边界与状态所有权。

## 4. HQ 园区网络设计

- VLAN10 OFFICE / VLAN20 IOT / VLAN30 MANAGEMENT；
- SW-CORE / SW-ACCESS；
- LACP EtherChannel、Trunk；
- SVI、三层转发、DHCP；
- Gate 1 ACL 安全域；
- Port Security / sticky MAC；
- 已有 Gate 1 基线如何被 Final Architecture v2 保留。

## 5. Branch 分部网络设计

- Branch VLSM；
- VLAN40 BR-OFFICE / VLAN50 BR-MGMT；
- Router-on-a-Stick；
- BR-OFFICE IPv4 DHCP；
- BR-ADMIN / SW-BRANCH 管理地址；
- HQ 与 Branch 采用不同 VLAN 间路由模型的设计理由。

## 6. 企业 WAN 与 Internet 设计

- HQ Transit；
- R-HQ / R-ISP / R-BRANCH；
- HQ OSPF Area 0；
- eBGP AS65001 / AS65000 / AS65002；
- R-HQ 默认出口设计，避免把完整 BGP 表灌入 HQ Core；
- BR-OFFICE → HQ-SERVICE 业务流；
- HQ ADMIN → Branch centralized management。

## 7. NAT、DNS、HTTP 与服务发布

- HQ OFFICE PAT；
- INTERNET-SERVER DNS + HTTP；
- `www.edgecampus.net` 业务访问；
- TCP/80 static mapping；
- 为什么 IOT 默认不开放 Internet PAT；
- 静态映射只用于 Packet Tracer 模拟服务，不代表真实 FastAPI 公网发布。

## 8. IPv6 与跨站点 Overlay

- HQ SLAAC；
- Branch DHCPv6；
- 管理域 Static IPv6；
- ISP IPv4-only；
- IPv6-over-IPv4 Tunnel；
- IPv6 static route；
- BR-ADMIN → HQ MANAGEMENT 的运维业务意义。

## 9. Edge 本地自治设计

- TEMP01 → MCU → SBC → FAN01；
- PT API / 接线；
- threshold / hysteresis；
- AUTO 状态机；
- Cloud 不可达时仍运行；
- Fan 的 PT 物理值与协议 `ON/OFF` 映射。

## 10. Cloud Control Plane 设计

- Protocol v1.0；
- FastAPI / WebSocket；
- Telemetry / Status / Heartbeat；
- Policy / Command；
- ACK / Error；
- SystemState / Event Log；
- reconnect + state_sync；
- C Gate 1 placeholder 最终如何补齐（最终报告中只写真实完成情况）。

## 11. Dashboard 与可观测设计

- Online/Offline；
- Temperature / Fan / Mode；
- Policy Version / threshold / hysteresis；
- WARNING；
- Event Stream；
- Policy / Command UI；
- 页面展示与传输字段之间的边界。

## 12. 核心业务流实现

建议按业务而不是协议逐一说明：

1. Edge Local Loop；
2. Cloud Control Loop；
3. Branch Business Flow；
4. Remote Operations Flow；
5. Central Administration Flow；
6. Enterprise Internet Flow。

每条写：业务目标 → 路径 → 使用的网络/应用技术 → 安全策略 → 验收证据。

## 13. 实现过程与关键问题

重点记录真实过程：

- Packet Tracer SBC / MCU / Fan API 与接线验证；
- PT ↔ 真实主机 External Network Access；
- 为什么真实 WebSocket 不是经过模拟 WAN；
- EtherChannel / ACL / ROAS / BGP / NAT / IPv6 Tunnel 的实际问题；
- AI 建议与 Packet Tracer 9.0.1 IOS 差异如何修正；
- 如何通过分层 Gate 避免一次叠加过多协议。

## 14. 功能测试

严格按 `docs/ACCEPTANCE.md` 的最终测试矩阵组织。

每项至少包含：

```text
测试目的
前置条件
操作 / 命令
预期结果
实际结果
截图位置
截图内容解释
结论
```

每张截图后必须写：**观察到什么、为什么能证明该功能、对应哪一条验收要求。** 避免只写“结果如图所示”。

## 15. 前五次实验覆盖映射

单独放一张课程能力映射表，说明：

- 实验1：VLSM / DHCP / IPv6 / static route / remote management；
- 实验2：VLAN / Trunk / EtherChannel / SVI / ROAS；
- 实验3：ACL / NAT/PAT / static mapping / DNS / HTTP；
- 实验4：OSPF / BGP；
- 实验5：Port Security / MAC / IPv6-over-IPv4。

这部分是**覆盖证明**，不是报告主体结构。

## 16. 创新性分析

重点写：

- Edge Local Loop + Cloud Global Loop；
- 断云不断控；
- Policy Delivery + ACK；
- State Sync；
- 网络安全域强制业务路径；
- IPv4 Underlay + IPv6 Management Overlay；
- HQ / Branch 根据规模使用不同组网方案；
- 从单园区 IoT 原型升级为多园区业务系统，而不破坏稳定 Core。

## 17. 现场验收与问题回答准备

准备回答：

- 为什么 Edge 不依赖 Cloud？
- 为什么 HQ 用 SVI、Branch 用单臂路由？
- 为什么内部用 OSPF、WAN 用 BGP？
- 为什么 ISP 只提供 IPv4，却还设计 IPv6？
- 为什么 IOT 默认不 PAT 上 Internet？
- RealWSClient 到底有没有经过 Packet Tracer WAN？
- 为什么 BACKEND-STUB 不是实际 Backend？
- Cloud 恢复后为什么需要 State Sync？

## 18. 分工与 AI 协作记录

- A / B / C / D Owner 边界；
- Gate 分阶段推进；
- AI 生成建议、实机验证、修正与最终采用结果；
- C Gate 1 placeholder 必须在最终报告前形成真实结论，不能隐藏未完成项。

## 19. 总结与改进方向

改进方向可以写生产环境中的 SSH、认证、数据库、高可用、真实网络设备、MQTT/消息系统等，但不要把未实现内容写成当前系统功能。

## 2026-09-17 Gate4 归档更新

2026-09-17 当前审计：Gate4 已实现并有用户现场实测确认；B 离线 ON、真实 reconnect/hello/state_sync、Backend 恢复与 D 失联有截图，C 三项 Gate1 stability debt 清零。A N12-N15 用户确认已测，截图本次跳过后补；离线 OFF/Attributes、恢复后 Dashboard、G4 N1-N11 全量回归及 G3 修复后 ACK/完整 events 仍需归档。Gate4 为 IMPLEMENTED / USER-TESTED / EVIDENCE PENDING，未正式 COMPLETE；Gate5 NOT STARTED。

过程与配置：`docs/gate4/A_NETWORK_REPORT.md`、B/C/D/BCD 报告；自动验证：`docs/gate4/VALIDATION_REPORT.md`。报告应解释 Cloud outage/Edge restart、临时默认值/state_sync、NAT 业务入口、IPv4-only ISP、static IPv6、VTY ACL 和 sticky/restrict。
