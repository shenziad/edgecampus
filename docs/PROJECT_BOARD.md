# Integration Board — Final Architecture v2

只记录可验收能力与跨模块状态，不记录按钮颜色、函数改名等局部工作。

## 能力状态

| 能力 | Owner | 当前状态 | 证据 / 说明 | 下一动作 |
|---|---|---|---|---|
| Protocol v1.0 | B+C+D | **FROZEN** | `docs/PROTOCOL.md` | 不改字段/URL/ID |
| Backend 软件基线 | C | AVAILABLE | main 已有 FastAPI / state / events / fake 基线 | C 补 Gate1 owner 证据 + G2 真 Telemetry |
| C Gate1 Owner 验收 | C | **PLACEHOLDER** | `docs/gate1/C_BACKEND_REPORT.md` | Gate5 前必须清零 |
| Fake Edge | B+C | DONE | 可独立开发/联调 | 保留，不替代 PT 真链路 |
| Dashboard 基线 | D | **PASS G1** | `docs/gate1/D_DASHBOARD_REPORT.md` + 4 张 evidence | G2 接真 PT Telemetry |
| HQ VLAN/IP / SVI / DHCP | A | **PASS G1** | A Gate1 报告 / network evidence | 冻结 Core |
| HQ EtherChannel / Trunk | A | **PASS G1** | Po1 + trunk evidence | 新 WAN 后持续 regression |
| HQ ACL | A | **PASS G1** | OFFICE→IOT deny 等 | 新 WAN 不得破坏 |
| Edge Local Loop | B | **PASS G1** | TEMP→MCU→SBC→FAN / hysteresis / backend-off | G2 增量加 Telemetry |
| A+B canonical integration | A+B | **PASS G1** | `docs/gate1/AB_INTEGRATION_REPORT.md` | 作为 HQ Core baseline |
| PT → Real Host RealWSClient | A+B+C | VERIFIED | Gate0 实机 + 重开复测 | G2 承载真 Telemetry |
| Real PT Telemetry | B+C+D | **B EDGE SIDE PASS / C+D END-TO-END PENDING** | B 的 6 张 G2 实机证据 + `docs/gate2/B_EDGE_REPORT.md` | C/D 完成 TEMP→Dashboard |
| Branch LAN / ROAS | A | NOT STARTED | Final Architecture v2 | G2 |
| IPv4 WAN Underlay | A | NOT STARTED | Final Architecture v2 | G2 |
| HQ OSPF | A | NOT STARTED | Area0 SW-CORE↔R-HQ | G3 |
| WAN eBGP | A | NOT STARTED | AS65001/65000/65002 | G3 |
| Branch→HQ business | A | NOT STARTED | BR-OFFICE→HQ-SERVICE | G3 |
| HQ Internet PAT / DNS / HTTP | A | NOT STARTED | OFFICE→Internet | G3 |
| Static TCP/80 mapping | A | NOT STARTED | `203.0.113.1:80→192.168.30.10:80` | G3 |
| Cloud Policy / Command 真闭环 | B+C+D | READY FROM FAKE | 真 PT 未验收 | G3 |
| IPv6 address modes | A | NOT STARTED | SLAAC + DHCPv6 + Static | G4 |
| IPv6-over-IPv4 Overlay | A | NOT STARTED | BR-ADMIN→HQ MGMT | G4 |
| Central Network Admin | A | NOT STARTED | HQ ADMIN→Branch devices | G4 |
| Port Security / sticky MAC | A | NOT STARTED | HQ OFFICE access | G4 |
| Cloud-off local autonomy | B | PASS LOCALLY / FINAL PENDING | G1 backend-off local loop 已证；整套演示待 G4 | G4 |
| Cloud reconnect + State Sync | B+C+D | PASS FAKE / REAL PENDING | fake 基线存在 | G4 真 PT |
| Final canonical `.pkt` | A | IN DEVELOPMENT | HQ Core baseline 已存在；V2 WAN 待配置 | G5 freeze |

## Gate 状态

| Gate | 状态 | 说明 |
|---|---|---|
| G0 Contract Freeze | **COMPLETE** | 软件契约、HQ Core 规划、PT→Real Host 控制通道 |
| G1 四模块独立运行 | **CLOSED-WITH-PLACEHOLDER** | A/B/D PASS；A+B integration PASS；C owner evidence pending |
| G2 Real Telemetry + WAN Foundation | **IN PROGRESS** | B/C/D 真 TEMP→Dashboard；A Branch LAN + IPv4 Underlay |
| G3 Policy Loop + WAN Business | NOT STARTED | Policy/Command；OSPF/eBGP/NAT/DNS/HTTP/Branch business |
| G4 Failure Recovery + IPv6/Security | NOT STARTED | 断云恢复；IPv6 Tunnel、Port Security、Central Admin |
| G5 Freeze + 3 Rehearsals | NOT STARTED | 清零 placeholder、final `.pkt`、三轮完整彩排 |

## 当前 Critical Path

```text
B: PT real temperature + local fan
          ↓
C: Backend receives Protocol v1 telemetry
          ↓
D: Dashboard renders real PT state
```

A 与主 Critical Path 并行：

```text
Branch VLAN40/50
      ↓
Router-on-a-Stick
      ↓
IPv4 WAN Underlay
      ↓
G3 OSPF/eBGP/NAT
      ↓
G4 IPv6 Tunnel / Port Security
```

## Owner 边界

- **A Network**：唯一 canonical `.pkt` Owner。Final Architecture v2 的新增设备/链路也由 A 合入正式文件；不得为了 WAN 重写 HQ Gate1 Core。
- **B Edge**：只增量修改 `edge/` 与 SBC 适配；Local Loop 优先于 Cloud 通信。
- **C Control Plane**：`backend/`；不得因 G2 真 PT 接入更改 Protocol v1；同时补齐 Gate1 placeholder。
- **D UI & Integration**：`dashboard/`、`tests/`、端到端 evidence；不得把展示字段改成新的传输契约。

## Integration Check 记录

| 时间 | 参与 | Gate | 成功项 | 缺口 / 决策 |
|---|---|---|---|---|
| 2026-09-14 | 全组 | G0 | HQ topology / protocol / RealWSClient frozen | G0 COMPLETE |
| 2026-09-15 | A | G1 | VLAN/Trunk/EtherChannel/SVI/DHCP/ACL/N1-N3 PASS | A PASS |
| 2026-09-15 | B | G1 | TEMP→MCU→SBC→FAN、hysteresis、backend-off autonomy PASS | B PASS |
| 2026-09-15 | A+B | G1 | canonical integration + HQ regression PASS | A+B PASS |
| 2026-09-15 | D | G1 | NORMAL/WARNING/OFFLINE/RECONNECT evidence archived | D PASS |
| 2026-09-15 | C | G1 | 软件 baseline 已存在，但 Owner 专属证据未提交 | 建立 placeholder；不阻塞 G2；G5 前必须补 |
| 2026-09-15 | 全组 | Re-baseline | Final Architecture v2 冻结：HQ + ISP/Internet + Branch；保留双控制环与 Protocol v1 | 进入 G2 |
| 2026-09-15 | B | G2 | RealWSClient / hello / real TEMP telemetry / status / heartbeat / physical FAN state 2 + Protocol ON PASS | B Edge-side PASS；等待 C/D 完整 TEMP→Dashboard 联调 |

## Final Architecture v2 课程覆盖追踪

| 课程能力 | 目标 Gate | 状态 |
|---|---|---|
| VLSM / IPv4 DHCP | G2 | Branch 待实现；HQ DHCP 已 PASS |
| VLAN / Trunk / SVI / EtherChannel | G1/G2 | HQ PASS；Branch ROAS 待 G2 |
| OSPF / BGP | G3 | NOT STARTED |
| ACL / NAT/PAT / DNS/HTTP / static mapping | G1/G3 | HQ ACL PASS；其他待 G3 |
| SLAAC / DHCPv6 / Static IPv6 / IPv6 static route | G4 | NOT STARTED |
| MAC / Port Security | G4 | NOT STARTED |
| IPv6-over-IPv4 Tunnel | G4 | NOT STARTED |
| Remote management | G4 | NOT STARTED |
