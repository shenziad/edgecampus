# 最终实验报告素材与截图清单

整理日期：2026-09-19。适用版本：当前 `feat/edge`，项目状态 **验收完成，报告准备中**。本清单针对最终报告的四项要求：**完整功能演示、完整配置信息、前五次实验逐项对照、明确创新点**。已阅读本地代码、配置总览、实验映射、G1–G4报告和现有证据目录，并核对来源提交后将21张G4网络原图纳入当前分支。

本清单共有 **70组截图用途**：**44组已有可复用素材**、**25组报告补图任务**，另有I08直接复用这些补图。引用 **73张不同的已有原图**（均已纳入当前分支；其中21张G4网络图保留来源提交）；同图多处出现是交叉引用，不重复拍摄。另列完整配置非截图附件CFG01–CFG09。

**多人分工**：见 [截图分工与操作手册（四人）](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)，四人各自使用自己的完整项目，可独立同时操作；25组报告补图任务已经拆成70张明确PNG：A30张、B12张、C15张、D13张，每张都有编号、文件名、操作步骤和预期画面。

**直接准备报告图片**：先看 [§10 只补缺图速查](#missing-shots)，需要截图细节再按代号回查前文。配置信息与五次实验对照分别见§6、§7，创新点素材见§8。

## 1. 如何使用这份清单

- `[x]`：已有可直接用于所述内容的图片，后面给出真实文件名/链接；表示素材存在，不表示整个项目最终验收全部通过。
- `[ ]`：该画面没有可用归档图，明确说明需要拍什么。**只优先补这些项，已有图无需为报告重复拍摄。** 同一截图能满足多项时交叉引用。
- **本地已有**：链接指向当前工作树文件。21张G4网络原图已从来源提交 `4e0d31491689f24ce2d5e2a8bd6c7663af1f12d8` 原样纳入 `evidence/network/`。
- 代号 `T/F/N/U/C/I/Q/V` 分别代表拓扑、Edge功能、网络功能、NOC界面、配置、创新、排查、最终复核。新图片使用 **代号-内容.png**；同组多张加 `-01/-02` 或 `-off/-on`。代号不等于张数。
- 新素材统一建议归档 `evidence/final_report/`；目录与缺图文件在真正留证时创建，本次没有制造空白图片。已有图保留原路径和像素，不为凑统一命名搬走历史证据。
- 正文按业务/模块组织。相同原图在“功能、配置、实验映射、创新”中反复引用，不重复插满报告。建议最终选约25–35组正文图，其余关键配置/完整记录置于附录；多图子图仍须保证CLI文字可读。

配置正文直接使用 [FINAL_CONFIGURATION.md](FINAL_CONFIGURATION.md)；五次实验的技术与落点使用 [EXPERIMENT_MAPPING.md](EXPERIMENT_MAPPING.md)，共71项技术与验证内容。前五次实验需要补强的5张图片见 [EXPERIMENT_EVIDENCE_COVERAGE.md](EXPERIMENT_EVIDENCE_COVERAGE.md)，逐张给出操作和预期画面。完整程序/CLI/地址表应作为文字或文件附录，**不要通过截文档页面替代配置内容或技术解释**。

本轮按用户确认：G4/network原则上与当前网络配置一致，作为当前基线，叠加NC增量。G4网络原图已纳入当前分支，可直接用于报告基线；动态租约、计数和策略版本按截图当次结果记录。当前网络和NAT取值以配置总览及本清单为准。历史验收清单的最终包/当前版本回归要求仍保留。

## 2. 总体设计与报告开篇

本节用于报告“实验目标、场景需求、总体架构”。旧图用于解释稳定网络结构；最终全景必须补上 NC。

- [x] **T01｜HQ—ISP—Branch 与 IoT 基础拓扑**

  说明总部、运营商、分部三块区域，以及 TEMP→MCU→SBC→FAN 的设备关系。旧图不含 NC，不称为当前最终全景。

  **本地已有**：[evidence/network/G2-A-01-topology-check-pass.png](../evidence/network/G2-A-01-topology-check-pass.png)。


- [ ] **T02｜当前完整 PT 拓扑（含 NC）**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **A01**｜`T02-final-topology.png`：HQ、ISP、Branch三区域名称，路由器、交换机、PC、Server、NC-HQ、TEMP01、MCU、SBC、FAN及连线可辨；NC-HQ连接SW-CORE。


- [x] **T03｜IoT 物理链路与接口**

  复用 T01 的 IoT 区域。若报告单独排图，截取可辨认设备和连线的区域；A0/USB0/D0 精确接口以配置总览和源码表补充，不仅凭线条颜色推断。

  **本地已有**：[evidence/network/G2-A-01-topology-check-pass.png](../evidence/network/G2-A-01-topology-check-pass.png)。


- [x] **T04｜Packet Tracer 版本**

  报告运行环境可直接使用现有版本图；软件提交、Python 环境、端口 8000/58000 另写文字表，不要求为版本信息重拍。

  **本地已有**：[evidence/network/G1-00b-pt-version.png](../evidence/network/G1-00b-pt-version.png)。


## 3. 完整功能演示：真实 Edge 控制闭环

按“上线→策略→AUTO→MANUAL→断云→恢复”的顺序写。历史图可证明既有功能，不把不同会话的策略版本拼成同一次实验。

- [x] **F01｜真实 Edge 接入与遥测**

  真实 PT Gate2 正常 Dashboard 与 SBC TX telemetry 交叉引用，解释温度、FAN、AUTO、心跳及连接。不是 Fake Edge。

  **本地已有**：[evidence/dashboard/gate2/G2-D-01-dashboard-normal-real-pt-pass.png](../evidence/dashboard/gate2/G2-D-01-dashboard-normal-real-pt-pass.png)。

  **本地已有**：[evidence/backend/G2-C-04-sbc-tx-telemetry-pass.png](../evidence/backend/G2-C-04-sbc-tx-telemetry-pass.png)。


- [x] **F02｜Policy 下发、应用与 Edge 返回 ACK**

  SBC 收到 thermal-01、新 version、AUTO/33℃/迟滞1，出现 CLOUD POLICY APPLIED 与 TX POLICY_ACK APPLIED。该图只证明 Edge 发送 ACK；Dashboard 最终收到 ACK 用 F06。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-01-policy-apply-ack-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-01-policy-apply-ack-pass.png)。

  **本地已有**：[evidence/gate3_bcd/G3-INT-02-policy-e2e-pass.png](../evidence/gate3_bcd/G3-INT-02-policy-e2e-pass.png)。


- [x] **F03｜AUTO 低温关闭与高温开启**

  两张一组：约31.8℃ TURN_OFF/FAN OFF；约34.9℃ TURN_ON/FAN ON，阈值均33℃。报告并列说明真实温度驱动控制。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-02-auto-low-temp-off-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-02-auto-low-temp-off-pass.png)。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-03-auto-high-temp-on-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-03-auto-high-temp-on-pass.png)。


- [x] **F04｜迟滞区间保持 HOLD**

  现有 v1/30℃基线日志含30.2℃ ON、29.4℃ HOLD、28.6℃ OFF。可用于解释算法，图注必须注明历史阈值30℃，不能改写成33℃测试。33℃策略两端用 F03。

  **本地已有**：[edge/packet_tracer/evidence/B1_hysteresis_console.png](../edge/packet_tracer/evidence/B1_hysteresis_console.png)。


- [x] **F05｜MANUAL 远程 FAN OFF/ON 与返回 ACK**

  复用 MANUAL 策略应用、远程 OFF、远程 ON 三图。高温时仍能 OFF，是区分 MANUAL 与 AUTO 的有效观察；含 REMOTE-MANUAL、TX COMMAND_ACK。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-04-manual-policy-apply-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-04-manual-policy-apply-pass.png)。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-05-manual-command-off-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-05-manual-command-off-pass.png)。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-06-manual-command-on-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-06-manual-command-on-pass.png)。


- [ ] **F06｜当前 Dashboard 的 Policy ACK APPLIED**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **B06**｜`F06-policy-ack.png`：表单为AUTO/33/1；策略确认ACK显示实际版本vN和APPLIED；事件流出现策略下发和确认。


- [ ] **F07｜当前 Dashboard 的 Command ACK 与物理 FAN**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **B07**｜`F07-command-ack-off.png`：控制模式MANUAL，FAN OFF；命令确认ACK为APPLIED；FAN01物理state=0。
  - **B08**｜`F07-command-ack-on.png`：FAN ON；命令确认ACK为APPLIED；FAN01物理state=2。


- [x] **F08｜真实停 Backend 后保留最后策略、离线 FAN ON**

  三图一组：断云前 v2/33℃策略→Backend 停止后 SBC CLOUD DISCONNECTED、保留策略→真实升温33.3℃触发 TURN_ON。Dashboard disconnected 用第三张说明观察通道断开。

  **本地已有**：[evidence/edge/gate4/G4-B-01-last-policy-before-outage-pass.png](../evidence/edge/gate4/G4-B-01-last-policy-before-outage-pass.png)。

  **本地已有**：[evidence/edge/gate4/G4-B-02-backend-down-local-auto-on-pass.png](../evidence/edge/gate4/G4-B-02-backend-down-local-auto-on-pass.png)。

  **本地已有**：[evidence/dashboard/gate4/G4-D-01-control-plane-disconnected-pass.png](../evidence/dashboard/gate4/G4-D-01-control-plane-disconnected-pass.png)。


- [ ] **F09｜真正离线降温 FAN OFF 及物理输出**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **B09**｜`F09-offline-fan-on-attributes.png`：8000监听数量0；SBC CLOUD OFFLINE，仍保留断云前Policy版本/33/1；本地TURN_ON/FAN ON，FAN物理state=2。
  - **B10**｜`F09-offline-fan-off.png`：8000监听数量0；CLOUD OFFLINE，Policy版本/33/1与上一张相同；本地TURN_OFF/FAN OFF，FAN物理state=0。


- [x] **F10｜Backend 恢复、自动重连与真实 state_sync**

  复用 SBC CLOUD RECONNECTED→hello→state_sync 与 Backend 同步事件、恢复状态。观察最后策略仍为 v2/33/1，不把 hello 单独当作同步成功。

  **本地已有**：[evidence/edge/gate4/G4-B-03-auto-reconnect-state-sync-pass.png](../evidence/edge/gate4/G4-B-03-auto-reconnect-state-sync-pass.png)。

  **本地已有**：[evidence/backend/gate4/G4-C-02-state-sync-event-pass.png](../evidence/backend/gate4/G4-C-02-state-sync-event-pass.png)。

  **本地已有**：[evidence/backend/gate4/G4-C-05-reconnect-state-sync-restored-pass.png](../evidence/backend/gate4/G4-C-05-reconnect-state-sync-restored-pass.png)。


- [ ] **F11｜恢复后的最终中文 Dashboard**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **B11**｜`F11-dashboard-recovered.png`：当前策略仍为断云前版本、AUTO/33/1；事件流出现STATE_SYNC。
  - **B12**｜`F11-edge-recovered.png`：Dashboard Edge ONLINE、Cloud CONNECTED，温度/FAN与SBC一致；Console出现CLOUD RECONNECTED和TX STATE_SYNC。


- [x] **F12｜协议错误安全拒绝与服务继续运行（扩展/附录可选）**

  错误消息拒绝、错误摘要和恢复状态两图，作为鲁棒性或附录素材；不作为主功能演示的必选大图。

  **本地已有**：[evidence/backend/gate4/G4-C-03-invalid-message-reject-pass.png](../evidence/backend/gate4/G4-C-03-invalid-message-reject-pass.png)。

  **本地已有**：[evidence/backend/gate4/G4-C-04-invalid-summary-restored-state-pass.png](../evidence/backend/gate4/G4-C-04-invalid-summary-restored-state-pass.png)。


## 4. 完整功能演示：真实园区与跨站点网络

本节主要复用网络图。按用户确认 G4/network 为当前网络基线；后续 NC 管理变更以 C15–C17 补充。协议状态用 IOS，不能用 NC 的 Managed 推断。

- [x] **N01｜HQ 获址、跨 VLAN 允许与 OFFICE→IOT 拒绝**

  HQ DHCP、允许域互通、OFFICE→IOT拒绝、ADMIN→IOT允许，用既有正负向图。G4行为图中部分首次 ping 有丢包，如实写实际结果。

  **本地已有**：[evidence/network/G1-07-dhcp-pass.png](../evidence/network/G1-07-dhcp-pass.png)。

  **本地已有**：[evidence/network/G1-09-n1-crossvlan-ping-pass.png](../evidence/network/G1-09-n1-crossvlan-ping-pass.png)。

  **本地已有**：[evidence/network/G1-10-n2-office-to-iot-deny.png](../evidence/network/G1-10-n2-office-to-iot-deny.png)。

  **本地已有**：[evidence/network/G1-11-n3-mgmt-access-pass.png](../evidence/network/G1-11-n3-mgmt-access-pass.png)。

  **本地已有**：[evidence/network/G4-A-05d-full-regression-behaviors-pass.png](../evidence/network/G4-A-05d-full-regression-behaviors-pass.png)。


- [x] **N02｜Branch VLSM、DHCP、ROAS 与网关可达**

  BR-OFFICE DHCP得到172.16.40.2/26、网关.1；管理域/27见 C05。租约是图中当次结果，不把 DHCP 地址当静态配置。

  **本地已有**：[evidence/network/G2-A-04-branch-dhcp-ping-pass.png](../evidence/network/G2-A-04-branch-dhcp-ping-pass.png)。

  **本地已有**：[evidence/network/G2-A-03-branch-roas-pass.png](../evidence/network/G2-A-03-branch-roas-pass.png)。


- [x] **N03｜HQ OSPF 与 HQ—ISP—Branch eBGP**

  G4 routing 综合图优先；细节不清时增用 G3 OSPF/BGP表图。OSPF FULL；BGP Established按摘要实际输出判定。两条 eBGP 会话、四条邻居条目，不写“三条会话”。

  **本地已有**：[evidence/network/G4-A-05c-full-regression-routing-pass.png](../evidence/network/G4-A-05c-full-regression-routing-pass.png)。

  **本地已有**：[evidence/network/G3-A-01b-ospf-rhq-neighbor-routes-pass.png](../evidence/network/G3-A-01b-ospf-rhq-neighbor-routes-pass.png)。

  **本地已有**：[evidence/network/G3-A-02-bgp-neighbors-pass.png](../evidence/network/G3-A-02-bgp-neighbors-pass.png)。

  **本地已有**：[evidence/network/G3-A-02b-bgp-routes-ospf-default-pass.png](../evidence/network/G3-A-02b-bgp-routes-ospf-default-pass.png)。


- [x] **N04｜Branch 私网 HTTP 与公网 TCP80 发布同时成立**

  首选最终共存图：浏览器 http://192.168.30.10 和 http://203.0.113.1 同时可用，NAT表端口正常。说明 identity 映射在前、公网映射在后；旧冲突失败图只在 Q01 过程分析使用。

  **本地已有**：[evidence/network/G4-A-07b-n7-n11-coexist-confirm-pass.png](../evidence/network/G4-A-07b-n7-n11-coexist-confirm-pass.png)。


- [x] **N05｜Branch 办公域对 IoT/管理域访问限制**

  G4行为图直接证明 Branch→IoT失败；需要管理域负向时引用 G3 BR-OFFICE ping图，注明目标与结果。无法连通还需路由/ACL配置交叉解释，不能只凭丢包断言命中了哪条 ACL。

  **本地已有**：[evidence/network/G4-A-05d-full-regression-behaviors-pass.png](../evidence/network/G4-A-05d-full-regression-behaviors-pass.png)。

  **本地已有**：[evidence/network/G3-A-03b-br-office-ping-pass.png](../evidence/network/G3-A-03b-br-office-ping-pass.png)。


- [x] **N06｜HQ OFFICE PAT、DNS 与 HTTP**

  OFFICE浏览器地址栏 www.edgecampus.net +成功页面；PAT转换/统计与Internet可达图补充。域名页验证组合业务，不是 DNS 服务配置截图。

  **本地已有**：[evidence/network/G3-A-04c-office-dns-http-pass.png](../evidence/network/G3-A-04c-office-dns-http-pass.png)。

  **本地已有**：[evidence/network/G3-A-04b-office-internet-pat-pass.png](../evidence/network/G3-A-04b-office-internet-pat-pass.png)。

  **本地已有**：[evidence/network/G3-A-04d2-nat-translations-session-pass.png](../evidence/network/G3-A-04d2-nat-translations-session-pass.png)。


- [x] **N07｜IPv6三种地址模式**

  一组复用 HQ Static、HQ SLAAC、Branch DHCPv6图。03c右侧Branch当时也显示SLAAC，不将其作为最终Branch DHCPv6证明；03d服务端绑定与客户端完全一致才是DHCPv6决定性证据。

  **本地已有**：[evidence/network/G4-A-03b-ipv6-hq-admin-static-pass.png](../evidence/network/G4-A-03b-ipv6-hq-admin-static-pass.png)。

  **本地已有**：[evidence/network/G4-A-03c-ipv6-slaac-client-pass.png](../evidence/network/G4-A-03c-ipv6-slaac-client-pass.png)。

  **本地已有**：[evidence/network/G4-A-03d-ipv6-dhcpv6-pass.png](../evidence/network/G4-A-03d-ipv6-dhcpv6-pass.png)。


- [x] **N08｜IPv4-only ISP 上 IPv6 Tunnel 双向与跨站点业务**

  两端 Tunnel up/up、IPv6/IP、端点互 ping，另用 BR-ADMIN→HQ-SERVICE 2001:db8:30::10 4/4成功图。接口UP、端点ping和端到端业务三层证据分别说明。

  **本地已有**：[evidence/network/G4-A-04-ipv6-tunnel-rhq-pass.png](../evidence/network/G4-A-04-ipv6-tunnel-rhq-pass.png)。

  **本地已有**：[evidence/network/G4-A-04b-ipv6-tunnel-rbranch-pass.png](../evidence/network/G4-A-04b-ipv6-tunnel-rbranch-pass.png)。

  **本地已有**：[evidence/network/G4-A-04d-br-admin-to-hq-service-ipv6-pass.png](../evidence/network/G4-A-04d-br-admin-to-hq-service-ipv6-pass.png)。


- [x] **N09｜ADMIN-PC 真实 Telnet 登录两台 Branch 设备**

  同一现有图可见 telnet .40.65→R-BRANCH> 与 .40.66→SW-BRANCH>，可直接放报告。此图是G4线路密码阶段；当前login local/NC准入配置用 C17，不声称旧画面已验证新增认证。

  **本地已有**：[evidence/network/G4-A-01b-remote-admin-telnet-pass.png](../evidence/network/G4-A-01b-remote-admin-telnet-pass.png)。


- [x] **N10｜普通 OFFICE 真实管理请求被拒**

  现图有 OFFICE对.40.65 Connection refused，与N09构成允许/拒绝对照。该图没有覆盖BR-OFFICE或所有目标；最终NC ACL回归见 V01。

  **本地已有**：[evidence/network/G4-A-01c-remote-admin-office-deny.png](../evidence/network/G4-A-01c-remote-admin-office-deny.png)。


- [x] **N11｜真实 Port Security 正常→非法MAC→恢复**

  三图复用：max1/sticky/restrict正常；非法MAC0000.1111.2222触发日志、计数5；恢复合法MAC后ping4/4。restrict丢弃非法流量，端口仍Secure-up，不写成物理shutdown。

  **本地已有**：[evidence/network/G4-A-02-port-security-config-pass.png](../evidence/network/G4-A-02-port-security-config-pass.png)。

  **本地已有**：[evidence/network/G4-A-02b-port-security-violation-pass.png](../evidence/network/G4-A-02b-port-security-violation-pass.png)。

  **本地已有**：[evidence/network/G4-A-02c-port-security-restore-pass.png](../evidence/network/G4-A-02c-port-security-restore-pass.png)。


## 5. 完整功能演示：最终中文 NOC 与真实 NC

这一节是最终版本主要缺图处。一次正常会话可以连续拍多张；截图上保留真实数据/模拟数据/配置展示等来源说明。

- [x] **U01｜NC 真实设备清单（已有）**

  原图含SW-CORE 192.168.30.1 MultiLayerSwitch、SW-BRANCH 172.16.40.66 Switch，均Managed；另三项Unsupported。该图证明NC有两台Managed，不证明Dashboard接通或协议状态。

  **本地已有**：[evidence/noc/NOC-NC-01-controller-managed-inventory.png](../evidence/noc/NOC-NC-01-controller-managed-inventory.png)。


- [ ] **U02｜最终中文 Dashboard 五位一体全景**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **D01**｜`U02-noc-overview-01.png`：导航和面板标题为中文；Edge ONLINE、Cloud CONNECTED，温度和FAN状态有实时读数。


- [ ] **U03｜真实 Network Health、NC清单与API对应**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **C10**｜`U03-nc-dashboard-api.png`：SW-CORE 192.168.30.1、SW-BRANCH 172.16.40.66显示ONLINE/Managed；OSPF、BGP、Tunnel0均为NOT COLLECTED。
  - **C11**｜`U03-controller-table.png`：CONNECTED和采集时间可见；两个Managed设备名/IP/type可读，其余设备的Unsupported状态可见。
  - **C12**｜`U03-controller-api.png`：SW-CORE、SW-BRANCH的设备名、IP、类型、collectionStatus=Managed可读。


- [ ] **U04｜NC断连失败→恢复**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **C14**｜`U04-nc-unavailable.png`：控制器UNAVAILABLE；提示无法连接控制器；设备表和原ONLINE设备卡片清空；协议状态仍为NOT COLLECTED。
  - **C15**｜`U04-nc-recovered.png`：控制器回到CONNECTED；设备表重新出现，SW-CORE/SW-BRANCH回到ONLINE/Managed。


- [ ] **U05｜真实NC物理拓扑读取或实际降级结果**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **C13**｜`U05-controller-topology-response.png`：控制器CONNECTED；终端显示topology和topology_error的实际返回值；页面显示对应的拓扑采集内容。


- [ ] **U06｜Security模拟攻击、红色事件与恢复**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **D06**｜`U06-security-attack.png`：端口安全VIOLATION、端口BLOCKED；累计违规数增加1；出现PORT_SECURITY_VIOLATION红色事件及“检测到未经授权的MAC·端口已阻断”。
  - **D07**｜`U06-security-restored.png`：端口安全SECURE，端口FORWARDING；事件显示恢复，累计违规数与攻击后的数值相同。


- [ ] **U07｜ACL阻断模拟事件**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **D08**｜`U07-acl-block-event.png`：ACL_BLOCK_EVENT红色卡片，文字为“检测到未授权流量·ACL已阻断”；ACL ACTIVE，端口安全SECURE，端口FORWARDING。


- [ ] **U08｜分部运维Router/Switch检查**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **D02**｜`U08-branch-check-router.png`：R-BRANCH IP为172.16.40.65；结果显示远程管理PASS、VTY ACL ALLOW；模拟数据标签可见。
  - **D03**｜`U08-branch-check-switch.png`：SW-BRANCH IP为172.16.40.66；结果显示远程管理PASS、VTY ACL ALLOW。
  - **D04**｜`U08-branch-check-denied-api.png`：device为R-BRANCH，management为DENIED，acl为DENY，source为SIMULATED。


- [ ] **U09｜Campus三类策略与Edge底层ACK**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **D05**｜`U09-campus-policy.png`：园区策略版本可见；Edge thermal-01/实际vN/33/AUTO，Network Branch Access ALLOW与IoT Isolation启用，Security Port Security STRICT；策略ACK为同一vN/APPLIED。


- [ ] **U10｜Cloud Failure按钮实际中断WS**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **D09**｜`U10-cloud-ws-failure.png`：Cloud OFFLINE，边缘控制为本地自治模式（预期）；状态同步显示等待恢复云端；FAN显示最后观测值。
  - **D10**｜`U10-cloud-ws-local-fan.png`：Console CLOUD OFFLINE、本地TURN_ON/FAN ON及最后策略33/1可见；FAN物理state=2。
  - **D11**｜`U10-cloud-ws-restored.png`：Cloud ONLINE，状态同步为同步成功SUCCESS，实时遥测恢复；SBC出现CLOUD RECONNECTED和TX STATE_SYNC。


- [ ] **U11｜NC-only模式禁用Network Failure**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **D12**｜`U11-network-simulation-disabled.png`：模拟网络故障、恢复网络连接两个按钮灰色禁用；网络健康面板显示“PT 控制器·实际数据”。
  - **D13**｜`U11-network-disabled-api.png`：请求路径/api/simulation/network；Server response为409，detail显示真实NC模式不支持模拟网络状态。


## 6. 完整配置信息：正文应选的关键配置图

现有配置片段适合正文。完整配置放结构化表/CLI附录和最终导出文件，不能把一张show局部图称为“所有设备全部配置”。章节顺序沿用 FINAL_CONFIGURATION：二层→IPv4→路由→安全→服务→IPv6/Tunnel→IoT→NOC。

- [x] **C01｜HQ VLAN与Access端口**

  Core/Access VLAN10/20/30，以及Access Fa0/1–4所属VLAN。正文可合为两幅子图，图注逐设备解释。

  **本地已有**：[evidence/network/G1-02-swcore-vlan-brief-pass.png](../evidence/network/G1-02-swcore-vlan-brief-pass.png)。

  **本地已有**：[evidence/network/G1-01-swaccess-vlan-brief-pass.png](../evidence/network/G1-01-swaccess-vlan-brief-pass.png)。

  **本地已有**：[evidence/network/G1-03-swaccess-access-ports-pass.png](../evidence/network/G1-03-swaccess-access-ports-pass.png)。


- [x] **C02｜HQ Trunk/LACP/Port-channel**

  Core与Access Po1(SU)、LACP、两成员bundled、802.1Q、allowed10/20/30、Native VLAN1。可直接用两图，说明聚合已成立，不凭它声称已经测得双倍吞吐或故障切换。

  **本地已有**：[evidence/network/G1-04-swcore-trunk-etherchannel-pass.png](../evidence/network/G1-04-swcore-trunk-etherchannel-pass.png)。

  **本地已有**：[evidence/network/G1-05-swaccess-trunk-etherchannel-pass.png](../evidence/network/G1-05-swaccess-trunk-etherchannel-pass.png)。

  **本地已有**：[evidence/network/G4-A-05-full-regression-swcore-pass.png](../evidence/network/G4-A-05-full-regression-swcore-pass.png)。


- [x] **C03｜Core SVI、ip routing、DHCP**

  Core三个SVI .1、Transit接口、DHCP配置与绑定；pool/排除段/网关/DNS完整命令见配置总览，最终逐设备导出见§9。

  **本地已有**：[evidence/network/G1-06-swcore-svi-routing-pass.png](../evidence/network/G1-06-swcore-svi-routing-pass.png)。

  **本地已有**：[evidence/network/G1-07-dhcp-pass.png](../evidence/network/G1-07-dhcp-pass.png)。

  **本地已有**：[evidence/network/G4-A-05b-full-regression-swcore-l3-pass.png](../evidence/network/G4-A-05b-full-regression-swcore-l3-pass.png)。


- [x] **C04｜HQ数据ACL与接口绑定**

  OFFICE-IN/IOT-IN条目和SVI inbound绑定，配N01正负向业务图解释规则顺序。

  **本地已有**：[evidence/network/G1-08-swcore-acl-config.png](../evidence/network/G1-08-swcore-acl-config.png)。

  **本地已有**：[evidence/network/G2-A-07b-hq-regression-swcore-acl-pass.png](../evidence/network/G2-A-07b-hq-regression-swcore-acl-pass.png)。


- [x] **C05｜Branch VLAN/Trunk/管理SVI/ROAS/DHCP**

  Branch VLAN40/50、Gi0/1允许40,50/Native1，SW管理.66/27；R-BRANCH G0/1.40/.50 encapsulation、.1/26/.65/27及DHCP。解释HQ SVI与Branch单臂路由差异。

  **本地已有**：[evidence/network/G2-A-02-branch-vlan-trunk-pass.png](../evidence/network/G2-A-02-branch-vlan-trunk-pass.png)。

  **本地已有**：[evidence/network/G2-A-03-branch-roas-pass.png](../evidence/network/G2-A-03-branch-roas-pass.png)。

  **本地已有**：[evidence/network/G2-A-04-branch-dhcp-ping-pass.png](../evidence/network/G2-A-04-branch-dhcp-ping-pass.png)。


- [x] **C06｜IPv4 Transit与WAN各接口**

  Core—HQ10.255.0/30、HQ—ISP203.0.113/30、ISP—Branch198.51.100/30、Internet192.0.2/24。四台核心/路由设备各有图，可将正文地址表与一张代表图结合，其余放附录。

  **本地已有**：[evidence/network/G2-A-05-wan-swcore-underlay-pass.png](../evidence/network/G2-A-05-wan-swcore-underlay-pass.png)。

  **本地已有**：[evidence/network/G2-A-05b-wan-rhq-underlay-pass.png](../evidence/network/G2-A-05b-wan-rhq-underlay-pass.png)。

  **本地已有**：[evidence/network/G2-A-05c-wan-risp-underlay-pass.png](../evidence/network/G2-A-05c-wan-risp-underlay-pass.png)。

  **本地已有**：[evidence/network/G2-A-05d-wan-rbranch-underlay-pass.png](../evidence/network/G2-A-05d-wan-rbranch-underlay-pass.png)。


- [x] **C07｜OSPF/BGP学习表与默认出口**

  现有邻居/路由表用于解释动态协议结果；router ospf/network/router-id、router bgp/AS/neighbor/network及default-information originate的完整配置文字直接用FINAL_CONFIGURATION和最终导出。没有redistribute，不写路由重分发。

  **本地已有**：[evidence/network/G3-A-01-ospf-swcore-neighbor-regression-pass.png](../evidence/network/G3-A-01-ospf-swcore-neighbor-regression-pass.png)。

  **本地已有**：[evidence/network/G3-A-01b-ospf-rhq-neighbor-routes-pass.png](../evidence/network/G3-A-01b-ospf-rhq-neighbor-routes-pass.png)。

  **本地已有**：[evidence/network/G3-A-02b-bgp-routes-ospf-default-pass.png](../evidence/network/G3-A-02b-bgp-routes-ospf-default-pass.png)。

  **本地已有**：[evidence/network/G4-A-05c-full-regression-routing-pass.png](../evidence/network/G4-A-05c-full-regression-routing-pass.png)。


- [x] **C08｜WAN-IN ACL**

  现有R-HQ ACL条目与接口应用图，用于服务host例外、IoT/管理域拒绝、端口/协议方向说明；配N04/N05。

  **本地已有**：[evidence/network/G3-A-03-wan-in-acl-pass.png](../evidence/network/G3-A-03-wan-in-acl-pass.png)。


- [x] **C09｜PAT Inside/Outside与最终两条静态TCP映射**

  PAT配置用旧基线图；最终静态映射与条目顺序以G4共存图为准。192.168.30.10:80→自身的identity条目先，203.0.113.1:80公网条目后；不能仅用旧单条映射图代替最终共存配置。

  **本地已有**：[evidence/network/G3-A-04-pat-config-pass.png](../evidence/network/G3-A-04-pat-config-pass.png)。

  **本地已有**：[evidence/network/G4-A-07b-n7-n11-coexist-confirm-pass.png](../evidence/network/G4-A-07b-n7-n11-coexist-confirm-pass.png)。


- [ ] **C10｜DNS Server实际服务设置**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **A02**｜`C10-dns-config.png`：DNS为On；www.edgecampus.net对应192.0.2.10，status.edgecampus.net对应203.0.113.1。


- [ ] **C11｜两台PT服务器HTTP服务与地址**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **A03**｜`C11-http-config-hq.png`：HTTP为On，页面文件列表可读。
  - **A04**｜`C11-http-config-internet.png`：HTTP为On，页面文件列表可读。
  - **A05**｜`C11-server-address-hq.png`：IPv4 192.168.30.10，掩码255.255.255.0，网关192.168.30.1；IPv6 2001:db8:30::10/64，网关2001:db8:30::1。
  - **A06**｜`C11-server-address-internet.png`：IPv4 192.0.2.10，掩码255.255.255.0，网关192.0.2.1。


- [x] **C12｜IPv6接口、DHCPv6池与四条静态路由**

  现图显示Core/R-HQ/Branch地址、BR-V6与M标志/绑定、三台IPv6路由表。配文字列出四条路由，不使用旧错误tunnel 0形式；IoT VLAN20 IPv6未启用。

  **本地已有**：[evidence/network/G4-A-03-ipv6-addressing-pass.png](../evidence/network/G4-A-03-ipv6-addressing-pass.png)。

  **本地已有**：[evidence/network/G4-A-03d-ipv6-dhcpv6-pass.png](../evidence/network/G4-A-03d-ipv6-dhcpv6-pass.png)。

  **本地已有**：[evidence/network/G4-A-04c-ipv6-route-tables-pass.png](../evidence/network/G4-A-04c-ipv6-route-tables-pass.png)。


- [x] **C13｜Tunnel两端参数**

  source HQ G0/1、destination198.51.100.2；source Branch G0/0、destination203.0.113.1；ff::1/ff::2、mode ipv6ip。现有状态图与完整CLI文字配合，不把ISP当Tunnel终结点。

  **本地已有**：[evidence/network/G4-A-04-ipv6-tunnel-rhq-pass.png](../evidence/network/G4-A-04-ipv6-tunnel-rhq-pass.png)。

  **本地已有**：[evidence/network/G4-A-04b-ipv6-tunnel-rbranch-pass.png](../evidence/network/G4-A-04b-ipv6-tunnel-rbranch-pass.png)。


- [x] **C14｜VTY与Port Security G4基线配置**

  两Branch设备MGMT-ALLOW/access-class绑定、ADMIN来源；Access Fa0/1 sticky/max1/restrict。VTY基线图为后续NC变更前状态，当前认证以C17为准。

  **本地已有**：[evidence/network/G4-A-01-remote-admin-vty-acl-pass.png](../evidence/network/G4-A-01-remote-admin-vty-acl-pass.png)。

  **本地已有**：[evidence/network/G4-A-02-port-security-config-pass.png](../evidence/network/G4-A-02-port-security-config-pass.png)。


- [ ] **C15｜NC-HQ接入端口与自身地址**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **C01**｜`C15-nc-access-address-core.png`：Gi1/0/10为access，Access VLAN为30。
  - **C02**｜`C15-core-interface-config.png`：接口配置含switchport mode access和switchport access vlan 30。
  - **C03**｜`C15-nc-access-address-nc.png`：IP为192.168.30.30，掩码255.255.255.0。
  - **C04**｜`C15-nc-gateway.png`：默认网关192.168.30.1。


- [ ] **C16｜NC API External Access与Discovery**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **C05**｜`C16-nc-external-preferences.png`：该选项已勾选，选项名称和Preferences窗口标题可读。
  - **C06**｜`C16-nc-external-discovery-access.png`：Access Enabled已开启，HTTP Port为58000，Server Status显示监听。
  - **C07**｜`C16-nc-external-discovery-results.png`：浏览器地址栏192.168.30.30、发现目标、采用的协议和任务结果可读。


- [ ] **C17｜NC后的管理认证、ACL绑定与R-HQ Loopback**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **A07**｜`C17-management-final-swcore-acl.png`：管理ACL名称、permit/deny顺序和来源地址清晰可读；管理员地址192.168.30.20的允许条目可见。SW-CORE/SW-BRANCH的NC允许来源192.168.30.30可见。
  - **A08**｜`C17-management-final-swcore-vty.png`：line vty范围、认证方式、transport input telnet及access-class绑定的ACL名称可读。
  - **A09**｜`C17-management-final-rhq-acl.png`：管理ACL名称、permit/deny顺序和来源地址清晰可读；管理员地址192.168.30.20的允许条目可见。
  - **A10**｜`C17-management-final-rhq-vty.png`：line vty范围、认证方式、transport input telnet及access-class绑定的ACL名称可读。
  - **A11**｜`C17-management-final-rbranch-acl.png`：管理ACL名称、permit/deny顺序和来源地址清晰可读；管理员地址192.168.30.20的允许条目可见。
  - **A12**｜`C17-management-final-rbranch-vty.png`：line vty范围、认证方式、transport input telnet及access-class绑定的ACL名称可读。
  - **A13**｜`C17-management-final-swbranch-acl.png`：管理ACL名称、permit/deny顺序和来源地址清晰可读；管理员地址192.168.30.20的允许条目可见。SW-CORE/SW-BRANCH的NC允许来源192.168.30.30可见。
  - **A14**｜`C17-management-final-swbranch-vty.png`：line vty范围、认证方式、transport input telnet及access-class绑定的ACL名称可读。
  - **A15**｜`C17-management-final-rhq-loopback.png`：Loopback0地址10.255.255.1，Status和Protocol均为up。


- [ ] **C18｜实际终端地址、SBC地址与课程功能补强**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **A16**｜`C18-host-addresses-branch-admin.png`：IPv4 172.16.40.70，掩码255.255.255.224，网关172.16.40.65；IPv6 2001:db8:50::70/64，网关2001:db8:50::1。
  - **A17**｜`C18-host-addresses-sbc-ip.png`：IPv4 192.168.20.10，掩码255.255.255.0。
  - **A18**｜`C18-host-addresses-sbc-gateway.png`：IPv4默认网关192.168.20.1。
  - **A19**｜`C18-office-dhcp-dns-slaac.png`：IPv4选择DHCP，实际地址属于192.168.10.0/24，网关192.168.10.1，DNS 192.0.2.10；IPv6选择Auto Config，地址属于2001:db8:10::/64。
  - **A20**｜`C18-branch-dhcpv6-client.png`：IPv6选择DHCP，已获取2001:db8:40::/64内地址，IPv6地址和Link-local地址可读。
  - **A21**｜`C18-same-vlan-ping.png`：来源ADMIN-PC为192.168.30.20，目标HQ-SERVICE为192.168.30.10；最后一次ping四次回复、丢包0%。
  - **A22**｜`C18-ipv6-pc-to-pc-hq.png`：目标2001:db8:50::70，四次IPv6回复、丢包0%；ADMIN-PC标题可见。
  - **A23**｜`C18-ipv6-pc-to-pc-branch.png`：目标2001:db8:30::20，四次IPv6回复、丢包0%；BR-ADMIN-PC标题可见。


- [x] **C19｜物理FAN协议值映射**

  OFF state=0与ON state=2现图均存在；与OFF/ON字符串对照。ON图为Gate2 v1/30℃、OFF图为Gate3 v10/33℃，只能说明物理映射，不混作同一次Policy实验。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-07-gate2-regression-auto-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-07-gate2-regression-auto-pass.png)。

  **本地已有**：[edge/packet_tracer/evidence/gate2/B-G2-06-real-fan-on-status.png](../edge/packet_tracer/evidence/gate2/B-G2-06-real-fan-on-status.png)。


- [ ] **C20｜当前包内MCU/SBC真实运行程序与关键参数**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **B01**｜`C20-pt-program-config-mcu.png`：设备名、项目名、A0采样、USB(0,9600)、温度转换和1000ms采样间隔可读。
  - **B02**｜`C20-pt-program-config-sbc-params.png`：EDGE/TEMP/FAN/POLICY标识、ws://127.0.0.1:8000/ws/edge、Protocol1.0，以及遥测1000ms/心跳5000ms/重连2000ms参数可读。
  - **B03**｜`C20-pt-program-config-sbc-loop.png`：USB读取、本地AUTO控制、物理FAN输出以及主循环执行顺序可读。
  - **B04**｜`C20-pt-program-config-sbc-sync.png`：重连后发送hello和state_sync的代码、运行策略及风扇状态的同步字段可读。
  - **B05**｜`C20-pt-program-running.png`：CLOUD CONNECTED，实际TEMP、FAN、本地控制来源和持续更新的运行日志可见。


- [ ] **C21｜Backend启动端口与两个真实通道**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **C08**｜`C21-backend-started.png`：Uvicorn running on http://127.0.0.1:8000；Edge WebSocket已接入。
  - **C09**｜`C21-runtime-status.png`：端口表有8000、58000监听；控制器source为PT_CONTROLLER、status为CONNECTED。


## 7. 前五次实验详细对照：71项技术怎样选图

**这部分不要求再拍71张图。** 下表逐项列出技术、当前落点、上面已选素材代号；同一配置/测试图支撑多个知识点。完整解释沿用EXPERIMENT_MAPPING：每项写“课程原理→本项目设备/接口→配置方法→解决的问题→截图观察/限制”。仅放五张实验名称图或只列协议缩写不能满足详细对照要求。

标注未启用的变体必须如实说明，不列为缺图任务，也不为了报告临时改变网络。NOC模拟页面可以作知识解释的补充图，真实课程技术用IOS/PT图证明。

### 7.1 实验1：IPv6与远程管理

| 技术编号 | 课程技术 | 当前项目落点 | 报告素材代号 / 说明 |
|---|---|---|---|
| E1-01 | IPv6地址/前缀规划 | HQ VLAN10 `10::/64`、MGMT `30::/64`、Transit `100::/64`；Branch40/50；Tunnel `ff::/64`，均属于2001:db8 | C12、N07、C18；地址规划表 |
| E1-02 | Global Unicast Address形式 | Core SVI、R-HQ/Branch接口与管理PC/Server | C12、N07；注明2001:db8实验地址 |
| E1-03 | Link-local Address | 启用IPv6的接口、OFFICE/BR-OFFICE客户端 | N07（03c/03d） |
| E1-04 | 路由器/三层接口IPv6地址 | Core VLAN10/30与Gi1/0/24；R-HQ G0/0；Branch G0/1.40/.50 | C12 |
| E1-05 | PC/Server固定IPv6地址 | ADMIN-PC30::20、HQ-SERVICE30::10、BR-ADMIN50::70 | N07、C18、C11 |
| E1-06 | SLAAC | HQ OFFICE-PC，SW-CORE VLAN10 | N07（03c的HQ侧）；C18补Auto Config选项GUI |
| E1-07 | Router Advertisement（RA） | Core VLAN10与Branch G0/1.40 | C12、N07（03d的M标志/Link-local网关） |
| E1-08 | 有状态DHCPv6地址分配 | Branch VLAN40，BR-OFFICE-PC | N07（03d） |
| E1-09 | DHCPv6 Server | R-BRANCH | C12（BR-V6） |
| E1-10 | DHCPv6 Client | BR-OFFICE-PC | N07（03d） |
| E1-11 | DHCPv6 DNS等参数下发 | 当前BR-V6未登记此配置 | 未登记DNS/domain选项；如实文字说明，不要求截图或新增功能 |
| E1-12 | IPv6 Static Route | Core/R-HQ/R-BRANCH四条管理域路由 | C12（04c四条路由） |
| E1-13 | Telnet Remote Management | ADMIN-PC `.30.20`→R-BRANCH `.40.65`/SW-BRANCH `.40.66`；NC增量Discovery使用Telnet | N09/N10；当前增量V01 |
| E1-14 | VTY管理入口 | R-BRANCH/SW-BRANCH；NC报告涉及实际被管理设备 | C14；当前增量C17 |
| E1-15 | 远程用户认证 | G4基线line password/login；后续NC报告username admin/login local | N09/C14为线路密码历史，C17为当前login local |
| E1-16 | IPv6连通、地址获取与登录验证 | ADMIN/BR-ADMIN、OFFICE/BR-OFFICE、Core/R-HQ/Branch | N07/N08/N09/N10；C18补双向PC对PC IPv6 ping |

### 7.2 实验2：VLAN与二三层园区架构

| 技术编号 | 课程技术 | 当前项目落点 | 报告素材代号 / 说明 |
|---|---|---|---|
| E2-01 | VLAN划分 | HQ Core/Access VLAN10 OFFICE、20 IOT、30 MANAGEMENT；Branch40 OFFICE、50 MGMT | C01/C05/T02 |
| E2-02 | 广播域与部门隔离 | OFFICE/IOT/MGMT及分部两域 | C01/C05/N01/N05；广播域解释写文字 |
| E2-03 | Access端口 | Access Fa0/1→10、Fa0/2→20、Fa0/3–4→30；Branch Fa0/1→40、Fa0/2→50；Core Gi1/0/10→30 | C01/C05/C15 |
| E2-04 | Trunk链路 | HQ Core↔Access的Po1；Branch SW Gi0/1↔Router G0/1 | C02/C05 |
| E2-05 | IEEE 802.1Q | HQ Trunk、Branch .40/.50路由子接口 | C02/C05（trunk/encapsulation） |
| E2-06 | Native VLAN | 现有802.1Q Trunk的相关属性 | C02/C05（Native VLAN1） |
| E2-07 | LACP协商 | Core Gi1/0/1–2、Access Gi0/1–2 | C02（LACP） |
| E2-08 | EtherChannel/Port-channel | HQ Po1 | C02（Po1 SU/member bundled） |
| E2-09 | 聚合带宽/可靠性 | HQ双链路Core↔Access | C02只证明聚合成立；带宽/可靠性为设计说明，未有实测吞吐/切链结果 |
| E2-10 | SVI三层交换网关 | SW-CORE Vlan10/20/30 | C03 |
| E2-11 | Inter-VLAN Routing | HQ由Core SVI；Branch由Router子接口 | N01/C03 |
| E2-12 | Router-on-a-Stick | R-BRANCH G0/1.40/.50与SW-BRANCH Trunk | C05/N02 |
| E2-13 | IPv4 DHCP/IP/Gateway/DNS | HQ Core OFFICE池；Branch Router BR-OFFICE池 | C03/C05/N01/N02；C18补HQ DHCP客户端DNS值，C10为服务端；Branch池未登记DNS |
| E2-14 | 同VLAN/跨VLAN、Trunk、聚合、获址验证 | Core/Access/Branch与PC | N01/N02/C02/C05；C18补同VLAN ping |

### 7.3 实验3：ACL、NAT与服务发布

| 技术编号 | 课程技术 | 当前项目落点 | 报告素材代号 / 说明 |
|---|---|---|---|
| E3-01 | Extended ACL | Core OFFICE-IN/IOT-IN，R-HQ WAN-IN | C04/C08 |
| E3-02 | ACL源地址匹配 | OFFICE/IoT两个/24，BR-OFFICE/26与BR-MGMT/27 | C04/C08/C17 |
| E3-03 | ACL目的地址匹配 | HQ-SERVICE host `.30.10`、HQ管理/IoT网段 | C04/C08/N04/N05 |
| E3-04 | ACL协议/端口匹配 | tcp80、tcp8000、icmp、tcp23/22及ip规则 | C04/C08（tcp/icmp/端口） |
| E3-05 | ACL应用方向与顺序 | Core VLAN10/20 inbound；R-HQ G0/1 inbound | C04/C08（access-group方向和条目顺序） |
| E3-06 | Standard ACL | NAT-INSIDE与管理来源ACL | C09（NAT-INSIDE）、C14/C17（VTY来源） |
| E3-07 | NAT地址转换 | R-HQ | C09/N04/N06 |
| E3-08 | PAT/Overload | R-HQ OFFICE `/24`→G0/1 `203.0.113.1` | C09/N06 |
| E3-09 | NAT Inside/Outside边界 | R-HQ G0/0 inside，G0/1 outside | C09（inside/outside） |
| E3-10 | Static NAT/Port Mapping | R-HQ TCP `203.0.113.1:80→192.168.30.10:80` | C09/N04；全协议1:1 Static NAT未部署 |
| E3-11 | DNS Server/域名解析 | INTERNET-SERVER `192.0.2.10` | N06/C10 |
| E3-12 | HTTP/Web Server | Internet Server与HQ-SERVICE/BACKEND-STUB | N04/N06/C11 |
| E3-13 | NAT转换表/公网映射验证 | R-HQ、BR-OFFICE与Internet Server | N04/N06/C09；排查Q01可选 |
| E3-14 | ACL命中、DNS与HTTP正负向验证 | HQ/Branch PC与网络设备 | N01/N04/N05/N06/N10/C04/C08 |

### 7.4 实验4：OSPF/eBGP

| 技术编号 | 课程技术 | 当前项目落点 | 报告素材代号 / 说明 |
|---|---|---|---|
| E4-01 | OSPF/IGP | HQ SW-CORE↔R-HQ | N03/C07 |
| E4-02 | OSPF Area 0 | Transit10.255.0.0/30及Core HQ网段 | C07及完整CLI附录 |
| E4-03 | OSPF Router ID | Core10.255.0.1，R-HQ10.255.0.2 | N03/C07（实际RID） |
| E4-04 | OSPF Network宣告 | Core声明Transit与三个/24；R-HQ声明Transit | C07及完整CLI附录 |
| E4-05 | OSPF邻居与动态路由学习 | Core/R-HQ | N03 |
| E4-06 | BGP/EGP | R-HQ、R-ISP、R-BRANCH | N03/C07 |
| E4-07 | AS自治系统规划 | HQ65001、ISP65000、Branch65002 | N03/C07/T02；AS规划表 |
| E4-08 | eBGP Neighbor | HQ↔ISP `.113.1/.2`；ISP↔Branch `.100.1/.2` | N03（两会话、四条邻居条目） |
| E4-09 | BGP Route Advertisement | HQ发布192.168.30/24；Branch两个VLSM前缀；ISP发布192.0.2/24及两WAN/30 | C07/N03（BGP表及network/mask附录） |
| E4-10 | AS Path | 各路由器BGP表内跨AS路径属性 | N03（G3-A-02b的AS Path）；未做过滤/prepend |
| E4-11 | OSPF+BGP融合 | R-HQ两类路由交汇；Core由默认出口外出 | C07（Core默认出口+RHQ双协议）；无redistribute |
| E4-12 | 前缀/出口路由策略 | HQ管理网发布，IoT不对外发布；Core仅需默认路由 | C07/C08/N05；未做route-map/MED/local-pref调优 |
| E4-13 | 路由表/BGP表/跨区域Ping验证 | 三个路由器、Core与Branch PC | N03/N04/N06 |

### 7.5 实验5：Port Security与IPv6 Overlay

| 技术编号 | 课程技术 | 当前项目落点 | 报告素材代号 / 说明 |
|---|---|---|---|
| E5-01 | Port Security | SW-ACCESS Fa0/1→OFFICE-PC | C14/N11 |
| E5-02 | Sticky MAC | 同一Fa0/1 | N11（合法SecureSticky） |
| E5-03 | Maximum MAC | Fa0/1 maximum1 | C14/N11（max1） |
| E5-04 | MAC Binding/端口绑定 | 合法OFFICE MAC↔Fa0/1/VLAN10 | N11（sticky绑定）；非手工静态MAC命令 |
| E5-05 | Violation Mode选择 | Fa0/1 | C14/N11（restrict） |
| E5-06 | Restrict | Fa0/1非法MAC流量 | N11（非法流量丢弃但Secure-up） |
| E5-07 | Shutdown/err-disable | 当前项目未选择 | 未选择shutdown/err-disable；如实文字说明，不要求截图或新增功能 |
| E5-08 | Violation Counter | SW-ACCESS show port-security interface fa0/1 | N11（违规计数0→5为历史当次测试） |
| E5-09 | 未授权终端替换/检测日志 | 临时更改OFFICE终端MAC为0000.1111.2222 | N11（非法MAC/日志/丢包） |
| E5-10 | 安全恢复与正负向对照 | Fa0/1与OFFICE-PC | N11（三阶段） |
| E5-11 | IPv6-over-IPv4 Tunnel/封装 | R-HQ↔R-BRANCH，经过IPv4-only R-ISP | N08/C13/C06 |
| E5-12 | Tunnel Interface与端点参数 | 两端Tunnel0，ff::1/ff::2；HQ source G0/1→198.51.100.2；Branch source G0/0→203.0.113.1 | C13/N08 |
| E5-13 | IPv4 Underlay与IPv6 Overlay路由配合 | ISP BGP发布两个WAN/30；企业四条IPv6静态路由 | C06/C07/C12/N08 |
| E5-14 | MAC违规/Tunnel状态/IPv6 Ping验证 | Access、R-HQ/Branch、BR-ADMIN | N11/N08/C12 |

## 8. 创新点：每个主张对应哪组证据

以下创新是课程技术的系统集成与应用扩展，不声称发明OSPF/BGP/Tunnel等协议。已打勾的是对应截图素材已存在；需要最终版本配图的部分引用前面的报告补图项，不新增重复摄影任务。

- [x] **I01｜感知—边缘决策—云端管理—物理执行双闭环**

  可明确写成创新：TEMP/MCU/SBC/FAN本地闭环与WS Policy/Command云端闭环结合。用T01/F02/F03/F05/C19同一组图解释路径；最终Dashboard配图F06/U02补后引用。

  **本地已有**：[evidence/network/G2-A-01-topology-check-pass.png](../evidence/network/G2-A-01-topology-check-pass.png)。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-01-policy-apply-ack-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-01-policy-apply-ack-pass.png)。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-05-manual-command-off-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-05-manual-command-off-pass.png)。


- [x] **I02｜断云不断控、最后有效策略保留**

  使用非默认策略v2/33℃→真正Backend停机→离线TURN_ON→重连保留策略。创新点是Cloud transport与Local Loop解耦；不宣称Edge重启后策略持久化。离线OFF物理补图F09归入该创新。

  **本地已有**：[evidence/edge/gate4/G4-B-01-last-policy-before-outage-pass.png](../evidence/edge/gate4/G4-B-01-last-policy-before-outage-pass.png)。

  **本地已有**：[evidence/edge/gate4/G4-B-02-backend-down-local-auto-on-pass.png](../evidence/edge/gate4/G4-B-02-backend-down-local-auto-on-pass.png)。


- [x] **I03｜版本化Policy、执行后ACK与状态归属**

  Policy/Command有ID/version、应用后ACK，区分发送成功与设备执行成功；用Edge ACK图F02/F05和后补Dashboard ACK F06/F07。严格递增/拒绝旧版本依据源码及测试，不仅凭不同历史version推断。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-01-policy-apply-ack-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-01-policy-apply-ack-pass.png)。

  **本地已有**：[edge/packet_tracer/evidence/gate3/G3-B-06-manual-command-on-pass.png](../edge/packet_tracer/evidence/gate3/G3-B-06-manual-command-on-pass.png)。


- [x] **I04｜恢复时state_sync消除云边状态偏差**

  hello之后真实温度/FAN/最后Policy整包同步，Backend与UI恢复；SBC/Backend图已存在，UI用F11补齐。

  **本地已有**：[evidence/edge/gate4/G4-B-03-auto-reconnect-state-sync-pass.png](../evidence/edge/gate4/G4-B-03-auto-reconnect-state-sync-pass.png)。

  **本地已有**：[evidence/backend/gate4/G4-C-02-state-sync-event-pass.png](../evidence/backend/gate4/G4-C-02-state-sync-event-pass.png)。


- [x] **I05｜从模拟园区走向真实NC可观测**

  现图可证明真实NC至少两台Managed；最终报告配U03真实NC API→Backend→Dashboard链路，不能只凭清单宣称链路已留证。创新是实际只读Northbound集成、来源明确、Managed映射与未采集协议边界。

  **本地已有**：[evidence/noc/NOC-NC-01-controller-managed-inventory.png](../evidence/noc/NOC-NC-01-controller-managed-inventory.png)。


- [x] **I06｜IPv4 Underlay承载IPv6管理Overlay**

  现有跨站点IPv6业务与路由图，说明ISP不升级IPv6仍能支持企业IPv6运维；同时对应实验一和五，是组合应用创新。

  **本地已有**：[evidence/network/G4-A-04c-ipv6-route-tables-pass.png](../evidence/network/G4-A-04c-ipv6-route-tables-pass.png)。

  **本地已有**：[evidence/network/G4-A-04d-br-admin-to-hq-service-ipv6-pass.png](../evidence/network/G4-A-04d-br-admin-to-hq-service-ipv6-pass.png)。


- [x] **I07｜按站点规模选择SVI/ROAS，并用多层安全约束业务**

  HQ三层Core+LACP与Branch ROAS/VLSM结合；VLAN、IP ACL、VTY来源ACL、PortSecurity分别约束不同层次。用C02/C03/C05/C08/N09/N11交叉引用。

  **本地已有**：[evidence/network/G1-06-swcore-svi-routing-pass.png](../evidence/network/G1-06-swcore-svi-routing-pass.png)。

  **本地已有**：[evidence/network/G2-A-03-branch-roas-pass.png](../evidence/network/G2-A-03-branch-roas-pass.png)。

  **本地已有**：[evidence/network/G4-A-02b-port-security-violation-pass.png](../evidence/network/G4-A-02b-port-security-violation-pass.png)。


- [ ] **I08｜统一NOC与Campus Policy上层展示**

  必须一张最终中文Campus/安全/运维/演练相关界面；用U02/U06/U08/U09/U10同一批待补图即可。图注说明Edge策略可真实执行，网络/安全为展示或模拟，Campus上层不破坏thermal-01/version/ACK。此项当前没有满足要求的完整最终界面图，不重复生成新拍摄代号。

  **命名/补图**：直接使用 `U02-noc-overview-*.png` / `U09-campus-policy.png` 等，不另拍 `I08` 图。


## 9. 排查过程与最终附件

排查图用于“实现过程与关键问题”；最终配置导出/彩排记录用于附件。它们不需要占据主功能演示大量篇幅。

- [x] **Q01｜PT静态NAT误抓私网HTTP：失败→修复→共存（扩展/附录可选）**

  现有坏会话（端口0）图和最终两页面同时成功图，适合写真实问题定位与修复。失败图标题必须写“修复前”，不要列入最终失败结果。

  **本地已有**：[evidence/network/G4-A-06-n7-nat-conflict-evidence.png](../evidence/network/G4-A-06-n7-nat-conflict-evidence.png)。

  **本地已有**：[evidence/network/G4-A-07-n7-n11-coexist-fix-pass.png](../evidence/network/G4-A-07-n7-n11-coexist-fix-pass.png)。

  **本地已有**：[evidence/network/G4-A-07b-n7-n11-coexist-confirm-pass.png](../evidence/network/G4-A-07b-n7-n11-coexist-confirm-pass.png)。


- [ ] **V01｜当前NC准入后的最终管理正负向回归**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **A24**｜`V01-final-vty-regression-allow-router.png`：来源ADMIN-PC、目标172.16.40.65和R-BRANCH设备命令行提示符同时可见。
  - **A25**｜`V01-final-vty-regression-allow-switch.png`：目标172.16.40.66和SW-BRANCH设备命令行提示符可见。
  - **A26**｜`V01-final-vty-regression-deny-office.png`：来源为192.168.10.0/24；两次telnet均未出现设备登录提示符，无法建立Telnet会话，连接失败结果可见。
  - **A27**｜`V01-final-vty-regression-deny-branch-office.png`：来源为172.16.40.0/26；两次telnet均未出现设备登录提示符，无法建立Telnet会话，连接失败结果可见。
  - **A28**｜`V01-nc-managed-after-vty-check.png`：控制器CONNECTED；SW-CORE 192.168.30.1和SW-BRANCH 172.16.40.66仍为ONLINE/Managed。


- [ ] **V02｜保存重开当前.pkt与在线状态**

  **逐张拍摄**（操作步骤见[四人清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)对应图号）：

  - **A29**｜`V02-final-reopen-topology.png`：重开后总部、ISP、分部、NC及IoT设备和连线完整显示。
  - **A30**｜`V02-final-reopen-online.png`：左侧Edge ONLINE、Cloud CONNECTED、温度/FAN有读数；右侧控制器CONNECTED，两台交换机Managed/ONLINE。


### 9.1 完整配置必须补齐的非截图附件

以下不是要求把所有CLI拍成几十张图。关键片段用C类图，**完整配置信息**通过当前真实导出文件和配置总览形成可检索附录：

- [ ] **CFG01**：`CFG01-SW-CORE-running.txt`，SVI/DHCP/ACL/OSPF/IPv6、Po1及NC接入/管理认证；另保存`show vlan brief`/Trunk/Port-channel结果，因为VLAN数据库不一定只靠running-config完整呈现。
- [ ] **CFG02**：`CFG02-SW-ACCESS-running.txt`，VLAN/Access/Trunk/LACP/Fa0/1 PortSecurity/sticky；另保存VLAN/聚合/安全状态输出。
- [ ] **CFG03**：`CFG03-R-HQ-running.txt`，接口/Loopback、OSPF/BGP/默认路由、WAN-IN、PAT与两静态映射、Tunnel/IPv6路由、VTY认证与ACL绑定。
- [ ] **CFG04**：`CFG04-R-ISP-running.txt`，三个IPv4接口、AS65000/两邻居/发布前缀；对照ISP未启用原生IPv6/Tunnel的事实。
- [ ] **CFG05**：`CFG05-R-BRANCH-running.txt`，ROAS/DHCP/BR-V6/RA标志、BGP/Tunnel/IPv6静态路由、最终VTY。
- [ ] **CFG06**：`CFG06-SW-BRANCH-running.txt`，VLAN/Trunk/管理SVI/default-gateway与最终VTY；另保存VLAN/Trunk状态。
- [ ] **CFG07**：`CFG07-hosts-services.csv`或Markdown地址表，覆盖所有PC/Server/NC/SBC的IPv4/IPv6、掩码/前缀、网关、地址来源、DNS/HTTP开关；TEMP/MCU/FAN无该链路IP需求的设备标明接口接线，不编造地址。
- [ ] **CFG08**：实际包内运行的MCU/SBC源码导出、包名/保存重开记录，与仓库Gate4源码差异说明；截图用C20，长代码用文件。
- [x] **CFG09**：Backend/Dashboard/NC适配器源码、配置字段与启动脚本已在仓库，报告附录可直接整理 [FINAL_CONFIGURATION](FINAL_CONFIGURATION.md)、[PROTOCOL](PROTOCOL.md)、[start_pt_backend.ps1](../scripts/start_pt_backend.ps1)、[pt_controller.py](../backend/app/pt_controller.py)、[dashboard/index.html](../dashboard/index.html)；无需截图整份代码。实际NC凭据不收进报告。

CLI截图/导出在设备上执行`show running-config`，需要补充运行态时用`show ip route`、`show ip ospf neighbor`、`show ip bgp summary`/`show ip bgp`、`show ipv6 route`、`show interfaces tunnel 0`、`show access-lists`、`show ip nat translations`、`show port-security interface fa0/1`等。以PT设备真实支持语法为准；本文不要求运行任何配置写入命令。

### 9.2 同次API/日志附件

U03/U04/U05配套`/api/controller/state`、`/api/network/state`；F06/F07/F11配套`/api/state`；U06/U07配套`/api/security/state`及NOC事件；U09配套`/api/campus-policy`；U10配套`/api/simulation/state`。保留完整对象、实际时间与状态，不只截JSON顶部。数据含秘密时去除密码/ticket，不改其他事实字段。

<a id="missing-shots"></a>

## 10. 只补缺图：拍摄任务速查

下面是前文所有尚缺画面的汇总，可直接按代号命名。一组可能需要多张，正文是否采用由报告篇幅决定。“必补”指完整最终报告所需；“配置复现”指用于呈现完整配置和当前系统状态；同画面已满足多项时合并，不增加重复任务。

| 代号 | 建议主文件名 | 必须看到什么 | 优先级 |
|---|---|---|---|
| T02 | `T02-final-topology.png` | 当前HQ/ISP/Branch/NC/IoT最终完整拓扑 | 必补；可合图复用 |
| F06 | `F06-policy-ack.png` | Policy APPLIED ACK、同一ID/version、33℃/AUTO/迟滞 | 必补；可合图复用 |
| F07 | `F07-command-ack.png` | MANUAL OFF/ON、Command APPLIED ACK、物理状态 | 必补；可合图复用 |
| F09 | `F09-offline-fan-off.png` | Backend真正停止期间CLOUD OFFLINE、TURN_OFF、FAN state=0；必要时补离线ON state=2 | 必补；可合图复用 |
| F11 | `F11-dashboard-recovered.png` | Backend恢复后中文UI、原Policy/温度/FAN与state_sync | 必补；可合图复用 |
| U02 | `U02-noc-overview-01.png` | 最终中文Edge首屏；其他板块按U03/U06/U08/U09/U10拍摄 | 必拍 |
| U03 | `U03-nc-dashboard-api.png` | 两台Managed→ONLINE、NC CONNECTED、NOT COLLECTED及同次API | 必补；可合图复用 |
| U04 | `U04-nc-unavailable.png` | NC关闭时清空旧卡片、恢复时重新采集 | 必补；可合图复用 |
| U05 | `U05-controller-topology-response.png` | NC物理拓扑实际JSON，或真实降级错误且清单仍可用 | 必补；可合图复用 |
| U06 | `U06-security-attack.png` | 安全模拟攻击红色事件、计数与恢复审计 | 必补；可合图复用 |
| U07 | `U07-acl-block-event.png` | ACL_BLOCK_EVENT红色事件；端口SECURE/FORWARDING | 必拍 |
| U08 | `U08-branch-check.png` | Router/Switch模拟PASS/ALLOW，保留模拟标签 | 必补；可合图复用 |
| U09 | `U09-campus-policy.png` | Campus Version及Edge/Network/Security，配置展示说明 | 必补；可合图复用 |
| U10 | `U10-cloud-ws-failure.png` | 按钮真实WS断开、离线最后观测、恢复state_sync SUCCESS | 必补；可合图复用 |
| U11 | `U11-network-simulation-disabled.png` | Network Failure禁用/说明，必要时附409 | 必补；可合图复用 |
| C10 | `C10-dns-config.png` | DNS On与两个A记录 | 报告配置复现 |
| C11 | `C11-http-config.png` | 两Server HTTP On、页面资源与地址 | 报告配置复现 |
| C15 | `C15-nc-access-address.png` | Core Gi1/0/10 access30及NC .30.30/24/GW | 报告配置复现 |
| C16 | `C16-nc-external-discovery.png` | External Access/RWA58000与实际Discovery结果 | 报告配置复现 |
| C17 | `C17-management-final.png` | 当前login local、VTY ACL与绑定、R-HQ Loopback/路由 | 报告配置复现 |
| C18 | `C18-host-addresses.png`及补强后缀 | ADMIN/BR-ADMIN/SBC地址；HQ DHCP DNS/Auto Config、同VLAN与双向PC IPv6 ping | 报告配置复现 |
| C20 | `C20-pt-program-config.png` | 当前.pkt内MCU/SBC运行程序与关键参数 | 报告配置复现 |
| C21 | `C21-backend-started.png`、`C21-runtime-status.png` | Backend8000/NC58000/真实WS成功启动 | 报告配置复现 |
| V01 | `V01-final-vty-regression.png` | NC增量后管理来源允许/拒绝对照 | 报告配置复现 |
| V02 | `V02-final-reopen-topology.png`、`V02-final-reopen-online.png` | 保存重开后的拓扑、真实Edge和NC在线 | 报告配置复现 |

**执行顺序**：A按A01–A30、B按B01–B12、C按C01–C15、D按D01–D13，从上到下完成[四人逐张操作清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)。

若完整全页U02已经清晰覆盖U09/U11，直接将对应项更新为引用U02。同一次F06截图也能同时支撑I01/I03；F09/F10/F11支撑I02/I04；U01/U03支撑I05。创新点不另造一套新截图。

## 11. 不能直接使用的图片与图注要求

- `evidence/gate3_bcd/G3-INT-01-real-edge-online-pass.png`：实际是启动前OFFLINE/WAITING、无温度，不能作真实在线成功图；需要启动前基线时可以放附录并写真实标题。
- `edge/packet_tracer/evidence/B2_fan_state_topology.png`：本轮检查文件内容无法被图片解码器识别，不是可直接插入的可读PNG。未修改文件；物理FAN证明改用C19两张有效图，IoT连线改用T01/T03。无需为这一损坏文件单独增加补图任务。
- G1 Fake Edge以及早期Dashboard示例图：可以讲软件开发过程，最终真实PT功能优先使用F01及Gate2之后真实链路图，不混成实机验收。
- `G3-C-02-dashboard-policy-33-pass.jpg`：可以补充历史页面v3/33℃展示，但无Dashboard ACK面板，不能替代F06。
- G4-A-03c右侧BR-OFFICE显示SLAAC阶段地址；最终Branch DHCPv6用03d。G4-A-06为修复前NAT失败，仅用于Q01；最终N7/N11结果用07b。
- G4 VTY旧图显示MGMT-ALLOW与线路密码；NC后本地用户和ACL改动用C17/V01，不能将不同阶段配置写成同时生效。

每组图注至少写四件事：**操作/设备与时间阶段、可观察结果、该结果证明的功能/技术、局限或来源**。例如：“HQ OFFICE通过域名打开Internet Web，结合PAT会话说明解析与出口业务可用；不证明SBC真实WS经过PT WAN。”不能只写“结果如图”。

截图保留设备/窗口标题、目标地址、关键命令和完整结果，字体可读；原图保留，报告排版副本允许裁边/加框但不得改IP、状态、计数或版本。不同历史测试的v2/v3/v10和温度不是同一会话，同次闭环新图须记录实际递增版本，不强制回到固定版本。失败记录保留实际失败，不靠文件名PASS自动判定。

## 12. 推荐最终报告的素材安排

“完整功能演示”正文必须按 **园区管理 → 中心物联网控制 → Dashboard 面板控制** 排列。下表中的素材分类用于选图，不代表正文出现顺序；逐场景脚本见 [最终功能演示设计](FINAL_FUNCTION_DEMO.md)。

| 报告内容 | 应放的素材 | 解释重点 |
|---|---|---|
| 实验目标/场景/总体架构 | T02；T01/T03局部；地址/AS/角色表 | 三区域、IoT本地链路、真实带外WS和NC REST各自的路径 |
| 网络与设备配置 | C01–C18关键片段、FINAL_CONFIGURATION正文、CFG01–CFG07完整附录 | 按技术模块→区域→设备写，不按截图时间机械罗列 |
| Edge/Cloud配置与控制 | C19/C20/C21、程序/协议字段表、F02–F07 | 温度采样、迟滞、AUTO/MANUAL、Policy/Command/ACK |
| 完整功能验证 | 先用N01–N11及A19–A28完成园区管理，再用F01–F11完成中心物联网控制，最后用U01–U06/U08–U11完成Dashboard面板控制 | 每项操作→预期→实际→截图观察→结论；真实与模拟分清 |
| 前五次实验对照 | §7全部71项技术的落点和素材引用；EXPERIMENT_MAPPING详细解释 | 逐项说明用于哪里、为什么、如何验证；未启用变体明确说明 |
| 创新点 | I01–I08对应素材，重用功能图 | 双闭环、断云自治、ACK/version、同步、真实NC、Overlay、多层安全、统一NOC |
| 排查/局限/总结 | Q01、F12可选；U11真实边界 | PT兼容/NAT问题、未采集协议、展示/模拟能力范围 |
| 最终交付/附录 | CFG01–CFG09、API/日志、V01/V02 | 当前配置可重现、包内程序、保存重开、彩排真实记录 |

素材清单不改变项目代码、PT设备配置或原始截图，不启动服务，不将未留证项改成已通过。
