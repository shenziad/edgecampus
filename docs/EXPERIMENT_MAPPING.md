# EdgeCampus 五次实验技术映射

更新日期：2026-09-19。课程技术目录以用户本次提供的“五次实验梳理”为准，不把较早 NOC 提示中的实验编号混用。配置来源、设备地址、命令及版本记录见 [FINAL_CONFIGURATION](FINAL_CONFIGURATION.md)。

按用户确认，G4/network 原则上与当前网络配置一致，作为当前网络基线；后续 NC 接入为增量。本次查看了 G4 的关键配置/验证图片，映射同时区分“实际网络配置”“软件模拟/展示”“课程涉及但项目未启用”。不能因为课程讲过某技术，就声称最终作品已部署该技术的所有变体。

## 1. 阅读方法与实验总表

各表逐项回答：课程技术是什么、在本项目的哪个区域/设备/接口使用、解决什么问题、怎样验证。编号用于逐项核对，共 **71 项技术与验证内容**，其中包含明确未启用的课程变体；它们不是71项全部通过的验收结论。

| 实验 | 原实验主题 | 当前作品主要落点 | 配置章节 / 验收 |
|---|---|---|---|
| 一 | IPv6网络配置与基础互联 | HQ SLAAC、Branch DHCPv6、管理Static IPv6、四条IPv6路由、中央Telnet/VTY认证 | [IPv6](FINAL_CONFIGURATION.md#ipv6)、[Tunnel路由](FINAL_CONFIGURATION.md#tunnel)、[管理](FINAL_CONFIGURATION.md#security)；N12–N14 |
| 二 | VLAN与园区二层/三层架构 | HQ VLAN10/20/30、Po1 LACP、Core SVI；Branch VLAN40/50、Trunk/ROAS；IPv4 DHCP | [二层](FINAL_CONFIGURATION.md#layer2)、[IPv4](FINAL_CONFIGURATION.md#ipv4)；N1/N3/N4 |
| 三 | 企业出口访问控制与公网服务发布 | Core SVI ACL、R-HQ WAN-IN/PAT/TCP80映射、Internet DNS/HTTP | [安全](FINAL_CONFIGURATION.md#security)、[服务](FINAL_CONFIGURATION.md#services)；N2/N7–N11 |
| 四 | 企业路由协议与跨域互联 | Core↔R-HQ OSPF Area0；HQ65001↔ISP65000↔Branch65002 eBGP | [路由](FINAL_CONFIGURATION.md#routing)；N5/N6及跨站点业务 |
| 五 | 网络安全增强与IPv6 Overlay | Access Fa0/1 sticky/max1/restrict；R-HQ/R-BRANCH IPv6-over-IPv4 Tunnel | [端口安全](FINAL_CONFIGURATION.md#security)、[Overlay](FINAL_CONFIGURATION.md#tunnel)；N15/N13 |

用户提供的实验五目录中有shutdown/restrict两种违规模式；当前项目选择restrict。实验二讲Native VLAN，HQ与Branch的现有Trunk证据均显示默认VLAN1，未登记自定义Native VLAN。实验一讲DHCPv6 DNS下发，当前地址池未登记此选项。下面逐项保留这些差别。

## 2. 实验一：IPv6网络配置与基础互联

对应配置总览 §6、§8、§9；核心作用是让总部/分部管理域获得可规划、可分配、可跨站点使用的IPv6地址，并建立可控远程管理。

| ID | 课程技术 | 在当前项目用在哪里 | 作用、配置要点与验证 |
|---|---|---|---|
| E1-01 | IPv6地址/前缀规划 | HQ VLAN10 `10::/64`、MGMT `30::/64`、Transit `100::/64`；Branch40/50；Tunnel `ff::/64`，均属于2001:db8 | 按区域分配/64，避免把LAN与隧道混为一个网段；完整前缀见总览。IoT20::/64为规划未启用 |
| E1-02 | Global Unicast Address形式 | Core SVI、R-HQ/Branch接口与管理PC/Server | 使用2001:db8文档实验地址验证全局地址形式；不是可在真实Internet发布的生产公网地址 |
| E1-03 | Link-local Address | 启用IPv6的接口、OFFICE/BR-OFFICE客户端 | 用于链路邻接/RA等；BR-OFFICE证据中的FE80客户端与网关实际存在。未手工统一配置fe80::1，IPv6接口/PC输出核验 |
| E1-04 | 路由器/三层接口IPv6地址 | Core VLAN10/30与Gi1/0/24；R-HQ G0/0；Branch G0/1.40/.50 | `ipv6 unicast-routing`与`ipv6 address …/64`提供LAN网关和IPv6转发；看接口地址及up/up |
| E1-05 | PC/Server固定IPv6地址 | ADMIN-PC30::20、HQ-SERVICE30::10、BR-ADMIN50::70 | 管理目标固定，便于运维；GUI Static、/64及各自::1网关。ADMIN→服务、本地/跨站点ping验证 |
| E1-06 | SLAAC | HQ OFFICE-PC，SW-CORE VLAN10 | 客户端Auto Config，依据RA自动生成地址，减少办公终端逐台配置；G4-A-03c为客户端证据 |
| E1-07 | Router Advertisement（RA） | Core VLAN10与Branch G0/1.40 | 提供前缀/路由信息，Branch M标志通知DHCPv6取地址；没有登记禁止SLAAC的no-autoconfig，不把M=1说成SLAAC自动关闭 |
| E1-08 | 有状态DHCPv6地址分配 | Branch VLAN40，BR-OFFICE-PC | 当前基线BR-V6地址池分配40::/64地址，区别于HQ SLAAC；服务端绑定与客户端实际地址对应才证明本次分配 |
| E1-09 | DHCPv6 Server | R-BRANCH | `ipv6 dhcp pool BR-V6`、address prefix；G0/1.40绑定server BR-V6与managed-config-flag，集中维护地址 |
| E1-10 | DHCPv6 Client | BR-OFFICE-PC | IPv6选DHCP；G4-A-03d中客户端地址与R-BRANCH IA_NA绑定一致。默认IPv6路由由RA/主机配置获取，非DHCPv6默认网关选项 |
| E1-11 | DHCPv6 DNS等参数下发 | 当前BR-V6未登记此配置 | 课程包含该能力，项目已使用有状态地址分配，但没有记录dns-server/domain-name；不能用HQ IPv4 DHCP DNS代替此项覆盖 |
| E1-12 | IPv6 Static Route | Core/R-HQ/R-BRANCH四条管理域路由 | Branch到HQ30、HQ到Branch50及Core回程；指向Transit/对端Tunnel IPv6地址，不引入OSPFv3。见G4-A-04c |
| E1-13 | Telnet Remote Management | ADMIN-PC `.30.20`→R-BRANCH `.40.65`/SW-BRANCH `.40.66`；NC增量Discovery使用Telnet | 真正远程维护设备；基线以实际登录提示符与允许/拒绝证明，Branch页面模拟PASS不能替代登录。未声称已部署SSH |
| E1-14 | VTY管理入口 | R-BRANCH/SW-BRANCH；NC报告涉及实际被管理设备 | line vty上的transport与access-class控制谁可登录；与接口数据ACL的ip access-group区分。当前NC增量需保留管理员并允许`.30.30` |
| E1-15 | 远程用户认证 | G4基线line password/login；后续NC报告username admin/login local | 认证从线路密码向本地用户方式演进。NC Web/API账号与设备CLI凭据分开；不将两阶段写成同时生效的两种登录方式 |
| E1-16 | IPv6连通、地址获取与登录验证 | ADMIN/BR-ADMIN、OFFICE/BR-OFFICE、Core/R-HQ/Branch | PC ipconfig、DHCPv6 binding、show ipv6 interface/route、实际IPv6 ping/Telnet。N12地址分配、N13跨站点、N14远程登录分别验收 |

相关远程证据：G4-A-03/03b/03c/03d、04/04b/04c/04d、01/01b/01c；[完整G4证据目录](https://github.com/shenziad/edgecampus/tree/4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8/evidence/network)。图片中的动态地址/计数是当次实测，不是固定配置。

## 3. 实验二：VLAN与园区二层/三层架构

对应配置总览 §3、§4；总部以三层Core提供规模化网关，分部以单臂路由降低设备复杂度，两者共同组成分区网络。

| ID | 课程技术 | 在当前项目用在哪里 | 作用、配置要点与验证 |
|---|---|---|---|
| E2-01 | VLAN划分 | HQ Core/Access VLAN10 OFFICE、20 IOT、30 MANAGEMENT；Branch40 OFFICE、50 MGMT | 一个物理网络划分多个逻辑业务区域；NC接入VLAN30，独立运维设备不进入普通办公区 |
| E2-02 | 广播域与部门隔离 | OFFICE/IOT/MGMT及分部两域 | VLAN隔离二层广播；一旦启用三层路由，权限仍依靠ACL，不能说仅有VLAN就自动阻断全部跨域访问 |
| E2-03 | Access端口 | Access Fa0/1→10、Fa0/2→20、Fa0/3–4→30；Branch Fa0/1→40、Fa0/2→50；Core Gi1/0/10→30 | 固定终端归属；switchport mode access/access vlan，show vlan brief与端口表核验 |
| E2-04 | Trunk链路 | HQ Core↔Access的Po1；Branch SW Gi0/1↔Router G0/1 | 一条逻辑/物理上联承载多个VLAN；HQ allowed10/20/30，Branch40/50，show interfaces trunk核验 |
| E2-05 | IEEE 802.1Q | HQ Trunk、Branch .40/.50路由子接口 | VLAN标签标识流量归属；Branch encapsulation dot1Q 40/50使同一Router物理口服务两个网关 |
| E2-06 | Native VLAN | 现有802.1Q Trunk的相关属性 | HQ Po1与Branch Gi0/1的真实证据均显示默认Native VLAN1；业务允许列表分别为10/20/30与40/50。未登记自定义switchport trunk native vlan设置，不把管理VLAN宣称为Native VLAN；证据链接见总览二层章节 |
| E2-07 | LACP协商 | Core Gi1/0/1–2、Access Gi0/1–2 | channel-group 1 mode active，两条链路协商为同一聚合；成员(P)和LACP状态为验证依据 |
| E2-08 | EtherChannel/Port-channel | HQ Po1 | 两个物理成员形成逻辑Trunk；Po1(SU)证明二层聚合使用中。分部没有另建聚合，不按拓扑对称推断 |
| E2-09 | 聚合带宽/可靠性 | HQ双链路Core↔Access | 提供多流量分担及单成员失效时仍有另一链路；不保证单条流翻倍。已有聚合状态不等于已归档拔线容灾测试 |
| E2-10 | SVI三层交换网关 | SW-CORE Vlan10/20/30 | .10.1/.20.1/.30.1配合ip routing实现HQ三层网关；SW-BRANCH Vlan50仅为本机管理SVI，没有ip routing |
| E2-11 | Inter-VLAN Routing | HQ由Core SVI；Branch由Router子接口 | 允许域跨VLAN互通，非法业务由ACL约束；接口直连路由与端到端允许/拒绝结合验证 |
| E2-12 | Router-on-a-Stick | R-BRANCH G0/1.40/.50与SW-BRANCH Trunk | /26办公网与/27管理网共享物理上联；体现VLSM，网关`.1`与`.65`不能配置成同一/24 |
| E2-13 | IPv4 DHCP/IP/Gateway/DNS | HQ Core OFFICE池；Branch Router BR-OFFICE池 | HQ发放IP/网关及192.0.2.10 DNS，排除.1–.9；Branch发放/26 IP与网关，排除.1，未登记DNS选项。办公终端自动获取，管理终端Static |
| E2-14 | 同VLAN/跨VLAN、Trunk、聚合、获址验证 | Core/Access/Branch与PC | show vlan/trunk/etherchannel、SVI接口、DHCP binding及PC租约/允许域ping；N1/N3/N4对应。历史租约不是永久固定IP |

配置/历史证据：[本地CONFIG_LOG](../packet_tracer/CONFIG_LOG.md)、G1网络证据、G2-A-02/03/04及G4-A-05/05b；当前参数与接口全表见配置总览。

## 4. 实验三：企业出口访问控制与公网服务发布

对应配置总览 §6、§7；通过业务允许与隔离规则控制访问，通过PAT提供Internet出口，通过TCP80映射发布总部服务。

| ID | 课程技术 | 在当前项目用在哪里 | 作用、配置要点与验证 |
|---|---|---|---|
| E3-01 | Extended ACL | Core OFFICE-IN/IOT-IN，R-HQ WAN-IN | 对HQ相互隔离、Branch业务与管理权限应用精细规则；不是所有流量都默认拒绝，记录中末尾有permit ip any any |
| E3-02 | ACL源地址匹配 | OFFICE/IoT两个/24，BR-OFFICE/26与BR-MGMT/27 | 根据来源角色区分权限，wildcard分别0.0.0.255/.63/.31；VLSM对应ACL掩码，不把掩码与反掩码混用 |
| E3-03 | ACL目的地址匹配 | HQ-SERVICE host `.30.10`、HQ管理/IoT网段 | 服务host例外先于管理网拒绝；Branch办公可访问业务Server，不因此获得全部管理网权限 |
| E3-04 | ACL协议/端口匹配 | tcp80、tcp8000、icmp、tcp23/22及ip规则 | 分开Web、模拟控制业务、连通性与Telnet/SSH；ACL提到22不代表项目配置了SSH服务 |
| E3-05 | ACL应用方向与顺序 | Core VLAN10/20 inbound；R-HQ G0/1 inbound | ip access-group限制进入路由/出口的流量，先匹配例外再deny；VTY管理规则应使用access-class，不混成接口ACL |
| E3-06 | Standard ACL | NAT-INSIDE与管理来源ACL | NAT-INSIDE选择HQ办公PAT来源；管理ACL选择ADMIN/NC来源，两种用途不同。NAT匹配ACL本身不是接口拒绝规则 |
| E3-07 | NAT地址转换 | R-HQ | 支撑私网办公到模拟公网、内部服务对外发布；本项目具体使用PAT与静态TCP端口映射，不是所有NAT变体都部署 |
| E3-08 | PAT/Overload | R-HQ OFFICE `/24`→G0/1 `203.0.113.1` | 多个内部会话复用出口地址；NAT-INSIDE permit办公源，overload按端口/标识区分；IoT未获通用PAT，Branch未登记PAT |
| E3-09 | NAT Inside/Outside边界 | R-HQ G0/0 inside，G0/1 outside | 保证转换方向正确，与HQ/ISP业务路径对应；不是SBC带外WS的NAT路径 |
| E3-10 | Static NAT/Port Mapping | R-HQ TCP `203.0.113.1:80→192.168.30.10:80` | 采用静态端口映射发布HQ Web，未登记全协议一对一NAT；身份映射在前为PT共存修复，使Branch私网HTTP与公网HTTP都能用 |
| E3-11 | DNS Server/域名解析 | INTERNET-SERVER `192.0.2.10` | DNS On；www.edgecampus.net→192.0.2.10，status.edgecampus.net→203.0.113.1；HQ DHCP下发DNS，未登记AAAA/IPv6 DNS |
| E3-12 | HTTP/Web Server | Internet Server与HQ-SERVICE/BACKEND-STUB | Internet页面验证DNS+PAT，HQ页面验证Branch业务/静态映射；这两个PT服务器不是真实FastAPI控制平面 |
| E3-13 | NAT转换表/公网映射验证 | R-HQ、BR-OFFICE与Internet Server | show ip nat translations/statistics加两端浏览器，核对PAT与私网/公网TCP80会话；G4-A-07b为共存证据，不用ping代替HTTP |
| E3-14 | ACL命中、DNS与HTTP正负向验证 | HQ/Branch PC与网络设备 | show access-lists、允许业务和拒绝IoT/MGMT的对照、租约DNS/域名页面；IoT跨站点不通还可能源自BGP未发布，不能仅靠丢包判定ACL命中 |

实测来源：G3-A-03/04系列，G4-A-05及06/07/07b。[NAT共存最终证据](https://github.com/shenziad/edgecampus/blob/4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8/evidence/network/G4-A-07b-n7-n11-coexist-confirm-pass.png)已目视核对；修复前私网HTTP失败保留为排查历史，不是最终预期。

## 5. 实验四：企业路由协议与跨域互联

对应配置总览 §5；HQ内部使用IGP，企业与ISP之间使用EGP，实现有分工的企业WAN，并为后续IPv6 Tunnel提供IPv4 Underlay。

| ID | 课程技术 | 在当前项目用在哪里 | 作用、配置要点与验证 |
|---|---|---|---|
| E4-01 | OSPF/IGP | HQ SW-CORE↔R-HQ | 内部动态学习HQ三个VLAN网段；只在HQ内部，不把ISP/Branch全加入同一OSPF域 |
| E4-02 | OSPF Area 0 | Transit10.255.0.0/30及Core HQ网段 | 单骨干区域，保持内部设计简单；network语句area0与邻居FULL验证 |
| E4-03 | OSPF Router ID | Core10.255.0.1，R-HQ10.255.0.2 | 显式标识邻居，不与NC新增Loopback10.255.255.1混同；查看neighbor ID和running-config |
| E4-04 | OSPF Network宣告 | Core声明Transit与三个/24；R-HQ声明Transit | 在匹配接口启用OSPF并发布相应连接信息；使用wildcard，未登记将WAN链路加入OSPF |
| E4-05 | OSPF邻居与动态路由学习 | Core/R-HQ | G4-A-05c显示FULL与R-HQ三条O路由；DR/BDR是当次选举结果，不能固定宣称某设备永久DR |
| E4-06 | BGP/EGP | R-HQ、R-ISP、R-BRANCH | 自治系统之间交换IPv4前缀，支撑异地业务和Internet LAN；不是Dashboard自动采集协议状态 |
| E4-07 | AS自治系统规划 | HQ65001、ISP65000、Branch65002 | 按企业站点与运营商边界分角色；router bgp本地AS与neighbor remote-as匹配 |
| E4-08 | eBGP Neighbor | HQ↔ISP `.113.1/.2`；ISP↔Branch `.100.1/.2` | 两条AS间会话，三个路由器共四条邻居条目；ISP有两个peer，不能称为三个独立会话 |
| E4-09 | BGP Route Advertisement | HQ发布192.168.30/24；Branch两个VLSM前缀；ISP发布192.0.2/24及两WAN/30 | 显式network/mask，业务前缀可达；不自动发布IoT/Office全部网络，BGP network还依赖实际路由存在 |
| E4-10 | AS Path | 各路由器BGP表内跨AS路径属性 | 验证远端业务路由经过ISP的AS序列；本项目未登记AS-path过滤/手工prepend命令，不将普通AS Path观测当成策略调优 |
| E4-11 | OSPF+BGP融合 | R-HQ两类路由交汇；Core由默认出口外出 | R-HQ静态默认指ISP并default-information originate；BGP显式network发布业务；**无redistribute**，不把融合说成路由重分发 |
| E4-12 | 前缀/出口路由策略 | HQ管理网发布，IoT不对外发布；Core仅需默认路由 | 减少外部路由进入园区并限制可达范围；路由不发布与WAN ACL构成隔离。未部署route-map、MED/local-pref调优 |
| E4-13 | 路由表/BGP表/跨区域Ping验证 | 三个路由器、Core与Branch PC | show ip route、show ip bgp、show ip bgp summary及跨区域ping；PfxRcd数字表明已建立。协议JSON NOT COLLECTED，Managed只证明NC管理状态 |

实测来源：G3-A-01/02系列与G4-A-05c；基线show输出已经记录，NC升级后的实时状态仍按现场读取。增加管理Loopback不自动意味着已新增BGP/OSPF发布或改变Router ID。

## 6. 实验五：网络安全增强与IPv6 Overlay

对应配置总览 §6.5、§9；接入层限制未授权设备，跨站点层在IPv4-only ISP上建立IPv6管理通道。

| ID | 课程技术 | 在当前项目用在哪里 | 作用、配置要点与验证 |
|---|---|---|---|
| E5-01 | Port Security | SW-ACCESS Fa0/1→OFFICE-PC | access VLAN10端口开启switchport port-security，控制接入设备；没有对每个交换端口都启用该功能 |
| E5-02 | Sticky MAC | 同一Fa0/1 | 自动学习合法MAC并写入运行配置；G4图中SecureSticky 00E0.F9B0.77EE，保存入startup-config需保存重开核验 |
| E5-03 | Maximum MAC | Fa0/1 maximum1 | 每端口只允许一个安全MAC；不是整个VLAN只允许一台终端，show port-security核对Max |
| E5-04 | MAC Binding/端口绑定 | 合法OFFICE MAC↔Fa0/1/VLAN10 | 通过sticky实现绑定，未登记手工静态MAC命令；历史MAC具体值有证据，当前使用终端仍应按实际匹配 |
| E5-05 | Violation Mode选择 | Fa0/1 | 当前明确选择restrict，结合演示可恢复性；不是同时配置shutdown和restrict |
| E5-06 | Restrict | Fa0/1非法MAC流量 | 丢弃非法流量、增加计数/日志，端口保持Secure-up；合法MAC恢复即可继续业务，不把模拟BLOCKED等同于物理shutdown |
| E5-07 | Shutdown/err-disable | 当前项目未选择 | 课程涉及的另一违规模式，本项目没有该配置/该模式验收；不能以restrict记录声称shutdown测试也完成 |
| E5-08 | Violation Counter | SW-ACCESS show port-security interface fa0/1 | G4非法MAC测试计数由0增长至5；只表明那次测试，当前计数按现场读取，Dashboard模拟计数不对应交换机计数 |
| E5-09 | 未授权终端替换/检测日志 | 临时更改OFFICE终端MAC为0000.1111.2222 | 触发PSECURE_VIOLATION并非法流量丢弃；测试MAC是临时工具，不新增永久攻击节点 |
| E5-10 | 安全恢复与正负向对照 | Fa0/1与OFFICE-PC | 正常终端业务→非法MAC拒绝→恢复原MAC后业务恢复；G4-A-02/02b/02c，不能只展示一次告警 |
| E5-11 | IPv6-over-IPv4 Tunnel/封装 | R-HQ↔R-BRANCH，经过IPv4-only R-ISP | IPv6内层封装为IPv4外层，企业两端终结；tunnel mode ipv6ip。未用GRE、IPsec，也不承载真实FastAPI带外WS |
| E5-12 | Tunnel Interface与端点参数 | 两端Tunnel0，ff::1/ff::2；HQ source G0/1→198.51.100.2；Branch source G0/0→203.0.113.1 | 接口名source适配PT，source/destination对称；ISP没有企业Tunnel0接口，不把ISP画成终结点 |
| E5-13 | IPv4 Underlay与IPv6 Overlay路由配合 | ISP BGP发布两个WAN/30；企业四条IPv6静态路由 | 先IPv4端点可达，再Overlay管理业务及回程；IPv6静态路由也对应实验一，属于同一配置被两个实验知识共同解释 |
| E5-14 | MAC违规/Tunnel状态/IPv6 Ping验证 | Access、R-HQ/Branch、BR-ADMIN | show port-security/address、show interfaces tunnel0/ipv6 route，端点互ping与BR-ADMIN→HQ-SERVICE30::10；接口UP之外还需端到端成功 |

G4图片已直接核对：02/02b为restrict与非法MAC；04/04b为两端up/up和IPv6/IP；04c为四条静态路由。其他恢复/业务图可从远程完整证据目录查看，原像素保持。

## 7. 五次实验如何在一条业务路径上协同

| 项目场景 | 共同使用的实验技术 | 实际含义 |
|---|---|---|
| HQ OFFICE域名访问Internet Web | 实验二VLAN/SVI/DHCP；实验四OSPF默认出口；实验三ACL/PAT/DNS/HTTP | 办公终端获址后经Core与R-HQ出口访问Internet服务，NAT会话与HTTP页面共同验证 |
| Branch访问HQ Web与公网发布共存 | 实验二VLSM/ROAS；实验四eBGP；实验三WAN ACL/HTTP/静态端口映射 | 私网业务与公网发布均保留；PT共存修复的身份映射避免历史HTTP冲突 |
| ADMIN集中管理Branch设备 | 实验二管理VLAN/SVI/ROAS；实验四路由；实验一Telnet/VTY/认证；实验三来源ACL | 管理可达、管理服务、准入是三个层次，不能用ping替代真实登录 |
| BR-ADMIN跨IPv4 ISP进行IPv6管理通信 | 实验一Static IPv6/静态路由；实验四Underlay可达；实验五Tunnel封装 | 企业原生IPv6通过IPv4外层跨站点，管理域端到端互通，ISP无需IPv6升级 |
| OFFICE接入安全与业务隔离 | 实验二VLAN；实验三数据ACL；实验五MAC绑定/违规检测 | 接入授权与三层访问权限分别控制，不将两个机制混成同一种安全规则 |

## 8. G4后 NOC 与课程知识的关系

NOC是上层统一入口，不增加一套“已经自动验证所有课程技术”的结论。

| NOC板块 | 对应知识 | 当前真实作用与边界 |
|---|---|---|
| Network Health / NC | 实验二管理VLAN/SVI；实验一远程管理/认证；实验四基础路由；实验三来源ACL | 真实NC清单名/IP/type/collectionStatus，Managed→ONLINE；没有直接采集OSPF/BGP/Tunnel状态，协议仍NOT COLLECTED |
| Security Center | 实验三ACL；实验五PortSecurity/违规检测 | 模拟事件、次数、红色卡片，不是实际交换机日志/端口动作；真实实验功能由PT配置与G4证据证明 |
| Branch Operations | 实验一Telnet/VTY/认证；实验三管理来源ACL | 模拟ADMIN-PC访问规则解释，不实际Telnet/SSH；真实登录用N14证据 |
| Campus Policy | 实验二业务分区、实验三访问隔离、实验五接入安全；Edge策略扩展 | Network/Security为配置展示，不下发IOS；thermal使用既有Edge策略与ACK，Campus上层版本不破坏底层version |
| Simulation | 实验四/五网络故障概念、实验三/五安全告警、Edge自治创新 | Cloud实际断开Edge WS；Security模拟；Network按钮禁用/409，不能用模拟路由状态证明真实故障 |

新增NC-HQ `.30.30`接VLAN30、VTY允许NC来源、Discovery设备CLI与localhost58000 Northbound API，是在既有课程能力上增加真实可观测。设备Managed是管理采集状态，不等价于ADMIN-PC VTY验收、全部业务ONLINE或协议FULL。

## 9. 超出五次实验的项目扩展与未覆盖项

TEMP→MCU→SBC→FAN本地闭环、迟滞温控、Protocol1.0双向WS、thermal-01严格递增版本/ACK、Cloud断连最后策略保留、hello/state_sync恢复、中文Dashboard，是本项目的Edge/Cloud扩展；它们依托课程网络背景，但不是前五次实验原有技术清单中的同名网络协议。

当前不能写成已覆盖的项目：DHCPv6 DNS/domain参数、自定义Native VLAN、PortSecurity shutdown/err-disable模式、手工静态MAC绑定变体、全协议一对一Static NAT、原生ISP IPv6、HQ IoT IPv6、OSPFv3、GRE/IPsec、真实SSH管理、BGP高级route-map/AS-path策略，以及Dashboard直接采集OSPF/BGP/Tunnel。这些不作为已实现能力宣传，也不因课程目录出现就自动要求新增功能。

最终状态为**验收完成，报告准备中**：当前分支已归档21张G4 A网络原图，NC/API/Dashboard配套截图、最终包内程序和展示彩排记录继续按最新版本整理为报告素材。详情见 [配置总览§12](FINAL_CONFIGURATION.md)与[最终完成报告](final/PROJECT_COMPLETION_REPORT.md)。
