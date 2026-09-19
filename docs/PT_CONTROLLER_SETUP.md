# Packet Tracer 控制器实际数据接入

## 当前实际接入结论（2026-09-19）

项目完成（待补证据）。用户已确认 Dashboard 真实设备显示成功，并提供配置报告：NC-HQ `192.168.30.30/24`/网关 `.30.1`，GE0接SW-CORE Gi1/0/10 access VLAN30；R-HQ管理Loopback0 `10.255.255.1/32`；VTY新增允许NC `.30.30`同时保留ADMIN `.30.20`。这是用户实施记录，尚待完整running-config与成功Dashboard/API归档。两项Managed原图已入库，见 [最终报告](final/PROJECT_COMPLETION_REPORT.md)。

下方‘尚未联调通过’或UNAVAILABLE检查描述的是早期开发时刻，不能作为当前失败结论。Managed映射仍仅依据collectionStatus；报告中的R-HQ发现不代表已Managed。

Backend接入为只读：登录控制器并读取设备清单与物理拓扑，不写设备配置或关闭链路。当前正式 `.pkt` 采用用户最新保存版本，PT控制器配置由用户在当前PT工作区完成。Edge Protocol v1.0 不变；最新收尾状态以最终报告为准。

## 1. 在 PT 添加 NC-HQ

1. End Devices 中拖入 Network Controller，命名 NC-HQ。连接其管理接口到 HQ 交换机的空闲端口（以设备界面为准）。
2. 将交换机该端口设为 access VLAN30，不改现有 trunk、业务接口或链路。先用 show vlan brief / show interfaces status 确认所选端口空闲。
3. 建议新增地址 192.168.30.30/24，网关 192.168.30.1；先确认地址未占用，再配置控制器管理接口。若选用其他地址，下面用实际地址替换。此地址是新增建议，并非既有冻结设备地址。
4. ADMIN-PC（192.168.30.20）的 Desktop → Web Browser 访问 http://192.168.30.30，首次创建管理员账户。保留用户名与密码供本机启动脚本输入，不发到聊天或提交到 Git。
5. Provisioning → 配置实际路由器/交换机的 CLI 凭据（按设备支持的协议）；Discovery 中按 IP 范围或 CDP 发现设备。先发现 HQ 设备，再扩展 Branch。新增控制器自身不保证发现成功，需要管理网络可达、凭据正确和设备协议支持。
6. 既有 VTY ACL 如果只允许 ADMIN-PC 192.168.30.20，将拒绝来自 NC-HQ 的管理连接。需要使用现有 ACL 类型与名称，额外允许控制器的准确管理 IP，并保留 ADMIN-PC 与原 deny 规则；不要放开整个网段或删除 ACL。设备成功被发现后，控制器清单才有数据。该变更需在当前 PT 拓扑实测，不由 Backend 自动执行。
7. PT Preferences 中启用 Enable External Access for Network Controller REST API。
8. 控制器的 Real World Access 中启用 Access Enabled，HTTP Port 填 58000，确认 Server Status 在监听。若配置区域只读，回查 Preferences。

VLAN 端口配置示例（将占位符换成已确认空闲的实际端口名）：

```text
configure terminal
interface <实际空闲端口>
 switchport mode access
 switchport access vlan 30
 no shutdown
end
```

## 2. 启动真实控制器模式 Backend

如果原来 Backend 正运行，在其 PowerShell 终端 Ctrl+C 停止，再运行：

```powershell
cd D:\Develop\sommerom\bighomework\edgecampus-g3
.\scripts\start_pt_backend.ps1
```

脚本交互询问 NC-HQ 管理员用户名、密码，密码输入不回显。控制器端口默认 58000，Backend 默认 8000。脚本临时设置进程环境变量，Backend 退出后恢复之前的环境变量。不会把密码写入文件。环境变量在启动 Backend 时读取，修改后需重启。

自定义端口：

```powershell
.\scripts\start_pt_backend.ps1 -ControllerPort 58000 -BackendPort 8000
```

若 PowerShell 执行策略阻止脚本，可仅对这次子进程使用：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_pt_backend.ps1
```

若不存在 runtime/noc-venv，先用可用的 Python 3.11+ 执行 `python -m venv runtime/noc-venv`，再执行 `runtime/noc-venv/Scripts/python.exe -m pip install -r requirements.txt`。当前本机已有该环境。

## 3. 查看与验证

浏览器打开 http://127.0.0.1:8000。网络控制器区展示 CONNECTED、设备数量、设备名、管理 IP、控制器提供的状态和采集时间，展开可查看拓扑 nodes/links JSON。

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/controller/state | ConvertTo-Json -Depth 20
Invoke-RestMethod http://127.0.0.1:8000/api/network/state | ConvertTo-Json -Depth 20
```

验收：在 PT 中让控制器发现设备，Dashboard 设备名/IP 应与控制器清单一致。手动改变设备连接后，需要等待控制器自身完成重新采集，再等待 Backend 最多 5 秒的查询缓存；不能保证立即检测链路故障。关闭控制器 Real World Access 后，页面应显示 UNAVAILABLE，清空设备/拓扑，而非显示模拟正常。恢复后自动重试。

## 4. 数据真实性与范围

- GET /api/controller/state 单独返回控制器状态；GET /api/network/state 和 /api/noc/state 包含同一次缓存采集结果。
- Network Health 仅采用 PT_CONTROLLER 来源；真实失败不回退 Mock，未配置控制器时没有设备健康数据。
- OSPF/BGP/Tunnel/分部业务状态为 NOT COLLECTED：本版 inventory/topology 不直接提供这些协议的验收结果。不把管理可达等同于协议建立，不把已发现等同于当前在线。
- Network Failure / Restore Network 按钮禁用，接口返回 409，不混入模拟路由状态。
- Security Center、分部 VTY 检查、Campus Network/Security 策略仍为模拟/配置展示，保留其来源标签，与真实控制器区分开。SBC/FAN 仍使用既有真实 Edge 通道。
- 控制器端口 58000 与 Backend/SBC 端口 8000 不同。真实主机地址为 localhost:58000，不能用 PT 内部 192.168.30.30 地址替代。
- 只向本机 HTTP 控制器地址发送登录信息；不跟随重定向，不使用系统代理，页面与 API 不返回密码或认证票据。
- 超时与认证失败给出明确状态；401 重新登录后只重试一次。拓扑读取失败时保留已成功读取的清单，并显示拓扑不可用。
- 实际 PT 联调由用户完成上述控制器配置并启动脚本。本地 HTTP fixture 测试不替代真实 PT 验收。

## 官方依据

[Network Controller 与 Real World Access](https://tutorials.ptnetacad.net/help/default/config_NetworkControllers.htm)

[Northbound API：POST /ticket、GET /network-device、GET /topology/physical-topology](https://tutorials.ptnetacad.net/help/default/NetconRestAPI/index.html)

## 本地验证
46 项 Python 测试、3 项 Node 前端验证及 Protocol contract 检查通过；PowerShell 启动脚本通过语法解析。Controller fixture 覆盖实际 HTTP 认证/读取、401 重登录、500 后清空旧数据、501 拓扑降级、空清单、响应格式错误、缓存隔离和凭据不外泄。前端验证覆盖实际来源标签、真实设备状态、设备文本渲染、认证失败和模拟网络按钮禁用。开发阶段仅使用 fixture；后续用户已确认 NC-HQ 实际接入，证据状态见本页顶部。


## 设备健康展示更新

Network Health 展示 NC 实际设备清单中的 hostname/name、managementIpAddress/ipAddress 与 collectionStatus。只有 collectionStatus 严格等于 Managed 时映射 ONLINE（绿色）；其他值保留控制器原值，字段缺失显示 NOT COLLECTED，不通过 reachabilityStatus 推断 Managed。此 ONLINE 是控制器管理状态，不证明所有业务流或路由协议已正常。

OSPF/BGP/Tunnel 均显示 NOT COLLECTED，移除原 UNKNOWN 与模拟分部连接展示。设备卡片和表格都只接受 PT_CONTROLLER 来源且 CONNECTED 的采集结果；读取失败、未配置、Backend 失联时清空设备，不能保留旧 ONLINE 卡片或模拟替代。

本次验证：46 项 Python、3 项 Node 与协议检查通过。只读检查当前 8000 /api/controller/state 时返回 UNAVAILABLE，因此没有将该时刻记为真实卡片在线验收；用户已确认此前 NC API 能返回设备及 collectionStatus。恢复控制器连接后可继续现场检查 Managed → ONLINE。
