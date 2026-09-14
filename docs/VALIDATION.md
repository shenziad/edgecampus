# 初始基线验证记录

## 已通过

- Python 全量语法编译。
- 9 项单元测试：协议拒绝错误字段/版本/范围、Edge 迟滞控制、MANUAL 保持、策略更新、Backend 状态与 State Sync。
- 公共契约漂移检查。
- Dashboard JavaScript 语法检查。
- Backend + Fake Edge + Dashboard WebSocket 真实进程联调。
- Dashboard 下发 Policy 与 Command，Edge 返回对应 ACK。
- 停止 Cloud 后 Fake Edge 持续在 34℃/27℃ 场景切换 Fan ON/OFF。
- Cloud 恢复后 Edge 自动重连，Backend 接收 `state_sync`。

## 尚需实验环境验证

- Packet Tracer 设备型号与接口命令。
- Packet Tracer SBC 的实际传感器/执行器 API。
- Packet Tracer 与真实主机双向通信方式。
- 浏览器在最终演示电脑上的视觉与交互确认。
- VLAN/ACL/EtherChannel 全部现场配置和三轮彩排。

上述未验证项都在文档中标记为 TODO，没有把 PT 适配模板误称为已完成实现。
