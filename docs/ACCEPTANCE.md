# Gate 与验收标准

## Gate 0：Contract Freeze

| 验收项 | 状态 |
|---|---|
| 项目定位、三平面与双控制环 | DONE |
| 设备 ID、消息协议、WS 路径 | DONE |
| VLAN/IP 逻辑规划 | DONE |
| 物理设备型号、接口映射 | A 待补 |
| PT 与真实主机互通方式 | A+B+C 待实测 |
| 最终 6 分钟 Demo | DONE |

Gate 0 结束后，公共契约只通过 RFC 改动。

## Gate 1：四模块独立运行

- A：VLAN、Trunk、EtherChannel、SVI、DHCP、ACL 独立通过。
- B：PT 内改变 TEMP01，SBC 能在无 Cloud 条件下控制 FAN01。
- C：`fake_edge.py` 接入 Backend，`/api/state` 能看到遥测。
- D：Dashboard 可用 fake 数据展示状态、事件和策略表单。

证据目录：`evidence/network/`、`edge/`、`backend/`、`dashboard/`。

## Gate 2：单向数据链路

```text
Packet Tracer TEMP01 → SBC → Backend → Dashboard
```

验收动作：PT 温度从 28℃ 改到 32℃；Dashboard 在可接受延迟内显示 32℃ 与 WARNING，事件流出现 SENSOR 记录。

## Gate 3：双向策略闭环

```text
Dashboard threshold 30→33 → Backend → Edge → policy_ack
```

验收动作：下发 33℃，温度 32℃ 时风扇保持 OFF，温度 34℃ 时风扇 ON；事件流能区分 CLOUD-POLICY 与 EDGE-AUTO。

增强验收：Dashboard 手动下发 FAN01 ON/OFF，收到 `command_ack`。

## Gate 4：断云不断控

1. 正常连接，确认 Cloud/Edge ONLINE。
2. 停止 Backend，Dashboard 显示失联。
3. 在 PT 内将温度改到阈值之上，Fan 仍由 SBC 开启。
4. 再改到阈值减迟滞区间之下，Fan 关闭。
5. 恢复 Backend；Edge 自动重连并发送当前温度、风扇和 Policy Version。

这是项目的核心创新性证据，必须保留连续录屏或按时间顺序的截图。

## Gate 5：Freeze 与三轮彩排

第三天只允许修 Bug、改善 UI、补日志和异常处理。完整流程连续演示三轮都成功后冻结版本。

## 最终功能测试矩阵

| ID | 测试 | 操作 | 预期 | Owner |
|---|---|---|---|---|
| N1 | VLAN/路由 | 跨允许域 ping/访问 | 可达 | A |
| N2 | ACL 隔离 | OFFICE 直连 IOT | 拒绝 | A |
| N3 | 控制面访问 | OFFICE 访问 Backend:8000 | 允许 | A+C |
| E1 | 本地自治 | 断开 Cloud 后跨阈值调温 | Fan 正确动作 | B |
| C1 | 遥测 | fake/PT 发送温度 | Backend 状态更新 | B+C |
| D1 | 可视化 | 温度跨阈值 | 页面状态与告警更新 | C+D |
| P1 | 策略下发 | 阈值 30→33 | Edge 应用并 ACK | B+C+D |
| R1 | 状态恢复 | Cloud 重启 | Edge 重连并同步 | B+C+D |

## 截图命名

`G<Gate>-<序号>-<内容>-<结果>.png`，例如：

```text
G1-01-vlan-trunk-pass.png
G2-01-temperature-dashboard-pass.png
G3-02-policy-ack-pass.png
G4-03-cloud-offline-edge-auto-pass.png
G4-04-reconnect-state-sync-pass.png
```
