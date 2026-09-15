# 四人 + AI 协作规范 — Final Architecture v2

## Owner 与边界

| Owner | 可独立修改 | Final Architecture v2 主责 | 跨界前必须沟通 |
|---|---|---|---|
| A Network | `packet_tracer/`、网络证据 | HQ Core regression、Branch/WAN、OSPF/BGP、NAT、IPv6 Tunnel、Port Security；唯一 canonical `.pkt` Owner | VLAN/IP/AS/接口、真实主机接入方式 |
| B Edge | `edge/`、Edge 证据 | Local Loop、PT Telemetry、Policy/Command、重连 | 消息字段、设备 ID、连接方式 |
| C Control Plane | `backend/`、Backend 证据 | WebSocket、状态、事件、策略转发；补 C Gate1 placeholder | WS/API 路径、消息语义 |
| D UI & Integration | `dashboard/`、`tests/`、联调证据 | Dashboard、端到端联调、证据与彩排 | 公共字段、验收流程 |

任何人都可以修文档错字；修改 Public Contract 或 Final Architecture v2 冻结网络项必须走 RFC。

## 分支

```text
main
├── feat/network
├── feat/edge
├── feat/backend
└── feat/dashboard
```

Gate 1 的 A+B 集成和 D 证据已经归档到 `main`。后续开发仍在各 Owner 分支完成，达到当前 Gate 的 Definition of Done 后再合入 `main`。

A 是唯一可以提交/替换正式 `packet_tracer/EdgeCampus.pkt` 的 Owner。B 若需要开发 PT Edge，应使用副本并只提交可复用代码、接线/API 说明，由 A 合并回 canonical `.pkt`。

## Final Architecture v2 的项目级 Re-baseline

Final Architecture v2 是全组批准的架构升级，不视为某个 Owner 擅自改变 Gate 0。它明确：

- 保留 HQ VLAN10/20/30 和 Gate 1 Core；
- 从 `SW-CORE Gi1/0/24` 向外扩展 HQ Edge / ISP / Branch；
- 新增 Branch VLAN40/50、WAN prefixes、AS65001/65000/65002、IPv6 prefixes；
- Protocol v1.0 完全不变。

**从 Final Architecture v2 文档发布后，这些新增项也成为冻结公共项。** 任何后续重编号、换接口、换 AS、改业务权限的建议都必须先 RFC。

## Commit 约定

```text
feat(edge): send real packet tracer telemetry
feat(network): build branch router-on-a-stick
feat(network): add ospf bgp wan routing
fix(backend): reject malformed telemetry safely
test(integration): verify real pt telemetry dashboard
fix(network): restore hq acl regression
```

禁止把未运行的 AI 输出直接提交。

软件提交前至少执行：

```bash
python -m compileall backend edge tests
python -m unittest discover -s tests -v
```

Packet Tracer 提交前必须执行本 Gate 对应的网络 regression，并把关键命令/结果写入 `packet_tracer/CONFIG_LOG.md` 或阶段报告。

## Public Contract / 冻结红线

### 软件红线

- Protocol version `1.0`；
- 设备 ID；
- JSON 字段、类型、单位；
- WebSocket/API 路径；
- Policy 格式；
- 顶层项目目录；
- Edge Local Loop 的迟滞语义。

### 网络红线

- HQ VLAN10/20/30 与 IPv4 网段；
- Gate 1 已验证 HQ 端口映射；
- Final Architecture v2 的新增物理接口映射；
- Branch VLAN40/50；
- WAN IPv4 prefixes；
- AS65001 / AS65000 / AS65002；
- Final Architecture v2 IPv6 prefixes；
- A 对 canonical `.pkt` 的唯一所有权；
- Packet Tracer 数据平面与 RealWSClient 带外控制通道的真实性边界。

对已有模块要求 AI 修改时固定追加：

> 只做增量修改。先列出要修改的文件、原因、公共接口影响、Gate 影响和验证方式；若影响 Public Contract、Final Architecture v2 冻结网络项或其他 Owner，请暂停并输出 RFC，不要直接重构。

## 轻量 RFC

```text
RFC 标题：
提出人：
当前 Gate：
拟修改的公共项：
原因：
影响 Owner：
是否影响已有 Gate 证据：
迁移方式：
回归测试：
结论：ACCEPTED / REJECTED
```

三个受影响 Owner 回复 OK 后：

1. 先更新权威文档：软件改 `docs/PROTOCOL.md`；网络改 `docs/NETWORK_PLAN.md`；架构改 `docs/ARCHITECTURE.md`。
2. 再修改代码 / `.pkt`。
3. 最后完成相关 Gate regression。

## Packet Tracer 分层实施规则

A 与协助 A 的 AI 必须按层推进：

```text
Physical topology
→ Branch VLAN / ROAS
→ IPv4 adjacent links
→ OSPF
→ eBGP
→ ACL / business flows
→ NAT / DNS / HTTP
→ IPv6 addressing
→ IPv6 Tunnel / static routes
→ Port Security
→ Full regression
```

不要一次性叠加多个协议后再排错。

## Gate 1 C Placeholder 规则

`docs/gate1/C_BACKEND_REPORT.md` 当前是明确占位符。

- 占位符允许项目进入 Gate 2；
- 占位符不等于 PASS；
- C 应在 G2 期间尽早补验收；
- Gate 5 Freeze 前必须替换为正式 Owner 报告和证据；
- 不允许通过改文档措辞把未完成验收“改成已完成”。

## 合并定义（Definition of Done）

- 功能在自己模块/设备独立运行。
- 当前 Gate 的必要 fake 或真实对端测试通过。
- 未擅自改公共契约。
- 有运行/配置命令和测试结果。
- 有可用于报告/验收的证据，或明确说明为何无需截图。
- 对已有 Gate 做必要 regression。
- `docs/PROJECT_BOARD.md` 已同步。
- 涉及 PT 网络时，明确区分模拟 Data Plane 与真实带外 Control Channel。
