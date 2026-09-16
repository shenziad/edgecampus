# Packet Tracer 控制器实际数据接入

本次接入为只读：Backend 登录控制器，读取设备清单与物理拓扑。未运行设备发现、写配置、关闭链路或编辑 canonical .pkt。PT 控制器的配置由用户在当前 PT 工作区完成。现有 Gate 状态与 Edge Protocol v1.0 不变。

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
- PT_CONTROLLER_URL 设置后采用 PT_CONTROLLER 来源，真实失败不回退 Mock；未设置时原模拟演示仍可使用，并明确标注。
- OSPF/BGP/Tunnel/分部业务状态仍为 UNKNOWN：本版 inventory/topology 不直接提供这些协议的验收结果。不把管理可达等同于协议建立，不把已发现等同于当前在线。
- 真实模式下 Network Failure / Restore Network 按钮禁用，接口返回 409，不混入模拟路由状态。
- Security Center、分部 VTY 检查、Campus Network/Security 策略仍为模拟/配置展示，保留其来源标签，与真实控制器区分开。SBC/FAN 仍使用既有真实 Edge 通道。
- 控制器端口 58000 与 Backend/SBC 端口 8000 不同。真实主机地址为 localhost:58000，不能用 PT 内部 192.168.30.30 地址替代。
- 只向本机 HTTP 控制器地址发送登录信息；不跟随重定向，不使用系统代理，页面与 API 不返回密码或认证票据。
- 超时与认证失败给出明确状态；401 重新登录后只重试一次。拓扑读取失败时保留已成功读取的清单，并显示拓扑不可用。
- 实际 PT 联调需要用户完成上述控制器配置并启动脚本。本地 HTTP fixture 测试不替代真实 PT 验收。

## 官方依据

[Network Controller 与 Real World Access](https://tutorials.ptnetacad.net/help/default/config_NetworkControllers.htm)

[Northbound API：POST /ticket、GET /network-device、GET /topology/physical-topology](https://tutorials.ptnetacad.net/help/default/NetconRestAPI/index.html)

## 本地验证
46 项 Python 测试、3 项 Node 前端验证及 Protocol contract 检查通过；PowerShell 启动脚本通过语法解析。Controller fixture 覆盖实际 HTTP 认证/读取、401 重登录、500 后清空旧数据、501 拓扑降级、空清单、响应格式错误、缓存隔离和凭据不外泄。前端验证覆盖实际来源标签、UNKNOWN 状态、设备文本渲染、认证失败和模拟网络按钮禁用。尚未宣称 NC-HQ 实机联调通过。
