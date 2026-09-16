# Gate4 自动验证与最终门禁

日期：2026-09-17；分支 feat/edge。默认 Python 为损坏的 GTKWave 安装，旧 .venv 的 Python 3.13 路径失效。使用 Codex bundled Python 3.12.14 / Node 24.19.0；requirements.txt 在临时隔离目录安装，未改项目依赖文件、原 .venv 或全局环境。

## 自动测试结果

| 检查 | 结果 | 验证范围 |
|---|---|---|
| python -m py_compile edge/packet_tracer/sbc_gate4_controller.py | PASS | PT 源码语法；不 import/run PT API |
| python -m compileall backend edge tests scripts | PASS | 全软件语法 |
| python -m unittest discover -s tests -v | PASS，29 tests，无 skip | 原有 19 + Gate4 validator/state 7 + 实际主机 WS 3 |
| node tests/test_dashboard_ack.cjs | PASS | ACK waiting/response、telemetry 后保留 ACK、后续 command |
| node tests/test_dashboard_recovery.cjs | PASS | close禁用、重连 open 等 snapshot、真实值自动恢复、Edge offline禁用 |
| python scripts/check_contract.py | PASS | 冻结 Public Contract 无 drift |
| gate4_invalid_ws_test.py | PASS | WS 专项调用真实随机端口测试 Backend，三类 INVALID_MESSAGE，无 PT 替代宣称 |
| Markdown 全仓库图片相对路径检查 | PASS | 真实图引用全部存在；待补清单没有失效图片链接 |
| git diff --check / staged diff --check | PASS | 最终提交前检查 |

WebSocket 测试在随机 loopback 端口运行，不占用现场 8000，不停止现场 Edge/Backend；events 写入临时目录。临时依赖安装目录不提交。

## 报告真实性与限制

A N12-N15 PASS 来自用户实测确认，截图仍缺，因此明确 USER-REPORTED PASS / EVIDENCE PENDING。B 离线 ON、reconnect/state_sync、C offline/非法拒绝/恢复、D 失联有逐张看过的真实图片。R1 离线 OFF/物理 Attributes、R2 恢复 Dashboard、G4 N1-N11 全量回归、G3 修复后 Dashboard ACK/完整 SENT/ACK events 待归档。历史 G3 私网 HTTP 页面不得支持最终 static mapping 共存场景。

自动测试不证明 PT 网络配置或现场 FAN 物理状态；canonical .pkt 由用户预先修改，本次不编辑其内容。包的哈希仅用于可追溯，不证明 N12-N15。

## 结论

C Gate1 三项 stability debt：CLEARED（真实证据见 C 报告）。Gate3：EVIDENCE PENDING。Gate4：IMPLEMENTED / USER-TESTED / EVIDENCE PENDING，尚未正式 COMPLETE。Gate5：NOT STARTED；完整门禁尚不满足，不把占位清单当作已归档截图。
