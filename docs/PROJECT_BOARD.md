# Integration Board

只记录端到端能力，不记录按钮颜色、函数改名等局部工作。

| 能力 | Owner | 独立测试 | 联调 | 状态 | 下一动作 |
|---|---|---:|---:|---|---|
| 公共协议 v1 | B+C+D | ✅ | ✅（fake） | DONE | 冻结 |
| Backend 基线 | C | ✅ | ✅（fake） | DONE | Gate 1 稳定化 |
| Fake Edge | B+C | ✅ | ✅ | DONE | 保留为开发替身 |
| Dashboard 基线 | D | ✅（代码检查） | ✅（WS） | READY | Gate 1 实机浏览器确认 |
| VLAN/IP 逻辑规划 | A | ✅ | — | DONE | Gate 1 实施 |
| PT 设备型号/端口映射 | A | ✅ | — | DONE | 冻结 |
| PT → 真实主机控制通道 | A+B+C | ✅ | ✅ | VERIFIED | Gate 2 接真实 Telemetry |
| Edge 本地自治 | B | ✅（核心逻辑） | ❌（PT） | TESTING | Gate 1 映射 PT API |
| Telemetry 全链路 | B+C+D | ✅（fake） | ❌（PT） | TESTING | Gate 2 |
| Policy 下发 | B+C+D | ✅（协议） | ❌（PT） | TESTING | Gate 3 |
| 断云不断控 | B+C | ✅（fake） | ✅（fake） | TESTING | PT Gate 4 |
| 云恢复状态同步 | B+C+D | ✅（fake） | ✅（fake） | TESTING | PT Gate 4 |

## Gate 状态

| Gate | 状态 | 说明 |
|---|---|---|
| G0 Contract Freeze | **COMPLETE** | 设备/端口、公共协议、VLAN/IP、ACL 放置原则、PT→Real Host 通道均已冻结或实测 |
| G1 四模块独立运行 | IN PROGRESS | A/B/C/D 可并行推进 |
| G2 单向数据链路 | NOT STARTED | 等 G1 完成后接入真实 PT Telemetry |
| G3 双向策略闭环 | NOT STARTED | 等 G2 |
| G4 断云不断控 | NOT STARTED | 核心创新验收 |
| G5 Freeze 与三轮彩排 | NOT STARTED | 最终冻结 |

## Gate 1 并行边界

- **A Network**：唯一维护 canonical `.pkt`，完成 VLAN、Trunk、LACP EtherChannel、SVI、DHCP、ACL 与网络独立验收。
- **B Edge**：使用自己的 PT 开发副本验证 TEMP01 / FAN01 API 和 `TEMP01 → SBC → FAN01` 本地自治；不要把开发副本直接覆盖 canonical `.pkt`。
- **C Control Plane**：使用 `fake_edge.py` 独立稳定 Backend、状态管理、协议校验、断连处理和事件日志，不等待 B。
- **D UI & Integration**：使用 fake/Backend snapshot 独立完成 Dashboard 状态、事件、告警与策略表单，并维护集成测试与验收证据。

Gate 1 每位 Owner 最长独立开发 4 小时，之后进行一次 Integration Check。谁先完成自己的 Gate 1 任务，优先支援当前 Critical Path，不新增非必要功能。

## Integration Check 记录

| 时间 | 参与人 | 当前 Gate | 成功项 | 阻塞项 | 决策 |
|---|---|---|---|---|---|
| 初始化 | 全组 | G0 | 仓库/契约/基线 | PT 实机信息 | 优先验证 PT↔Host |
| 自动验证 | B+C+D | G1 | Policy/Command、断云自治、重连同步（fake） | PT 尚未接入 | 软件基线可并行开发 |
| 2026-09-14 | G0 Owner | G0 | 3650/2960 型号与端口冻结；RealWSClient→FastAPI 实测通过；重开 PT 后复测通过 | 无 G0 阻塞项 | **Gate 0 COMPLETE，进入 Gate 1 四路并行** |
