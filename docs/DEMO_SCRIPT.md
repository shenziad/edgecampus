# 最终现场演示与彩排脚本

项目：**完成（待补证据）**。版本：2026-09-18。主讲约6分钟；最终完整验收/三轮彩排需额外时间。实际操作先彩排，不把模拟界面当作真实网络证明。

## 演示前

1. 打开当前canonical `packet_tracer/EdgeCampus.pkt`，确认PT版本、HQ/WAN/Branch/NC/IoT。核对运行SBC程序与仓库Gate4版本，确认最后有效AUTO阈值/迟滞，不假定默认v1。
2. NC Real World Access监听58000，Backend用8000；NC清单SW-CORE/SW-BRANCH Managed。启动方式见 [PT_CONTROLLER_SETUP](PT_CONTROLLER_SETUP.md)。真实演示不启动Fake Edge。
3. IOS预检查：Po1 SU、OSPF邻居/路由、BGP会话/前缀、Tunnel/IPv6静态路由、VTY ACL、NAT。Dashboard协议NOT COLLECTED是采集范围，不是协议故障。
4. 准备固定温度操作人、原图/JSON保存目录、停止Backend的Ctrl+C与重启命令。温度操作使用实际阈值/迟滞，调低到关闭阈值以下后再上升，避免迟滞导致误判。

## 主展示：约6分钟

| 时间 | 操作与讲解 |
|---|---|
| 0:00–0:45 | 拓扑与Dashboard全景：Edge Control + Network Operation + Security Operation + Policy Management + Failure Simulation。说明Edge真实控制、NC真实只读、Security/Branch模拟、Network/Security策略展示 |
| 0:45–1:40 | 打开Network Health：设备名/IP/类型/collectionStatus与NC清单对照；两台Managed→ONLINE。OSPF/BGP/Tunnel NOT COLLECTED，协议验收快速切IOS show输出。NC管理健康不等于全部业务可达 |
| 1:40–2:40 | Temperature Policy设AUTO/33℃（version自动递增），观察APPLIED ACK；按迟滞先降温关闭，再约32℃保持OFF、约34℃开启，PT FAN与Dashboard一致。Command ON/OFF及ACK可快速展示，随后恢复AUTO |
| 2:40–4:05 | 核心：真停Backend（Ctrl+C），Dashboard失联；Edge保留最后策略，调温跨阈值和关闭迟滞观察物理FAN ON/OFF。重启同一NC启动脚本，展示自动reconnect/hello/state_sync与UI温度/FAN/策略/version恢复，无默认回退 |
| 4:05–5:00 | 校园网络业务：Branch访问`http://203.0.113.1`命中HQ-SERVICE；HQ OFFICE域名DNS/HTTP与PAT；BR-ADMIN IPv6跨Tunnel访问管理域。真实远程管理允许与普通用户拒绝可用现场操作或清晰预先证据解释 |
| 5:00–6:00 | Security Attack模拟红色事件与恢复审计；Branch Check模拟VTY规则解释；Campus三策略状态与Edge ACK对应。主动说明Network Failure已禁用，不能伪造BGP DOWN；真实Port Security另在交换机上验收 |

Cloud按钮中断WS演练可在扩展验收展示：HTTP仍服务，恢复后WAITING_FOR_STATE_SYNC→真实state_sync→SUCCESS；这与主展示真正停Backend不同。离线页面FAN为最后观测，物理实时动作在PT观察。

## 扩展真实网络验收命令

在相应PT设备特权模式执行，以PT实际支持的语法/输出为准：

```text
show vlan brief
show interfaces trunk
show etherchannel summary
show ip interface brief
show ip route
show ip ospf neighbor
show ip bgp summary
show ip bgp
show access-lists
show running-config
show ip nat translations
show ip nat statistics
show ipv6 interface brief
show ipv6 route
show interfaces tunnel 0
show port-security interface fa0/1
show mac address-table interface fa0/1
```

配合真实SLAAC/DHCPv6/Static地址分配、IPv6端到端ping、ADMIN Telnet两台Branch设备、OFFICE/BR-OFFICE拒绝、不同MAC违例与恢复。restrict丢弃非法MAC流量，不自动等于物理shutdown。

## 最终连续三轮彩排（EV-28）

同一最终包/代码版本连续完成3轮；每轮按清单覆盖：Edge+NC基线、Policy/Command ACK、真实停Backend升降温与恢复、N1–N15关键业务/安全验证、NOC中文五板块和模拟边界。记录日期/操作者/包哈希/软件提交、阈值/version、预期/实际、截图/JSON/日志位置和异常。

当前尚无三轮记录，**待执行并留证**。某轮失败应保存真实失败、修复后重新取得连续3轮，不补写不存在的PASS。完整待补项见 [28组清单](final/EVIDENCE_PENDING.md)。

## 讲解时保持的边界

PT WAN是模拟企业数据平面；RealWSClient→宿主机FastAPI为带外通道，不经过PT BGP/NAT。NC REST是另一个宿主机对外API端口；HQ-SERVICE/BACKEND-STUB不是FastAPI。项目开发完成与证据齐全/三轮验收通过是不同状态，当前为完成（待补证据）。
