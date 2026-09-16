# Gate 4 — Failure Recovery + IPv6/Security（发布准备）

> 状态：DRAFT / NOT RELEASED。Gate 3 证据补齐并正式关闭后，将本任务书发布至 docs/CURRENT_GATE.md。Gate 5 仍 NOT STARTED。

## 基线与边界

基于 Gate 3 A 网络 canonical 拓扑与 BCD 控制器/Backend/Dashboard。保持 Protocol 1.0、设备 ID、WS/API 路径、默认 Policy 格式、冻结网络地址/AS/接口及 Gate 1/2/3 能力。A 唯一维护 canonical .pkt。PT 网络为模拟数据平面；RealWSClient → FastAPI 是宿主机带外通道。

## A — IPv6 Overlay + Access Security

按冻结 NETWORK_PLAN 逐层实施，每层验收后再叠加下一层：

1. HQ OFFICE SLAAC，BR-OFFICE DHCPv6，管理域 Static IPv6；实际核验 PT 9.0.1 支持及地址/参数，不擅自替换 DHCPv6 验收。
2. ISP Underlay 继续 IPv4-only，禁止原生 IPv6。
3. R-HQ ↔ R-BRANCH IPv6-over-IPv4 Tunnel；验证 IPv4 endpoint 可达后再验证 Tunnel。
4. IPv6 静态路由，BR-ADMIN ↔ HQ MANAGEMENT 管理路径，验证双向返回路由；不新增 OSPFv3。
5. HQ ADMIN 可管理 Branch 网络设备；普通 OFFICE 禁止管理。先验证路由，再验证管理服务/VTY ACL，不把 G3 ping 可达当作正式远程管理 PASS。
6. SW-ACCESS Fa0/1 sticky MAC / Port Security，验证正常终端、非法 MAC、violation 计数和恢复；按冻结建议 maximum 1 / restrict。
7. 全量回归 N1-N11、HQ Core、OSPF、eBGP、PAT、Branch、ACL、DNS/HTTP、Static mapping，并验收 N12 IPv6 modes、N13 Tunnel、N14 Remote Admin、N15 Port Security。

## B+C+D — 断云不断控 + 恢复同步

1. 正常连接，记录真实 temperature、fan_state、最后有效 AUTO Policy 和 Policy Version。若 G3 最终停于 MANUAL，先提交递增版本切回 AUTO，记录真实值，不能假定 v2。
2. 真正停止 FastAPI/Uvicorn。Dashboard 显示控制平面 disconnected，Edge 检测 Cloud disconnect。
3. Backend 关闭期间改变真实 TEMP01 温度，跨越最后有效策略的启动阈值和迟滞关闭阈值，真实 FAN 正确 ON/OFF，Local Loop 不停止。
4. 重启 Backend，Edge 自动 reconnect，发送 hello + state_sync。
5. Backend/Dashboard 从真实 Edge 恢复 temperature、fan_state、Policy、Policy Version；不能回退默认 v1/30 C。验证最终 Dashboard 与 Edge 一致。
6. R1 Cloud Failure、R2 Reconnect 均须真实 PT 证据，fake 测试只作为开发补充。

## 分工与产物

| Owner | 任务 | 产物 |
|---|---|---|
| B | disconnect 检测、Local Loop、保留最后策略、自动 reconnect、hello + state_sync，携带真实温度/FAN/Policy | Gate 4 Edge report + R1/R2 Edge evidence |
| C | socket disconnect→EDGE_OFFLINE、向 Dashboard 广播 offline snapshot；Backend 重启恢复；hello/state_sync 更新真实状态；Protocol validation | Backend report，disconnect/reconnect/state_sync、malformed/unsupported/wrong-version 拒绝证据 |
| D | Backend/WS down、重连状态可视化，恢复真实 temperature/FAN/Policy/version；集成证据 | Dashboard report + BCD recovery integration report/evidence |
| A | IPv6/Overlay/管理/Port Security及 N1-N15 回归，canonical 拓扑 | Network report、CONFIG_LOG、canonical .pkt、network evidence |

完整 Backend down 时其进程不能广播 snapshot；D 必须依靠 WS 断开显示控制平面失联。C 的 Edge disconnect→offline snapshot 在 Backend 仍运行的断连场景单独验收。

## DoD 与债务

- [ ] A：N12-N15 PASS，N1-N11 回归 PASS，IPv4 基线无退化。
- [ ] BCD：真实 Backend-off 下最后有效 AUTO Policy 仍控 FAN，R1 PASS。
- [ ] BCD：自动 reconnect + hello + state_sync，恢复真实状态与策略且无版本回退，R2 PASS。
- [ ] C：malformed/unsupported/wrong-version 安全拒绝、disconnect→offline、reconnect+state_sync 稳定性证据齐全。三项全部完成后才清零 Gate 1 debt。
- [ ] Protocol 1.0 无 drift，真实性边界保持，报告/evidence 可追溯。

Gate 5 为 Freeze + 3 Rehearsals，暂不启动。其硬条件：C debt 清零、final canonical .pkt、Protocol 无 drift、HQ Core/G2/G3/G4 PASS、完整流程连续三次成功。只允许 bug fix、必要可读性、日志/错误处理、报告/证据和 final .pkt；不新增协议、设备、业务场景或架构。
