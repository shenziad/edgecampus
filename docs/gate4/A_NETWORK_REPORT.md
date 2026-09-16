# A — Network Owner 阶段报告（Gate 4）

| 项目 | 内容 |
|---|---|
| Owner | **A / Network** |
| 模块 | Final Architecture v2 — IPv6 Overlay + Access Security |
| 分支 | `feat/network` |
| 依据文档 | `docs/ACCEPTANCE.md` Gate 4（`## A：IPv6 Overlay + Access Security`）、`docs/NETWORK_PLAN.md` §9 / §11 / §13 第 8–12 步、`docs/ACCEPTANCE.md` 测试矩阵 **N12–N15** |
| 配置记录 | `packet_tracer/CONFIG_LOG.md`（「Gate 4」段） |
| 证据目录 | `evidence/network/` |
| 截图命名依据 | `docs/ACCEPTANCE.md`：`G<Gate>-<Owner>-<序号>-<内容>-<结果>.png` |

> **说明**：Gate 4 正式任务书已于 **2026-09-16 发布**（`docs/CURRENT_GATE.md` → `# Gate 4 — Failure Recovery + IPv6/Security`，状态 **RELEASED / IN PROGRESS**）。本报告与该任务书 **`## A — IPv6 Overlay + Access Security`** 的 7 条要求及其 **DoD** 逐条对照，见 **§7.4**。

> **分支基线说明**：任务书要求"各成员先 `fetch origin`，将 `origin/main` 合入自己的 feature 分支后再开发"。本阶段的实际顺序为**先完成 Gate 4 实施、后同步 `origin/main`**（同步动作在本报告提交前后合入本分支）；由于本阶段**未改动任何被他人修改的文件**（唯一共享文件 `docs/PROJECT_BOARD.md` 在合并时按主干版本重排），该顺序差异**不影响任何验收结论**，已如实记录于此。

---

## 1. 阶段目标

### 1.1 本阶段做什么

按 `NETWORK_PLAN.md` §13 的 **第 8–12 步** 推进，对应测试矩阵 **N12–N15**：

| 步 | 内容 | 验收 ID |
|---|---|---|
| 8 | **Central Administration**：HQ ADMIN → R-BRANCH / SW-BRANCH；普通 Office 被拒绝 | **N14** |
| 9 | **IPv6 Addressing**：HQ SLAAC、Branch DHCPv6、管理域静态 IPv6 | **N12** |
| 10 | **IPv6-over-IPv4 Tunnel + IPv6 静态路由**：BR-ADMIN → HQ MANAGEMENT | **N13** |
| 11 | **Port Security**：HQ Office sticky MAC + violation | **N15** |
| 12 | **Full Regression**：重验 Gate 1 网络与业务矩阵，确保扩展未破坏 Core | — |

### 1.2 本阶段不做什么

- **不做 OSPFv3**：`NETWORK_PLAN.md` §9.4 明确"不引入 OSPFv3"，跨站点 IPv6 一律用**静态路由**；
- **不改 ISP**：ISP 保持 **IPv4-only**（§9 总原则），IPv6 只在企业内部与跨站点管理平面；
- 不改动 HQ Gate 1 Core 与 Gate 2/3 已验证成果；
- 不新增任何设备（IPv6 与安全能力全部落在既有设备上）；
- 不做 Gate 5 的收尾工作（placeholder 清零、final `.pkt` 冻结、三轮彩排）。

### 1.3 验收标准

> **HQ OFFICE：SLAAC；BR-OFFICE：DHCPv6；管理域：Static IPv6；ISP 保持 IPv4-only；R-HQ ↔ R-BRANCH IPv6-over-IPv4 Tunnel；IPv6 静态路由：BR-ADMIN → HQ MANAGEMENT；HQ ADMIN → Branch devices 中央远程管理、普通 Office 被拒绝；SW-ACCESS Fa0/1 sticky MAC / Port Security；最终 ACL / 业务矩阵回归。**（`docs/ACCEPTANCE.md` Gate 4 A 列表）

---

## 2. 实验与开发环境

### 2.1 IPv6 地址规划（按 `NETWORK_PLAN.md` §9 冻结值）

| 区域 | Prefix | 分配方式 | 本阶段实测地址 |
|---|---|---|---|
| HQ OFFICE VLAN10 | `2001:db8:10::/64` | **SLAAC** | SVI10 = `2001:db8:10::1/64`；OFFICE-PC 自动获得 `2001:DB8:10:0:2E0:F9FF:FEB0:77EE` |
| HQ IOT VLAN20 | `2001:db8:20::/64` | 静态 / 按需 | **本阶段未启用**（规划为"按设备需要"，N12 三种模式已由 VLAN10/30/40/50 覆盖） |
| HQ MANAGEMENT VLAN30 | `2001:db8:30::/64` | **静态** | SVI30 = `2001:db8:30::1/64`；HQ-SERVICE `::10`；ADMIN-PC `::20` |
| HQ Transit | `2001:db8:100::/64` | 静态 | SW-CORE Gi1/0/24 `::1`；R-HQ G0/0 `::2` |
| BR-OFFICE VLAN40 | `2001:db8:40::/64` | **DHCPv6** | R-BRANCH G0/1.40 `::1`；BR-OFFICE-PC 由池分配 `2001:DB8:40:0:1990:FD7C:D148:C4A6` |
| BR-MGMT VLAN50 | `2001:db8:50::/64` | **静态** | R-BRANCH G0/1.50 `::1`；BR-ADMIN-PC `::70` |
| **Tunnel** | `2001:db8:ff::/64` | 静态 | R-HQ Tunnel0 `::1`；R-BRANCH Tunnel0 `::2` |

### 2.2 IPv6-over-IPv4 Tunnel 参数（§9.3）

| 设备 | Tunnel0 IPv6 | IPv4 source | IPv4 destination |
|---|---|---|---|
| R-HQ | `2001:db8:ff::1/64` | `203.0.113.1`（G0/1） | `198.51.100.2` |
| R-BRANCH | `2001:db8:ff::2/64` | `198.51.100.2`（G0/0） | `203.0.113.1` |

> 隧道能建立的**前提**是两端 IPv4 可达 —— 这来自 Gate 3 中 ISP 发布的 `203.0.113.0/30` 与 `198.51.100.0/30`（§6.2 的设计意图在此兑现）。

### 2.3 IPv6 静态路由（§9.4）

| 设备 | 路由 | 作用 |
|---|---|---|
| R-BRANCH | `ipv6 route 2001:db8:30::/64 2001:db8:ff::1` | 去 HQ 管理域 → 走隧道 |
| R-HQ | `ipv6 route 2001:db8:50::/64 2001:db8:ff::2` | 去 Branch 管理域 → 走隧道 |
| R-HQ | `ipv6 route 2001:db8:30::/64 2001:db8:100::1` | 去 HQ VLAN30 → 经 SW-CORE |
| SW-CORE | `ipv6 route 2001:db8:50::/64 2001:db8:100::2` | **回程路由** → 经 R-HQ 回 Branch |

### 2.4 中央远程管理与 Port Security 参数

| 项 | 值 |
|---|---|
| 管理来源 ACL | `MGMT-ALLOW` = `permit 192.168.30.20`（仅 HQ ADMIN） |
| VTY 限制 | `access-class MGMT-ALLOW in` + `transport input telnet` + `password cisco` / `login` |
| 被管理设备 | R-BRANCH（`172.16.40.65`）、SW-BRANCH（`172.16.40.66`） |
| Port Security 位置 | `SW-ACCESS Fa0/1`（OFFICE-PC） |
| Port Security 参数 | `maximum 1` + `mac-address sticky` + **`violation restrict`**（§11 推荐，便于展示 Violation Count 且不 err-disable 中断演示） |
| 合法 MAC（sticky） | `00E0.F9B0.77EE` |
| 测试用非法 MAC | `0000.1111.2222`（临时修改，测完已恢复） |

---

## 3. 架构与连接关系

### 3.1 IPv6 覆盖网络（Overlay）

```text
        HQ 内部（原生 IPv6）                    IPv4-only 世界                       Branch（原生 IPv6）
   ┌──────────────────────┐                                                   ┌──────────────────────┐
   │  2001:db8:10::/64    │  SLAAC                                            │  2001:db8:40::/64    │  DHCPv6
   │  2001:db8:30::/64    静态                            （ISP 只转发 IPv4） │  2001:db8:50::/64    静态
   └──────────┬───────────┘                                                   └──────────┬───────────┘
              │                                                                          │
          SW-CORE ──── 2001:db8:100::/64 ──── R-HQ ══════ Tunnel0 ══════ R-ISP ══════ Tunnel0 ══════ R-BRANCH
                                             2001:db8:ff::1                        2001:db8:ff::2
                                             （IPv6 封装进 IPv4 穿越 ISP）
```

**封装原理**：

```text
原始：  [ IPv6 包头 | 数据 ]
封装后：[ IPv4 外层头 | IPv6 包头 | 数据 ]    ← ISP 按 IPv4 正常转发
对端：  拆除外层 → [ IPv6 包头 | 数据 ]
```

### 3.2 管理平面与安全平面

| 平面 | 机制 | 本阶段内容 |
|---|---|---|
| 管理可达性（IPv4） | Telnet + **VTY ACL** | 仅 `192.168.30.20` 可管理 R-BRANCH / SW-BRANCH |
| 管理可达性（IPv6） | **IPv6 Overlay** + 静态路由 | BR-ADMIN-PC → `2001:db8:30::10` |
| 接入安全 | **Port Security / sticky MAC** | `SW-ACCESS Fa0/1`，maximum 1 + violation restrict |

### 3.3 真实性与边界（ADR-012）

| 路径 | 性质 |
|---|---|
| PT 模拟企业数据平面（VLAN / ACL / 路由 / NAT / **IPv6 / Tunnel / Port Security**） | 本 Gate 的配置对象 |
| Edge–Cloud 带外控制通道（`RealWSClient → ws://127.0.0.1:8000/ws/edge`） | **与 PT 网络无关** |

**禁止表述**：真实 FastAPI WebSocket 经过 R-HQ、R-ISP、BGP、NAT、PT VLAN 或 **IPv6 Tunnel**。
本 Gate 的 IPv6 Overlay 是**模拟企业网络内部的管理平面**，不承载真实控制流量。

---

## 4. 实现过程

严格按 `NETWORK_PLAN.md` §13 的层级顺序执行，**每层完成后立即验证并留证**。

> **输出呈现说明**：本节命令输出做了必要的摘录与排版整理（省略与结论无关的冗余行），**所有数值、状态与字段均与原始输出一致**；完整原始输出见 §8 截图索引。

### 4.1 第 8 层：Central Administration（N14）

**目标**：HQ ADMIN 可集中管理分部设备，普通 Office 被拒绝。

**配置（R-BRANCH 与 SW-BRANCH 各一份）**：

```text
ip access-list standard MGMT-ALLOW
 permit 192.168.30.20
exit

line vty 0 4
 access-class MGMT-ALLOW in
 transport input telnet
 password cisco
 login
exit
```

**关键解释**：

- **ACL 只列出允许来源**，其余由**隐含 deny** 兜底 —— 因此无需显式拒绝任何地址；
- `access-class` 必须配在 **`line vty`** 下（这是 VTY 的专用 ACL 挂载点，**不能**用 `ip access-group`）；
- SW-BRANCH 是 2960，其管理流量的回程依赖 `ip default-gateway 172.16.40.65`，由 R-BRANCH 转发。

**结果**：

| 测试 | 结果 |
|---|---|
| ADMIN-PC → `telnet 172.16.40.65` | `...Open` → 输密码 → 进入 **`R-BRANCH>`** ✅ |
| ADMIN-PC → `telnet 172.16.40.66` | 进入 **`SW-BRANCH>`** ✅ |
| **OFFICE-PC → `telnet 172.16.40.65`** | **`% Connection refused by remote host`** ✅ 拒绝 |
| 两台 `show access-lists` | `Standard IP access list MGMT-ALLOW` / `10 permit host 192.168.30.20` ✅ |
| 两台 `show running-config \| include access-class` | `access-class MGMT-ALLOW in` ✅ |

**截图**：【G4-A-01】【G4-A-01b】【G4-A-01c】

---

### 4.2 第 9 层：IPv6 地址（N12）

**目标**：同时展示 **SLAAC / DHCPv6 / 静态** 三种 IPv6 地址模式。

**配置**：

```text
! 三台路由器（SW-CORE / R-HQ / R-BRANCH）
ipv6 unicast-routing

! SW-CORE
interface gigabitEthernet 1/0/24  ipv6 address 2001:db8:100::1/64
interface vlan 10                 ipv6 address 2001:db8:10::1/64
interface vlan 30                 ipv6 address 2001:db8:30::1/64

! R-HQ
interface gigabitEthernet 0/0     ipv6 address 2001:db8:100::2/64

! R-BRANCH
interface gigabitEthernet 0/1.40  ipv6 address 2001:db8:40::1/64
interface gigabitEthernet 0/1.50  ipv6 address 2001:db8:50::1/64

! DHCPv6 服务端（BR-OFFICE VLAN40）
ipv6 dhcp pool BR-V6
 address prefix 2001:db8:40::/64
exit
interface gigabitEthernet 0/1.40
 ipv6 dhcp server BR-V6
 ipv6 nd managed-config-flag
exit
```

终端（GUI）：HQ-SERVICE `2001:db8:30::10/64`、ADMIN-PC `2001:db8:30::20/64`、BR-ADMIN-PC `2001:db8:50::70/64`（网关均为各自 `::1`）；OFFICE-PC 选 **Auto Config**、BR-OFFICE-PC 选 **DHCP**。

**关键解释**：

- `ipv6 unicast-routing` 是**前提**：没有它，路由器不会转发 IPv6，也不会发送 RA；
- **SLAAC** 依赖路由器接口的 RA（`ipv6 address .../64` 默认带 A 标志），PC 用 EUI-64 生成接口 ID；
- **DHCPv6 需要两步**：池（`ipv6 dhcp pool`）+ 接口启用（`ipv6 dhcp server`），**还必须有 `ipv6 nd managed-config-flag`** —— 否则 RA 会告诉主机"用 SLAAC"，主机**根本不会发起 DHCPv6 请求**（详见 §6.2）；
- **管理域用静态**：管理设备地址固定，便于远程管理与 ACL 引用。

**结果**：

| 模式 | 设备 | 实测 |
|---|---|---|
| **SLAAC** | OFFICE-PC | `2001:DB8:10:0:2E0:F9FF:FEB0:77EE`（EUI-64，源自 MAC `00E0.F9B0.77EE`）✅ |
| **DHCPv6** | BR-OFFICE-PC | `2001:DB8:40:0:1990:FD7C:D148:C4A6` ✅ |
| **DHCPv6 服务端绑定** | R-BRANCH | `show ipv6 dhcp binding`：`Client FE80::2E0:B0FF:FE02:9A86` / `IA NA` / **`Address 2001:DB8:40:0:1990:FD7C:D148:C4A6`** ✅ |
| **静态** | SW-CORE / R-HQ / R-BRANCH | `show ipv6 interface brief` 显示全部预期地址 up/up ✅ |
| **静态** | ADMIN-PC | `2001:DB8:30::20`，网关 `2001:DB8:30::1` ✅ |
| IPv6 连通性（HQ 内） | ADMIN-PC → HQ-SERVICE | `ping 2001:db8:30::10` **4/4 通** ✅ |
| IPv6 连通性（Transit） | SW-CORE → R-HQ | `ping 2001:db8:100::2` **4/5 通** ✅ |

> **DHCPv6 的决定性证据**：客户端地址与**服务端绑定记录完全一致**，且为**非 EUI-64** 形式（`...1990:FD7C:D148:C4A6`，而 EUI-64 应为 `...2E0:B0FF:FE02:9A86`）—— 证明地址确实来自 **地址池**，而非 SLAAC。

**截图**：【G4-A-03】【G4-A-03b】【G4-A-03c】【G4-A-03d】

---

### 4.3 第 10 层：IPv6-over-IPv4 Tunnel（N13）

**目标**：让被 IPv4-only ISP 隔开的 HQ 与 Branch 管理域能用 IPv6 互通。

**配置**：

```text
! R-HQ
interface tunnel 0
 tunnel source gigabitEthernet 0/1
 tunnel destination 198.51.100.2
 tunnel mode ipv6ip
 ipv6 address 2001:db8:ff::1/64

! R-BRANCH
interface tunnel 0
 tunnel source gigabitEthernet 0/0
 tunnel destination 203.0.113.1
 tunnel mode ipv6ip
 ipv6 address 2001:db8:ff::2/64

! 四条 IPv6 静态路由见 §2.3
```

**关键解释**：

- `tunnel source` 用**接口名**而非 IP（PT 不支持 IP 形式，且接口形式在源地址变化时自动跟随）；
- `tunnel mode ipv6ip` = IPv6-over-IPv4（PT 实测支持；另一选项为 `gre`）；
- **不引入 OSPFv3**：跨站点 IPv6 用 4 条静态路由，其中 **SW-CORE 的回程路由**最易遗漏。

**结果**：

| 检查项 | 实际 |
|---|---|
| R-HQ `show interfaces tunnel 0` | `up, line protocol is up`；`Tunnel source 203.0.113.1 (GigabitEthernet0/1), destination 198.51.100.2`；**`Tunnel protocol/transport IPv6/IP`** ✅ |
| R-BRANCH `show interfaces tunnel 0` | `up, line protocol is up`；source `198.51.100.2 (G0/0)` → dest `203.0.113.1`；`IPv6/IP` ✅ |
| R-HQ `ping 2001:db8:ff::2` | **5/5（100%）** ✅ |
| R-BRANCH `ping 2001:db8:ff::1` | **5/5（100%）** ✅ |
| **`BR-ADMIN-PC ping 2001:db8:30::10`** | **4/4（0% loss）**，TTL=125 ✅ ← **N13 核心验收** |

**截图**：【G4-A-04】【G4-A-04b】【G4-A-04c】【G4-A-04d】

---

### 4.4 第 11 层：Port Security（N15）

**目标**：HQ Office 接入端口绑定 MAC 并阻止非法终端。

**配置**：

```text
interface fastEthernet 0/1
 switchport mode access
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation restrict
exit
```

**关键解释**：

- **`restrict` 而非 `shutdown`**：§11 明确推荐 —— 非法流量被丢弃并计数，但端口**不 err-disable**，现场演示不会中断，还能展示 Violation Count；
- **`sticky`**：交换机自动把学到的 MAC 写入运行配置，无需手工输入 MAC；
- 首次配置时 `Total/Sticky MAC = 0` 属**正常**（PC 还没发流量，交换机尚未学到）。

**结果**：

| 阶段 | 实际 |
|---|---|
| 初始 | `Port Security: Enabled` / `Secure-up` / `Violation Mode: Restrict` / `Max MAC: 1` / **Violation Count: 0** ✅ |
| 正常终端业务不受影响 | OFFICE-PC → `192.168.30.20` **4/4 通** ✅ |
| 学到合法 MAC | `Total MAC: 1` / `Sticky MAC: 1` / `show port-security address` → `10  00E0.F9B0.77EE  SecureSticky  Fa0/1` ✅ |
| **替换为非法 MAC** `0000.1111.2222` | 触发系统日志 **`%PORT_SECURITY-2-PSECURE_VIOLATION`**；**Violation Count = 5**；`Last Source Address:Vlan = 0000.1111.2222:10`；ping **100% 丢包** ✅ |
| 合法 MAC 仍在表 | `SecureSticky  00E0.F9B0.77EE` 未被清除 ✅ |
| 恢复原 MAC | ping **恢复 4/4 通** ✅ |

**截图**：【G4-A-02】【G4-A-02b】【G4-A-02c】

---

### 4.5 第 12 层：Full Regression + 跨层问题修复

#### 4.5.1 全量回归（N1–N11）

| 检查 | 结果 |
|---|---|
| SW-CORE `show etherchannel summary` | `Po1(SU)` / `Gig1/0/1(P)` / `Gig1/0/2(P)` ✅ |
| SW-CORE `show vlan brief` | VLAN 10 / 20 / 30 active ✅ |
| SW-CORE `show access-lists` | `OFFICE-IN` / `IOT-IN` 规则完整 ✅ |
| SW-CORE `show ip interface brief` | Vlan10/20/30 = `.10.1/.20.1/.30.1`；Gi1/0/24 = `10.255.0.1` ✅ |
| SW-CORE `show ip dhcp binding` | `192.168.10.10 / 00E0.F9B0.77EE` ✅ |
| OSPF（两端） | 双向 **FULL** ✅ |
| `R-HQ show ip route ospf` | 三条 O 路由 ✅ |
| eBGP（三台） | 三会话 **Established**（PfxRcd = 4）✅ |
| R-HQ `show ip nat translations` | 公网映射 + PAT 会话正常 ✅ |
| 行为矩阵 | OFFICE→IOT 拒绝 / OFFICE→ADMIN 通 / ADMIN→IOT 通 / BR-OFFICE→IOT 拒绝 / OFFICE Telnet 被拒 / ADMIN Telnet 成功 / OFFICE→Internet 通 ✅ |

**截图**：【G4-A-05】【G4-A-05b】【G4-A-05c】【G4-A-05d】

#### 4.5.2 发现并修复：静态 NAT 误抓穿越流量（N7）

**现象**：全量回归中 **BR-OFFICE-PC 浏览器打不开 `http://192.168.30.10`**（N7），而同样的测试在 Gate 3 曾通过。

**定位过程**：

1. BR-OFFICE **ping `192.168.30.10` 通** → 排除路由问题（ICMP 不匹配 TCP:80 的静态条目）；
2. 检查 `R-HQ show ip nat translations`，发现异常会话：

```text
tcp  203.0.113.1:80   192.168.30.10:80   172.16.40.2:1036   172.16.40.2:0
                                                              ↑ 端口 0 = 坏会话
```

3. **对照实验**：临时移除静态映射后，BR-OFFICE 的页面**立刻恢复正常** → 因果坐实；
4. 确认 Packet Tracer 不支持给静态映射加过滤（`route-map` ❌ / `ip nat inside destination` ❌ / `type rotary` ❌）；
5. **端口敏感性实验**：把映射临时改为 `8080 → 8080` 后，BR-OFFICE 访问 **80 端口**恢复正常 → 证明 PT 的误匹配按 **(地址 + 端口)** 进行。

**根因**：**Packet Tracer 的静态 NAT 在反向查找时以 inside-local（地址 + 端口）为匹配键**，因此"**目的地 = 内网服务地址**"的**穿越流量**也会被纳入翻译。真实 IOS 以 inside-global 为键，不存在此问题。

**处置（遮蔽条目）**：在配置前部插入一条"**翻译成自身**"的条目，让穿越流量被它接走（无害），公网流量继续走真正的映射：

```text
ip nat inside source static tcp 192.168.30.10 80 192.168.30.10 80     ! 遮蔽：身份翻译，必须在前面
ip nat inside source static tcp 192.168.30.10 80 203.0.113.1 80       ! 真正的公网端口映射
```

**验证（两条需求同时成立）**：

| 测试 | 结果 |
|---|---|
| **N7** BR-OFFICE-PC `http://192.168.30.10` | **页面打开** ✅ |
| **N11** INTERNET-SERVER `http://203.0.113.1` | **页面打开** ✅ |
| 穿越流量的 NAT 会话 | `192.168.30.10:80 ↔ 192.168.30.10:80`（**身份翻译**）；对端 `172.16.40.2:1039 ↔ 172.16.40.2:1039`（**端口一致，无 0**）✅ |
| 设计偏离 | **零** —— 地址、端口、NAT 位置全部保持冻结值 ✅ |

**截图**：【G4-A-06】【G4-A-07】【G4-A-07b】

---

## 5. 关键配置解释（要点归纳）

1. **`ipv6 unicast-routing` 是 IPv6 的"总开关"**：没有它，三层设备既不转发 IPv6，也不发送 RA，SLAAC/DHCPv6 全部无从谈起。
2. **SLAAC 靠 RA，DHCPv6 靠"池 + 接口 + M 标志"**：三者缺一，客户端就会退回 SLAAC（§6.2 的教训）。
3. **`ipv6 nd managed-config-flag` 是状态化 DHCPv6 的信号**：它让 RA 携带 M=1，主机才会去请求地址。
4. **跨站点 IPv6 不引入 OSPFv3**（§9.4）：用 4 条静态路由实现，其中 **回程路由（SW-CORE → R-HQ）** 最易遗漏，是"去程通、回程不通"的典型陷阱。
5. **Tunnel 的 IPv4 可达性来自 Gate 3 的 ISP 前缀发布**：`203.0.113.0/30` 与 `198.51.100.0/30` 被 ISP 用 BGP 发布，才使隧道两端能互相到达 —— 这是分层设计的价值兑现。
6. **VTY ACL 只能用 `access-class`**：挂在 `line vty` 下，且 ACL 只需列出**允许**来源（隐含 deny 兜底）。
7. **Port Security 用 `restrict`**：兼顾"阻断 + 可观测（Violation Count）+ 演示不中断"。
8. **遮蔽条目的顺序即语义**：身份翻译条目必须排在真正的端口映射**之前**，否则公网流量会被它接走。"**配置顺序本身就是逻辑**"在本 Gate 再次得到验证。

---

## 6. 问题与排查过程

### 6.1 静态 NAT 误抓穿越流量，导致 N7 失效（本 Gate 最重要的发现）

见 §4.5.2。要点：

- **症状具有欺骗性**：ACL 放行、路由可达、服务正常、ping 通，**唯独 HTTP 打不开**；
- **唯一线索**：`show ip nat translations` 中 `Outside global` 的**端口为 0**；
- **性质**：Packet Tracer 静态 NAT 反向查找以 **inside-local** 为键，属**平台实现差异**；
- **教训**：**逐层回归必须覆盖完整验收矩阵**。Gate 3 第 3 层测过 N7，但第 4 层加静态映射后**没有回头重测**，问题被埋到 Gate 4 才由全量回归暴露；
- **处置结果**：遮蔽条目使 N7 与 N11 **同时成立**，且**零设计偏离**。

### 6.2 DHCPv6 服务端配好、客户端却拿不到地址（RA 缺 M 标志）

**现象**：`ipv6 dhcp pool` 与 `ipv6 dhcp server` 均已配置、接口也加入了 `FF02::1:2`（All-DHCP-Servers 组），但：

```text
R-BRANCH#show ipv6 dhcp binding
（空）
```

且 BR-OFFICE-PC 拿到的是 **EUI-64** 形式地址（SLAAC 特征）。

**排查**：查 `show ipv6 interface g0/1.40`，末行写着：

```text
  Hosts use stateless autoconfig for addresses.     ← 关键
```

**根因**：接口 RA **没有携带 M（Managed）标志**，等于告诉主机"地址自己 SLAAC 生成"，主机因此**从不发起 DHCPv6 请求**。

**修复**：

```text
interface gigabitEthernet 0/1.40
 ipv6 nd managed-config-flag
```

修复后 `show ipv6 dhcp binding` 立即出现绑定，客户端地址 `...1990:FD7C:D148:C4A6` 与绑定**完全一致**（非 EUI-64），确认来自地址池。

**说明**：按 `NETWORK_PLAN.md` §9.2 的要求 —— **先记录实测再调整命令，未删除 DHCPv6 验收项**。

### 6.3 `tunnel source <IP>` 报 `Invalid input`

**现象**：`tunnel source 203.0.113.1` → `% Invalid input detected`。

**根因**：PT 的隧道接口不认 IP 形式的 source（只认**接口名**）。

**修复**：改用接口形式 `tunnel source gigabitEthernet 0/1`（R-BRANCH 为 `0/0`）。

**附带优点**：接口形式在源地址变化时自动跟随，比硬编码 IP 更规范。

### 6.4 IPv6 静态路由用 `tunnel 0` 作下一跳被拒

**现象**：`ipv6 route 2001:db8:30::/64 tunnel 0` → `% Invalid input detected`。

**根因**：`tunnel 0` 是 **IPv4** 静态路由的下一跳写法；**IPv6 静态路由的下一跳必须写地址**（或接口名连写为 `Tunnel0`）。

**修复**：写对端隧道 IPv6 地址：

```text
R-BRANCH: ipv6 route 2001:db8:30::/64 2001:db8:ff::1
R-HQ:     ipv6 route 2001:db8:50::/64 2001:db8:ff::2
```

### 6.5 `show ipv6 route static` 被当成主机名解析

**现象**：

```text
SW-CORE#show ipv6 route static
Translating "static"...domain server (255.255.255.255)
% Invalid input detected
```

**根因**：PT 的 `show ipv6 route` 不接受 `static` 过滤关键字，于是把它当作**主机名**去解析（`Translating "static"...` 就是 IOS 在做名字解析）。

**修复**：改用 `show ipv6 route`（看 `S` 开头的行）或 `show running-config | include ipv6 route`。

### 6.6 配置模式层级导致的 `Invalid input`（复现一次）

在 `(config-dhcpv6)` 模式下敲 `tunnel mode ipv6ip` 报错 —— 与 Gate 3 的 `router bgp` @ `#` 是**同一类错误**：**先看提示符，再敲命令**。

---

## 7. 验收结果

### 7.1 Gate 4 A 侧验收（N12–N15）

| ID | 验收项 | 预期 | 实际 | 结果 | 证据 |
|---|---|---|---|---|---|
| **N12** | IPv6 modes | SLAAC / DHCPv6 / Static 正确 | 三种模式全部实测成立；DHCPv6 有服务端绑定佐证 | **PASS** | G4-A-03 / 03b / 03c / 03d |
| **N13** | IPv6 Tunnel | BR-ADMIN → HQ MANAGEMENT | 隧道两端 up/up、互 ping 5/5；BR-ADMIN → `2001:db8:30::10` **4/4** | **PASS** | G4-A-04 / 04b / 04c / 04d |
| **N14** | Remote Admin | HQ ADMIN 允许，普通 Office 拒绝 | 两台登录成功；OFFICE `Connection refused` | **PASS** | G4-A-01 / 01b / 01c |
| **N15** | Port Security | 非法 MAC violation / 阻断 | 系统日志触发 + Violation Count 5 + 100% 丢包 + 可恢复 | **PASS** | G4-A-02 / 02b / 02c |

### 7.2 全量回归（N1–N11）

| ID | 验收项 | 结果 | 证据 |
|---|---|---|---|
| N1 | HQ VLAN / SVI | PASS | G4-A-05b |
| N2 | HQ ACL OFFICE→IOT | PASS（拒绝） | G4-A-05d |
| N3 | EtherChannel | PASS（Po1 SU） | G4-A-05 |
| N4 | Branch VLSM / ROAS | PASS | G4-A-05c / 05d |
| N5 | OSPF | PASS（双向 FULL） | G4-A-05c |
| N6 | eBGP | PASS（三会话 Established） | G4-A-05c |
| N7 | Branch→HQ Business | PASS（修复后成立） | G4-A-07b |
| N8 | Branch Isolation | PASS（100% 丢包） | G4-A-05d |
| N9 | PAT | PASS（3/4 通 + NAT 会话） | G4-A-05c / 05d |
| N10 | DNS / HTTP | PASS（`www.edgecampus.net`） | G3-A-04c（未变） |
| N11 | Static Port Map | PASS（与 N7 同时成立） | G4-A-07b |

### 7.3 公共契约与冻结项检查

| 检查项 | 结果 |
|---|---|
| HQ VLAN10/20/30 与 IPv4 网段 | **未修改** |
| Gate 1 已验证 HQ 端口映射与 IoT 接线 | **未修改** |
| v2 冻结物理接口 | **未修改**（无新增链路/设备） |
| Branch VLAN40/50、WAN 前缀、Internet LAN、AS 号 | **未修改** |
| **IPv6 前缀（§9 冻结值）** | **逐条按冻结值实施** ✅ |
| **Tunnel 前缀 `2001:db8:ff::/64` 与端点地址** | **按冻结值实施** ✅ |
| **Static TCP/80 映射（地址与端口）** | **未修改**（遮蔽条目为**新增**条目，不改动原映射） ✅ |
| Protocol v1.0 / 设备 ID / WS 路径 | **未涉及** |
| `TEMP01 → MCU → SBC → FAN01` 接线 | **未改动** |
| **本 Gate 是否新增冻结项变更** | **无**（遮蔽条目属 R-HQ 内部 NAT 实现细节，不改变对外接口） |

### 7.4 与 Gate 4 正式任务书 / `NETWORK_PLAN.md` §13 的逐条对照

#### 7.4.1 与 `docs/CURRENT_GATE.md`（Gate 4 任务书，2026-09-16 发布）`## A — IPv6 Overlay + Access Security`

| # | 任务书要求 | 本报告对应 | 结果 |
|---|---|---|---|
| **1** | HQ OFFICE SLAAC、BR-OFFICE DHCPv6、管理域 Static IPv6；**实际核验 PT 9.0.1 支持及地址/参数，不擅自替换 DHCPv6 验收** | 4.2 / 7.1 N12 / 6.2 | ✅ 三种模式全部实测；DHCPv6 遇 RA 缺 M 标志，**先记录实测再补 `managed-config-flag`，未替换或删除该验收项** |
| **2** | ISP Underlay 继续 IPv4-only，**禁止原生 IPv6** | 4.2 / §2.1 | ✅ R-ISP 全程未配置任何 IPv6 |
| **3** | R-HQ ↔ R-BRANCH IPv6-over-IPv4 Tunnel；**验证 IPv4 endpoint 可达后再验证 Tunnel** | 4.3 / §2.2 | ✅ 先确认 `203.0.113.0/30` 与 `198.51.100.0/30` 的 IPv4 可达（Gate 3 eBGP 成果），再建 Tunnel |
| **4** | IPv6 静态路由，BR-ADMIN ↔ HQ MANAGEMENT 管理路径，**验证双向返回路由**；不新增 OSPFv3 | 4.3 / §2.3 | ✅ 四条静态路由（含 **SW-CORE 回程路由**）；未引入 OSPFv3 |
| **5** | HQ ADMIN 可管理 Branch 网络设备；普通 OFFICE 禁止；**先验证路由，再验证管理服务/VTY ACL，不把 G3 ping 可达当作正式远程管理 PASS** | 4.1 / 7.1 N14 | ✅ 以 **Telnet 登录 + VTY ACL 命中** 作为正式判据；Gate 3 的 ping 可达仅作前置 |
| **6** | `SW-ACCESS Fa0/1` sticky MAC / Port Security；验证正常终端、非法 MAC、**violation 计数**和恢复；**maximum 1 / restrict** | 4.4 / 7.1 N15 | ✅ 四项全部实测（正常终端 / 非法 MAC / 计数 5 / 恢复） |
| **7** | 全量回归 **N1–N11** + **N12–N15** | 4.5.1 / 7.2 | ✅ N1–N11 全部 PASS；N12–N15 全部 PASS |

**任务书 DoD 中 A 侧条目**：

| DoD 条目 | 结果 |
|---|---|
| A：N12–N15 PASS | ✅ |
| A：N1–N11 回归 PASS | ✅ |
| A：IPv4 基线无退化 | ✅（含 EtherChannel / Trunk / ACL / 路由 / NAT / PAT 全部回归通过） |
| A：canonical 拓扑与 Network report / CONFIG_LOG / network evidence 齐全 | ✅ |

#### 7.4.2 与 `NETWORK_PLAN.md` §13 第 8–12 步的对照

| 步 | 要求 | 本报告对应 | 结果 |
|---|---|---|---|
| **8** | Central Administration：HQ ADMIN → R-BRANCH / SW-BRANCH；普通 Office 管理被拒绝 | 4.1 / 7.1 N14 | ✅ |
| **9** | IPv6 Addressing：HQ SLAAC、Branch DHCPv6、管理域静态 IPv6 | 4.2 / 7.1 N12 | ✅ 三种模式全部实测 |
| **10** | IPv6-over-IPv4 Tunnel + IPv6 static routes：BR-ADMIN → HQ MANAGEMENT | 4.3 / 7.1 N13 | ✅ 不引入 OSPFv3 |
| **11** | Port Security：HQ Office sticky MAC + violation 验收 | 4.4 / 7.1 N15 | ✅ restrict 模式，计数可展示 |
| **12** | Full Regression：重验 Gate 1 网络与 Edge Local Loop，确保扩展未破坏 Core | 4.5.1 / 7.2 | ✅ 并额外发现并修复 N7 跨层冲突 |
| — | §13 总要求："**每完成一步就提交阶段报告、关键命令、结果和建议截图点。不要一次性配置完再排错**" | 全文 | ✅ 逐层实施、逐层验证、逐层留证 |

---

## 8. 截图索引

全部位于 `evidence/network/`，命名遵循 `docs/ACCEPTANCE.md`（Gate 4 共 **21 张**）。

| 编号 | 文件 | 内容 | 证明什么 |
|---|---|---|---|
| G4-A-01 | `G4-A-01-remote-admin-vty-acl-pass.png` | 两台 `show access-lists` + `access-class` | `MGMT-ALLOW` 已挂载到 VTY |
| G4-A-01b | `G4-A-01b-remote-admin-telnet-pass.png` | ADMIN-PC 登录 `172.16.40.65` / `.66` | N14 允许侧成立 |
| G4-A-01c | `G4-A-01c-remote-admin-office-deny.png` | OFFICE-PC Telnet 被拒 | N14 拒绝侧成立 |
| G4-A-02 | `G4-A-02-port-security-config-pass.png` | 配置命令 + `show port-security interface` | Port Security 生效、正常终端不受影响 |
| G4-A-02b | `G4-A-02b-port-security-violation-pass.png` | 非法 MAC 触发 violation（日志 + Count 5 + 丢包） | N15 核心 |
| G4-A-02c | `G4-A-02c-port-security-restore-pass.png` | 恢复原 MAC 后通信恢复 | 可恢复性 |
| G4-A-03 | `G4-A-03-ipv6-addressing-pass.png` | 三台 `show ipv6 interface brief` | IPv6 地址按规划就位 |
| G4-A-03b | `G4-A-03b-ipv6-hq-admin-static-pass.png` | SW-CORE IPv6 连通性 + ADMIN-PC 静态 IPv6 + ping HQ-SERVICE | 静态模式 + HQ 内 IPv6 可达 |
| G4-A-03c | `G4-A-03c-ipv6-slaac-client-pass.png` | OFFICE-PC / BR-OFFICE-PC `ipconfig` | **SLAAC 客户端**证据 |
| G4-A-03d | `G4-A-03d-ipv6-dhcpv6-pass.png` | R-BRANCH `show ipv6 dhcp binding` + BR-OFFICE-PC `ipconfig` | **DHCPv6 决定性证据**（地址完全一致） |
| G4-A-04 | `G4-A-04-ipv6-tunnel-rhq-pass.png` | R-HQ Tunnel0 状态 + IPv6 端点 + ping 对端 5/5 | 隧道建立 |
| G4-A-04b | `G4-A-04b-ipv6-tunnel-rbranch-pass.png` | R-BRANCH Tunnel0 状态 + ping 对端 5/5 | 隧道双向 |
| G4-A-04c | `G4-A-04c-ipv6-route-tables-pass.png` | 三台 IPv6 路由表 + 拓扑 | 四条静态路由就位 |
| G4-A-04d | `G4-A-04d-br-admin-to-hq-service-ipv6-pass.png` | **BR-ADMIN-PC → `2001:db8:30::10` 4/4** | **N13 核心验收** |
| G4-A-05 | `G4-A-05-full-regression-swcore-pass.png` | SW-CORE EtherChannel / VLAN / ACL | N1 / N2 / N3 回归 |
| G4-A-05b | `G4-A-05b-full-regression-swcore-l3-pass.png` | SW-CORE 三层接口 + DHCP 绑定 | N1 / N4 回归 |
| G4-A-05c | `G4-A-05c-full-regression-routing-pass.png` | OSPF / eBGP / NAT 表 | N5 / N6 / N9 回归 |
| G4-A-05d | `G4-A-05d-full-regression-behaviors-pass.png` | 三台 PC 的行为矩阵 | N2 / N8 / N9 / N14 回归 |
| G4-A-06 | `G4-A-06-n7-nat-conflict-evidence.png` | **NAT 坏会话（端口 0）** + 移除映射后页面恢复 | 问题定位证据 |
| G4-A-07 | `G4-A-07-n7-n11-coexist-fix-pass.png` | 遮蔽条目配置 + 两页面同时可用 | 修复方案 |
| G4-A-07b | `G4-A-07b-n7-n11-coexist-confirm-pass.png` | **最终配置下两页面刷新仍可用** + NAT 表端口正常 | 最终确认 |

**"一图多证据"示例**：`G4-A-03d`（服务端绑定 + 客户端地址同屏，构成 DHCPv6 闭环）、`G4-A-05c`（OSPF + 三台 BGP + NAT 同屏）、`G4-A-07b`（两条需求 + NAT 表同屏）。

---

## 9. 本阶段交付物

| 交付物 | 位置 | 说明 |
|---|---|---|
| 正式拓扑文件 | `packet_tracer/EdgeCampus.pkt` | 已包含 Gate 1–4 全部网络配置 |
| 配置与验证日志 | `packet_tracer/CONFIG_LOG.md` | 「Gate 4」段：第 8–12 层真实命令、验证结果、6 条问题记录 |
| 验收证据 | `evidence/network/G4-A-01 ~ G4-A-07b`（21 张） | 见 §8 |
| 集成看板更新 | `docs/PROJECT_BOARD.md` | A 侧 G4 四行 → **PASS G4**，新增 Gate 4 Track A Integration Check 与 Integration Check 记录，课程覆盖 G4 四项 → ✅ |
| Gate 3 报告补充说明 | `docs/gate3/A_NETWORK_REPORT.md` | §7.1 增加"后续说明"，交代 N7 的时序前提与 Gate 4 修复 |
| 本阶段报告 | `docs/gate4/A_NETWORK_REPORT.md` | 本文档 |

---

## 10. 创新性支撑

> **归属说明**：项目级核心创新（**双控制环**、**断云不断控**）属全组共有，其正式验收在 Gate 4 的 **B/C/D 轨道**。本 Gate 对创新的贡献在于**把管理平面与接入平面做成可隔离、可验证、可解释的安全体系**。

### 10.1 IPv6 Overlay：不改造 ISP，也能获得端到端 IPv6 管理平面

ISP 保持 **IPv4-only**（冻结原则），企业的跨站点 IPv6 管理平面通过 **IPv6-over-IPv4 隧道**构建：

```text
HQ 管理域 ── 原生 IPv6 ── R-HQ ══ 隧道（封装进 IPv4）══ R-BRANCH ── 原生 IPv6 ── Branch 管理域
```

**创新点**：**不要求运营商升级**即可获得端到端 IPv6 管理能力 —— 这是真实企业网在 IPv4/IPv6 过渡期的标准做法，本项目用**最少的静态配置**（1 条隧道 + 4 条路由）实现了它，且**没有引入 OSPFv3**，保持了配置的可审计性。

### 10.2 三种 IPv6 地址模式并存：一套网络覆盖全部课程要求

| 模式 | 落点 | 意义 |
|---|---|---|
| **SLAAC** | HQ OFFICE | 无状态自动配置，零运维 |
| **DHCPv6** | BR-OFFICE | 状态化集中管理，可控 |
| **静态** | HQ MANAGEMENT / BR-MGMT | 管理平面地址固定，便于 ACL 与远程管理 |

**创新点**：不是"演示三种命令"，而是**按区域的管理需求选择模式** —— 办公区求简、分部求控、管理域求稳。同一条网络上三种模式并存且互不干扰。

### 10.3 管理平面与接入平面双重收口

| 维度 | 机制 | 效果 |
|---|---|---|
| **谁能管理设备** | VTY ACL（仅 `192.168.30.20`） | 普通 Office 无法登录任何分部设备 |
| **谁能接入网络** | Port Security sticky MAC | 非法终端被阻断且**可计数** |

**创新点**：与 Gate 1/3 的"用网络设备定义权限"一脉相承 —— **管理权与接入权都在网络层强制**，而不是依赖应用层登录页。

### 10.4 "遮蔽条目"：把平台缺陷转化为可解释的工程解法

面对 Packet Tracer 的静态 NAT 实现缺陷，我们没有选择"绕过验收"或"伪造结果"，而是：

1. 用**对照实验**定位到具体 NAT 规则；
2. 用**端口敏感性实验**确认匹配键的构成；
3. 用"**翻译成自身**"的身份条目把穿越流量无害化；
4. **零设计偏离**地让两条冻结需求同时成立。

**创新点**：这体现的是一种工程方法论 —— **当平台与设计冲突时，先精确刻画平台行为，再寻找不牺牲设计语义的解法**，并把全过程留成可复现的证据链。

### 10.5 在最终报告与课程覆盖中的位置

| 用途 | 位置 | 素材 |
|---|---|---|
| 网络设计章节 | `docs/REPORT_OUTLINE.md` | §2–§5、§10 |
| 课程覆盖说明 | `docs/ACCEPTANCE.md` 五次实验覆盖核对 | **实验 1**（SLAAC / DHCPv6 / 静态 IPv6 / IPv6 route / 远程管理）、**实验 5**（Port Security / IPv6-over-IPv4 Tunnel） |
| 功能测试章节 | 最终功能测试矩阵 **N12–N15** | §7.1 |
| 现场演示 | `docs/DEMO_SCRIPT.md` | G4 证据链（登录分部设备 → 非法 MAC 触发 violation → IPv6 Overlay 访问 HQ-SERVICE） |

---

## 11. 分工与 AI 协作记录

### 11.1 本人角色与边界

| 项目 | 内容 |
|---|---|
| Owner | **A / Network** |
| 本阶段可修改范围 | `packet_tracer/`（canonical `.pkt`、`CONFIG_LOG.md`）、`evidence/network/`、本报告、Gate 3 报告的补充说明 |
| 明确不修改 | `backend/`（C）、`edge/`（B）、`dashboard/` 与 `tests/`（D） |
| 排他约定 | A 为 canonical `.pkt` 唯一 Owner |

### 11.2 本阶段承担明细

中央远程管理（VTY ACL）→ IPv6 三模式（SLAAC / DHCPv6 / 静态）→ IPv6-over-IPv4 隧道与 4 条静态路由 → Port Security → 全量回归 → **N7 跨层冲突的定位与修复** → 21 张证据 → `CONFIG_LOG.md` / `PROJECT_BOARD.md` / 本报告。

### 11.3 与各 Owner 的接口

| 对象 | 接口内容 |
|---|---|
| **B / Edge** | 本 Gate 未触及 Edge 侧；`TEMP01 → MCU → SBC → FAN01` 接线与 A+B 集成结果**未改动**。全量回归中已确认 Local Loop 未受网络扩展影响 |
| **C / Control Plane** | `HQ-SERVICE = 192.168.30.10`（IPv4）与 `2001:db8:30::10`（IPv6）均未改动；本 Gate 的遮蔽条目**不改变任何对外接口** |
| **D / UI & Integration** | A 提供 IPv6/安全侧证据；端到端联调由 B/C/D 主线负责 |
| **全组** | HQ Gate 1 Core、v2 冻结网络项、Protocol v1.0、设备 ID、WS 路径**均未修改**；**本 Gate 无冻结项变更、无待追认 RFC** |

### 11.4 协作机制与流程遵守

| 机制 | 本阶段执行情况 |
|---|---|
| Owner 边界（`docs/CONTRIBUTING.md`） | 严格遵守，未跨模块修改 |
| 分层实施规则（`NETWORK_PLAN.md` §13） | 严格执行第 8–12 步，逐层验证留证 |
| 冻结项（IPv6 前缀、隧道参数、映射地址端口） | **全部按冻结值实施，零偏离** |
| 公共契约变更须走 RFC | **未触发**（遮蔽条目为新增内部规则，不改变对外接口） |
| HQ Core 不得破坏 | 全量回归 N1–N11 全部 PASS，含 EtherChannel / Trunk / ACL / 路由 / NAT |
| canonical `.pkt` 所有权 | 全程由 A 维护 |

### 11.5 AI 协作记录

| 项目 | 内容 |
|---|---|
| AI 承担的角色 | 分层实施指导、调试记录员、截图证据管理员、阶段报告整理者 |
| **红线遵守** | 未修改 HQ VLAN/IP、Gate 1 端口映射、v2 冻结接口、IPv6 前缀、隧道参数、映射地址端口、Protocol 字段、设备 ID、WS 路径 |
| **AI 参与的真实排查** | ① N7 与静态映射的**跨层冲突**（对照实验 + 端口敏感性实验 + 遮蔽解法）；② DHCPv6 不生效的 **RA M 标志**判定；③ `tunnel source <IP>`、`ipv6 route ... tunnel 0`、`show ipv6 route static` 三处 PT 语法差异 |
| **AI 的判断被纠正** | AI 曾断言"Gate 3 报告里 N7 的 PASS 不成立"，**该表述过重**。经 Owner 指出后复核更正为："**证据真实、结论当时成立，缺的是时序说明**"；处理方式由"推翻"改为"**补充说明**" |
| **AI 的自我纠错（截图误读）** | AI 曾在缩小的宽截图上把 ADMIN-PC 的 `192.168.30.20` 误读为 `192.168.10.20`，并在同一批图中把 SW-CORE 的 `ipv6 route ... 2001:DB8:100::2` 误读为 `via ::, Tunnel0`。两次均在 Owner 追问下**重新核对并更正**，此后**凡涉及精确地址/路由值一律改由 Owner 提供文字** |
| **AI 明确拒绝的做法** | 全程未采用"跳过验收项""伪造截图""绕过失败测试"等做法；N7 失效时选择**如实记录 + 定位 + 修复**，而非删除或忽略 |
| **AI 的排查纪律** | 坚持"**先定位、后修改**"：NAT 冲突先做对照实验、DHCPv6 先记录实测再调整，未在根因未确认前改动冻结配置 |

### 11.6 真实性声明

- 本报告中的**全部命令与输出**均为实际执行所得，未编造；
- 每项结论均对应**可追溯的截图**（§8 索引，21 张）；
- 存在平台偏差的数值（如 `Violation Count`、ping 丢包率）**如实记录并注明以实际效果为准**；
- **本 Gate 中曾被误判或修正的内容已如实记录**（§11.5），未隐去；
- 未完成内容（B/C/D 的断云恢复、仪表板与真实 Policy/Command 闭环）**明确列出**，未以"理论可用"替代实测；
- **`docs/gate3/A_NETWORK_REPORT.md` 的 N7 结论未被改写**，仅在 §7.1 后补充时序说明，保持历史一致性。

---

## 12. 未完成项与后续工作

### 12.1 本 Gate 明确不做、留给 Gate 5 的部分

| 项 | 说明 |
|---|---|
| ~~`docs/CURRENT_GATE.md` 的 Gate 4 正式任务书~~ | ✅ **已解决**：Gate 4 任务书已于 **2026-09-16 发布**（RELEASED / IN PROGRESS）；本报告 **§7.4.1** 已与其 `## A — IPv6 Overlay + Access Security` 的 7 条要求及 DoD **逐条对照，全部吻合** |
| **同步 `origin/main` 到本分支** | 任务书要求开工前先合入 `origin/main`；本分支的同步动作在本报告提交时一并执行（唯一共享文件 `docs/PROJECT_BOARD.md` 按主干版本重排） |
| final canonical `.pkt` 冻结 | Gate 5 才正式冻结 |
| 三轮完整彩排 | Gate 5 |
| C 的 Gate 1 三项稳定性欠账清零 | Gate 5 前 |

### 12.2 其他 Owner 的 Gate 4 范围（非 A 职责）

| 项 | Owner | 说明 |
|---|---|---|
| **断云不断控**：停止 Backend 后 Edge 仍按最后有效 Policy 工作 | **B** | 温度跨迟滞阈值时 FAN 仍正确动作 |
| **恢复同步**：Edge 自动重连并发送 `hello` + `state_sync` | **B+C+D** | Dashboard 恢复真实 temperature / fan_state / Policy Version |
| Dashboard 显示失联状态 | **C+D** | `EDGE_OFFLINE` 语义 |
| Gate 3 遗留：真实 Policy / Command 闭环 | **B+C+D** | 若 Gate 3 未收口则顺延 |

### 12.3 待团队确认事项

| 事项 | 说明 |
|---|---|
| **canonical `.pkt` 版本归并** | `main` 上存在项目总指挥上传的 `.pkt`，**不含 Gate 3 / Gate 4 网络配置**；A 分支为含 Gate 1–4 的最新版本。`.pkt` 为二进制、无法自动合并，合并时应**以 A 的版本为准** |
| **Gate 4 正式任务书** | 见 §12.1；建议发布后由 A 回填对照 |
| ~~DHCP `dns-server` 增量 / 遮蔽条目是否需 RFC~~ | ✅ **已明确：无需 RFC** —— 两者均不改变对外接口与冻结项 |

### 12.4 后续网络层工作（A）

1. Gate 5 前完成 **final `.pkt` 冻结**与**全矩阵最终回归**（N1–N15 一次性跑通）；
2. 配合全组完成**三轮完整彩排**中的网络侧演示脚本（登录分部设备 → 非法 MAC 触发 violation → IPv6 Overlay 访问 HQ-SERVICE）；
3. 持续维护 canonical `.pkt`，并在每次变更后更新 `CONFIG_LOG.md` 与 `PROJECT_BOARD.md`；
4. 若 `CURRENT_GATE.md` 发布 Gate 4/5 正式任务书，按条目回填本报告。

---

## 13. Gate 4 状态小结

```text
Gate 状态：A（Network）侧 Gate 4 IPv6 Overlay + Access Security 完成

已完成：
  - 第 8 层 中央远程管理：HQ ADMIN → R-BRANCH / SW-BRANCH Telnet + VTY ACL；
    普通 OFFICE 被拒（N14 PASS）
  - 第 9 层 IPv6 三模式：SLAAC（HQ OFFICE）/ DHCPv6（BR-OFFICE，有服务端绑定佐证）/
    静态（HQ MANAGEMENT、BR-MGMT）（N12 PASS）
  - 第 10 层 IPv6-over-IPv4 Tunnel：隧道两端 up/up、互 ping 5/5；
    BR-ADMIN → HQ-SERVICE IPv6 4/4（N13 PASS）
  - 第 11 层 Port Security：sticky MAC + violation restrict；
    非法 MAC 触发 violation 且计数为 5（N15 PASS）
  - 第 12 层 全量回归：N1–N11 全部 PASS
  - 额外成果：定位并修复 N7 ↔ 静态映射的 PT NAT 跨层冲突（遮蔽条目，零设计偏离），
    使 N7 与 N11 同时成立
  - 21 张验收证据 + CONFIG_LOG + PROJECT_BOARD + Gate 3 报告补充说明

未完成（设计内，属 Gate 5 或其他 Owner）：
  - B/C/D 的断云不断控与恢复同步（Gate 4 软件轨道）
  - final .pkt 冻结、三轮彩排（Gate 5）
  - C 的 Gate 1 三项稳定性欠账（Gate 5 前）

证据：evidence/network/G4-A-01 ~ G4-A-07b（21 张，见第 8 节截图索引）

阻塞项：无

建议是否提交 PR：建议提交（feat/network → main），
  由项目总指挥复核后合入；.pkt 合并时采用 A 分支版本。
```

---

**报告结论**

A 侧 Gate 4 在**不引入 OSPFv3、不改动 ISP、不新增设备、不改动任何冻结项**的前提下，完成了：

- **管理平面**：HQ ADMIN 可集中管理分部设备（VTY ACL 收口），普通 Office 被拒绝；
- **IPv6 覆盖网络**：SLAAC / DHCPv6 / 静态三种模式并存，并通过 **IPv6-over-IPv4 隧道**跨越 IPv4-only 的 ISP，实现 BR-ADMIN → HQ-SERVICE 的 IPv6 可达；
- **接入安全**：`SW-ACCESS Fa0/1` sticky MAC + violation restrict，非法终端可阻断且可计数。

验收矩阵 **N12–N15 全部 PASS**，全量回归 **N1–N11 无退化**。过程中定位并修复了一个**跨层交互缺陷**（Packet Tracer 静态 NAT 误抓穿越流量），以**零设计偏离**的方式使 N7 与 N11 同时成立；同时对 AI 自身的两次误判与一次过度表述做了**如实记录与更正**。

本阶段严格按 §13 第 8–12 步分层实施，未越界实现 Gate 5 内容，未修改任何公共契约与冻结项。
