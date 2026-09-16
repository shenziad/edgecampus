# Integration Board — Final Architecture v2

只记录可验收能力与跨模块状态，不记录局部样式或函数改名。

## 能力状态

| 能力 | Owner | 当前状态 | 证据 / 说明 | 下一动作 |
|---|---|---|---|---|
| Protocol v1.0 | B+C+D | **FROZEN** | `docs/PROTOCOL.md` | 不改字段/URL/ID |
| Backend 软件基线 | C | AVAILABLE | FastAPI / state / events / fake baseline | G3 Policy/Command 真转发 |
| C Gate1 Owner 验收 | C | **CORE PASS / STABILITY PENDING** | `docs/gate1/C_BACKEND_REPORT.md` + G1-01~07 | Gate5 前补 malformed/offline/reconnect |
| Fake Edge | B+C | DONE | 独立开发替身 | 保留，不替代 PT 真链路 |
| Dashboard | D | **PASS G1 + G2** | G1/G2 Dashboard reports + evidence | G3 Policy/Command 真闭环 |
| HQ VLAN/IP / SVI / DHCP | A | **PASS G1** | A G1 evidence | 冻结 Core |
| HQ EtherChannel / Trunk | A | **PASS G1** | Po1 / trunk evidence | 每层网络变更 regression |
| HQ ACL | A | **PASS G1** | OFFICE→IOT deny 等 | G3 继续回归 |
| Edge Local Loop | B | **PASS G1 + G2 REGRESSION** | TEMP→MCU→SBC→FAN | G3 使用运行时 Policy |
| A+B Gate1 canonical integration | A+B | **PASS G1** | `docs/gate1/AB_INTEGRATION_REPORT.md` | 历史基线 |
| PT → Real Host RealWSClient | A+B+C | VERIFIED | G0 + G2 真 Telemetry | G3 真下行 |
| Real PT Telemetry | B+C+D | **PASS G2** | TEMP01→Dashboard 真链路 | 保持回归 |
| Branch LAN / ROAS | A | **PASS G2** | VLAN40/50 + ROAS + DHCP/管理地址 | G3 Branch 业务 |
| IPv4 WAN Underlay | A | **PASS G2** | 四段链路相邻可达 | G3 OSPF/eBGP |
| HQ Gate1 Regression after WAN | A | **PASS G2** | G2-A-07* | 每层继续回归 |
| HQ OSPF | A | IN PROGRESS G3 | Area0 SW-CORE↔R-HQ | 邻居与路由学习 |
| WAN eBGP | A | NOT STARTED G3 | AS65001/65000/65002 | OSPF后实施 |
| Branch→HQ business | A | NOT STARTED G3 | BR-OFFICE→HQ-SERVICE | eBGP后验证 |
| HQ Internet PAT / DNS / HTTP | A | NOT STARTED G3 | OFFICE→Internet | 路由后实施 |
| Static TCP/80 mapping | A | NOT STARTED G3 | 203.0.113.1:80→192.168.30.10:80 | 实测留证 |
| WAN / Branch Business ACL | A | NOT STARTED G3 | 权限矩阵 | 路由通后实施 |
| Real Policy Loop | B+C+D | IN PROGRESS G3 | Dashboard→Backend→Edge→ACK | threshold 30→33 |
| Real FAN Command | B+C+D | IN PROGRESS G3 | command→Edge→ACK | 保持 AUTO/MANUAL 语义 |
| IPv6 address modes | A | NOT STARTED G4 | SLAAC + DHCPv6 + Static | G4 |
| IPv6-over-IPv4 Overlay | A | NOT STARTED G4 | BR-ADMIN→HQ MGMT | G4 |
| Central Network Admin | A | NOT STARTED G4 | HQ ADMIN→Branch devices | G4 |
| Port Security / sticky MAC | A | NOT STARTED G4 | HQ OFFICE access | G4 |
| Cloud-off local autonomy | B | PASS LOCALLY / FINAL PENDING | G1/G2 local loop architecture | G4 full outage |
| Cloud reconnect + State Sync | B+C+D | PASS FAKE / REAL PENDING | fake baseline | G4 real PT |
| Repo canonical `.pkt` | A | **G2 A NETWORK BASELINE** | 与 A Gate2 report/evidence 可追溯 | A+B 整合包待本地正常 push |
| Owner-provided A+B G2 `.pkt` | A+B | **PACKAGE VERIFIED LOCALLY** | SHA-256 `8a299abad7ec701bcc17505cc1dd9f578eb9f11dbe0af448c4bc0d2077ebdae6` | 由 A 本地替换 canonical 后 push |

## Gate 状态

| Gate | 状态 | 说明 |
|---|---|---|
| G0 Contract Freeze | **COMPLETE** | 软件契约、HQ Core、PT→Real Host 通道 |
| G1 四模块独立运行 | **CLOSED-WITH-PENDING-STABILITY** | A/B/D PASS；A+B PASS；C Core PASS，3项稳定性待补 |
| G2 Real Telemetry + WAN Foundation | **COMPLETE** | A 网络基础 + B/C/D 真 TEMP→Dashboard 全部 PASS |
| G3 Policy Loop + WAN Business | **IN PROGRESS** | Policy/Command；OSPF/eBGP/NAT/DNS/HTTP/Branch business |
| G4 Failure Recovery + IPv6/Security | NOT STARTED | 断云恢复；IPv6 Tunnel、Port Security、Central Admin |
| G5 Freeze + 3 Rehearsals | NOT STARTED | 清零 C 稳定性欠账、final `.pkt`、三轮彩排 |

## Gate 2 Integration Check

```text
A: Branch VLAN40/50 + ROAS + DHCP + IPv4 WAN Underlay      PASS
A: HQ Gate1 Regression                                      PASS
B: Real TEMP01 Telemetry + Local AUTO + FAN Status          PASS
C: Real PT Telemetry → Backend /api/state                   PASS
D: Real PT NORMAL/WARNING/FAN/Event Dashboard               PASS
B+C+D: TEMP01 → MCU → SBC → RealWSClient → Backend → UI     PASS
Public Contract drift                                       NONE
Truthfulness boundary                                       PRESERVED
```

集成报告：`docs/gate2/INTEGRATION_REPORT.md`。

## 当前 Critical Path — Gate 3

软件 / IoT：

```text
D Dashboard Policy/Command
          ↓
C Backend forward
          ↓
B Real Edge receive/apply
          ↓
policy_ack / command_ack
          ↓
C → D 展示结果
```

网络：

```text
A OSPF
  ↓
eBGP
  ↓
Branch→HQ Business
  ↓
PAT / DNS / HTTP / Static Mapping
  ↓
Business ACL + Regression
```

两条 Track 可独立推进，Gate 3 收口时统一验收。

## Owner 边界

- **A Network**：唯一 canonical `.pkt` Owner；`packet_tracer/`、网络 evidence。
- **B Edge**：`edge/`；Local Loop 优先于 Cloud，不在 callback 内阻塞。
- **C Control Plane**：`backend/`；保持 Protocol v1，负责状态、事件和双向转发。
- **D UI & Integration**：`dashboard/`、`tests/`、端到端 evidence。

## Integration Check 记录

| 日期 | 参与 | Gate | 成功项 | 决策 |
|---|---|---|---|---|
| 2026-09-14 | 全组 | G0 | HQ topology / protocol / RealWSClient frozen | G0 COMPLETE |
| 2026-09-15 | A/B/D | G1 | Network / Edge / Dashboard 独立 PASS | 进入集成 |
| 2026-09-15 | A+B | G1 | canonical integration + HQ regression PASS | A+B PASS |
| 2026-09-15 | C | G1 | 核心 owner evidence 后补 | 3项稳定性欠账留 Gate5 前清零 |
| 2026-09-15 | 全组 | Re-baseline | Final Architecture v2 frozen | G2 开始 |
| 2026-09-15 | A | G2 | Branch LAN / ROAS / Underlay / HQ regression | A PASS |
| 2026-09-15 | B | G2 | RealWSClient + real telemetry + local loop + status/heartbeat | B PASS |
| 2026-09-16 | C | G2 | 真 PT TEMP 进入 Backend state | C PASS |
| 2026-09-16 | D | G2 | 真 PT NORMAL/WARNING/FAN/Event UI | D PASS |
| 2026-09-16 | 全组 | G2 | 两条轨道满足 DoD；报告/evidence 合并 main | **G2 COMPLETE，进入 G3** |

## 课程覆盖追踪

| 课程能力 | Gate | 状态 |
|---|---|---|
| VLSM / IPv4 DHCP | G1/G2 | ✅ HQ + Branch |
| VLAN / Trunk / SVI / EtherChannel / ROAS | G1/G2 | ✅ |
| OSPF / BGP | G3 | IN PROGRESS |
| ACL / NAT/PAT / DNS/HTTP / static mapping | G1/G3 | HQ ACL ✅；其余 G3 |
| SLAAC / DHCPv6 / Static IPv6 / IPv6 route | G4 | NOT STARTED |
| Port Security / sticky MAC | G4 | NOT STARTED |
| IPv6-over-IPv4 Tunnel | G4 | NOT STARTED |
| Remote management | G4 | NOT STARTED |
