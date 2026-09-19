# 架构决策记录

## ADR-001：采用 FastAPI + WebSocket

状态：Accepted

原因：一个进程同时提供 API、双向消息和静态 Dashboard，满足课程综合实验原型，不引入消息队列或微服务。

## ADR-002：Edge 保存最后有效策略

状态：Accepted

原因：控制动作不能依赖 Cloud 永久在线；断云时继续本地 AUTO 循环。

## ADR-003：首版使用内存状态 + JSONL 事件日志

状态：Accepted

原因：现场系统无需复杂查询，数据库会增加部署与恢复风险。正式持久化作为后续增强。

## ADR-004：统一摄氏单位为 `C`

状态：Accepted

原因：传输字段保持 ASCII 与跨平台一致；Dashboard 可展示为 `℃`。

## ADR-005：迟滞控制

状态：Accepted

原因：温度达到阈值时开启，降到“阈值减迟滞”时关闭，避免临界点频繁开关。

## ADR-006：Final Architecture v2 只向外扩展，不重构 Gate 1 HQ Core

状态：Accepted — 2026-09-15

决策：保留 VLAN10/20/30、HQ IPv4、EtherChannel、SVI/DHCP/ACL、TEMP→MCU→SBC→FAN 接线和 Protocol v1.0；新增网络从 `SW-CORE Gi1/0/24` 向 R-HQ 扩展。

原因：Gate 1 已经实测通过。课程覆盖需要扩展 OSPF/BGP/NAT/IPv6 等能力，但没有理由冒险重写已经稳定的核心。

## ADR-007：升级为 HQ + ISP/Internet + Branch 多站点系统

状态：Accepted — 2026-09-15

决策：新增 R-HQ、R-ISP、R-BRANCH、SW-BRANCH、BR-OFFICE-PC、BR-ADMIN-PC、INTERNET-SERVER。

业务定义：

- BR-OFFICE 是异地普通员工，访问总部允许的 HQ-SERVICE；
- BR-ADMIN 是异地运维人员，通过 IPv6 Overlay 访问 HQ MANAGEMENT；
- HQ ADMIN 是中央 NOC 管理员，管理 Branch 网络设备；
- INTERNET-SERVER 提供模拟 DNS/HTTP 公网服务。

原因：这样 WAN 不再是“补实验命令”，而是成为总部—分部业务与运维的真实承载网络。

## ADR-008：HQ 使用 SVI，Branch 使用 Router-on-a-Stick

状态：Accepted — 2026-09-15

原因：HQ 规模大，采用三层交换机 SVI；Branch 规模小，使用 R-BRANCH 单臂路由降低设备复杂度。两种方案体现按站点规模选择架构，而不是重复配置。

## ADR-009：IPv4 采用 HQ OSPF + WAN eBGP 分层

状态：Accepted — 2026-09-15

决策：

```text
SW-CORE -- OSPF Area 0 -- R-HQ AS65001 -- eBGP -- R-ISP AS65000 -- eBGP -- R-BRANCH AS65002
```

R-HQ 向 HQ OSPF 发布默认路由；不把完整 BGP 表重分发进 Core。

原因：IGP 管企业内部，EGP 管自治系统边界，职责清晰，也避免为了覆盖课程而做不必要的大范围重分发。

## ADR-010：IPv4 Underlay + IPv6 Overlay

状态：Accepted — 2026-09-15

决策：ISP 保持 IPv4-only；HQ 和 Branch 内部使用 IPv6；R-HQ ↔ R-BRANCH 建立 IPv6-over-IPv4 Tunnel；跨站点 IPv6 使用静态 IPv6 路由。

原因：给实验五 Tunnel 明确业务意义，同时覆盖静态 IPv6 路由，不额外引入 OSPFv3。

## ADR-011：R-HQ 统一承担 HQ Internet Edge

状态：Accepted — 2026-09-15

决策：R-HQ 负责 HQ OFFICE PAT、实验所需 TCP/80 static mapping、WAN ACL 与企业出口。

安全边界：HQ IOT 默认不直接获得 Internet PAT；外部只开放验收所需 HTTP/80 映射，不把整个 MANAGEMENT 域暴露出去。

## ADR-012：真实 FastAPI 控制通道与 Packet Tracer WAN 严格分离

状态：Accepted — 2026-09-15

决策：RealWSClient 继续通过 External Network Access 连接真实 FastAPI，属于带外 Edge–Cloud 控制通道。Packet Tracer 的 R-HQ/R-ISP/BGP/NAT/Tunnel 只模拟企业 Data Plane。

原因：保持技术表述真实。不得在答辩中声称真实 WebSocket 经过 Packet Tracer WAN。

## ADR-013：Gate 1 C 采用显式 Placeholder，不阻塞 Gate 2

状态：Accepted — 2026-09-15

决策：A/B/D 和 A+B integration 已满足推进条件，C 的 Owner 专属 Gate 1 证据暂以 `docs/gate1/C_BACKEND_REPORT.md` 占位。Gate 2 可以开始，但 placeholder 不等于 PASS，Gate 5 Freeze 前必须补齐。

原因：Backend 软件基线已经存在，继续等待形式性交付会阻塞关键路径；同时通过显式占位避免把未验证内容写成已完成。

## 2026-09-17 Gate4 归档决定

用户明确继续在 feat/edge 整理并提交；A N12-N15 已实测，截图跳过后补，以 Markdown 清单占位而非伪造 PNG。Gate4 保留 IMPLEMENTED / USER-TESTED / EVIDENCE PENDING，Gate5 NOT STARTED。C stability debt 依据真实截图清零。最终 Branch HTTP 入口按用户实测采用 203.0.113.1 static TCP/80，私网直连 HTTP FAIL，不重编号冻结地址。

## 2026-09-19 项目状态纠正

用户确认项目已经完成验收。当前统一状态为 **验收完成，报告准备中 / ACCEPTANCE COMPLETE — REPORT PREPARATION**。此后计划补拍的PNG、配置导出和展示彩排记录全部用于实验报告与答辩准备，不再作为项目验收门槛。G1–G4文档中的 EVIDENCE PENDING、G5 NOT STARTED 等状态保留为当时的历史过程记录。
