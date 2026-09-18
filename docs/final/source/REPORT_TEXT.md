# 用户提供的 NOC 配置报告：文本提取

来源：同目录原始 DOCX。只提取文字，没有图片；文内配置是用户提供的实施记录，不是本次读取的 running-config。原文保留，不将压平的 CLI 行作为可直接执行脚本。报告中的设备 CLI 实验凭据不等同于 NC Web/API 账户。

EdgeCampus NOC功能升级过程与配置报告

本文档记录 EdgeCampus 项目在完成基础 Edge-SBC 控制、网络实验功能后，进一步升级为融合网络控制器的 NOC（Network Operations Center）平台的完整过程。升级目标是将原有 Dashboard 从仅展示边缘设备状态，扩展为能够感知 Packet Tracer 真实网络设备状态，实现边缘控制与园区网络管理融合。

一、升级背景与目标

原 EdgeCampus 系统已经实现：SBC 温度采集、风扇自动控制、策略下发、云端 Dashboard 展示等功能。但网络部分主要依赖实验配置和人工验证，缺少真实网络设备状态接入。

因此本次升级引入 Packet Tracer Network Controller（NC-HQ），建立 Dashboard 后端与真实网络拓扑之间的数据通道，实现：

网络控制器接入园区管理网络

自动发现 Cisco 网络设备

读取设备管理状态

在 Dashboard 展示真实设备健康状态

形成 Edge Control + Network Operation 的统一管理平台

二、总体架构设计

升级后的系统架构如下：

Dashboard        |Backend(FastAPI)        |+----------------+|                |Edge WebSocket   Network Controller API|                |SBC Controller   NC-HQ                 |          Packet Tracer Network Devices          R-HQ / SW-CORE / SW-BRANCH

三、Network Controller接入配置过程

3.1 添加Network Controller设备

在 Packet Tracer 中新增 Network Controller，命名为 NC-HQ。使用 GigabitEthernet0 接入核心交换机管理网络。

3.2 接入管理VLAN30

由于项目已有管理网络 VLAN30，因此将 NC-HQ 接入该 VLAN。管理地址规划如下：

NC-HQ: 192.168.30.30/24

Management Gateway: 192.168.30.1

ADMIN-PC: 192.168.30.20

SW-CORE 对应接口配置：

interface gigabitEthernet 1/0/10 switchport mode access switchport access vlan 30 no shutdown

四、网络设备管理平面配置

4.1 R-HQ增加管理Loopback

为了避免影响已有业务链路，将R-HQ原有G0/0作为OSPF链路保留，新增Loopback接口作为稳定管理地址。

interface loopback0 ip address 10.255.255.1 255.255.255.255 description MANAGEMENT_LOOPBACK

4.2 VTY远程管理配置

为了允许Network Controller访问设备，需要配置统一CLI认证。

username admin privilege 15 secret edgecampusline vty 0 4 login local transport input telnet

4.3 VTY访问控制

新增VTY ACL，仅允许管理员PC和Network Controller访问设备管理接口。

ip access-list standard VTY-HQ-ADMIN permit host 192.168.30.20 permit host 192.168.30.30 deny any

五、Network Controller设备发现

通过NC-HQ的Discovery功能进行网络设备发现。配置CLI Credential：

Username: admin

Password: edgecampus

Protocol: Telnet

成功发现设备包括：

SW-CORE: 192.168.30.1

SW-BRANCH: 172.16.40.66

R-HQ管理接口: 10.255.255.1

六、Dashboard真实网络状态接入

Backend增加Network Controller数据读取逻辑，将控制器提供的真实设备状态转换为Dashboard数据。

当前可稳定获取的数据包括：

设备名称

管理IP地址

设备类型

Managed/Reachable状态

由于Packet Tracer Network Controller接口限制，OSPF、BGP、IPv6 Tunnel等协议级状态暂不能直接通过控制器接口获取，因此Dashboard将其标记为NOT COLLECTED，而不使用模拟数据。

七、最终展示效果

Network Controller显示真实Managed设备列表

Dashboard显示真实网络设备健康状态

Edge SBC状态与园区网络状态统一展示

形成边缘计算+网络运维一体化NOC平台

八、测试结果总结

本次升级测试结果：

NC-HQ成功接入VLAN30管理网络

ADMIN-PC可以访问NC-HQ

NC-HQ成功发现Packet Tracer网络设备

SW-CORE与SW-BRANCH状态显示Managed

Dashboard成功进入真实控制器读取模式

九、后续可扩展方向

后续可以进一步扩展CLI Telemetry或设备Agent，获取OSPF邻居、BGP会话、Tunnel状态等协议级信息，进一步完善网络健康分析能力。
