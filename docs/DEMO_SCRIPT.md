# 现场 6 分钟演示脚本

## 演示前检查

- 打开最终 `.pkt`，确认所有链路稳定。
- Backend 与 Dashboard 未提前残留旧进程。
- 事件流清理或明确从当前时间开始。
- 已准备一条停止/恢复 Backend 的确定命令。
- 主讲人和每次操作人固定，不现场临时换手。

## 0:00–0:40 架构与创新

展示三平面架构图，说明三个安全域、Edge SBC、Cloud Controller 和双控制环。

话术：

> EdgeCampus 不是把物联网设备简单连接到网页，而是以园区网络为数据平面、SBC 为边缘控制节点、FastAPI 为云端控制平面，实现网络隔离、边缘自治、云端策略编排与闭环可观测。

## 0:40–1:30 网络隔离

- OFFICE 访问 Dashboard 成功。
- OFFICE 直接访问 IOT 控制区失败。
- 快速展示 VLAN、Trunk/EtherChannel、ACL 状态。

强调：网络强制普通用户通过控制平面操作 IoT，而不是绕过平台直控设备。

## 1:30–2:40 温度闭环

- PT 将温度由 28℃ 改为 32℃。
- SBC 自动开启 FAN01。
- Dashboard 显示 32℃、WARNING、Fan ON。
- 事件流显示来源 `SENSOR` 与 `EDGE-AUTO`。

## 2:40–3:40 策略下发

- Dashboard 把阈值从 30℃ 改为 33℃。
- 展示 `policy_ack v2 APPLIED`。
- 证明 32℃ 不再启动，34℃ 时重新启动。

强调：这是 Cloud-to-Edge Policy Delivery，不只是遥控开关。

## 3:40–5:15 核心高潮：断云不断控

- 停止 Backend，说明 Cloud Connection Lost。
- PT 中 26℃ → Fan OFF；34℃ → Fan ON。
- 说明 Edge 保留最后有效策略并继续运行。
- 恢复 Backend，展示 Edge 自动重连、`state_sync` 和当前 Policy Version。

## 5:15–6:00 总结与分工

依次指出：网络分区、安全隔离、边缘自治、策略编排、状态同步。每个 Owner 用一句话讲自己的可验收成果。

收尾：

> 因此，本系统形成了从感知、网络传输、边缘决策、云端编排到设备执行的完整闭环，并具备网络故障下的服务降级能力。
