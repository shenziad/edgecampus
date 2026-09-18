# 最终归档软件验证

日期：2026-09-18。代码基线 `1aaa81d`，本轮未修改运行代码；新增最终文档及原样归档用户最新 `.pkt`、报告、NC 原图。

| 检查 | 实际结果 |
|---|---|
| `runtime/noc-venv/Scripts/python.exe -m unittest discover -s tests -q` | PASS，46 tests，7.105 s |
| `runtime/noc-venv/Scripts/python.exe -m compileall -q backend edge tests` | PASS，exit 0 |
| `runtime/noc-venv/Scripts/python.exe scripts/check_contract.py` | PASS，public contract v1.0 consistent |
| `node tests/test_noc_dashboard.cjs` | PASS，真实 NC 卡片、Managed 精确映射、缺字段、无模拟/陈旧数据、协议未采集 |
| `node tests/test_dashboard_ack.cjs` | PASS，ACK 等待/响应/遥测与后续命令 |
| `node tests/test_dashboard_recovery.cjs` | PASS，失联禁用控制、snapshot 恢复真实状态、offline 控制禁用 |

Node 使用本机 Codex bundled Node 路径；Python 使用已有 `runtime/noc-venv`。测试中的 Uvicorn 使用临时端口，测试完成退出；未启动长期 8000 服务。HTTP fixture/Fake Edge 测试不构成 PT 现场验收或 G5 彩排。

Word 报告通过 OOXML 提取全部正文，媒体条目为零。原文和源文件归档；本次没有创建或改排 Word，不声明新的 Word 排版验收。真实 NC 清单截图已目视核对：两项 Managed、三项 Unsupported。

归档复核通过：修改文档的本地 Markdown 链接与代码围栏有效；EV-01–28 连续且不重复；[ARTIFACT_MANIFEST.json](ARTIFACT_MANIFEST.json) 中 93 个二进制交付/历史证据文件的大小和 SHA-256 全部匹配；归档 DOCX 与用户原件逐字节一致，当前 .pkt 与本次开始时的用户包哈希一致。git diff --check 无错误。
