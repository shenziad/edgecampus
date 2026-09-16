# A — Network Owner 阶段报告（Gate 1）

| 项目 | 内容 |
|---|---|
| Owner | **A / Network** |
| 模块 | Packet Tracer 园区网络底座（数据平面） |
| 分支 | `feat/network` |
| 依据文档 | `docs/CURRENT_GATE.md` §2、`docs/ACCEPTANCE.md`、`docs/NETWORK_PLAN.md` |
| 配置记录 | `packet_tracer/CONFIG_LOG.md` |
| 证据目录 | `evidence/network/` |
| 截图命名依据 | `docs/ACCEPTANCE.md`：`G<Gate>-<序号>-<内容>-<结果>.png` |

---

## 1. 阶段目标

### 1.1 本阶段做什么

把 Gate 0 已冻结的网络规划，在 Packet Tracer 中实现为一个**可独立运行、可独立验收**的园区网络底座，具体包括：

1. VLAN 10 / 20 / 30 创建与命名；
2. Access 端口按冻结映射划入对应 VLAN；
3. 两条 Core–Access 链路配置 **LACP EtherChannel**，Port-Channel 配置 **Trunk 且仅放行 VLAN 10/20/30**；
4. SW-CORE 建立三个 **SVI** 并开启三层转发；
5. OFFICE 使用 **DHCP**，IOT / MANAGEMENT 核心节点使用冻结的**静态地址**；
6. 按冻结的放置原则部署 **ACL**（VLAN 10 inbound、VLAN 20 inbound）；
7. 完成 N1 / N2 / N3 网络独立验证并留存证据。

### 1.2 本阶段不做什么

- 不接入真实 Packet Tracer 遥测（属 Gate 2）；
- 不实现 `TEMP01 → SBC → FAN01` 本地自治与 IoT 控制（属 B / Edge）；
- 不做 Backend / Dashboard 相关工作（属 C / D）；
- 不新增烟雾、门禁、Guest VLAN、数据库、MQ、微服务等非核心功能；
- 不修改任何公共契约（VLAN/IP、设备 ID、协议字段、WS/API 路径、目录结构）。

### 1.3 验收标准

> **不依赖 B / C / D 的任何代码，A 单独打开正式 `.pkt` 即可完成本阶段全部网络验收。**

对应功能测试矩阵（`docs/ACCEPTANCE.md`）：

| ID | 测试 | 预期 |
|---|---|---|
| N1 | VLAN / 路由 | 跨允许域 ping / 访问**可达** |
| N2 | ACL 隔离 | OFFICE 直连 IOT **被拒绝** |
| N3 | 控制面访问 | OFFICE 访问逻辑管理服务**按设计允许** |

---

## 2. 实验与开发环境

| 项目 | 内容 |
|---|---|
| 仿真平台 | **Cisco Packet Tracer 9.0.1.0858** |
| 三层交换 | `SW-CORE` = **Cisco 3650-24PS** |
| 二层交换 | `SW-ACCESS` = **Cisco 2960-24TT** |
| 终端设备 | `OFFICE-PC`（PC-PT）、`ADMIN-PC`（PC-PT）、`BACKEND-STUB`（Server-PT）、`EDGE-SBC-01`（SBC-PT） |
| IoT 设备 | `TEMP01`（Temperature Sensor）、`FAN01`（Fan）——本阶段不接线（见第 12 节） |
| 配置方式 | Packet Tracer CLI（Cisco IOS 命令） |
| 编程语言 | 无（本模块不涉及代码） |
| 依赖 | 无 |
| Git 分支 | `feat/network` |
| 正式拓扑文件 | `packet_tracer/EdgeCampus.pkt`（canonical，A 唯一维护） |

### 2.1 地址与安全域规划（Gate 0 冻结值）

| 安全域 | VLAN | 网段 | 网关 | 策略定位 |
|---|---:|---|---|---|
| OFFICE | 10 | `192.168.10.0/24` | `192.168.10.1` | 可访问管理平台，不可直控 IoT |
| IOT | 20 | `192.168.20.0/24` | `192.168.20.1` | IoT 安全域，仅允许必要业务 |
| MANAGEMENT | 30 | `192.168.30.0/24` | `192.168.30.1` | 最高信任运维域 |

### 2.2 端口与链路映射（Gate 0 冻结值）

| 链路 / 端口 | 对端 | VLAN / 模式 |
|---|---|---|
| `SW-ACCESS Fa0/1` | OFFICE-PC | access VLAN 10 |
| `SW-ACCESS Fa0/2` | EDGE-SBC-01 | access VLAN 20 |
| `SW-ACCESS Fa0/3` | ADMIN-PC | access VLAN 30 |
| `SW-ACCESS Fa0/4` | BACKEND-STUB | access VLAN 30 |
| `SW-ACCESS Gi0/1 ↔ SW-CORE Gi1/0/1` | — | LACP trunk |
| `SW-ACCESS Gi0/2 ↔ SW-CORE Gi1/0/2` | — | LACP trunk |

### 2.3 终端地址

| 设备 | IP | 掩码 | 网关 | 方式 |
|---|---|---|---|---|
| OFFICE-PC | `192.168.10.10` | `255.255.255.0` | `192.168.10.1` | DHCP |
| EDGE-SBC-01 | `192.168.20.10` | `255.255.255.0` | `192.168.20.1` | 静态 |
| ADMIN-PC | `192.168.30.20` | `255.255.255.0` | `192.168.30.1` | 静态 |
| BACKEND-STUB | `192.168.30.10` | `255.255.255.0` | `192.168.30.1` | 静态 |

---

## 3. 架构与连接关系

本阶段实现的是「Packet Tracer 模拟园区数据平面」。整体连接关系如下：

```text
                    SW-CORE (3650-24PS)
                SVI10 .10.1 / SVI20 .20.1 / SVI30 .30.1
                    ip routing · DHCP · ACL(inbound)
                              |
                Gi1/0/1 ══════╪══════ Gi1/0/2
                (LACP EtherChannel → Port-channel1, Trunk, VLAN 10/20/30)
                              |
                    SW-ACCESS (2960-24TT)
                              |
        ┌──────────┬──────────┼──────────┐
      Fa0/1      Fa0/2      Fa0/3      Fa0/4
        |          |          |          |
   OFFICE-PC  EDGE-SBC-01  ADMIN-PC  BACKEND-STUB
   VLAN 10      VLAN 20     VLAN 30     VLAN 30
                  |
             (TEMP01 / FAN01 本阶段未接线)
```

### 3.1 两条路径的重要区分

| 路径 | 组成 | 性质 |
|---|---|---|
| **PT 模拟数据平面** | VLAN + SVI + ACL + Trunk + EtherChannel | 课程要求中的二层/三层组网与安全域隔离 |
| **Edge–Cloud 带外控制通道** | SBC `RealWSClient` → `ws://127.0.0.1:8000/ws/edge` | Packet Tracer External Network Access 提供的带外通道 |

> ⚠️ **本报告中 ACL 放行的 `192.168.30.10:8000` 是 Packet Tracer 内的「逻辑管理服务」节点**（对应 `BACKEND-STUB`）。
> 真实 FastAPI 控制平面运行在与 Packet Tracer 同一台物理主机上，属于**带外通道**，
> **不得描述为「真实 WebSocket 流量经过 VLAN 20/30」**。

---

## 4. 实现过程

以下按**真实操作顺序**记录，每一步包含：目标 / 思路 / 配置 / 关键解释 / 结果 / 截图点。

> **输出呈现说明**：为便于阅读，本节引用的命令输出做了必要的**摘录与排版整理**（省略了与结论无关的冗余行），**但所有数值、状态与字段均与原始输出完全一致**；完整原始输出见第 8 节对应截图。

### 4.1 SW-ACCESS：创建并命名 VLAN 10/20/30

**目标**：建立三个安全域的二层广播域。

**思路**：先在接入交换机创建 VLAN 并命名，为后续端口划分与 Trunk 放行提供依据。

**配置**：

```text
hostname SW-ACCESS
vlan 10
 name OFFICE
vlan 20
 name IOT
vlan 30
 name MANAGEMENT
```

**关键解释**：VLAN 名称必须与 `docs/NETWORK_PLAN.md` 冻结值一致，它是验收点之一，不是装饰。

**结果**：`show vlan brief` 中 VLAN 10 `OFFICE`、VLAN 20 `IOT`、VLAN 30 `MANAGEMENT` 均为 `active`，Ports 列为空（端口尚未划分，属正常）。

**截图点**：【G1-01】

---

### 4.2 SW-ACCESS：Access 端口划分

**目标**：把四个终端端口按冻结映射划入对应 VLAN。

**思路**：OFFICE 与 IOT / MANAGEMENT 分属不同安全域，必须从接入层就完成隔离的基础划分。

**配置**：

```text
interface fastEthernet 0/1
 switchport mode access
 switchport access vlan 10
interface fastEthernet 0/2
 switchport mode access
 switchport access vlan 20
interface fastEthernet 0/3
 switchport mode access
 switchport access vlan 30
interface fastEthernet 0/4
 switchport mode access
 switchport access vlan 30
```

**关键解释**：`Gig0/1`、`Gig0/2` 为上行链路端口，本步**刻意不做任何改动**，留待 4.3 配置 EtherChannel。

**结果**：`show vlan brief` 显示 `Fa0/1` 属 VLAN 10、`Fa0/2` 属 VLAN 20、`Fa0/3` 与 `Fa0/4` 属 VLAN 30；VLAN 1 中只剩 Fa0/5–Fa0/24 与 Gig0/1、Gig0/2。

**截图点**：【G1-03】

---

### 4.3 两台交换机：LACP EtherChannel + Trunk

**目标**：把两条并行的 Core–Access 链路聚合成一条逻辑链路，并只放行三个业务 VLAN。

**思路**：两条物理链路若各自独立，STP 会阻塞其中一条（带宽浪费）；用 LACP 聚合成 `Port-channel1` 后，STP 只看到一条逻辑链路，两条物理链路同时转发，同时获得链路冗余。

**配置（SW-ACCESS）**：

```text
interface range gigabitEthernet 0/1 - 2
 channel-group 1 mode active
interface port-channel 1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
```

**配置（SW-CORE）**：

```text
interface range gigabitEthernet 1/0/1 - 2
 channel-group 1 mode active
interface port-channel 1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
```

**关键解释**：

- `mode active` 表示**主动发起 LACP 协商**，两端都配 active 才能协商成功；
- **2960 只支持 dot1q 封装，不配置 `switchport trunk encapsulation dot1q`**（该命令在 2960 上不存在）；
- `switchport trunk allowed vlan 10,20,30` 是**替换**语义：配置后 Trunk 上只剩这三个 VLAN，未列出的（含 VLAN 1）一律不放行——这正是隔离要求。

**结果**：

```text
SW-CORE# show etherchannel summary
1      Po1(SU)           LACP   Gig1/0/1(P) Gig1/0/2(P)

SW-CORE# show interfaces trunk
Po1         on           802.1q         trunking      1
Vlans allowed on trunk:                  10,20,30
Vlans allowed and active in management:  10,20,30
Vlans in spanning tree forwarding state: 10,20,30
```

SW-ACCESS 侧对称：`Po1(SU)`，成员 `Gig0/1(P)`、`Gig0/2(P)`。

`Po1(SU)` 中 `S` 表示二层、`U` 表示 in use；成员口的 `(P)` 表示已加入 Port-channel。

**截图点**：【G1-04】（SW-CORE）、【G1-05】（SW-ACCESS）

---

### 4.4 SW-CORE：三个 SVI + 开启三层转发

**目标**：为三个 VLAN 提供网关，实现跨安全域的三层转发。

**思路**：3650 为三层交换机，用 SVI 承载各 VLAN 的网关地址，并启用 `ip routing`。

**配置**：

```text
ip routing

interface vlan 10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
interface vlan 20
 ip address 192.168.20.1 255.255.255.0
 no shutdown
interface vlan 30
 ip address 192.168.30.1 255.255.255.0
 no shutdown
```

**关键解释**：SVI 是**三层逻辑接口**，其启用状态依赖对应的二层 VLAN 存在；`no shutdown` 必须显式配置，否则接口可能保持 `administratively down`。

**结果**：

```text
SW-CORE# show ip interface brief
Vlan10                 192.168.10.1    YES manual up    up
Vlan20                 192.168.20.1    YES manual up    up
Vlan30                 192.168.30.1    YES manual up    up

SW-CORE# show ip route
C    192.168.10.0/24 is directly connected, Vlan10
L    192.168.10.1/32 is directly connected, Vlan10
C    192.168.20.0/24 is directly connected, Vlan20
L    192.168.20.1/32 is directly connected, Vlan20
C    192.168.30.0/24 is directly connected, Vlan30
L    192.168.30.1/32 is directly connected, Vlan30
```

**截图点**：【G1-06】

---

### 4.5 SW-CORE：OFFICE 的 DHCP 服务

**目标**：让 OFFICE 域终端自动获取地址，IOT / MANAGEMENT 保持静态。

**思路**：在 SW-CORE 上配置 DHCP 地址池，并排除网关及低地址段。

**配置**：

```text
ip dhcp excluded-address 192.168.10.1 192.168.10.9

ip dhcp pool OFFICE
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
```

**关键解释**：`excluded-address` 必须在地址池可用范围中排除网关 `.1`，否则可能出现网关地址被分配出去的风险。

**结果**：

```text
SW-CORE# show ip dhcp binding
192.168.10.10    00E0.F9B0.77EE     --    Automatic
```

OFFICE-PC 侧 `ipconfig`：

```text
IPv4 Address....................: 192.168.10.10
Subnet Mask.....................: 255.255.255.0
Default Gateway.................: 192.168.10.1
```

**截图点**：【G1-07】（PC `ipconfig` 与交换机绑定表同屏）

---

### 4.6 终端地址配置

**目标**：按冻结规划为终端配置地址与网关。

| 设备 | 配置方式 | 配置位置（Packet Tracer） |
|---|---|---|
| OFFICE-PC | DHCP | Desktop → IP Configuration → DHCP |
| ADMIN-PC | 静态 | Desktop → IP Configuration → Static |
| BACKEND-STUB | 静态 | Config → FastEthernet0（IP/掩码）+ Config → Settings → Gateway/DNS（网关） |
| EDGE-SBC-01 | 静态 | Config → FastEthernet0（IP/掩码）+ Config → Settings → Gateway/DNS（网关） |

**关键解释**：Packet Tracer 中 **PC-PT 的网关与 IP 在同一页面**，而 **Server-PT / SBC-PT 的网关不在接口页，而在 `Config → GLOBAL → Settings` 的 `Gateway/DNS` 字段**（详见 6.4）。

---

### 4.7 SW-CORE：ACL 部署

**目标**：让安全域隔离策略真实生效，而非仅作为配置展示。

**思路**：按 Gate 0 冻结的放置原则——**按源安全域在进入三层核心时即进行策略判定**，即 ACL 挂在 SVI 的 **inbound** 方向。

**配置**：

```text
ip access-list extended OFFICE-IN
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.30.10 eq 8000
 permit icmp 192.168.10.0 0.0.0.255 192.168.30.0 0.0.0.255
 deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255
 permit ip any any

ip access-list extended IOT-IN
 permit tcp 192.168.20.0 0.0.0.255 host 192.168.30.10 eq 8000
 permit icmp 192.168.20.0 0.0.0.255 192.168.30.0 0.0.0.255
 deny ip 192.168.20.0 0.0.0.255 192.168.10.0 0.0.0.255
 permit ip any any

interface vlan 10
 ip access-group OFFICE-IN in
interface vlan 20
 ip access-group IOT-IN in
```

**规则与冻结意图的对应关系**：

| ACL 行 | 冻结意图（`docs/NETWORK_PLAN.md`） |
|---|---|
| OFFICE-IN 第 1 条（TCP/8000 → 管理节点） | ① OFFICE → 管理平台 TCP/8000：允许 |
| IOT-IN 第 1 条（TCP/8000 → 管理节点） | ③ IOT → MANAGEMENT 必要管理服务：允许 |
| OFFICE-IN 第 3 条（deny → IOT 网段） | ② OFFICE → IOT 全网段：拒绝 |
| IOT-IN 第 3 条（deny → OFFICE 网段） | ④ IOT → OFFICE：拒绝 |
| 两条 ACL 的第 4 条 `permit ip any any` | ⑥ 其余流量按需放行（显式保留） |
| VLAN 30 不配置 ACL | ⑤ MANAGEMENT → OFFICE/IOT：允许（最高信任运维域） |

**关键解释**：

- **ACL 自上而下逐条匹配，命中即执行**，因此 `deny` 必须排在兜底的 `permit ip any any` **之前**；
- 扩展 ACL 末尾隐含 `deny any`，本方案显式写出 `permit ip any any` 以保留"其余放行"的语义；
- ACL 挂在 **SVI inbound**，因此只对**进入该安全域的流量**生效，不影响 VLAN 30 自己发出的流量（规则⑤自然满足）。

**结果（挂载确认与命中计数）**：

```text
SW-CORE# show running-config
interface Vlan10
 ip address 192.168.10.1 255.255.255.0
 ip access-group OFFICE-IN in
interface Vlan20
 ip address 192.168.20.1 255.255.255.0
 ip access-group IOT-IN in

SW-CORE# show access-lists
Extended IP access list OFFICE-IN
    10 permit tcp 192.168.10.0 0.0.0.255 host 192.168.30.10 eq 8000
    20 permit icmp 192.168.10.0 0.0.0.255 192.168.30.0 0.0.0.255
    30 deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 (8 match(es))
    40 permit ip any any
Extended IP access list IOT-IN
    ...（同上结构）
```

**截图点**：【G1-08】（running-config 中的挂载证据）、【G1-10】（deny 命中计数）

---

## 5. 关键配置解释（要点归纳）

1. **LACP `mode active`**：主动发起 LACP 协商；两端同为 active 才能建立聚合。聚合后 STP 将两条物理链路视为一条逻辑链路，消除阻塞、提升带宽并获得冗余。
2. **2960 不配置 `switchport trunk encapsulation dot1q`**：该平台仅支持 dot1q 封装，命令不存在；3650 则需要显式指定封装类型。
3. **`switchport trunk allowed vlan` 为替换语义**：配置后仅保留列出的 VLAN，这是"只放行 10/20/30"的实现方式，也是 OFFICE 无法通过 Trunk 到达其他 VLAN 的前提。
4. **ACL 挂 SVI inbound 而非物理口**：与"进入三层核心时即做策略判定"的冻结原则一致；物理端口为二层 switchport，本不承载三层 ACL。
5. **`permit ip any any` 的作用**：显式保留"其余流量按需放行"的语义，避免被扩展 ACL 末尾的隐含 deny 全部阻断。
6. **DHCP `excluded-address`**：排除网关地址，防止地址池把网关分配给终端。

---

## 6. 问题与排查过程

### 6.1 EtherChannel 配置后，SW-CORE 侧 Trunk 的 STP 转发态为 `none`

**现象**：EtherChannel 与 Trunk 配置完成、`Po1` 已 `trunking` 后，`show interfaces trunk` 最后一段显示：

```text
Port        Vlans in spanning tree forwarding state and not pruned
Po1         none
```

而 SW-ACCESS 侧同一命令已显示 `10,20,30`。

**初步判断**：怀疑 EtherChannel 或 Trunk 配置有误（例如协商未成功、或某条成员链路异常）。

**排查步骤**：

1. `show etherchannel summary` → `Po1(SU)`、成员 `Gig1/0/1(P) Gig1/0/2(P)`，聚合本身正常；
2. `show interfaces trunk` → `Status = trunking`、`Vlans allowed = 10,20,30`、`active = 10,20,30`，Trunk 属性正常；
3. 等待约 30–60 秒后重新执行 `show interfaces trunk`。

**根因**：EtherChannel 刚建立时，生成树处于**侦听 / 学习**阶段，尚未进入转发态，因此该字段暂不列出任何 VLAN。这是 STP 收敛的正常过程，**并非配置错误**。

**修复**：无需修复，等待收敛。

**验证**：重新执行后显示：

```text
Port        Vlans in spanning tree forwarding state and not pruned
Po1         10,20,30
```

**结论**：该现象属收敛期表现，配置正确。此经验已记入 `CONFIG_LOG.md`。

---

### 6.2 `show ip interface vlan 10/20` 显示 `Inbound access list is not set`

**现象**：ACL 已创建并挂载后，执行：

```text
SW-CORE# show ip interface vlan 10
  Inbound  access list is not set     ← 与预期"OFFICE-IN"不符
```

**初步判断**：怀疑 `ip access-group` 命令未生效（可能被漏敲或未保存）。

**排查步骤**：

1. 在接口配置模式下重新执行 `ip access-group OFFICE-IN in`，随后再次查看 `show ip interface vlan 10`，**结果仍显示 `not set`**；
2. 使用 `show running-config` 查看接口段落的**实际落盘配置**；
3. 结合后续 N2 测试的实际拦截效果交叉验证。

**根因**：`show running-config` 中明确存在：

```text
interface Vlan10
 ip access-group OFFICE-IN in
interface Vlan20
 ip access-group IOT-IN in
```

说明**配置确实已挂载并保存**。问题在于 **Packet Tracer 对 SVI 接口的 ACL 显示不刷新**：`show ip interface <SVI>` 会固定显示 `not set`，即使 ACL 已配置。这是仿真平台的显示缺陷，而非配置缺陷。

**修复**：无需修复配置；调整**证据取材方式**——以 `show running-config` 作为"ACL 已挂载"的权威证据，不再使用 `show ip interface`。

**验证**：由 6.3 的 N2 命中计数证明 ACL 实际生效。

**结论**：在 Packet Tracer 中判断 SVI 上的 ACL，应以 `show running-config` 与实际流量行为为准。

---

### 6.3 N2 结果为 `Destination host unreachable`，是否代表 ACL 已生效

**现象**：OFFICE-PC 执行 `ping 192.168.20.10`（IOT 域设备）返回：

```text
Reply from 192.168.10.1: Destination host unreachable.   （4 次，100% loss）
```

**初步判断**：两种可能——

- (a) 包被 ACL 拦截丢弃；但 ACL 静默丢弃通常表现为 `Request timed out`；
- (b) 目标设备未响应 ARP（地址未配置 / 接口未启用），即**并非 ACL 的功劳**。

**排查步骤**：

1. 确认 IOT 域终端 `EDGE-SBC-01` 的 IP 与端口状态（配置正常）；
2. 执行 `show access-lists`，检查 ACL 各条的**命中计数**；
3. 将命中次数与发送的 ping 包数量比对。

**根因**：ACL 计数显示 deny 规则**命中 8 次**，与两次测试共发送的 8 个 ICMP 请求**一一对应**，说明这些包确实在 SVI 10 的入方向被 deny 规则匹配并丢弃。`Destination host unreachable` 是 Packet Tracer 对被 SVI ACL 丢弃流量的一种呈现方式。

**修复**：无需修复。

**验证**：

```text
SW-CORE# show access-lists
Extended IP access list OFFICE-IN
    30 deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 (8 match(es))
```

**结论**：**应以 ACL 命中计数而非 ping 的提示文字来判断策略是否生效**。N2 隔离确认成立。

---

### 6.4 Packet Tracer 中 Server-PT / SBC-PT 找不到"网关"输入框

**现象**：配置终端静态地址时，PC-PT 的 IP 配置页可同时填写 IP、掩码、网关；而 Server-PT（BACKEND-STUB）与 SBC-PT（EDGE-SBC-01）的接口页**只有 IP 与掩码，没有网关字段**。

**排查步骤**：

1. 在设备 `Config` 标签下逐项展开；
2. 对比 PC-PT 与 Server-PT 的配置项结构。

**根因**：Packet Tracer 中不同设备类型的网关配置位置不同——PC-PT 的网关与 IP 同页（Desktop → IP Configuration）；而 Server-PT / SBC-PT 的网关位于 **`Config → GLOBAL → Settings → Gateway/DNS`**，接口页（`Config → FastEthernet0`）仅配置 IP 与掩码。

**解决**：在 `Settings → Gateway/DNS` 中分别填写 `192.168.30.1`（BACKEND-STUB）与 `192.168.20.1`（EDGE-SBC-01）。

**验证**：管理域两个节点后续均可被正常 ping 通（见第 7 节 N1 / N3）。

---

### 6.5 首次 ping 出现 25% 丢包（首包超时）

**现象**：`ping 192.168.30.20`、`ping 192.168.30.10` 的统计均为 `Sent=4, Received=3, Lost=1 (25% loss)`，第 1 个包为 `Request timed out`。

**根因**：首次通信需要先完成 **ARP 解析**，第 1 个 ICMP 报文在 ARP 完成前即超时；后续报文全部正常。

**结论**：**非故障**。判断连通性时应关注"是否收到回包"，而非单看 25% 的丢包率。

---

## 7. 验收结果

### 7.1 功能测试矩阵

| ID / 验收项 | 操作 | 预期 | 结果 | 证据 |
|---|---|---|---|---|
| VLAN 创建与命名（SW-ACCESS） | `show vlan brief` | 10/20/30 均 active 且命名正确 | **PASS** | G1-01 |
| VLAN 创建与命名（SW-CORE） | `show vlan brief` | 同上 | **PASS** | G1-02 |
| Access 端口划分 | `show vlan brief` | Fa0/1→10、Fa0/2→20、Fa0/3,4→30 | **PASS** | G1-03 |
| EtherChannel（LACP） | `show etherchannel summary` | `Po1(SU)`，成员均 `(P)` | **PASS** | G1-04 / G1-05 |
| Trunk 只放行三个 VLAN | `show interfaces trunk` | allowed / active / forwarding 均为 10,20,30 | **PASS** | G1-04 / G1-05 |
| SVI + 三层路由 | `show ip interface brief`、`show ip route` | 三个 SVI up/up，三条直连路由 | **PASS** | G1-06 |
| DHCP | `show ip dhcp binding` + PC `ipconfig` | PC 获取 `192.168.10.10`，网关 `.1` | **PASS** | G1-07 |
| ACL 挂载 | `show running-config` | Vlan10/20 入方向分别挂 OFFICE-IN / IOT-IN | **PASS** | G1-08 |
| **N1** 跨允许域可达 | OFFICE-PC `ping 192.168.30.20` | 可达 | **PASS**（4/4） | G1-09 |
| **N2** OFFICE → IOT 隔离 | OFFICE-PC `ping 192.168.20.10` | 被拒绝 | **PASS**（deny 命中 8 次） | G1-10 |
| **N3** 控制面访问 | OFFICE-PC `ping 192.168.30.10` | 按设计允许 | **PASS**（3/4，首包 ARP 超时） | G1-11 |
| IOT → Backend:8000 | 由 IOT 域发起 TCP:8000 流量 | 允许 | **待验证**（见第 12 节） | — |

### 7.2 关键实测输出摘录

```text
# N1（OFFICE → ADMIN，跨允许域）
Reply from 192.168.30.20: bytes=32 time<1ms TTL=127   ×4
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)

# N2（OFFICE → IOT，被隔离）
Reply from 192.168.10.1: Destination host unreachable.  ×4
Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)
→ ACL OFFICE-IN 第 30 条 deny 命中

# N3（OFFICE → 逻辑管理节点）
Request timed out.
Reply from 192.168.30.10: bytes=32 time=6ms TTL=127   ×3
Packets: Sent = 4, Received = 3, Lost = 1 (25% loss)  ← 首包 ARP 超时
```

### 7.3 公共契约检查

| 检查项 | 结果 |
|---|---|
| VLAN 编号 / IP 网段 | **未修改**，与 Gate 0 冻结值一致 |
| 设备 ID（EDGE-SBC-01 / TEMP01 / FAN01） | **未修改** |
| 协议字段 / WS 路径 / Policy 格式 | **未涉及** |
| 目录结构 | **未修改** |

---

## 8. 截图索引

全部截图位于 `evidence/network/`，命名遵循 `docs/ACCEPTANCE.md`。

| 编号 | 文件 | 内容 | 证明什么 |
|---|---|---|---|
| G1-00 | `G1-00-topology-overview.png` | Packet Tracer 拓扑总览（六台设备 + 两条 Core–Access 链路） | 拓扑与 `docs/NETWORK_PLAN.md` 冻结规划一致 |
| G1-00b | `G1-00b-pt-version.png` | Packet Tracer `About` 版本信息 | 实验环境版本为 **9.0.1.0858** |
| G1-01 | `G1-01-swaccess-vlan-brief-pass.png` | SW-ACCESS `show vlan brief` | VLAN 10/20/30 已在接入层创建并命名 |
| G1-02 | `G1-02-swcore-vlan-brief-pass.png` | SW-CORE `show vlan brief` | VLAN 10/20/30 已在核心层创建并命名 |
| G1-03 | `G1-03-swaccess-access-ports-pass.png` | SW-ACCESS `show vlan brief`（划端口后） | Fa0/1→VLAN10、Fa0/2→VLAN20、Fa0/3,4→VLAN30 已按冻结映射落地 |
| G1-04 | `G1-04-swcore-trunk-etherchannel-pass.png` | SW-CORE `show etherchannel summary` + `show interfaces trunk` | 核心侧 LACP 聚合成功（`Po1(SU)`），Trunk 仅放行 10/20/30 且已进入转发态 |
| G1-05 | `G1-05-swaccess-trunk-etherchannel-pass.png` | SW-ACCESS 同两条命令 | 接入侧聚合与 Trunk 同样正确，两端一致 |
| G1-06 | `G1-06-swcore-svi-routing-pass.png` | SW-CORE `show ip interface brief` + `show ip route` | 三个 SVI 均 up/up，三条直连路由存在，三层转发就绪 |
| G1-07 | `G1-07-dhcp-pass.png` | OFFICE-PC `ipconfig` + SW-CORE `show ip dhcp binding` | DHCP 真实生效：PC 获得 `192.168.10.10` 与网关 `192.168.10.1` |
| G1-08 | `G1-08-swcore-acl-config.png` | `show running-config` 中 `interface Vlan10/20` 段落 | 两条 ACL 已挂载到对应 SVI 的 **inbound** 方向 |
| G1-09 | `G1-09-n1-crossvlan-ping-pass.png` | OFFICE-PC ping 结果（同屏含 IOT 被拒与管理域可达） | **N1 通过**（`.30.20` 4/4 通）；同屏可见 N2 的拒绝，形成对照 |
| G1-10 | `G1-10-n2-office-to-iot-deny.png` | SW-CORE `show access-lists` | **N2 通过**：deny 规则命中 8 次，隔离策略真实拦截流量 |
| G1-11 | `G1-11-n3-mgmt-access-pass.png` | OFFICE-PC ping `192.168.30.10` | **N3 通过**：控制面访问按设计放行 |

**"一图多证据"说明**：G1-07（PC 侧 + 交换机侧同屏）、G1-09（拒绝与放行同屏对照）、G1-10（规则定义与命中计数同屏）均属此类。

---

## 9. 本阶段交付物

| 交付物 | 位置 | 说明 |
|---|---|---|
| 正式拓扑文件 | `packet_tracer/EdgeCampus.pkt` | canonical `.pkt`，A 唯一维护 |
| 配置与验证日志 | `packet_tracer/CONFIG_LOG.md` | 环境信息、端口映射、各设备配置与验证结果、功能验证表 |
| 验收证据 | `evidence/network/G1-00 ~ G1-11`（13 张） | 每张均有明确证明目的（见第 8 节） |
| 集成看板更新 | `docs/PROJECT_BOARD.md` | A 能力行状态更新 + 新增 Integration Check 记录 |
| 本阶段报告 | `docs/gate1/A_NETWORK_REPORT.md` | 本文档 |

> 本模块不产出代码（纯网络配置），故交付物以拓扑文件、配置日志与证据为主。

---

## 10. 创新性支撑

> **归属说明**：本模块对应的创新点为「**网络策略强制控制路径**」。该创新点属**全组共有**，已在 `docs/DEMO_SCRIPT.md`（0:40–1:30 段落）与 `docs/REPORT_OUTLINE.md`（§10 创新性分析第一条）中冻结表述。**A 侧负责其实现与举证**；最终报告的创新性章节应由全组统一撰写，本节仅提供网络侧素材，避免与其他 Owner 的表述重复。

### 10.1 主张：把「谁能控制 IoT」的裁决从应用层下沉到网络层

OFFICE 域在不改变任何应用的前提下，被网络**强制性地**剥夺了直接操作 IoT 设备的能力。普通用户无法绕过控制平台直控设备，所有控制意图必须经由 `Dashboard → Backend → Edge → 设备` 的既定路径进入系统。

### 10.2 实现机制：策略作用于最靠近源的位置，一处定义、单点判定

| 设计选择 | 具体做法 | 带来的性质 |
|---|---|---|
| 判定位置 | ACL 挂在**源安全域的 SVI `inbound`**（进入三层核心即判定） | 一处定义、一处变更，便于审计 |
| 策略强度 | OFFICE → IOT **全网段拒绝** | 彻底堵死绕过平台的直控路径 |
| 放行通道 | OFFICE → 逻辑管理服务 **TCP/8000 放行** | 保留"经平台操作"的合法路径 |
| 信任域豁免 | VLAN 30 **不配置**限制性 ACL | 保持 MANAGEMENT 最高信任运维域 |

### 10.3 系统意义：网络强制路径是另外两个创新点成立的前提

若 OFFICE 能够直连 `FAN01`，则：

- **云端策略下发**可被绕过，策略形同虚设；
- **事件流审计**失效——控制动作不经平台，无法记录来源与责任；
- **断云仍按最后有效策略自治**失去意义——因为本地策略不再是唯一控制入口。

因此本模块的 ACL 不只是"安全域隔离"，它是整套控制系统**可信性的底座**：先由网络保证"只能走平台"，云端策略编排与边缘自治才有意义。

### 10.4 证据形态：成对证据优于单点隔离

| 证据 | 内容 | 单独看能证明什么 |
|---|---|---|
| **N2** | OFFICE → IOT **被拒绝**（ACL deny 命中 8 次，G1-10） | 只能证明"隔离" |
| **N3** | OFFICE → 逻辑管理服务 **被允许**（G1-11） | 只能证明"平台可达" |
| **N2 + N3 并存** | 禁止的路径被堵死 **且** 允许的路径畅通 | **证明"强制走平台"成立**——本创新点的直接证据 |

### 10.5 表述严谨性：区分数据平面与带外控制通道

本模块明确区分两条路径（见 3.1）：

- **PT 模拟数据平面**：VLAN / SVI / ACL / Trunk / EtherChannel —— ACL 策略作用于此；
- **Edge–Cloud 带外控制通道**：`RealWSClient → ws://127.0.0.1:8000/ws/edge` —— 由 Packet Tracer External Network Access 提供的带外通道。

报告与答辩中**不得**表述为"真实 WebSocket 流量经过 VLAN 20/30"。这种表述上的严格区分，本身也是设计成熟度的组成部分。

### 10.6 在最终报告与现场演示中的位置

| 用途 | 位置 | A 提供的素材 |
|---|---|---|
| 创新性分析 | `docs/REPORT_OUTLINE.md` §10 第一条 | 本节 10.1–10.5 |
| 功能测试 | `docs/REPORT_OUTLINE.md` §9 | 第 7 节验收表 + 第 8 节截图索引 |
| 现场演示 | `docs/DEMO_SCRIPT.md` **0:40–1:30 网络隔离** | G1-01 / G1-04 / G1-05 / G1-08 / G1-10 与 N1 / N2 / N3 实测结果 |

---

## 11. 分工与 AI 协作记录

### 11.1 本人角色与边界

| 项目 | 内容 |
|---|---|
| Owner | **A / Network** |
| 本阶段可修改范围 | `packet_tracer/`（含 canonical `EdgeCampus.pkt`、`CONFIG_LOG.md`）、网络证据 `evidence/network/`、本报告 |
| 明确不修改 | `backend/`（C）、`edge/`（B）、`dashboard/` 与 `tests/`（D） |
| 排他约定 | A 为 canonical `.pkt` 唯一 Owner，其他 Owner 不得并行覆盖该文件 |

### 11.2 本阶段承担明细

VLAN 创建与命名 → Access 端口划分 → LACP EtherChannel + Trunk → 三个 SVI + `ip routing` → OFFICE DHCP → 终端静态地址 → ACL 部署 → N1 / N2 / N3 验证 → 证据采集 → `CONFIG_LOG.md` / `PROJECT_BOARD.md` / 本报告。

### 11.3 与各 Owner 的接口

| 对象 | 接口内容 |
|---|---|
| **B / Edge** | A 提供 VLAN 20 接入与 `EDGE-SBC-01 = 192.168.20.10` 及网关；B 在其上实现 `TEMP01 → SBC → FAN01` 本地自治；Integration Check 时 B 已验证的接线 / API 方案并入 **A 维护的 canonical `.pkt`** |
| **C / Control Plane** | N3 中的"逻辑管理服务 TCP/8000"对应 C 的控制平面端口；**A 只负责网络放行，不实现服务本体** |
| **D / UI & Integration** | A 提供网络侧证据（VLAN / Trunk / EtherChannel / ACL），D 负责集成测试与证据归档 |
| **全组** | 公共契约（VLAN·IP / 设备 ID / 协议字段 / WS·API 路径 / 目录结构）本阶段**未被任何一方修改** |

### 11.4 协作机制与流程遵守

| 机制 | 本阶段执行情况 |
|---|---|
| Owner 边界（`docs/CONTRIBUTING.md`） | 严格遵守，未跨模块修改 |
| 分支约定 `A → feat/network` | 已遵守 |
| 达到 Gate 并有验证后才合 `main` | 本次仅推送 `feat/network`，**未合并 `main`** |
| 每位 Owner 独立验收 + Integration Check | 本模块已独立完成并留存证据；团队级 Integration Check 待 B / C / D 就绪后统一进行 |
| 公共契约变更须走 RFC | **未触发**（本阶段无契约变更） |
| 提交前静态检查（`compileall` / `unittest`） | 本模块未改动 Python 代码，**不适用** |

### 11.5 AI 协作记录

| 项目 | 内容 |
|---|---|
| AI 承担的角色 | 实验指导、调试记录员、截图证据管理员、阶段报告整理者（依据 `EdgeCampus_AI阶段记录与提交规范.md`） |
| **红线遵守** | 未修改设备 ID / VLAN·IP / 协议字段 / WS·API 路径 / Policy 格式 / 公共目录结构 |
| **AI 参与的真实排查** | ① EtherChannel 后 STP 转发态为 `none` 的收敛期误判；② `show ip interface` 显示 `not set` 的成因定位；③ N2 结果 `Destination host unreachable` 是否代表 ACL 生效的判定 |
| **AI 被纠正的记录** | AI 曾依据 `show ip interface vlan 10` 判定"ACL 未挂载"，后经 `show running-config` 与实际命中计数**纠正为"已挂载且生效"**（详见 6.2、6.3）。该过程如实保留，未做美化 |
| 由该次误判导出的结论 | 在 Packet Tracer 中判断 SVI 上的 ACL，应以 `show running-config` 与实际流量行为为准，而非 `show ip interface` |

### 11.6 真实性声明

- 本报告中的**全部命令与输出**均为实际执行所得，未编造未执行过的命令或未出现过的输出；
- 未验证项（`IOT → Backend:8000`）已明确标注 `待验证`，未以"理论应成功"替代实际结果；
- 归属于其他 Owner 范围的工作（B / C / D）已在报告中单独标注，未计入本模块成果。

---

## 12. 未完成项与后续工作

### 12.1 A 范围内尚未验证（待做）

| 项 | 状态 | 说明 |
|---|---|---|
| `IOT → Backend:8000` 允许 | **待验证** | 该 ACL 规则已配置并挂载于 IOT 域入方向（挂载证据见 G1-08），但其**实际流量效果尚未测试**——"从 IOT 域发起 TCP:8000 流量"需要 IOT 侧设备（EDGE-SBC-01）具备主动发包能力。该项与 B 侧 Edge 程序直接相关，计划在 **Gate 2 联调**时随真实 Telemetry 一并验证。 |

> **后续说明（团队结论，2026-09-15）**：该条目已按团队决策**不再作为 RealWSClient 的真实性证明**。真实 Edge–Cloud 通道已在 **Gate 0** 通过 External Network Access 实机验证；PT 内 `VLAN20 → BACKEND-STUB` 的网络测试**仅代表模拟数据平面**。详见 `packet_tracer/CONFIG_LOG.md` 中的对应说明。本条保留为 Gate 1 时点的真实状态记录，未做改写。

### 12.2 环境信息中待联调确认（涉及 B / C）

| 项 | 状态 | 说明 |
|---|---|---|
| 真实主机网络方式（PT External Network Access / `RealWSClient`） | **待联调确认** | 属 Edge–Cloud 带外通道，由 B / C 在真实主机侧确认后回填 `CONFIG_LOG.md` 环境信息。 |

### 12.3 其他 Owner 任务范围（非 A 职责）

| 项 | Owner | 说明 |
|---|---|---|
| `TEMP01` / `FAN01` 接线与 `TEMP01 → SBC → FAN01` 本地自治 | **B / Edge** | A 的拓扑中该两设备本阶段不接线，符合"先网络、后 IoT 控制"的既定顺序 |
| Backend / 协议校验 / 断线重连 | **C / Control Plane** | — |
| Dashboard / 集成测试 | **D / UI & Integration** | — |
| Gate 2 单向全链路（PT Telemetry → Dashboard） | 全组 | 等 Gate 1 四模块合流后开始 |
| Gate 3 双向策略闭环 / Gate 4 断云不断控 | 全组 | — |

### 12.4 Gate 1 Integration Check 时 A 的后续动作

1. 接收 B 在 PT 开发副本中验证通过的 `TEMP01` / `FAN01` 接线与 API 方案；
2. 由 A 将其并入 canonical `packet_tracer/EdgeCampus.pkt`（A 为该文件唯一 Owner）；
3. 复核公共契约未被任何一方擅自修改；
4. 更新 `docs/PROJECT_BOARD.md` 与证据目录。

---

## 13. Gate 1 状态小结

```text
Gate 状态：A（Network）侧 Gate 1 完成，可进入 Integration Check

已完成：
  - VLAN 10/20/30 创建与命名（两台交换机）
  - Access 端口按冻结映射划分
  - LACP EtherChannel + Trunk（仅放行 VLAN 10/20/30）
  - 三个 SVI + ip routing（三层转发就绪）
  - OFFICE DHCP（终端获取 192.168.10.10）
  - 终端静态地址（IOT / MANAGEMENT 核心节点）
  - ACL（VLAN 10 / VLAN 20 inbound），实测拦截生效
  - N1 / N2 / N3 三项网络独立验证全部通过
  - 13 张验收证据 + CONFIG_LOG + PROJECT_BOARD 同步

未完成：
  - IOT → Backend:8000 的流量级验证（待 Gate 2 与 B 侧联调）
  - CONFIG_LOG 环境信息中的"真实主机网络方式"回填（属 B/C）

证据：evidence/network/G1-00 ~ G1-11（13 张，见第 8 节截图索引）

阻塞项：无

建议是否提交 PR：建议提交（feat/network → main），
  由项目总指挥复核后合入；合入前不修改任何公共契约。
```

---

**报告结论**

A 侧 Gate 1 的网络底座已按 Gate 0 冻结规划完整实现并**独立验收通过**：二层（VLAN / Access / LACP EtherChannel / Trunk）、三层（SVI / 路由）、服务（DHCP）与安全策略（ACL 隔离）均已落地，N1 / N2 / N3 三项验收全部通过且有可复现证据。本阶段未修改任何公共契约，未跨越 Owner 边界。
