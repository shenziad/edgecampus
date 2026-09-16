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
| HQ OSPF | A | **PASS G3** | Area 0 双向 FULL；R-HQ 学到 HQ VLAN10/20/30；`G3-A-01/01b` | 冻结 |
| WAN eBGP | A | **PASS G3** | AS65001/65000/65002 三会话 Established；显式 `network` 发布、**无 redistribute**；`G3-A-02/02b` | 冻结 |
| Branch→HQ business | A | **PASS G3** | BR-OFFICE → HQ-SERVICE HTTP 允许；`G3-A-02c/03c` | G4 继续回归 |
| HQ Internet PAT / DNS / HTTP | A | **PASS G3** | HQ OFFICE 经 PAT 访问 Internet DNS/HTTP；`G3-A-04b/04c` | 冻结 |
| Static TCP/80 mapping | A | **PASS G3** | `203.0.113.1:80 → 192.168.30.10:80` 实测；`G3-A-04d/04d2` | 冻结 |
| WAN / Branch Business ACL | A | **PASS G3** | WAN-IN 权限矩阵；BR-OFFICE 禁 IOT / 管理设备 / Telnet·SSH；`G3-A-03*` | G4 继续回归 |
| HQ ADMIN → Branch 管理可达 | A | **PASS G3** | ADMIN → `.65` / `.66` 可达；`G3-A-05` | G4 正式远程管理 |
| Real Policy Loop | B+C+D | IN PROGRESS G3 | Dashboard→Backend→Edge→ACK | threshold 30→33 |
| Real FAN Command | B+C+D | IN PROGRESS G3 | command→Edge→ACK | 保持 AUTO/MANUAL 语义 |
| IPv6 address modes | A | NOT STARTED G4 | SLAAC + DHCPv6 + Static | G4 |
| IPv6-over-IPv4 Overlay | A | NOT STARTED G4 | BR-ADMIN→HQ MGMT | G4 |
| Central Network Admin | A | NOT STARTED G4 | HQ ADMIN→Branch devices | G4 |
| Port Security / sticky MAC | A | NOT STARTED G4 | HQ OFFICE access | G4 |
| Cloud-off local autonomy | B | PASS LOCALLY / FINAL PENDING | G1/G2 local loop architecture | G4 full outage |
| Cloud reconnect + State Sync | B+C+D | PASS FAKE / REAL PENDING | fake baseline | G4 real PT |
| Repo canonical `.pkt`（`main`） | A | **G2 UPLOADED / 未含 G3** | `main` 上的 `.pkt` 由项目总指挥上传（blob `733ff34e`，118,556 字节），**不含 Gate 3 网络配置** | 合并时以 A 的 G3 版本为准 |
| A Gate 3 canonical `.pkt` | A | **PUSHED ON `feat/network`** | blob `55605ee0`，120,703 字节；含 Gate 1 + 2 + 3 全部网络配置与 Edge 接线 | 合并 `main` 时**采用本版本**（二进制不可自动合并） |

## Gate 状态

| Gate | 状态 | 说明 |
|---|---|---|
| G0 Contract Freeze | **COMPLETE** | 软件契约、HQ Core、PT→Real Host 通道 |
| G1 四模块独立运行 | **CLOSED-WITH-PENDING-STABILITY** | A/B/D PASS；A+B PASS；C Core PASS，3项稳定性待补 |
| G2 Real Telemetry + WAN Foundation | **COMPLETE** | A 网络基础 + B/C/D 真 TEMP→Dashboard 全部 PASS |
| G3 Policy Loop + WAN Business | **IN PROGRESS** | **A 侧 PASS**（OSPF / eBGP / NAT / DNS / HTTP / Branch business，N5–N11）；B/C/D Policy-Command 闭环待完成 |
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

## Gate 3 Track A Integration Check

```text
A: HQ OSPF Area 0 (SW-CORE ↔ R-HQ)                          PASS
A: WAN eBGP 65001 / 65000 / 65002                           PASS
A: Branch→HQ Business (BR-OFFICE → HQ-SERVICE HTTP)         PASS
A: WAN-IN Business / Isolation ACL                          PASS
A: HQ OFFICE → PAT → Internet DNS / HTTP                    PASS
A: Static TCP/80 Mapping (203.0.113.1:80 → .30.10:80)       PASS
A: HQ ADMIN → Branch Management Reachability                PASS
A: Per-layer HQ Gate1 Regression (×4)                       PASS
Public Contract drift                                       NONE
Truthfulness boundary                                       PRESERVED
```

报告：`docs/gate3/A_NETWORK_REPORT.md`；配置记录：`packet_tracer/CONFIG_LOG.md`（Gate 3 段）。

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
| 2026-09-16 | A | G3 | OSPF / eBGP / WAN-IN ACL / PAT+DNS+HTTP / 静态映射全部 PASS；四层逐层 HQ regression PASS；21 张 evidence | **A 侧 G3 完成**（N5–N11 + ADMIN→Branch 可达） |

## 课程覆盖追踪

| 课程能力 | Gate | 状态 |
|---|---|---|
| VLSM / IPv4 DHCP | G1/G2 | ✅ HQ + Branch |
| VLAN / Trunk / SVI / EtherChannel / ROAS | G1/G2 | ✅ |
| OSPF / BGP | G3 | ✅ HQ OSPF Area 0 + WAN eBGP 65001/65000/65002 PASS |
| ACL / NAT/PAT / DNS/HTTP / static mapping | G1/G3 | ✅ HQ ACL；WAN/Branch ACL、PAT、DNS/HTTP、静态 TCP/80 映射均 PASS |
| SLAAC / DHCPv6 / Static IPv6 / IPv6 route | G4 | NOT STARTED |
| Port Security / sticky MAC | G4 | NOT STARTED |
| IPv6-over-IPv4 Tunnel | G4 | NOT STARTED |
| Remote management | G4 | NOT STARTED |
