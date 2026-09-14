# Integration Board

只记录端到端能力，不记录按钮颜色、函数改名等局部工作。

| 能力 | Owner | 独立测试 | 联调 | 状态 | 下一动作 |
|---|---|---:|---:|---|---|
| 公共协议 v1 | B+C+D | ✅ | ✅（fake） | DONE | 冻结 |
| Backend 基线 | C | ✅ | ✅（fake） | DONE | 接入 PT Edge |
| Fake Edge | B+C | ✅ | ✅ | DONE | 保留为开发替身 |
| Dashboard 基线 | D | ✅（代码检查） | ✅（WS） | READY | 实机浏览器视觉确认 |
| VLAN/IP 逻辑规划 | A | ✅ | ❌ | READY | 建立 PT 拓扑 |
| PT 端口映射 | A | ❌ | ❌ | TODO | 确认设备型号 |
| Edge 本地自治 | B | ✅（核心逻辑） | ❌（PT） | TESTING | 映射 PT API |
| PT → 真实主机 | A+B+C | ❌ | ❌ | HIGHEST RISK | 最早实测 |
| Telemetry 全链路 | B+C+D | ✅（fake） | ❌（PT） | TESTING | Gate 2 |
| Policy 下发 | B+C+D | ✅（协议） | ❌（PT） | TESTING | Gate 3 |
| 断云不断控 | B+C | ✅（fake） | ✅（fake） | TESTING | PT Gate 4 |
| 云恢复状态同步 | B+C+D | ✅（fake） | ✅（fake） | TESTING | PT Gate 4 |

## Integration Check 记录

| 时间 | 参与人 | 当前 Gate | 成功项 | 阻塞项 | 决策 |
|---|---|---|---|---|---|
| 初始化 | 全组 | G0 | 仓库/契约/基线 | PT 实机信息 | 优先验证 PT↔Host |
| 自动验证 | B+C+D | G1 | Policy/Command、断云自治、重连同步 | PT 尚未接入 | 软件基线可并行开发 |
