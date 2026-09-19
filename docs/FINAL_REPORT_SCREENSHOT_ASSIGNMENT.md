# 最终实验报告待截图操作清单（四人独立执行）

更新日期：2026-09-19。A、B、C、D各自在自己的电脑上运行完整项目。以下每个编号对应一张PNG，按各自章节从上到下操作。

截图可以按 A/B/C/D 并行完成；最终报告中的功能演示按 **园区管理 → 中心物联网控制 → Dashboard 面板控制** 排列。园区管理优先使用 A 类网络补图和现有 N 类证据，中心物联网使用 B 类，Dashboard 使用 C/D 类。详细演示顺序见 [最终功能演示设计](FINAL_FUNCTION_DEMO.md)。

图片保存到 `evidence/final_report/A/`、`B/`、`C/`、`D/`。每张整理好窗口后按 **Win+Shift+S → 矩形截取 → 点击截图通知 → Ctrl+S → 输入该行文件名**。

## 启动准备（每人做一次）

1. PowerShell进入自己的项目目录，打开 `packet_tracer/EdgeCampus.pkt`，另存为自己的工作副本。
2. PT保持Realtime；IO-MCU-01和EDGE-SBC-01的Programming程序保持Run。
3. PT Options→Preferences开启External Network Access和Network Controller REST API External Access。NC-HQ→Real World Access开启Access Enabled，HTTP Port设58000。
4. PowerShell窗口1执行以下命令，输入NC Web/API账户：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_pt_backend.ps1 -ControllerPort 58000 -BackendPort 8000
```

5. 浏览器打开 `http://127.0.0.1:8000`。启动完成的画面：Edge ONLINE、Cloud CONNECTED、温度有读数；控制器CONNECTED，SW-CORE和SW-BRANCH为Managed/ONLINE。
6. PowerShell窗口2执行以下准备：

```powershell
$ApiBase = 'http://127.0.0.1:8000'
function Show-Api {
    param([string]$Path)
    Invoke-RestMethod "$ApiBase$Path" | ConvertTo-Json -Depth 50
}
```

**CLI截图操作**：点击指定设备→CLI；在 `>` 提示符输入 `enable`，然后输入该图的命令。`--More--`按空格翻页，滚动到要求的配置片段再截。

**调温操作（B、D使用）**：PT工具栏Environment→选择TEMP01所在Location→Ambient Temperature→Edit；在Advanced Settings把Transference设0。需要开启风扇时温度设35℃，需要关闭时设31℃。等SBC Console的实际TEMP达到要求，再截Console与FAN01→Attributes中的state。

## A：网络配置与前五次实验补图（30张）

### A01｜完整最终拓扑

**文件名**：`T02-final-topology.png`

**怎么截**：PT→Logical，关闭设备弹窗，缩放到总部、ISP、分部和IoT设备均可见，截整个拓扑。

**预期画面**：HQ、ISP、Branch三区域名称，路由器、交换机、PC、Server、NC-HQ、TEMP01、MCU、SBC、FAN及连线可辨；NC-HQ连接SW-CORE。

### A02｜DNS服务配置

**文件名**：`C10-dns-config.png`

**怎么截**：INTERNET-SERVER→Services→DNS，截设备标题、开关和记录表。

**预期画面**：DNS为On；www.edgecampus.net对应192.0.2.10，status.edgecampus.net对应203.0.113.1。

### A03｜总部HTTP服务

**文件名**：`C11-http-config-hq.png`

**怎么截**：HQ-SERVICE（设备原名BACKEND-STUB）→Services→HTTP，截标题、HTTP开关和页面文件列表。

**预期画面**：HTTP为On，页面文件列表可读。

### A04｜Internet HTTP服务

**文件名**：`C11-http-config-internet.png`

**怎么截**：INTERNET-SERVER→Services→HTTP，截标题、HTTP开关和页面文件列表。

**预期画面**：HTTP为On，页面文件列表可读。

### A05｜总部服务器地址

**文件名**：`C11-server-address-hq.png`

**怎么截**：HQ-SERVICE→Desktop→IP Configuration，截完整地址表。

**预期画面**：IPv4 192.168.30.10，掩码255.255.255.0，网关192.168.30.1；IPv6 2001:db8:30::10/64，网关2001:db8:30::1。

### A06｜Internet服务器地址

**文件名**：`C11-server-address-internet.png`

**怎么截**：INTERNET-SERVER→Desktop→IP Configuration，截完整IPv4地址表。

**预期画面**：IPv4 192.0.2.10，掩码255.255.255.0，网关192.0.2.1。

### A07｜SW-CORE管理ACL

**文件名**：`C17-management-final-swcore-acl.png`

**怎么截**：SW-CORE→CLI输入：

```text
show access-lists
```

滚动到用于VTY管理的ACL，截设备提示符、ACL名称及整段规则。

**预期画面**：管理ACL名称、permit/deny顺序和来源地址清晰可读；管理员地址192.168.30.20的允许条目可见。SW-CORE/SW-BRANCH的NC允许来源192.168.30.30可见。

### A08｜SW-CORE远程登录配置

**文件名**：`C17-management-final-swcore-vty.png`

**怎么截**：SW-CORE→CLI输入：

```text
show running-config
```

翻页到line vty，截完整VTY段。

**预期画面**：line vty范围、认证方式、transport input telnet及access-class绑定的ACL名称可读。

### A09｜R-HQ管理ACL

**文件名**：`C17-management-final-rhq-acl.png`

**怎么截**：R-HQ→CLI输入：

```text
show access-lists
```

滚动到用于VTY管理的ACL，截设备提示符、ACL名称及整段规则。

**预期画面**：管理ACL名称、permit/deny顺序和来源地址清晰可读；管理员地址192.168.30.20的允许条目可见。

### A10｜R-HQ远程登录配置

**文件名**：`C17-management-final-rhq-vty.png`

**怎么截**：R-HQ→CLI输入：

```text
show running-config
```

翻页到line vty，截完整VTY段。

**预期画面**：line vty范围、认证方式、transport input telnet及access-class绑定的ACL名称可读。

### A11｜R-BRANCH管理ACL

**文件名**：`C17-management-final-rbranch-acl.png`

**怎么截**：R-BRANCH→CLI输入：

```text
show access-lists
```

滚动到用于VTY管理的ACL，截设备提示符、ACL名称及整段规则。

**预期画面**：管理ACL名称、permit/deny顺序和来源地址清晰可读；管理员地址192.168.30.20的允许条目可见。

### A12｜R-BRANCH远程登录配置

**文件名**：`C17-management-final-rbranch-vty.png`

**怎么截**：R-BRANCH→CLI输入：

```text
show running-config
```

翻页到line vty，截完整VTY段。

**预期画面**：line vty范围、认证方式、transport input telnet及access-class绑定的ACL名称可读。

### A13｜SW-BRANCH管理ACL

**文件名**：`C17-management-final-swbranch-acl.png`

**怎么截**：SW-BRANCH→CLI输入：

```text
show access-lists
```

滚动到用于VTY管理的ACL，截设备提示符、ACL名称及整段规则。

**预期画面**：管理ACL名称、permit/deny顺序和来源地址清晰可读；管理员地址192.168.30.20的允许条目可见。SW-CORE/SW-BRANCH的NC允许来源192.168.30.30可见。

### A14｜SW-BRANCH远程登录配置

**文件名**：`C17-management-final-swbranch-vty.png`

**怎么截**：SW-BRANCH→CLI输入：

```text
show running-config
```

翻页到line vty，截完整VTY段。

**预期画面**：line vty范围、认证方式、transport input telnet及access-class绑定的ACL名称可读。

### A15｜R-HQ管理Loopback

**文件名**：`C17-management-final-rhq-loopback.png`

**怎么截**：R-HQ→CLI输入：

```text
show ip interface brief
```

截设备提示符、命令和Loopback0所在行。

**预期画面**：Loopback0地址10.255.255.1，Status和Protocol均为up。

### A16｜分部管理员地址

**文件名**：`C18-host-addresses-branch-admin.png`

**怎么截**：BR-ADMIN-PC→Desktop→IP Configuration，截IPv4和IPv6地址。

**预期画面**：IPv4 172.16.40.70，掩码255.255.255.224，网关172.16.40.65；IPv6 2001:db8:50::70/64，网关2001:db8:50::1。

### A17｜SBC接口地址

**文件名**：`C18-host-addresses-sbc-ip.png`

**怎么截**：EDGE-SBC-01→Config→以太网接口，截接口名、IP和掩码。

**预期画面**：IPv4 192.168.20.10，掩码255.255.255.0。

### A18｜SBC默认网关

**文件名**：`C18-host-addresses-sbc-gateway.png`

**怎么截**：EDGE-SBC-01→Config→Global Settings，截默认网关。

**预期画面**：IPv4默认网关192.168.20.1。

### A19｜总部DHCP和SLAAC客户端

**文件名**：`C18-office-dhcp-dns-slaac.png`

**怎么截**：OFFICE-PC→Desktop→IP Configuration，截IPv4、DNS和IPv6选项。

**预期画面**：IPv4选择DHCP，实际地址属于192.168.10.0/24，网关192.168.10.1，DNS 192.0.2.10；IPv6选择Auto Config，地址属于2001:db8:10::/64。

### A20｜分部DHCPv6客户端

**文件名**：`C18-branch-dhcpv6-client.png`

**怎么截**：BR-OFFICE-PC→Desktop→IP Configuration，截IPv6配置区域和设备标题。

**预期画面**：IPv6选择DHCP，已获取2001:db8:40::/64内地址，IPv6地址和Link-local地址可读。

### A21｜同VLAN通信

**文件名**：`C18-same-vlan-ping.png`

**怎么截**：ADMIN-PC→Desktop→Command Prompt输入：

```text
ipconfig
ping 192.168.30.10
```

等地址学习完成，再执行一次ping并截最后一次统计。

**预期画面**：来源ADMIN-PC为192.168.30.20，目标HQ-SERVICE为192.168.30.10；最后一次ping四次回复、丢包0%。

### A22｜总部PC访问分部PC IPv6

**文件名**：`C18-ipv6-pc-to-pc-hq.png`

**怎么截**：ADMIN-PC→Desktop→Command Prompt输入：

```text
ping 2001:db8:50::70
```

等邻居学习完成，再执行一次并截最后一次统计。

**预期画面**：目标2001:db8:50::70，四次IPv6回复、丢包0%；ADMIN-PC标题可见。

### A23｜分部PC访问总部PC IPv6

**文件名**：`C18-ipv6-pc-to-pc-branch.png`

**怎么截**：BR-ADMIN-PC→Desktop→Command Prompt输入：

```text
ping 2001:db8:30::20
```

等邻居学习完成，再执行一次并截最后一次统计。

**预期画面**：目标2001:db8:30::20，四次IPv6回复、丢包0%；BR-ADMIN-PC标题可见。

### A24｜管理员真实登录分部路由器

**文件名**：`V01-final-vty-regression-allow-router.png`

**怎么截**：ADMIN-PC→Desktop→Command Prompt输入：

```text
telnet 172.16.40.65
```

输入设备CLI账户，出现提示符后截图；输入exit退出。

**预期画面**：来源ADMIN-PC、目标172.16.40.65和R-BRANCH设备命令行提示符同时可见。

### A25｜管理员真实登录分部交换机

**文件名**：`V01-final-vty-regression-allow-switch.png`

**怎么截**：ADMIN-PC命令窗口输入：

```text
telnet 172.16.40.66
```

输入设备CLI账户，出现提示符后截图；输入exit退出。

**预期画面**：目标172.16.40.66和SW-BRANCH设备命令行提示符可见。

### A26｜总部办公终端远程登录被拒绝

**文件名**：`V01-final-vty-regression-deny-office.png`

**怎么截**：OFFICE-PC→Desktop→Command Prompt依次输入：

```text
ipconfig
telnet 172.16.40.65
telnet 172.16.40.66
```

每条telnet等连接结束；卡在等待时按Ctrl+C，再输入下一条，截两次连接结果。

**预期画面**：来源为192.168.10.0/24；两次telnet均未出现设备登录提示符，无法建立Telnet会话，连接失败结果可见。

### A27｜分部办公终端远程登录被拒绝

**文件名**：`V01-final-vty-regression-deny-branch-office.png`

**怎么截**：BR-OFFICE-PC→Desktop→Command Prompt依次输入：

```text
ipconfig
telnet 172.16.40.65
telnet 172.16.40.66
```

每条telnet等连接结束；卡在等待时按Ctrl+C，再输入下一条，截两次连接结果。

**预期画面**：来源为172.16.40.0/26；两次telnet均未出现设备登录提示符，无法建立Telnet会话，连接失败结果可见。

### A28｜管理测试后的NC设备状态

**文件名**：`V01-nc-managed-after-vty-check.png`

**怎么截**：上述登录测试完成后，浏览器打开http://127.0.0.1:8000/#controllerCenter，截设备表。

**预期画面**：控制器CONNECTED；SW-CORE 192.168.30.1和SW-BRANCH 172.16.40.66仍为ONLINE/Managed。

### A29｜保存重开后的拓扑

**文件名**：`V02-final-reopen-topology.png`

**怎么截**：PT→File→Save保存工作副本；关闭后File→Open重开同一文件；在Logical页面截全景。

**预期画面**：重开后总部、ISP、分部、NC及IoT设备和连线完整显示。

### A30｜保存重开后的在线状态

**文件名**：`V02-final-reopen-online.png`

**怎么截**：重开后运行MCU/SBC，按启动准备运行Backend；浏览器分别打开#edgeControl和#controllerCenter，将两个浏览器窗口并排截图。

**预期画面**：左侧Edge ONLINE、Cloud CONNECTED、温度/FAN有读数；右侧控制器CONNECTED，两台交换机Managed/ONLINE。

## B：真实Edge控制、离线自治与恢复（12张）

### B01｜MCU采样程序

**文件名**：`C20-pt-program-config-mcu.png`

**怎么截**：IO-MCU-01→Programming→打开当前采样项目的Python文件，滚动到初始化与采样循环，截代码编辑区。

**预期画面**：设备名、项目名、A0采样、USB(0,9600)、温度转换和1000ms采样间隔可读。

### B02｜SBC连接参数

**文件名**：`C20-pt-program-config-sbc-params.png`

**怎么截**：EDGE-SBC-01→Programming→打开当前控制程序，滚动到常量和连接参数。

**预期画面**：EDGE/TEMP/FAN/POLICY标识、ws://127.0.0.1:8000/ws/edge、Protocol1.0，以及遥测1000ms/心跳5000ms/重连2000ms参数可读。

### B03｜SBC本地控制循环

**文件名**：`C20-pt-program-config-sbc-loop.png`

**怎么截**：同一SBC编辑器滚动到主循环的USB采样与本地控制调用，截该段代码。

**预期画面**：USB读取、本地AUTO控制、物理FAN输出以及主循环执行顺序可读。

### B04｜SBC重连同步程序

**文件名**：`C20-pt-program-config-sbc-sync.png`

**怎么截**：同一SBC编辑器滚动到重连后的hello/state_sync发送代码，截该段。

**预期画面**：重连后发送hello和state_sync的代码、运行策略及风扇状态的同步字段可读。

### B05｜真实程序运行

**文件名**：`C20-pt-program-running.png`

**怎么截**：打开EDGE-SBC-01的Programming Console，等Backend已连接并持续采样，截输出区和设备标题。

**预期画面**：CLOUD CONNECTED，实际TEMP、FAN、本地控制来源和持续更新的运行日志可见。

### B06｜自动策略下发与执行ACK

**文件名**：`F06-policy-ack.png`

**怎么截**：浏览器打开http://127.0.0.1:8000/#edgePolicyControls；选择自动AUTO，阈值33，迟滞1，点击下发新策略；等ACK出现后截控制策略和事件流。

**预期画面**：表单为AUTO/33/1；策略确认ACK显示实际版本vN和APPLIED；事件流出现策略下发和确认。

### B07｜手动关闭风扇

**文件名**：`F07-command-ack-off.png`

**怎么截**：在控制策略选择MANUAL、33、1并下发，等策略ACK；按调温步骤使实际TEMP大于33。打开#edgeControl，点击手动关闭；把Dashboard风扇/命令ACK与FAN01→Attributes并排截图。

**预期画面**：控制模式MANUAL，FAN OFF；命令确认ACK为APPLIED；FAN01物理state=0。

### B08｜手动开启风扇

**文件名**：`F07-command-ack-on.png`

**怎么截**：保持MANUAL，点击手动开启，等回报；把Dashboard风扇/命令ACK与FAN01→Attributes并排截图。

**预期画面**：FAN ON；命令确认ACK为APPLIED；FAN01物理state=2。

### B09｜真正停Backend后的本地开启

**文件名**：`F09-offline-fan-on-attributes.png`

**怎么截**：先下发AUTO/33/1并等ACK，调到实际TEMP≤32、FAN OFF。窗口1按Ctrl+C停止Backend，MCU/SBC保持Run。调温到实际TEMP≥33；窗口2执行下面命令，将终端、SBC Console和FAN Attributes并排截。

```powershell
@(Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue).Count
```

**预期画面**：8000监听数量0；SBC CLOUD OFFLINE，仍保留断云前Policy版本/33/1；本地TURN_ON/FAN ON，FAN物理state=2。

### B10｜真正停Backend后的本地关闭

**文件名**：`F09-offline-fan-off.png`

**怎么截**：保持Backend停止、MCU/SBC运行；调到实际TEMP≤32，等TURN_OFF。窗口2再次执行8000监听计数命令，将终端、SBC Console和FAN Attributes并排截。

**预期画面**：8000监听数量0；CLOUD OFFLINE，Policy版本/33/1与上一张相同；本地TURN_OFF/FAN OFF，FAN物理state=0。

### B11｜Backend重启后的状态同步

**文件名**：`F11-dashboard-recovered.png`

**怎么截**：窗口1执行启动准备中的Backend启动命令；保持SBC连续运行。等自动重连后打开#edgePolicyControls，截当前策略与事件流。

**预期画面**：当前策略仍为断云前版本、AUTO/33/1；事件流出现STATE_SYNC。

### B12｜Backend重启后的实时状态

**文件名**：`F11-edge-recovered.png`

**怎么截**：浏览器打开#edgeControl，把Edge面板和SBC Console并排截图。

**预期画面**：Dashboard Edge ONLINE、Cloud CONNECTED，温度/FAN与SBC一致；Console出现CLOUD RECONNECTED和TX STATE_SYNC。

## C：真实NC接入与设备健康（15张）

### C01｜NC接入交换机端口

**文件名**：`C15-nc-access-address-core.png`

**怎么截**：SW-CORE→CLI输入：

```text
show interfaces gigabitEthernet 1/0/10 switchport
```

截接口名、模式和Access VLAN。

**预期画面**：Gi1/0/10为access，Access VLAN为30。

### C02｜NC端口配置

**文件名**：`C15-core-interface-config.png`

**怎么截**：SW-CORE→CLI输入：

```text
show running-config
```

翻页到interface GigabitEthernet1/0/10，截该接口配置段。

**预期画面**：接口配置含switchport mode access和switchport access vlan 30。

### C03｜NC接口IP

**文件名**：`C15-nc-access-address-nc.png`

**怎么截**：NC-HQ→Config→GigabitEthernet0，截接口地址。

**预期画面**：IP为192.168.30.30，掩码255.255.255.0。

### C04｜NC网关

**文件名**：`C15-nc-gateway.png`

**怎么截**：NC-HQ→Config→Global Settings，截默认网关。

**预期画面**：默认网关192.168.30.1。

### C05｜允许NC外部API访问

**文件名**：`C16-nc-external-preferences.png`

**怎么截**：PT→Options→Preferences，定位Enable External Access for Network Controller REST API选项并截图。

**预期画面**：该选项已勾选，选项名称和Preferences窗口标题可读。

### C06｜NC真实世界访问端口

**文件名**：`C16-nc-external-discovery-access.png`

**怎么截**：NC-HQ→Real World Access，截完整页面。

**预期画面**：Access Enabled已开启，HTTP Port为58000，Server Status显示监听。

### C07｜NC发现任务

**文件名**：`C16-nc-external-discovery-results.png`

**怎么截**：ADMIN-PC→Desktop→Web Browser访问http://192.168.30.30，登录NC，进入Provisioning→Discovery，打开已有任务结果并截图。

**预期画面**：浏览器地址栏192.168.30.30、发现目标、采用的协议和任务结果可读。

### C08｜Backend启动日志

**文件名**：`C21-backend-started.png`

**怎么截**：窗口1运行Backend后，定位Uvicorn启动和Edge接入日志，截终端。

**预期画面**：Uvicorn running on http://127.0.0.1:8000；Edge WebSocket已接入。

### C09｜实际监听端口和连接状态

**文件名**：`C21-runtime-status.png`

**怎么截**：窗口2依次执行，截端口表和控制器状态开头：

```powershell
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in @(8000,58000) } | Select-Object LocalAddress,LocalPort,OwningProcess
$s = Invoke-RestMethod "$ApiBase/api/controller/state"
$s | Select-Object source,status,url,observed_at | ConvertTo-Json
```

**预期画面**：端口表有8000、58000监听；控制器source为PT_CONTROLLER、status为CONNECTED。

### C10｜真实设备健康卡片

**文件名**：`U03-nc-dashboard-api.png`

**怎么截**：浏览器打开http://127.0.0.1:8000/#networkHealth，等采集刷新，截整个网络健康面板。

**预期画面**：SW-CORE 192.168.30.1、SW-BRANCH 172.16.40.66显示ONLINE/Managed；OSPF、BGP、Tunnel0均为NOT COLLECTED。

### C11｜控制器真实设备表

**文件名**：`U03-controller-table.png`

**怎么截**：浏览器打开#controllerCenter，截控制器状态、采集时间和完整设备表。

**预期画面**：CONNECTED和采集时间可见；两个Managed设备名/IP/type可读，其余设备的Unsupported状态可见。

### C12｜真实API设备数据

**文件名**：`U03-controller-api.png`

**怎么截**：窗口2执行，截请求命令与两台Managed设备的JSON字段：

```powershell
$s = Invoke-RestMethod "$ApiBase/api/controller/state"
$s.devices | Where-Object { $_.collectionStatus -eq 'Managed' } | ConvertTo-Json -Depth 30
```

**预期画面**：SW-CORE、SW-BRANCH的设备名、IP、类型、collectionStatus=Managed可读。

### C13｜拓扑API采集结果

**文件名**：`U05-controller-topology-response.png`

**怎么截**：窗口2执行以下命令，浏览器打开#controllerCenter并展开查看控制器物理拓扑数据，终端和展开区域并排截图：

```powershell
$s = Invoke-RestMethod "$ApiBase/api/controller/state"
[pscustomobject]@{status=$s.status; topology=$s.topology; topology_error=$s.topology_error} | ConvertTo-Json -Depth 50
```

**预期画面**：控制器CONNECTED；终端显示topology和topology_error的实际返回值；页面显示对应的拓扑采集内容。

### C14｜NC访问关闭后的界面

**文件名**：`U04-nc-unavailable.png`

**怎么截**：NC-HQ→Real World Access取消Access Enabled；Backend和SBC保持运行。等待10秒，刷新浏览器#networkHealth，截健康面板和控制器面板。

**预期画面**：控制器UNAVAILABLE；提示无法连接控制器；设备表和原ONLINE设备卡片清空；协议状态仍为NOT COLLECTED。

### C15｜NC访问恢复后的界面

**文件名**：`U04-nc-recovered.png`

**怎么截**：NC-HQ→Real World Access重新开启Access Enabled，端口58000；等待10秒，刷新浏览器#networkHealth，截健康面板和控制器面板。

**预期画面**：控制器回到CONNECTED；设备表重新出现，SW-CORE/SW-BRANCH回到ONLINE/Managed。

## D：中文NOC功能演示（13张）

### D01｜最终中文Dashboard首屏

**文件名**：`U02-noc-overview-01.png`

**怎么截**：浏览器打开http://127.0.0.1:8000/#edgeControl，截顶部导航、温度、Edge节点和FAN三个面板。

**预期画面**：导航和面板标题为中文；Edge ONLINE、Cloud CONNECTED，温度和FAN状态有实时读数。

### D02｜分部路由器检查

**文件名**：`U08-branch-check-router.png`

**怎么截**：浏览器打开#branchOperations，点击检查路由器，等结果出现后截整个分部运维面板。

**预期画面**：R-BRANCH IP为172.16.40.65；结果显示远程管理PASS、VTY ACL ALLOW；模拟数据标签可见。

### D03｜分部交换机检查

**文件名**：`U08-branch-check-switch.png`

**怎么截**：同一面板点击检查交换机，等结果出现后截图。

**预期画面**：SW-BRANCH IP为172.16.40.66；结果显示远程管理PASS、VTY ACL ALLOW。

### D04｜非管理员来源检查

**文件名**：`U08-branch-check-denied-api.png`

**怎么截**：窗口2执行后截请求命令与JSON结果：

```powershell
Invoke-RestMethod "$ApiBase/api/branch/check" -Method Post -ContentType application/json -Body '{"device":"R-BRANCH","source_ip":"192.168.10.10"}' | ConvertTo-Json -Depth 20
```

**预期画面**：device为R-BRANCH，management为DENIED，acl为DENY，source为SIMULATED。

### D05｜园区三类策略与Edge ACK

**文件名**：`U09-campus-policy.png`

**怎么截**：打开#edgePolicyControls，下发AUTO/33/1并等ACK；一个浏览器窗口打开#policyCenter，另一窗口打开#edgePolicyControls，将园区策略和策略ACK并排截图。

**预期画面**：园区策略版本可见；Edge thermal-01/实际vN/33/AUTO，Network Branch Access ALLOW与IoT Isolation启用，Security Port Security STRICT；策略ACK为同一vN/APPLIED。

### D06｜非法MAC安全事件

**文件名**：`U06-security-attack.png`

**怎么截**：打开#securityCenter，先点恢复安全状态；再点模拟安全攻击一次，等界面更新，截完整安全中心。

**预期画面**：端口安全VIOLATION、端口BLOCKED；累计违规数增加1；出现PORT_SECURITY_VIOLATION红色事件及“检测到未经授权的MAC·端口已阻断”。

### D07｜安全事件恢复

**文件名**：`U06-security-restored.png`

**怎么截**：在安全中心点击恢复安全状态，等更新后截图。

**预期画面**：端口安全SECURE，端口FORWARDING；事件显示恢复，累计违规数与攻击后的数值相同。

### D08｜ACL阻断事件

**文件名**：`U07-acl-block-event.png`

**怎么截**：安全状态恢复后，窗口2执行下面命令；浏览器打开#securityCenter，截安全中心与红色事件卡片：

```powershell
Invoke-RestMethod "$ApiBase/api/simulation/security" -Method Post -ContentType application/json -Body '{"event":"ACL_BLOCK_EVENT"}' | ConvertTo-Json -Depth 20
```

截图后点击恢复安全状态。

**预期画面**：ACL_BLOCK_EVENT红色卡片，文字为“检测到未授权流量·ACL已阻断”；ACL ACTIVE，端口安全SECURE，端口FORWARDING。

### D09｜云端故障按钮效果

**文件名**：`U10-cloud-ws-failure.png`

**怎么截**：先下发AUTO/33/1并等ACK，调到实际TEMP≤32。打开#simulationPanel点击模拟云端故障，等更新后截故障演练面板。

**预期画面**：Cloud OFFLINE，边缘控制为本地自治模式（预期）；状态同步显示等待恢复云端；FAN显示最后观测值。

### D10｜云端故障期间物理风扇开启

**文件名**：`U10-cloud-ws-local-fan.png`

**怎么截**：保持云端故障和Backend运行，MCU/SBC保持Run；调温到实际TEMP≥33，将SBC Console与FAN01→Attributes并排截。

**预期画面**：Console CLOUD OFFLINE、本地TURN_ON/FAN ON及最后策略33/1可见；FAN物理state=2。

### D11｜云端按钮恢复与同步成功

**文件名**：`U10-cloud-ws-restored.png`

**怎么截**：故障演练面板点击恢复云端连接，等SBC自动重连和同步完成，截故障演练面板与SBC Console。

**预期画面**：Cloud ONLINE，状态同步为同步成功SUCCESS，实时遥测恢复；SBC出现CLOUD RECONNECTED和TX STATE_SYNC。

### D12｜网络故障按钮状态

**文件名**：`U11-network-simulation-disabled.png`

**怎么截**：一个浏览器窗口打开#simulationPanel，另一个打开#networkHealth，将网络故障按钮和网络数据来源标签并排截。

**预期画面**：模拟网络故障、恢复网络连接两个按钮灰色禁用；网络健康面板显示“PT 控制器·实际数据”。

### D13｜网络故障API响应

**文件名**：`U11-network-disabled-api.png`

**怎么截**：浏览器打开http://127.0.0.1:8000/docs；展开POST /api/simulation/network→Try it out→Execute；截请求路径和Server response。

**预期画面**：请求路径/api/simulation/network；Server response为409，detail显示真实NC模式不支持模拟网络状态。
