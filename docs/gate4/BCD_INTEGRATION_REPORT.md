# Gate 4 — B+C+D 恢复集成报告

日期：2026-09-17；实际归档分支 feat/edge。状态：真实恢复主链已留证，完整 DoD EVIDENCE PENDING。

## 过程与证据逻辑

Edge 一直运行→下发非默认 AUTO v2/33/1→停 FastAPI→Edge 保留 v2、33.3 C 离线 FAN ON→重启 FastAPI→自动 reconnect/hello/state_sync→/api/state 恢复 31.8/OFF/v2/33/1。不能把停 Edge/重启内存默认策略实验混入此链。

Backend 重启极短窗口出现默认 v1/30 可以接受；完成 Edge state_sync 后必须恢复真实状态。G4-C-05 与 G4-B-03 直接支持最终恢复，用户无需手动重新下发策略。

| DoD | 真实证据 | 结论 / 缺口 |
|---|---|---|
| R1 最后有效 Policy | G4-B-01，G4-B-02 | v2/33 保留、离线 ON PASS；离线 OFF/Attributes 后补 |
| R1 UI 失联 | G4-D-01 | 控制平面 disconnected PASS |
| R2 reconnect/hello/state_sync | G4-B-03，G4-C-05 | 真实链 PASS |
| R2 Backend 状态与事件 | G4-C-02，G4-C-04，G4-C-05 | 31.8/OFF/AUTO/v2/33/1 与 STATE_SYNC PASS |
| R2 Dashboard 恢复 | 用户实测说明 | 恢复后截图待补 |
| C Gate1 stability debt | G4-C-01/02/03/04/05 | 三项真实证据齐全，清零 |

各图实际路径见 [证据索引](EVIDENCE_INDEX.md)，B/C/D 报告含图片。此表的局部 PASS 不等于完整 Global G4。

## 尚未闭合的门禁

A N12-N15 用户确认实测，截图后补；G4 N1-N11 全量回归无新增记录。G3 修复后 Dashboard Policy/Command ACK、完整 Backend SENT/ACK events 仍待补。G3 Branch HTTP 按 static TCP/80 映射入口解释，不沿用最终私网直连 HTTP PASS。

Gate4：IMPLEMENTED / USER-TESTED / EVIDENCE PENDING，未正式 COMPLETE；Gate5：NOT STARTED，尚不满足正式进入门禁。此阶段完成归档工作，不虚构 missing evidence。
