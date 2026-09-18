# 全部待补证据清单

基准：2026-09-18 最新 `.pkt` 与 `feat/edge` 软件。项目为 **完成（待补证据）**。下表共 **28 组**，不是 28 张截图；同组可用多图、CLI 文本、JSON 或视频组合。一份证据覆盖多项时交叉引用，无需重复拍摄。

G4 A N12–N15 为用户确认已测但未归档；NOC NC 成功为用户确认且已有控制器清单原图。未留记录的最终回归/断连恢复/三轮彩排需实际执行并留证，不能只补写 PASS。所有截图保留原像素，标明日期、设备、来源与对应 ID；JSON 保存完整对象，移除密码/票据。

## A：真实 PT 网络与 G4 补证

推荐归档 `evidence/network/gate4/`。以下必须来自 PT，不能使用 NOC 模拟卡片。

| ID | 覆盖项 | 必须能直接观察的内容 |
|---|---|---|
| EV-01 | N12 HQ SLAAC | HQ OFFICE IPv6 地址/前缀、网关、SLAAC 模式及对应 SVI/RA 配置；实际分配结果 |
| EV-02 | N12 Branch DHCPv6 | BR-OFFICE 地址/网关；R-BRANCH DHCPv6 pool、接口与相关标志；PT 9.0.1 实际支持和分配结果，不把 SLAAC 冒充 DHCPv6 |
| EV-03 | N12 Static IPv6 | BR-ADMIN、HQ 管理设备/服务的静态 IPv6 地址、前缀、网关及允许域互通 |
| EV-04 | N13 Tunnel | IPv4 endpoints 先可达；两端 Tunnel0 地址/source/destination/mode ipv6ip、UP 状态、双向 IPv6 静态路由；BR-ADMIN→HQ MANAGEMENT IPv6 ping；ISP IPv4-only 配置 |
| EV-05 | N14 真实远程管理允许 | ADMIN-PC `.30.20` 对 R-BRANCH `.40.65`、SW-BRANCH `.40.66` 的实际 Telnet 登录/设备提示符；配套 VTY 配置，不用 ping 代替登录 |
| EV-06 | N14/NC ACL 负向 | 普通 HQ OFFICE 和 BR-OFFICE 管理请求被拒绝；VTY ACL 保留仅 `.30.20`/NC `.30.30` 准入与 deny any；区分管理拒绝与底层不可达 |
| EV-07 | N15 正常终端 | SW-ACCESS Fa0/1 sticky、maximum 1、restrict、合法 MAC、Secure-up/正常业务，起始 violation 计数 |
| EV-08 | N15 非法 MAC 与恢复 | 接入不同 MAC 后计数增加/非法流量被丢弃；恢复合法终端后正常业务。restrict 不等于端口物理 shutdown；按真实输出描述，不使用模拟 Port BLOCKED 证明 |
| EV-09 | 最终 N1–N4 回归 | HQ VLAN/SVI/DHCP、允许域互通与 OFFICE→IOT 拒绝、Trunk/Po1 SU/member bundled；Branch VLAN40/50 VLSM、ROAS、DHCP与网关；在加入 NC 后执行 |
| EV-10 | 最终 N5–N6 回归 | SW-CORE/R-HQ OSPF FULL 与学习路由；AS65001/65000/65002 BGP Established、业务前缀传播；增加 Loopback 后业务路由无退化 |
| EV-11 | 最终 N7–N11 回归 | Branch 私网 ping `.30.10` 与最终 HTTP `203.0.113.1`→HQ-SERVICE；Branch→IOT/MGMT 拒绝；HQ OFFICE PAT+Internet DNS/HTTP；静态 TCP/80 配置及会话。最终私网直连 HTTP FAIL 应如实记录，历史 G3 页面不能替代 |

## B+C+D：真实 Edge 闭环与恢复

归档 `evidence/integration/final/`（目录可在留证时创建）。既有真实图可复用，不重拍已充分覆盖的温度点。

| ID | 覆盖项 | 需补的内容 |
|---|---|---|
| EV-12 | G3 P1 修复后 Policy ACK | Dashboard 合法递增 vN、threshold 33/AUTO、APPLIED ACK 与实际 Edge 当前状态；与已有约 32 OFF/34 ON 实测图交叉引用；保存同次完整 `/api/state`，含 Policy SENT/ACK events、ID/version/source |
| EV-13 | G3 P2 修复后 Command ACK | 真实 FAN ON/OFF、Dashboard Command ACK、命令 ID 与 REMOTE-MANUAL 来源；同次完整 events/JSON，验证后恢复 AUTO。当前版本如实递增，不强行重置到 v1/v3 |
| EV-14 | G4 R1 离线 OFF/物理输出 | 真正停止 Backend 后，下调 TEMP01 跨越最后策略迟滞关闭阈值；SBC Cloud disconnected、本地循环、最后有效策略/version 与 FAN OFF；FAN Attributes 物理输出。既有离线 ON 图可复用；补足 ON/OFF 物理输出对应关系 |
| EV-15 | G4 R2 恢复 Dashboard | 重启 Backend 后真实 reconnect/hello/state_sync 的既有 Edge/Backend 图可复用；新增恢复 UI，与同次 PT/Backend 温度、FAN、policy_id/version/threshold一致，无默认 v1/30 回退 |

## C：真实 NC 接入（验收重点）

归档 `evidence/noc/`。已有 `NOC-NC-01-controller-managed-inventory.png` 为用户原图，只证明控制器清单；EV-18 为部分已有。

| ID | 覆盖项 | 需补的内容 |
|---|---|---|
| EV-16 | NC 物理/地址/对外 API | 最终拓扑 NC-HQ GE0→SW-CORE Gi1/0/10；VLAN30 access、NC `.30.30/24`/GW `.30.1`；ADMIN-PC 实际访问控制器；Preferences External Access 与 Real World Access Enabled/58000/监听状态 |
| EV-17 | 管理平面最终导出 | R-HQ Loopback0 `10.255.255.1/32` 与真实可达路由；实际变更设备的 username/login local/transport telnet、VTY-HQ-ADMIN、`access-class … in` 绑定；NC Discovery 使用的协议、发现目标与结果，凭据不出镜。报告称发现 R-HQ不等于 Managed；按实际状态记录 |
| EV-18 | NC→API→Dashboard 对照 | 成功的 Dashboard 全景/设备卡片：SW-CORE `.30.1`、SW-BRANCH `.40.66` Managed→ONLINE；同次 `/api/controller/state`、`/api/network/state` 完整 JSON（真实来源、采集时间、名称/IP/type/collectionStatus）；OSPF/BGP/Tunnel NOT COLLECTED，无 UNKNOWN/模拟替代。已有 NC 清单图可引用；其他 Unsupported 设备不得改写 ONLINE |
| EV-19 | 真实采集失败/恢复 | 关闭 NC Real World Access 后 UNAVAILABLE、健康卡片清空，无陈旧 ONLINE；重新开启后 CONNECTED、重新采集设备。需要当前版本的失败→恢复完整链路；过去失败截图不能代替成功恢复 |
| EV-20 | 真实物理拓扑读取 | Dashboard 展开的物理拓扑与 `/api/controller/state` 中 nodes/links 对照，说明控制器提供范围；若实际拓扑 API 不支持/失败，归档实际错误与清单保留的降级结果，不伪造拓扑 |

可在仓库根目录保存同次 API 快照（先创建 `evidence/noc`，服务按启动脚本运行）：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/controller/state | ConvertTo-Json -Depth 50 | Out-File evidence/noc/NOC-NC-controller-state.json -Encoding utf8
Invoke-RestMethod http://127.0.0.1:8000/api/network/state | ConvertTo-Json -Depth 50 | Out-File evidence/noc/NOC-NC-network-state.json -Encoding utf8
Invoke-RestMethod http://127.0.0.1:8000/api/state | ConvertTo-Json -Depth 50 | Out-File evidence/noc/NOC-edge-state.json -Encoding utf8
```

## D：NOC 页面验收（区分真实/模拟）

这些页面的软件测试已通过，最终中文 UI 操作画面尚未归档。SIMULATED 项不要求伪造真实 PT 作用。

| ID | 覆盖项 | 需补的内容 |
|---|---|---|
| EV-21 | Security Center | 模拟非法 MAC 红色事件、violation count、提示与恢复后审计保留；ACL_BLOCK_EVENT 操作画面/JSON；截图包含 SIMULATED。真实交换机违例由 EV-08 证明 |
| EV-22 | Branch Operations | Check Router/Switch 模拟 PASS/ALLOW 与非管理员来源 DENY；设备 `.65`/`.66`、模拟来源说明；不把此页面 PASS 当作真实远程登录证明（EV-05） |
| EV-23 | Campus Policy | Campus Version、thermal-01/真实递增 Edge version、threshold/mode 与 ACK对应；Edge/Network/Security 三类状态及 Network/Security 配置展示标签；与 EV-12 交叉引用 |
| EV-24 | Cloud Failure 按钮 | 使用真实 PT SBC：WS 实际断开、HTTP 页面仍可恢复、AUTONOMOUS MODE 说明/最后观测 FAN；PT 调温证实自治；恢复后 WAITING_FOR_STATE_SYNC→实际 state_sync→SUCCESS。仅 hello 不构成同步成功；不代替真正停 Backend 的 EV-14/15 |
| EV-25 | 真实 NC-only 模式边界 | 中文 Simulation Panel 的 Network Failure/Restore 禁用与说明；调用网络模拟接口返回 409，真实设备卡片不被模拟状态改写。验收无需展示虚构 BGP/Tunnel DOWN；实际协议状态由 EV-10/04 证明 |

## E：最终包与彩排（尚待实际核验/执行）

| ID | 覆盖项 | 需补的内容 |
|---|---|---|
| EV-26 | Final `.pkt` 保存重开/运行环境 | 在 PT 打开当前 144326 bytes 包，核对 HQ/WAN/Branch/NC/IoT 拓扑及版本，保存重开后配置和真实 Edge/NC 接入可用；导出完整设备最终配置，记录软件提交、PT 版本、包哈希。若保存使包变化，更新最终清单哈希；不能拿当前字节哈希替代打开验收 |
| EV-27 | SBC 包内程序一致性 | 导出/截取实际运行 MCU/SBC 程序、WS_URL/设备 ID/Protocol 1.0、策略保留与重连逻辑；对照仓库 Gate4 程序，解释必要适配；证明最新程序已保存入 final `.pkt`，不只存外部源码 |
| EV-28 | G5 连续三轮彩排 | 同一最终软件/拓扑版本连续 3 轮记录：Edge/NC 基线→Policy+Command ACK→真实离线升降温→恢复同步→最终业务/IPv6/管理/真实 Port Security→NOC模拟安全与策略说明；每轮日期、操作者、阈值/version、预期/实际、证据路径与异常。当前无记录，状态为待执行，出现失败后修复并重新取得连续3轮 |

## 已有证据，不重复要求

- G4：离线前策略、Backend-off 本地 ON、自动 reconnect/hello/state_sync、Backend offline/恢复、协议非法消息拒绝、Dashboard disconnected，共 9 张，见 [G4 索引](../gate4/EVIDENCE_INDEX.md)。C Gate1 stability debt 已清零。
- G1–G3：HQ/Branch/WAN 历史网络回归、真实 Telemetry/温度/FAN及 Edge-side Policy/Command证据保留，可交叉引用；不能代替加入 NC 后的最终回归。
- NC：SW-CORE/SW-BRANCH Managed 清单原图已复制入库；无需再次拍同一历史画面，但成功 Dashboard 与同次 API 仍缺。
- 本轮 46 项 Python、3 项 Node、compileall、Protocol contract 已实际通过并记录 [VALIDATION.md](VALIDATION.md)，无需用现场截图替代自动测试。
- 用户原始 Word 报告、配置文字、当前 `.pkt` 哈希与完成报告已归档；不需要为已存在的文档制造占位图片。

补证完成后，为每组填写真实文件路径/日期/结果与 SHA-256；失败保留为失败记录，不能仅靠文件名 PASS 判定。三轮彩排和包内程序未核验前，总状态保持“完成（待补证据）”。
