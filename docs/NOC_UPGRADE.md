# EdgeCampus Intelligent NOC Upgrade

状态：IMPLEMENTED / LOCAL VERIFIED；本地分支 feat/edge，使用最新 Gate1-Gate4 基线。NOC 升级是用户授权的独立增量工作，不改变现有 Gate4 证据状态或 Gate5 状态。

## 为什么升级

原 Dashboard 只有 Edge 温控实时数据，实验网络的 Routing、IPv6、ACL、Port Security 与 Remote Administration 不能在同一运维入口解释。目标为 Edge Control + Network Operation + Security Operation + Policy Management + Failure Simulation。

## 三段开发

1. Network Agent、network REST 状态/事件接口、Network Health。
2. Security Center、非法 MAC/ACL 阻断事件。
3. Remote Operations、Campus Policy 展示、三类故障模拟与恢复、完整演示回归。

## 模块与真实性

Network Agent 在 backend/app/network_agent.py，NetworkProvider 可替换；当前 MockNetworkProvider 从 config/network_baseline.json 返回配置状态，API 与 UI 明确 source=SIMULATED / MOCK ADAPTER。当前不读取 PT、不登录 SSH、不证明实际 OSPF/BGP/Tunnel 健康。

现有 /api/state、/ws/edge、/ws/dashboard 与 Protocol 1.0 的消息格式保持；NOC 数据通过独立 REST 接口获取。真实 Edge 遥测仍由连接的 Edge 提供。Campus Policy 作为上层展示，thermal-01/version/ACK 不改。网络模拟不影响 RealWSClient 带外事实。

## 第一段接口

- GET /api/network/state：ospf/bgp/ipv6_tunnel/branch_status，以及详细 routing/ipv6/branch/source。
- GET /api/network/events：独立 NOC 事件流，不挤掉 Edge Policy/Command ACK。

## 实验融合

| 实验 | NOC 表达 |
|---|---|
| 1 IPv6 基础 | Tunnel/IPv6 与模式规划 |
| 2 VLAN/Port Security | Security Center |
| 3 ACL/NAT | 安全事件与 Campus Network Policy；业务入口仍用冻结映射 |
| 4 OSPF/BGP | Network Health |
| 5 Tunnel/Remote Admin | Tunnel 与 Branch Operations |
| Edge 创新 | Policy/FAN/ACK 与断云本地自治 |

## 第一段验证

Network Agent adapter 隔离/替换测试、真实 HTTP network state 与原 Edge snapshot 分离测试、Dashboard 健康/不可用/降级渲染，另运行现有 Gate4/ACK/contract 回归。

## 第二段：Security Center
GET /api/security/state；POST /api/simulation/security（event 可选 PORT_SECURITY_VIOLATION / ACL_BLOCK_EVENT）；POST /api/simulation/security/restore。攻击显示红色告警、阻断状态和累计次数；恢复保留审计记录。全部为模拟，不实际关闭交换机端口。


## 第三段接口与边界

- GET /api/noc/state：五功能聚合快照，1.5 秒轮询，与 Edge WS 独立。
- GET /api/branch/state；POST /api/branch/check：device=R-BRANCH 或 SW-BRANCH，source_ip 默认 192.168.30.20。仅模拟 ADMIN-PC 的 VTY ACL；来源参数不构成真实身份认证。其他来源 DENY，链路故障时 UNAVAILABLE。
- GET /api/campus-policy：thermal 使用 Backend 既有策略对象；campus_version 为 campus-1 / thermal-vN，不伪造 Edge version。Network/Security 从配置展示，不下发路由器。
- GET /api/simulation/state；POST /api/simulation/cloud、/network，以及各自 /restore；Security 见第二段。
- Cloud Failure 实际关闭 Edge WebSocket 并拒绝重连，HTTP 保持服务用于恢复。AUTO 自治为 Edge 已有本地循环行为；断连期间 FAN 仅显示 LAST KNOWN，不能证明实时物理输出。恢复后只有收到合法真实 state_sync 才报告 SUCCESS，hello 不能触发成功。
- 这是控制通道中断演练；整个 Uvicorn 进程停止/恢复的 Gate4 测试仍按原测试方案执行。
- Network Failure 仅模拟 Branch Link Down：BGP/Tunnel/Branch 降级，HQ OSPF 保持 FULL；与 Edge 带外控制链路独立。
- 模拟状态、累计违例、最多 100 条 NOC 事件在内存，Backend 重启回归配置基线。原 Edge ACK 事件保留机制不变。

## 连续演示

启动本地 Backend：`runtime/noc-venv/Scripts/python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8017`。
软件演示使用 Fake Edge（不是 PT 证据）：`runtime/noc-venv/Scripts/python.exe -m edge.fake_edge --server ws://127.0.0.1:8017/ws/edge --temperatures 35 --interval 2`。

1. 打开 http://127.0.0.1:8017，查看 Edge / Network / Security。
2. Temperature Policy 设置 AUTO、33℃，下发，检查 vN APPLIED 与 FAN ON；Campus 同步显示 thermal-vN。
3. Cloud Failure：OFFLINE、AUTONOMOUS MODE (expected)、FAN 最后观测值；Edge 按最后策略继续本地循环。Edge 命令/策略禁用，NOC 恢复按钮保持可用。
4. Restore Cloud：WAITING_FOR_STATE_SYNC → Edge 重连并发送 state_sync → SUCCESS；恢复温度与 FAN 的实时观测。
5. Network Failure：BGP DOWN / Tunnel DOWN / Branch OFFLINE，Check Router 返回 UNAVAILABLE；Restore Network 恢复 ESTABLISHED / UP。
6. Security Attack：红色 PORT_SECURITY_VIOLATION，Unauthorized MAC detected / Port blocked；Restore Security 恢复转发但保留次数与最后告警。

## 验证记录

37 项 Python 测试通过，涵盖 HTTP 状态、ACL 来源拒绝、网络故障恢复、真实 WebSocket 关闭/拒绝重连、hello 不伪造同步、非默认策略恢复，以及原 Gate4/协议回归。三个 Node 验证通过：NOC 健康/不可用/降级，Edge ACK，断线恢复。check_contract.py 通过。
浏览器连续验证了 33℃策略 v2 APPLIED、FAN ON；补验 36℃ v3 时 FAN OFF，再恢复 33℃ v4 时 FAN ON、Cloud OFFLINE、恢复按钮可用、实际重连 STATE_SYNC SUCCESS、Remote Management PASS、BGP/Tunnel DOWN 和非法 MAC 红色事件；使用本机 Fake Edge + Mock Network，不替代 PT 验收截图。
未修改 .pkt、Protocol v1.0 或已有 Gate 状态；只作三个本地提交，不推送。


## 中文界面与 Packet Tracer 连接

界面导航、功能标题、操作按钮、提示和演练说明改为中文；保留 OSPF/BGP/IPv6/ACL/VTY、设备标识及必要协议状态码。API 和 Protocol 字段不变。

PT 既有 Gate4 程序使用 `ws://127.0.0.1:8000/ws/edge`，必须与 Backend 端口一致。8017/8018 是独立软件演示端口，运行其服务不会自动让 PT 的 8000 地址可用。

真实 PT 测试在仓库根目录运行：

```powershell
& .\runtime\noc-venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

打开 http://127.0.0.1:8000，在 PT 的 EDGE-SBC-01 Programming 中运行已实测 Gate4 程序，并确认 WS_URL 与上面一致。若连接仍失败，检查 PT 的 External Network Access 是否允许，以及 SBC Console 的实际错误。不要同时把 Fake Edge 接到同一个 Backend；同一 Backend 当前只有一个 Edge 会话槽位。在 8018 运行的 Fake Edge 不占用 8000 Backend。

可通过 `Invoke-RestMethod http://127.0.0.1:8000/healthz` 检查 Backend：status=ok 只说明服务可达，edge_online=true 才说明收到 Edge 消息；该标志本身不区分 Fake Edge 和 PT，因此真实测试不启动 Fake Edge。
