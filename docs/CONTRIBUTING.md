# 四人 + AI 协作规范

## Owner 与边界

| Owner | 可独立修改 | 跨界前必须沟通 |
|---|---|---|
| A Network | `packet_tracer/`、网络证据 | VLAN/IP、真实主机接入方式 |
| B Edge | `edge/`、Edge 证据 | 消息字段、设备 ID、连接方式 |
| C Control Plane | `backend/`、控制平面证据 | WS/API 路径、消息语义 |
| D UI & Integration | `dashboard/`、`tests/`、联调证据 | 公共字段、验收流程 |

任何人都可以修文档错字，但修改公共契约必须走 RFC。

## 分支

```text
main
├── feat/network
├── feat/edge
├── feat/backend
└── feat/dashboard
```

达到 Gate、验证成功后才合入 `main`。每位 Owner 最长独立开发 4 小时，之后无论完成度如何都进行一次 Integration Check。

## Commit 约定

```text
feat(edge): add local temperature control
feat(protocol): support policy acknowledgement
fix(backend): restore state after edge reconnect
docs(network): record vlan acl acceptance
test(integration): verify cloud reconnect flow
```

禁止把未运行的 AI 输出直接提交。每次提交前至少执行：

```bash
python -m compileall backend edge tests
python -m unittest discover -s tests -v
```

## AI 变更红线

以下是 Public Contract，AI 的建议也不能由一人直接修改：

- IP 地址和 VLAN 编号；
- 设备 ID；
- JSON 字段、类型与单位；
- WebSocket/API 路径；
- Policy 格式；
- 顶层项目目录；
- 最终 Demo 主线。

对已有模块要求 AI 修改时，固定追加：

> 只做增量修改。先列出要修改的文件、原因、公共接口影响和验证方式；若影响公共契约，请暂停并输出 RFC，不要直接给出跨模块重构。

## 轻量 RFC

在群里或 Issue 中使用：

```text
RFC 标题：
提出人：
拟修改的公共项：
原因：
影响 Owner：
迁移方式：
验证方式：
结论：ACCEPTED / REJECTED
```

三个受影响 Owner 回复 OK 后，先更新 `docs/PROTOCOL.md` 或 `docs/NETWORK_PLAN.md`，再改代码。

## 合并定义（Definition of Done）

- 功能在自己模块独立运行。
- 使用 fake 对端通过一次集成测试。
- 未擅自改公共契约。
- 有运行命令和测试结果。
- 有一张可用于报告/验收的证据，或明确说明为何无需截图。
- `docs/PROJECT_BOARD.md` 已同步。
