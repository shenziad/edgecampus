# 最终归档软件与文档验证

日期：2026-09-19。运行代码基线保持 `1aaa81d`；本轮更新当前PT包、G4网络证据和最终文档，没有修改Backend、Dashboard或Edge运行代码。

| 检查 | 实际结果 |
|---|---|
| `runtime/noc-venv/Scripts/python.exe -m unittest discover -s tests -q` | PASS，46 tests，18.935 s |
| `runtime/noc-venv/Scripts/python.exe -m compileall -q backend edge tests` | PASS |
| `runtime/noc-venv/Scripts/python.exe scripts/check_contract.py` | PASS，public contract v1.0 consistent |
| `node tests/test_noc_dashboard.cjs` | PASS，真实NC卡片、Managed精确映射、缺字段、无模拟/陈旧数据、协议未采集 |
| `node tests/test_dashboard_ack.cjs` | PASS，ACK等待/响应/遥测与后续命令 |
| `node tests/test_dashboard_recovery.cjs` | PASS，失联禁用控制、snapshot恢复真实状态、offline控制禁用 |

Python测试使用随机临时端口，完成后服务退出；没有占用现场8000端口。上述自动测试验证软件逻辑，不代替Packet Tracer现场截图。

## 归档一致性

- 当前PT包：147803 bytes，SHA-256 `6d6c154415700ff750cabe41272b0f1f5aa46f2d8ee341c3336625175fa7a4ba`。
- 21张G4网络原图已从提交 `4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8` 原样纳入当前分支。
- 最终素材总清单引用73张已有原图，25组待拍任务被拆为70个唯一PNG文件名。
- A01–A30、B01–B12、C01–C15、D01–D13编号连续，每项都有操作步骤和预期画面。
- 修改文档的Markdown代码围栏和本地链接已检查；PowerShell代码块通过解析。
- [ARTIFACT_MANIFEST.json](ARTIFACT_MANIFEST.json)登记130个二进制交付/证据文件，并保存大小与SHA-256。
- 原始DOCX保持归档；没有改写其内容。

项目状态保持**验收完成，报告准备中**。70张PNG、CFG01–CFG08和展示彩排记录继续按最终清单整理，作为报告与答辩素材，不作为新的验收门槛。
