# EdgeCampus 最终功能演示设计

更新日期：2026-09-19。本文规定最终报告和现场答辩的功能演示顺序。完整演示按 **园区管理 → 中心物联网控制 → Dashboard 面板控制** 三部分展开，先证明 Packet Tracer 数据平面的真实业务，再证明物联网本地闭环，最后展示集中可视化与控制。

演示时使用当前唯一正式包 `packet_tracer/EdgeCampus.pkt`。第一、二部分直接操作 Packet Tracer；第三部分再打开宿主机 Dashboard。已有证据和待补截图编号见 [最终素材总清单](FINAL_REPORT_SCREENSHOT_CHECKLIST.md)与[四人逐张截图清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)。

## 1. 演示总线

| 顺序 | 功能名称 | 要回答的问题 | 建议时长 |
|---|---|---|---:|
| 1 | 园区管理 | 总部、分部和 Internet 中的人员、设备和业务能否按规划接入、通信、隔离、发布和运维 | 8–10 分钟 |
| 2 | 中心物联网控制 | 温度是否被真实采集，SBC 是否能按策略驱动物理风扇，云端中断后是否继续自治 | 3–4 分钟 |
| 3 | Dashboard 面板控制 | 管理员能否在一个中文界面观察全局、下发真实 Edge 控制、读取真实 NC，并完成运维演练 | 4–5 分钟 |

完整演示约 15–19 分钟。若答辩限时 10 分钟，保留每个场景中标有“核心”的操作，其余用已有截图快速说明。

---

## 2. 功能一：园区管理

### 2.1 开场画面与讲解

先打开最终 PT 拓扑全景，画面同时包含 HQ、ISP/Internet、Branch、NC 和 IoT 区域。

讲解口径：

> 这是一个总部园区、运营商网络、互联网服务和异地分部组成的智慧校园。普通办公人员、园区管理员、物联网设备和对外服务分别进入不同业务区域。下面不按协议名孤立演示，而是按人员入网、跨园区办公、互联网访问、安全隔离和集中运维这些实际场景逐项测试。

预期画面：所有设备和连线完整，关键链路为绿色；总部三类业务域、ISP、分部两类业务域和 IoT 链路能清楚辨认。

证据：T02/A01；需要局部结构时复用 T01/T03。

### 2.2 场景一：总部员工入网与部门网络划分（核心）

**业务描述**：新入职的总部办公人员接入网络后，应自动获得地址和 Internet DNS；办公、物联网、管理设备属于不同部门网络，总部核心通过双链路上联承载这些业务。

按下面顺序操作：

1. 在 OFFICE-PC 打开 `Desktop → IP Configuration`，选择 DHCP；再选择 IPv6 `Auto Config`。
2. 在 OFFICE-PC 的 Command Prompt 执行：

   ```text
   ipconfig /all
   ```

3. 在 SW-ACCESS 执行：

   ```text
   enable
   show vlan brief
   show interfaces trunk
   show etherchannel summary
   ```

4. 在 SW-CORE 执行：

   ```text
   enable
   show ip interface brief
   show interfaces trunk
   show etherchannel summary
   show ip dhcp binding
   ```

5. 从 ADMIN-PC 验证管理区可访问 IoT 设备：

   ```text
   ping 192.168.20.10
   ```

6. 从 OFFICE-PC 验证办公区不能直接进入 IoT 区：

   ```text
   ping 192.168.20.10
   ```

预期结果：

- OFFICE-PC 获得 `192.168.10.0/24` 地址、网关 `192.168.10.1` 和 DNS `192.0.2.10`，IPv6 地址属于 `2001:db8:10::/64`；
- VLAN10/20/30 分别承载 OFFICE、IOT、MANAGEMENT；
- Po1 显示 `SU`，两个成员端口显示 `P`，Trunk 允许 VLAN10/20/30；
- SW-CORE 的三个 SVI 和 Transit 接口处于 up/up；
- ADMIN-PC 到 `192.168.20.10` 成功，OFFICE-PC 到同一地址被阻断。

这一场景同时证明 IPv4 DHCP、IPv6 SLAAC、VLAN、Access、Trunk、LACP EtherChannel、SVI、三层转发和基于角色的 ACL。

证据：N01、C01–C04、A19、A21，以及已有 G1/G4 网络图。

### 2.3 场景二：分部员工接入与低成本分区

**业务描述**：规模较小的异地分部仍需区分普通办公与管理人员，但使用单臂路由降低设备复杂度；普通办公地址自动分配，管理终端使用固定地址。

操作：

1. 在 BR-OFFICE-PC 的 IPv4 配置中选择 DHCP，IPv6 配置中选择 DHCP。
2. 打开 Command Prompt：

   ```text
   ipconfig /all
   ping 172.16.40.1
   ```

3. 在 BR-ADMIN-PC 查看固定地址并执行：

   ```text
   ipconfig /all
   ping 172.16.40.65
   ping 172.16.40.66
   ```

4. 在 SW-BRANCH 执行：

   ```text
   enable
   show vlan brief
   show interfaces trunk
   show ip interface brief
   ```

5. 在 R-BRANCH 执行：

   ```text
   enable
   show ip interface brief
   show ip dhcp binding
   show running-config
   ```

预期结果：

- BR-OFFICE-PC 获得 `172.16.40.0/26` 中的地址和网关 `172.16.40.1`；
- BR-ADMIN-PC 为 `172.16.40.70/27`，网关 `172.16.40.65`；SW-BRANCH 管理地址为 `172.16.40.66/27`；
- VLAN40 是分部办公区，VLAN50 是分部管理区；交换机到路由器的链路为 802.1Q Trunk；
- R-BRANCH 的 `.40`、`.50` 子接口分别作为两个 VLAN 的网关，接口 up/up；
- 两类人员地址段互不重叠，管理员能到达分部路由器和交换机的管理地址。

在 `show running-config` 输出中定位 `interface GigabitEthernet0/1.40` 和 `.50` 两段，核对各自的 `encapsulation dot1Q` 与地址。

这一场景证明 VLSM、IPv4 DHCP、VLAN、802.1Q、Router-on-a-Stick 和管理 SVI。

证据：N02、C05、A16、A20 和已有 G2/G4 图。

### 2.4 场景三：总部与分部跨园区办公（核心）

**业务描述**：总部内部使用 OSPF 自动交换园区路由，总部、运营商和分部之间使用 eBGP 交换跨域业务前缀。分部员工应能访问总部业务入口，但不能借此进入敏感管理区或 IoT 区。

操作：

1. 在 SW-CORE 和 R-HQ 分别执行：

   ```text
   enable
   show ip ospf neighbor
   show ip route
   ```

2. 在 R-HQ、R-ISP、R-BRANCH 分别执行：

   ```text
   enable
   show ip bgp summary
   show ip bgp
   ```

3. 在 BR-OFFICE-PC 执行三层连通测试：

   ```text
   ping 192.168.30.10
   ```

4. 在 BR-OFFICE-PC 的 Web Browser 打开：

   ```text
   http://203.0.113.1
   ```

5. 在 BR-OFFICE-PC 执行隔离测试：

   ```text
   ping 192.168.30.20
   ping 192.168.20.10
   ```

6. 在 R-HQ 执行：

   ```text
   show access-lists
   ```

预期结果：

- SW-CORE 与 R-HQ 的 OSPF 邻居为 FULL，R-HQ 学到总部三个 `/24` 网段；
- R-HQ AS65001、R-ISP AS65000、R-BRANCH AS65002 的相邻 eBGP 会话已建立；PT 的 `State/PfxRcd` 列显示数字即表示 Established；
- BR-OFFICE 到 `192.168.30.10` 的 ICMP 成功，证明跨园区三层路径；
- 浏览器访问 `203.0.113.1` 打开 HQ-SERVICE 页面，这是当前正式的分部业务 HTTP 入口；
- 对 HQ 管理终端和 IoT 设备的非授权访问失败，ACL 计数或返回路径与设计一致。

这一场景证明 OSPF、eBGP、路由表、跨站点业务访问和纵深访问控制。不要用 `http://192.168.30.10` 作为当前最终 HTTP 验收入口。

证据：N03、N04、N05 和已有 G3/G4 图。

### 2.5 场景四：园区员工访问互联网

**业务描述**：总部办公人员通过校园出口共享公网地址访问互联网服务，并通过校园 DNS 使用域名，不需要为每台终端分配公网地址。

操作：

1. 在 OFFICE-PC 执行：

   ```text
   ping 192.0.2.10
   ping www.edgecampus.net
   ```

2. 在 OFFICE-PC 的 Web Browser 打开：

   ```text
   http://www.edgecampus.net
   ```

3. 保持页面会话，在 R-HQ 执行：

   ```text
   show ip nat translations
   show ip nat statistics
   ```

预期结果：域名解析到 `192.0.2.10`，Internet 页面成功打开；R-HQ 出现 HQ OFFICE 经 `203.0.113.1` 的 PAT 会话。IoT 网络没有通用 Internet PAT。

这一场景证明 DHCP 下发 DNS、DNS 解析、HTTP、PAT/Overload 和受控出口。

证据：N06、C09–C11 和已有 G3/G4 图。

### 2.6 场景五：向外部发布校园业务

**业务描述**：外部访客只能通过总部公网地址的 Web 端口访问校园服务，内部服务器地址不会直接暴露在公网。

操作：

1. 在 INTERNET-SERVER 的 Web Browser 打开：

   ```text
   http://203.0.113.1
   ```

2. 在 R-HQ 执行：

   ```text
   show ip nat translations
   show ip nat statistics
   show access-lists
   ```

预期结果：浏览器显示 HQ-SERVICE 页面；NAT 表显示 `203.0.113.1:80 → 192.168.30.10:80` 的静态 TCP/80 映射及活动会话；WAN 入口只允许规定的业务流量。

这一场景证明静态端口映射、公网服务发布、外部 HTTP 和 WAN ACL。

证据：N04、C09–C11 和 G4 共存修复图。

### 2.7 场景六：IPv6 多方式入网

**业务描述**：不同类型终端采用适合其角色的 IPv6 地址方式：总部普通员工自动配置，分部办公人员由 DHCPv6 统一分配，固定管理节点采用静态地址。

操作：

1. 在 OFFICE-PC、BR-OFFICE-PC、ADMIN-PC、BR-ADMIN-PC、HQ-SERVICE 分别执行：

   ```text
   ipconfig /all
   ```

2. 在 R-BRANCH 执行：

   ```text
   enable
   show ipv6 dhcp binding
   show ipv6 interface brief
   ```

3. 在 SW-CORE 执行：

   ```text
   enable
   show ipv6 interface brief
   ```

预期结果：

- OFFICE-PC 使用 `2001:db8:10::/64` 的 SLAAC 地址；
- BR-OFFICE-PC 使用 `2001:db8:40::/64` 的 DHCPv6 地址，并能在绑定表中对应；
- ADMIN-PC、HQ-SERVICE、BR-ADMIN-PC 分别显示 `30::20`、`30::10`、`50::70` 静态地址及正确网关；
- 相关三层接口 IPv6 地址和状态正确。

这一场景证明 IPv6 前缀规划、RA/SLAAC、有状态 DHCPv6、静态 IPv6 和默认网关配置。

证据：N07、A16、A19、A20 和 G4-A-03 系列。

### 2.8 场景七：跨 IPv4 运营商的 IPv6 运维（核心）

**业务描述**：运营商只提供 IPv4，但总部管理员仍需要使用 IPv6 管理异地分部，因此在两端边界路由器之间建立 IPv6-over-IPv4 管理通道。

操作：

1. 在 R-HQ 和 R-BRANCH 分别执行：

   ```text
   enable
   show interfaces tunnel 0
   show ipv6 route
   ```

2. 在 R-HQ 执行：

   ```text
   ping 2001:db8:ff::2
   ```

3. 在 R-BRANCH 执行：

   ```text
   ping 2001:db8:ff::1
   ```

4. 在 ADMIN-PC 执行：

   ```text
   ping 2001:db8:50::70
   ```

5. 在 BR-ADMIN-PC 执行：

   ```text
   ping 2001:db8:30::20
   ping 2001:db8:30::10
   ```

预期结果：两端 Tunnel0 为 up/up，模式为 `ipv6ip`，端点 `ff::1` 与 `ff::2` 双向可达；路由表包含 HQ30 与 Branch50 的静态 IPv6 路由；总部和分部管理终端双向 IPv6 ping 零丢包。

这一场景证明 IPv4 Underlay、IPv6 Overlay、Tunnel、静态 IPv6 路由和跨站点 IPv6 通信。该 Tunnel 承载 PT 管理业务，不承载 SBC 到宿主机的真实 WebSocket。

证据：N08、C13、A22、A23 和 G4-A-04 系列。

### 2.9 场景八：中央管理员远程维护分部（核心）

**业务描述**：总部管理员可以远程维护分部设备，普通总部员工和分部办公人员不能登录网络设备。

操作：

1. 在 ADMIN-PC 执行：

   ```text
   telnet 172.16.40.65
   telnet 172.16.40.66
   ```

   第一次退出设备会话后再测试第二台，确保分别出现 R-BRANCH 和 SW-BRANCH 的命令行提示符。

2. 在 OFFICE-PC 执行同样两条命令。
3. 在 BR-OFFICE-PC 执行同样两条命令。
4. 在 R-BRANCH 和 SW-BRANCH 执行：

   ```text
   enable
   show access-lists
   show running-config
   ```

   截图时定位到 `line vty`、`login local` 或当前实际认证配置、`transport input telnet` 和 `access-class`。

5. 需要展示网络控制器时，在 ADMIN-PC 浏览器打开 NC 页面，确认 SW-CORE `192.168.30.1` 与 SW-BRANCH `172.16.40.66` 为 Managed。

预期结果：ADMIN-PC 能进入两台分部设备的命令行；OFFICE-PC 和 BR-OFFICE-PC 均无法建立登录会话；VTY 来源 ACL 只允许登记的管理员/NC 管理源；真实 NC 中两台交换机保持 Managed。

这一场景证明 Telnet 远程管理、VTY、用户认证、Standard ACL、管理源限制和集中设备管理。课程环境使用 Telnet，报告改进方向可写生产环境应迁移 SSH。

证据：N09、N10、A07–A15、A24–A28。

### 2.10 场景九：非法终端接入防护（核心）

**业务描述**：员工工位端口只允许登记终端接入。更换为未授权网卡后，交换机应丢弃其流量并记录违规；恢复合法终端后业务恢复。

操作：

1. 正常终端接入时，在 SW-ACCESS 执行：

   ```text
   enable
   show port-security interface fa0/1
   show port-security address
   show mac address-table interface fa0/1
   ```

2. 先将最终包另存为临时演示副本，不覆盖 canonical 包。断开 OFFICE-PC 与 SW-ACCESS Fa0/1 的连线，放置一台临时 PC-PT，将其 FastEthernet0 用 Copper Straight-Through 接到 SW-ACCESS Fa0/1；在临时 PC 配置 `192.168.10.99/24`、网关 `192.168.10.1`，执行 `ping 192.168.10.1`。
3. 再次执行：

   ```text
   show port-security interface fa0/1
   show port-security address
   show mac address-table interface fa0/1
   ```

4. 移除临时 PC，重新把原 OFFICE-PC 接回 SW-ACCESS Fa0/1，再次执行 `ping 192.168.10.1` 并读取状态；结束时关闭临时副本，不保存到正式包。

预期结果：初始状态为 Secure-up，最大 MAC 数为 1，合法地址为 sticky；非法 MAC 流量被阻断，violation 计数增加；由于违规模式为 `restrict`，端口保持工作而不是进入 shutdown；恢复原终端后正常通信。

这一场景证明 Port Security、Sticky MAC、Maximum、Restrict、违规计数和故障恢复。

证据：N11 和 G4-A-02/02b/02c。

### 2.11 园区管理覆盖核对

| 真实场景 | 主要技术 | 对应课程实验 |
|---|---|---|
| 总部员工入网与部门划分 | IPv4 DHCP、IPv6 SLAAC、VLAN、Trunk、LACP、SVI、ACL | 实验一、二、三 |
| 分部员工接入 | VLSM、DHCP/DHCPv6、VLAN、802.1Q、ROAS | 实验一、二 |
| 总部与分部办公 | OSPF、eBGP、路由表、跨站点 ACL | 实验三、四 |
| Internet 与服务发布 | DNS、HTTP、PAT、Static TCP/80、WAN ACL | 实验三 |
| IPv6 运维通道 | Static IPv6、IPv6-over-IPv4、Tunnel | 实验一、五 |
| 中央远程运维 | Telnet、VTY、认证、管理 ACL、NC | 实验一 |
| 非法终端防护 | Port Security、Sticky MAC、Restrict | 实验五 |

至此，前五次实验中实际部署于最终作品的技术已经全部进入真实业务演示；未部署的课程变体仍按 [五次实验技术映射](EXPERIMENT_MAPPING.md)如实标注。

---

## 3. 功能二：中心物联网控制

这一部分继续在 Packet Tracer 中操作，证明 `TEMP01 → IO-MCU-01 → EDGE-SBC-01 → FAN01` 是真实物理闭环。

### 3.1 环境感知与执行链

操作：打开 IoT 区域局部拓扑，同时打开 MCU/SBC 当前运行程序或 Console/Attributes，观察 TEMP01 温度、SBC 输出和 FAN01 状态。

预期结果：TEMP01 提供温度，MCU 采样后传给 SBC，SBC 根据模式和策略输出控制，FAN01 的物理状态与输出一致。截图中应能辨认四个设备、接线和正在运行的程序。

证据：C19/C20、B01–B05。

### 3.2 AUTO 自动温控与迟滞（核心）

使用当前已下发策略；建议演示前设置 `AUTO / 33℃ / hysteresis 1℃`。若现场最终值不同，以界面和 ACK 中的实际值为准。

操作顺序：

1. 将温度调到关闭边界以下，例如 `31.5℃`，等待一个采样周期；
2. 调到迟滞区间，例如 `32.5℃`；
3. 调到开启边界以上，例如 `34.0℃`；
4. 再调回关闭边界以下。

预期结果：低温时 FAN OFF；进入迟滞区间时保持前一状态；高于开启边界时 FAN ON；降到关闭边界以下后 FAN OFF。温度、决策状态和 FAN 物理状态一致，不在阈值附近反复抖动。

证据：F01、F02/F03、B06 及最终同次实测图。

### 3.3 断云本地自治（核心）

操作：

1. 记录断开前的实际 Policy ID、version、threshold、hysteresis 和 mode；
2. 在运行 Backend 的 PowerShell 中按 `Ctrl+C` 真正停止 8000 服务；
3. 保持 MCU/SBC 程序运行，分别把温度调到开启边界以上和关闭边界以下；
4. 直接观察 SBC 日志/状态和 FAN01 物理状态；
5. 用同一启动命令重新启动 Backend，等待 Edge 自动重连和 `state_sync`。

预期结果：云端停止后 SBC 继续使用最后有效策略，高温开启风扇、低温关闭风扇；重启 Backend 后依次出现 reconnect、hello、state_sync，原策略版本和当前温度/FAN 状态恢复，不回退到临时默认值。

证据：F08–F11、B09–B12。离线时 Dashboard 只能显示最后一次观测，物理实时动作必须在 PT 中证明。

---

## 4. 功能三：Dashboard 面板控制

### 4.1 启动真实 PT、NC 与 Backend

PT 中保持 NC Real World Access 端口 58000 和 SBC RealWSClient 运行。在仓库根目录执行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_pt_backend.ps1 -ControllerPort 58000 -BackendPort 8000
```

输入 NC Web/API 账户后打开 `http://127.0.0.1:8000`。预期 Backend 监听 8000、NC 为 CONNECTED、真实 Edge 为 ONLINE。

### 4.2 中文总览与实时监控（核心）

首先展示中文首页，依次指出：Edge Control、网络运行、安全运行、园区策略和故障演练五类能力。切换到 Edge 页面，观察实时温度、FAN、模式、策略版本和事件流；在 PT 中改变温度，确认页面读数随真实设备更新。

预期结果：页面状态与 PT 当前温度和 FAN 一致，Edge 为 ONLINE，Cloud 为 CONNECTED；事件时间顺序连续。

证据：U02/D01、F01、B12。

### 4.3 策略和手动命令闭环（核心）

操作：

1. 下发 AUTO 策略，例如 threshold `33℃`、hysteresis `1℃`；
2. 观察 Policy ID、递增 version 和 `APPLIED` ACK；
3. 调温验证物理 FAN；
4. 下发 MANUAL OFF，再下发 MANUAL ON；
5. 每次观察 Command ID、`APPLIED` ACK 和 PT FAN01；
6. 演示结束恢复 AUTO。

预期结果：页面不只是显示请求成功，而是收到真实 Edge 执行 ACK；同一个 ID/version 能在请求、设备状态和 ACK 中对应；手动命令与物理风扇一致。

证据：F06/F07、B06–B08。

### 4.4 真实 Network Controller 设备健康（核心）

打开“网络健康”页，并与 PT NC 页面或真实 API 对照。

预期结果：

- SW-CORE、SW-BRANCH 的设备名、管理 IP、类型、collection status 来自真实 NC API；
- `Controller status == Managed` 的设备在 Dashboard 映射为 ONLINE；
- Unsupported 设备不被改写成 ONLINE；
- OSPF、BGP、Tunnel 显示 `NOT COLLECTED`，因为 NC 没有提供这些协议状态；
- Dashboard 不使用模拟数据补齐真实 NC 缺失字段。

随后可临时关闭并恢复 NC External Access：失联时清空旧的在线卡片并显示不可用，恢复后重新采集。

证据：U01、U03–U05、C10–C15。

### 4.5 安全中心

点击“非法 MAC 接入”模拟按钮，观察 `PORT_SECURITY_VIOLATION`、Unauthorized MAC detected、Port blocked 和红色事件卡；执行恢复后观察安全状态回到正常并保留审计事件。再触发 `ACL_BLOCK_EVENT`，观察 ACL 阻断事件。

预期结果：攻击时状态、计数、端口和红色事件同步变化；恢复后当前状态恢复，历史事件仍可追溯。

这一页是 NOC 演示适配器。真实交换机 Port Security 和真实 ACL 已在“园区管理”第 2.9、2.10 场景中单独验证。

证据：U06/U07、D06–D08。

### 4.6 分部运维

在“分部运维”页面分别点击“检查路由器”和“检查交换机”，再将来源切换为普通办公网进行拒绝测试。

预期结果：R-BRANCH `172.16.40.65`、SW-BRANCH `172.16.40.66` 对 ADMIN-PC 来源显示 Remote Management PASS、VTY ACL ALLOW；普通来源显示 DENY。

该页面按真实配置规则返回演示结果，不会从浏览器直接发起 Telnet。真实 ADMIN-PC 登录和普通用户拒绝已在“园区管理”第 2.9 场景验证。

证据：U08、D02–D04。

### 4.7 园区策略中心

打开“园区策略”页面，展示：

- Edge Policy：`thermal-01`、实际 version、threshold、mode 和 ACK；
- Network Policy：Branch Access、IoT Isolation；
- Security Policy：Port Security 等级；
- Campus Policy Version：三类策略的统一展示版本。

预期结果：Edge 策略与真实 Policy/ACK 对应；Network/Security 策略清楚标明为上层配置展示，不直接写入 PT IOS；Campus Policy 不破坏原有 `policy_id`、version 和 ACK 机制。

证据：U09、D05。

### 4.8 故障演练中心

**云端故障按钮**：点击后真实关闭当前 Edge WebSocket，页面显示 Cloud OFFLINE、Edge AUTONOMOUS MODE；PT 保持本地控制。点击恢复后状态经过 `WAITING_FOR_STATE_SYNC`，收到真实 `state_sync` 后显示 SUCCESS。

**网络故障按钮**：保持禁用状态。点击或调用接口时显示真实 NC 只读模式不允许伪造 BGP/Tunnel DOWN，API 返回 409。

预期结果：云端演练能影响真实 WS 会话并依赖真实同步恢复；网络演练不会覆盖真实 NC 数据。

证据：U10/U11、D09–D13。完整“真正停 Backend”演示仍以第 3.3 节为准。

---

## 5. 最终收束画面

恢复到以下状态后结束：

- Packet Tracer：合法终端已恢复，关键链路绿色，FAN 处于当前 AUTO 策略应有状态；
- Edge：ONLINE；Cloud：CONNECTED；最后一次 state_sync：SUCCESS；
- Network Controller：CONNECTED；SW-CORE、SW-BRANCH：ONLINE/Managed；
- OSPF/BGP/Tunnel：`NOT COLLECTED`；
- Security：SECURE；Branch 运维状态恢复；Campus Policy 显示三类策略；
- Network Failure 保持禁用。

收束讲解：

> 园区管理部分证明前五次实验形成了可工作的总部、分部和 Internet 业务网络；中心物联网控制证明物理感知、边缘决策和断云自治；Dashboard 把真实 Edge 控制、真实 NC 只读数据以及标明边界的运维演练统一到一个中文 NOC 中。三部分共同构成 Network Infrastructure、Network Operation Center 和 Edge Autonomous Control 的完整链路。

## 6. N1–N15 与三部分对应表

| 验收项 | 演示位置 |
|---|---|
| N1 HQ VLAN/SVI | 2.2 |
| N2 OFFICE→IOT 隔离 | 2.2 |
| N3 EtherChannel | 2.2 |
| N4 Branch VLSM/ROAS | 2.3 |
| N5 OSPF | 2.4 |
| N6 eBGP | 2.4 |
| N7 Branch→HQ Business | 2.4 |
| N8 Branch Isolation | 2.4 |
| N9 PAT | 2.5 |
| N10 DNS/HTTP | 2.5 |
| N11 Static Port Map | 2.6 |
| N12 IPv6 modes | 2.7 |
| N13 IPv6 Tunnel | 2.8 |
| N14 Remote Admin | 2.9 |
| N15 Port Security | 2.10 |
| Edge Local Loop / ACK / outage / recovery | 3.2–3.3、4.3、4.8 |
| 真实 NC 与 NOC 五板块 | 4.2–4.8 |

## 7. 报告写法

最终报告“完整功能演示”一章直接使用本文三段结构。每个场景固定写五项：**业务目标、操作、预期现象、实际现象与截图、技术说明**。协议与命令写在对应业务场景之后，前五次实验逐项映射另放在实验对照章节，避免把同一演示重复写成两遍。
