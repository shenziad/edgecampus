# Gate 3 B+C+D Integration Report

> 日期：2026-09-16。状态：实测结果由项目负责人确认 PASS；仓库证据审核待补 Dashboard ACK / Backend events。全局 Gate 3 暂不关闭；按负责人决定 Gate 4 已提前发布，见 CURRENT_GATE。

## 1. Integration Objective

证明 Dashboard → Backend → Real EDGE-SBC-01 → policy_ack / command_ack → Backend → Dashboard 的真实闭环。B 已在独立 Gate 3 完成温度点、AUTO、MANUAL、Policy、Command、真实 FAN 与 ACK 验证；本次只归档必要的集成证据，引用 B 原图，不复制整套单点截图。

## 2. Baseline

BCD 基线 `94afba036876bbd2d74265b88ddd7cc6584b4cf7`，已包含 feat/edge、feat/dashboard、feat/backend。最终临时整合分支 gate3/final-integration 从 main `e9123aed20cb31352ba99d2c49ba744fee9607f7` 建立，纳入 feat/network `952c2d5` 与 BCD 基线。

## 3. Test Environment

Cisco Packet Tracer 9.0.1 / EDGE-SBC-01 / TEMP01 / FAN01；宿主机 FastAPI/Uvicorn；Dashboard。Gate 3 Edge Controller 由 `edge/packet_tracer/sbc_gate3_controller.py` 管理，并由项目负责人在真实 PT 联调中装载运行。

## 4. Truthfulness Boundary

PT VLAN/ACL/OSPF/eBGP/NAT/Tunnel 是模拟企业数据平面。RealWSClient → ws://127.0.0.1:8000/ws/edge → FastAPI 是宿主机带外控制通道。真实 WebSocket 不经过 R-HQ/R-ISP/BGP/NAT/PT WAN。

canonical `packet_tracer/EdgeCampus.pkt` 采用 A feat/network Gate 3 已验证版本，含完整 Gate 1+2+3 网络配置。未确认其中永久嵌入 Gate 3 SBC 源码，不作此声明。

## 5. Real Edge Connection

项目负责人确认启动真实 Edge 后 edge_online=true、cloud_state=CONNECTED，真实 telemetry、FAN、heartbeat 进入 Backend/Dashboard。INT-04 直接展示 EDGE-SBC-01 ONLINE/CONNECTED、31.8 C、FAN ON。

INT-01 文件名含 online-pass，但画面实际为启动前 OFFLINE/WAITING、无温度、FAN UNKNOWN、Policy v1、零 events。该图只作为启动前基线，不能用于证明 Real Edge ONLINE。

## 6. Policy E2E

项目负责人确认 Dashboard 下发 AUTO / 33 C / hysteresis 1 C，Edge 应用 runtime Policy、返回 APPLIED，Backend 更新 state/event，Dashboard 显示新策略与 ACK。

INT-02 可直接核验 Protocol 1.0、Policy v3/AUTO/33 C/1 C、CLOUD POLICY APPLIED、TX POLICY_ACK v3 APPLIED、31.8 C FAN OFF 和 heartbeat。Dashboard 收到 ACK 的画面尚未在本次四图中展示。

版本按连续联调递增：核心 Policy 图 v3；MANUAL Command 图 v4；最终 Backend 状态 v5。这是不同测试时刻，不能改写为原计划 v2，也不能混作同一个 snapshot。现有图显示递增结果；严格拒绝旧版本的能力依据 B 报告和实现，不仅凭三个版本值推断。

## 7. Command E2E

项目负责人确认 MANUAL 下 Dashboard FAN OFF/ON、真实 FAN 执行、REMOTE-MANUAL、command_ack APPLIED、Backend COMMAND_SENT/COMMAND_ACK 与 Dashboard ACK 成功。

INT-03 直接展示 MANUAL v4、收到 FAN01 ON command、真实控制日志 FAN ON、TX STATUS source=REMOTE-MANUAL、TX COMMAND_ACK APPLIED。OFF 单点复用 B-05；ON 单点复用 B-06。Dashboard ACK 与 Backend COMMAND_ACK 事件仍需补集成画面。

## 8. Backend / Dashboard State Consistency

INT-04 展示 Backend 在线、31.8 C、FAN ON、MANUAL、Policy thermal-01 v5/33 C/1 C。events 数组只显示开头，其内容被裁掉，不能宣称该图直接证明 send+ACK 事件。Dashboard 状态一致由项目负责人确认；正式归档还需展示 ACK 与恢复后的状态。

C 既有报告/证据可作为独立补充，不混作本次会话：其 Dashboard 图有 ONLINE/v3/33 C，Command 图含 COMMAND_SENT/REMOTE-MANUAL，但均未补齐本次 Dashboard ACK 画面。

## 9. Evidence Index

沿用实际已有唯一集成目录 `evidence/gate3_bcd/`，保留四图原名、原像素和原内容，不建重复根目录。

| 文件 | 直接可见内容 | 限制 |
|---|---|---|
| [INT-01](../../evidence/gate3_bcd/G3-INT-01-real-edge-online-pass.png) | 启动前 OFFLINE/WAITING/v1 | 文件名失配，不作 ONLINE PASS 证据 |
| [INT-02](../../evidence/gate3_bcd/G3-INT-02-policy-e2e-pass.png) | Edge Policy v3/33 C、APPLIED、TX ACK | 未展示 Dashboard 收 ACK |
| [INT-03](../../evidence/gate3_bcd/G3-INT-03-command-e2e-pass.png) | MANUAL v4、ON、REMOTE-MANUAL、TX ACK | 未展示 Dashboard 收 ACK；OFF 引用 B |
| [INT-04](../../evidence/gate3_bcd/G3-INT-04-final-backend-state-pass.png) | Backend ONLINE/CONNECTED、MANUAL v5、FAN ON | events 截断 |

B 原证据位于 `edge/packet_tracer/evidence/gate3/`：B-01 Policy/ACK，B-02 31.8 C OFF，B-03 34.9 C ON，B-05 MANUAL OFF，B-06 MANUAL ON，B-07 Gate 2 regression。详见 [B 报告](B_EDGE_REPORT.md)。A 网络验收及 N1-N11 回归见 [A 报告](A_NETWORK_REPORT.md)。C 独立验收见 [C 报告](../../evidence/backend/GATE3_C_REPORT.md)。

## 10. Regression / Conclusion

A Network Gate 3 PASS；B Edge-side Gate 3 PASS；C/D 与 BCD E2E 实测由项目负责人确认 PASS。自动检查结果见后续仓库验证记录。Protocol v1.0 文档/配置保持冻结。

正式关闭前补证：Dashboard Policy ACK APPLIED（v3/33 C 或注明后续真实递增版本）；Command ACK APPLIED 与 FAN/MANUAL；Backend POLICY_SENT/POLICY_ACK、COMMAND_SENT/COMMAND_ACK 的完整 events。不得为补证改图伪造版本，也不必重做 B 已完成的温度点。

C Gate 1 stability debt 仍保留：malformed/unsupported/wrong-version 安全拒绝、disconnect→offline、reconnect+state_sync 的正式稳定性证据。后两项由 Gate 4 真实断云/恢复流程验收；自动单测不替代实测。

## ACK 修复与阶段发布

Backend 真实 events.jsonl 已记录本次 ON/OFF command_ack APPLIED（对应 Command 图中的 command_id），因此 ACK 确实到达 Backend。持续遥测曾将 ACK 挤出 100 条事件窗口，造成 Dashboard 显示尚未收到；0749255 已修复保留策略及新请求等待显示。19 项 Python 和 JavaScript 行为测试 PASS，真实修复后 Dashboard 截图仍待补。

按项目负责人 2026-09-16 决定，先发布 Gate 4 供 A/B/C/D 并行开工；Gate 3 保持 EVIDENCE PENDING，未正式 COMPLETE。A/B 独立验收 PASS、BCD 实测已确认；ACK 修复已提交 0749255，修复后 Dashboard Policy/Command ACK 与完整 Backend state/events 待补。C Gate 1 stability debt 保留，Gate 5 NOT STARTED。
