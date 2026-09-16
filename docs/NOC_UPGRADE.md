# EdgeCampus Intelligent NOC Upgrade

状态：IN PROGRESS；本地分支 feat/edge，使用最新 Gate1-Gate4 基线。NOC 升级是用户授权的独立增量工作，不改变现有 Gate4 证据状态或 Gate5 状态。

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

Network Agent adapter 隔离/替换测试、真实 HTTP network state 与原 Edge snapshot 分离测试、Dashboard 健康/不可用/降级渲染，另运行现有 Gate4/ACK/contract 回归。后续段落随实际完成更新。

## 第二段：Security Center
GET /api/security/state；POST /api/simulation/security（event 可选 PORT_SECURITY_VIOLATION / ACL_BLOCK_EVENT）；POST /api/simulation/security/restore。攻击显示红色告警、阻断状态和累计次数；恢复保留审计记录。全部为模拟，不实际关闭交换机端口。
