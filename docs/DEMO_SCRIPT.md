# 最终现场演示与彩排脚本

项目：**完成（待补证据）**。版本：2026-09-19。最终演示固定采用 **园区管理 → 中心物联网控制 → Dashboard 面板控制** 的顺序。完整逐项操作、命令和预期画面见 [最终功能演示设计](FINAL_FUNCTION_DEMO.md)；本文用于现场快速串讲和彩排。

## 演示前

1. 打开当前canonical `packet_tracer/EdgeCampus.pkt`，确认PT版本、HQ/WAN/Branch/NC/IoT。核对运行SBC程序与仓库Gate4版本，确认最后有效AUTO阈值/迟滞，不假定默认v1。
2. NC Real World Access监听58000，Backend用8000；NC清单SW-CORE/SW-BRANCH Managed。启动方式见 [PT_CONTROLLER_SETUP](PT_CONTROLLER_SETUP.md)。真实演示不启动Fake Edge。
3. IOS预检查：Po1 SU、OSPF邻居/路由、BGP会话/前缀、Tunnel/IPv6静态路由、VTY ACL、NAT。Dashboard协议NOT COLLECTED是采集范围，不是协议故障。
4. 准备固定温度操作人、原图/JSON保存目录、停止Backend的Ctrl+C与重启命令。温度操作使用实际阈值/迟滞，调低到关闭阈值以下后再上升，避免迟滞导致误判。

## 主展示：约12分钟

| 时间 | 功能 | 操作与讲解 |
|---|---|---|
| 0:00–0:40 | 园区管理 | PT完整拓扑：总部、ISP/Internet、分部、NC、IoT。说明这是人员入网、业务访问、安全隔离与运维的统一校园场景 |
| 0:40–2:00 | 园区管理 | 总部员工DHCP/SLAAC；`show vlan brief`、Trunk、Po1 SU/P；ADMIN→IoT允许、OFFICE→IoT拒绝 |
| 2:00–3:05 | 园区管理 | 分部DHCP/VLSM、VLAN40/50和ROAS；展示办公地址`.0/26`与管理地址`.64/27` |
| 3:05–4:20 | 园区管理 | OSPF FULL、BGP表中PfxRcd数字、Branch访问`http://203.0.113.1`；普通分部用户访问管理/IoT失败 |
| 4:20–5:15 | 园区管理 | HQ OFFICE打开`www.edgecampus.net`并展示PAT；外部访问`203.0.113.1:80`命中HQ-SERVICE |
| 5:15–6:20 | 园区管理 | Tunnel0 up/up、双向IPv6 ping；ADMIN Telnet分部成功、普通用户失败；Port Security非法MAC计数增加并恢复 |
| 6:20–7:15 | 中心物联网控制 | 展示TEMP→MCU→SBC→FAN；AUTO/33℃/迟滞1℃，低温OFF、迟滞区保持、高温ON |
| 7:15–8:35 | 中心物联网控制 | 真停Backend；Edge保留最后策略并完成离线ON/OFF。重启后reconnect/hello/state_sync，策略和状态恢复 |
| 8:35–9:20 | Dashboard | 中文总览、实时温度/FAN；下发Policy与MANUAL命令，展示APPLIED ACK和物理FAN |
| 9:20–10:10 | Dashboard | Network Health与真实NC清单对照：两台Managed→ONLINE，OSPF/BGP/Tunnel为NOT COLLECTED |
| 10:10–11:10 | Dashboard | Security Attack与恢复、Branch Check、Campus Policy三类状态。说明真实网络结果已在第一部分直接验证 |
| 11:10–12:00 | Dashboard | Cloud Failure真实断开WS并等待state_sync恢复；Network Failure禁用/409。恢复ONLINE/CONNECTED/SECURE画面收束 |

Cloud按钮中断WS演练和真正停止Backend是两项不同验收：按钮验证Dashboard演练流程；真正停8000验证Edge在云端服务消失时仍自治。离线页面FAN为最后观测，物理实时动作在PT观察。

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

## 最终连续三轮彩排

同一最终包/代码版本连续完成3轮；每轮按清单覆盖：Edge+NC基线、Policy/Command ACK、真实停Backend升降温与恢复、N1–N15关键业务/安全验证、NOC中文五板块和模拟边界。记录日期/操作者/包哈希/软件提交、阈值/version、预期/实际、截图/JSON/日志位置和异常。

当前尚无三轮记录，**待执行并留证**。某轮失败应保存真实失败、修复后重新取得连续3轮，不补写不存在的PASS。完整待补项见 [最终待补索引](final/EVIDENCE_PENDING.md)。

## 讲解时保持的边界

PT WAN是模拟企业数据平面；RealWSClient→宿主机FastAPI为带外通道，不经过PT BGP/NAT。NC REST是另一个宿主机对外API端口；HQ-SERVICE/BACKEND-STUB不是FastAPI。项目开发完成与证据齐全/三轮验收通过是不同状态，当前为完成（待补证据）。
