# EdgeCampus NOC Upgrade 最终实现

状态：**验收完成，报告准备中**；2026-09-19，`feat/edge`。本页为最终行为；早期 Mock Network 的演示由真实 NC-only 行为替代。完整收尾与来源见 [完成报告](final/PROJECT_COMPLETION_REPORT.md)。

## 五位一体

| 功能 | API/通道 | 最终数据与作用 |
|---|---|---|
| Edge Control | `/api/state`、`/ws/edge`、`/ws/dashboard` | 既有真实 SBC 遥测/Policy/Command/ACK；Local Loop 优先 |
| Network Operation | `/api/controller/state`、`/api/network/state` | 真实 PT NC 设备清单/物理拓扑；健康卡片来自 collectionStatus |
| Security Operation | `/api/security/state`、`/api/network/events` | 模拟违例/ACL事件、累计次数、独立审计流 |
| Policy Management | `/api/campus-policy` | thermal 使用既有策略；Campus 上层展示 Edge/Network/Security |
| Failure Simulation | `/api/simulation/state`、`/api/simulation/*` | Cloud 真实中断控制通道；Security 模拟；Network 禁用 |

`/api/noc/state` 聚合各 NOC 快照，前端约 1.5 秒轮询。NC 采集采用约 5 秒缓存，HTTP 在线程池执行，不阻塞 Edge WS。NOC 事件与原 Edge ACK 事件分开。

## 真实 Network Health

控制器适配器 `backend/app/pt_controller.py` 登录 `/api/v1/ticket`，只读 `/api/v1/network-device` 与 `/api/v1/topology/physical-topology`。连接参数在启动时由环境读取；脚本交互输入账户，不写 NC 密码文件。页面/API 不返回密码与 ticket。

- 仅接受 `PT_CONTROLLER` 来源的 CONNECTED 清单，显示 hostname/name、managementIpAddress/ipAddress、type 和 collectionStatus。
- `collectionStatus == Managed` 精确映射 ONLINE；其他值保留控制器报告，缺字段为 NOT COLLECTED，不把 reachabilityStatus 代替 Managed。
- OSPF/BGP/IPv6 Tunnel 均 NOT COLLECTED；不推断 FULL/ESTABLISHED/UP，不展示 UNKNOWN。
- 无配置、认证/连接失败、Backend 失联时清空卡片，不回退 Mock，不保留旧 ONLINE。
- 拓扑读取失败保留已成功取得的设备清单并报告降级。
- 仅向本机控制器发送认证，不跟随重定向，不使用系统代理；401 重登录后重试一次。

用户已确认真实 NC 接入和 Dashboard 显示。已有 [NC Managed 清单截图](../evidence/noc/NOC-NC-01-controller-managed-inventory.png)，两项为 SW-CORE/SW-BRANCH。成功 Dashboard、同次 API、失败恢复配套留证见 [C01–C15逐张清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)。不声明 R-HQ 已 Managed。

## Security / Branch / Campus Policy

Security：`POST /api/simulation/security` 支持 PORT_SECURITY_VIOLATION 与 ACL_BLOCK_EVENT；`POST /api/simulation/security/restore` 恢复并保留累计次数/最后事件。红色卡片、Unauthorized MAC/Port blocked 为模拟，不改变 PT 端口。

Branch：`GET /api/branch/state`、`POST /api/branch/check`，展示 R-BRANCH `172.16.40.65`、SW-BRANCH `172.16.40.66`；按配置模拟 ADMIN-PC `192.168.30.20` 的 VTY ACL PASS/ALLOW，其他来源 DENY。请求中的 source_ip 不是认证，不发起 Telnet/SSH。真实登录证据另按 N14 验收。

Campus：thermal-01/version/ACK 机制不改，campus_version 为 campus-1 / thermal-vN。Backend thermal 对象是策略状态，实际执行以 Edge ACK/回报为准。Branch Access ALLOW、IoT Isolation ENABLE、Port Security STRICT 是 Network/Security 配置展示，不写 IOS。

模拟状态与最多 100 条 NOC 事件保存在内存，重启回到配置基线。

## 故障中心最终边界

- `POST /api/simulation/cloud` 实际关闭 Edge WebSocket并拒绝重连，HTTP 保持服务；离线 FAN 为 LAST KNOWN。自治提示表示预期行为，真实 FAN 动作须在 PT 中观察。
- `POST /api/simulation/cloud/restore` 放开连接；只有合法 Edge state_sync 才标记 SUCCESS，hello 不能代替同步。
- 此按钮与 G4 真正停止/重启 Uvicorn 是两项不同演示；报告复现时分别保留按钮流程和真实停服自治画面。
- `POST /api/simulation/network` 及 `/restore` 返回 409，界面禁用。不能演示模拟 BGP DOWN/Tunnel DOWN 来证明真实 NC 网络故障。
- 安全攻击仍为模拟，报告中的真实 Port Security 功能在 PT 手工触发并截图。

## 课程知识对应

以仓库 [ACCEPTANCE](ACCEPTANCE.md) 既有五次实验表为准：实验1 地址/IPv6与远程管理；实验2 VLAN/Trunk/EtherChannel/SVI/ROAS；实验3 ACL/NAT/DNS/HTTP；实验4 OSPF/eBGP；实验5 Port Security/Tunnel。NOC 是对这些基础设施能力的可观测与解释入口，控制器管理健康不等于所有实验协议均已被自动采集。

## 开发过程与验证

三段开发完成 Network Agent→Security→Branch/Policy/Simulation，再增加中文界面、PT 端口对齐、真实 NC 适配器与真实健康卡片。早期 Fake Edge+Mock Network 连续演示属于软件开发记录，不作为最终真实 PT 验收。

本次 46 Python、3 Node、compileall、Protocol contract 通过，详见 [VALIDATION](final/VALIDATION.md)。Protocol 1.0、设备 ID、Edge WS/API 与严格递增版本保持。最新正式 `.pkt` 已纳入当前分支；现场保存重开和包内程序一致性仍按最终清单核验。

真实启动与网络配置见 [PT_CONTROLLER_SETUP](PT_CONTROLLER_SETUP.md)，最终演示见 [DEMO_SCRIPT](DEMO_SCRIPT.md)，报告素材计划见 [清单](final/EVIDENCE_PENDING.md)。
