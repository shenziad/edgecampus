# 前五次实验功能演示：明确需要补拍的5张图片

这5张全部由A在自己的完整项目中拍摄。已有实验图片按[素材总清单](FINAL_REPORT_SCREENSHOT_CHECKLIST.md)直接取用；其他配置和Dashboard待截图见[四人逐张操作清单](FINAL_REPORT_SCREENSHOT_ASSIGNMENT.md)。

## A19｜总部DHCP和SLAAC客户端

**文件名**：`C18-office-dhcp-dns-slaac.png`

**怎么截**：OFFICE-PC→Desktop→IP Configuration，截IPv4、DNS和IPv6选项。

**预期画面**：IPv4选择DHCP，实际地址属于192.168.10.0/24，网关192.168.10.1，DNS 192.0.2.10；IPv6选择Auto Config，地址属于2001:db8:10::/64。

## A20｜分部DHCPv6客户端

**文件名**：`C18-branch-dhcpv6-client.png`

**怎么截**：BR-OFFICE-PC→Desktop→IP Configuration，截IPv6配置区域和设备标题。

**预期画面**：IPv6选择DHCP，已获取2001:db8:40::/64内地址，IPv6地址和Link-local地址可读。

## A21｜同VLAN通信

**文件名**：`C18-same-vlan-ping.png`

**怎么截**：ADMIN-PC→Desktop→Command Prompt输入：

```text
ipconfig
ping 192.168.30.10
```

等地址学习完成，再执行一次ping并截最后一次统计。

**预期画面**：来源ADMIN-PC为192.168.30.20，目标HQ-SERVICE为192.168.30.10；最后一次ping四次回复、丢包0%。

## A22｜总部PC访问分部PC IPv6

**文件名**：`C18-ipv6-pc-to-pc-hq.png`

**怎么截**：ADMIN-PC→Desktop→Command Prompt输入：

```text
ping 2001:db8:50::70
```

等邻居学习完成，再执行一次并截最后一次统计。

**预期画面**：目标2001:db8:50::70，四次IPv6回复、丢包0%；ADMIN-PC标题可见。

## A23｜分部PC访问总部PC IPv6

**文件名**：`C18-ipv6-pc-to-pc-branch.png`

**怎么截**：BR-ADMIN-PC→Desktop→Command Prompt输入：

```text
ping 2001:db8:30::20
```

等邻居学习完成，再执行一次并截最后一次统计。

**预期画面**：目标2001:db8:30::20，四次IPv6回复、丢包0%；BR-ADMIN-PC标题可见。
