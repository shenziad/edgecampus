# Packet Tracer 配置与验证日志

> 每条关键配置记录“目的—命令—结果”；不要把整份 running-config 无解释地堆入报告。

## 环境信息

- Packet Tracer 版本：`TODO`
- SW-CORE 型号：`TODO`
- SW-ACCESS 型号：`TODO`
- 真实主机网络方式：`TODO`

## 端口映射

见 `docs/NETWORK_PLAN.md`，Gate 0 完成后同步更新。

## SW-CORE

```text
TODO
```

验证：

```text
show vlan brief
show interfaces trunk
show etherchannel summary
show ip interface brief
show access-lists
show ip route
```

## SW-ACCESS

```text
TODO
```

## 功能验证结果

| 日期/时间 | 测试 | 预期 | 实际 | 证据路径 |
|---|---|---|---|---|
| TODO | OFFICE → Dashboard | 允许 | TODO | `evidence/network/` |
| TODO | OFFICE → IOT | 拒绝 | TODO | `evidence/network/` |
| TODO | IOT → Backend:8000 | 允许 | TODO | `evidence/network/` |
| TODO | EtherChannel 状态 | Up/In use | TODO | `evidence/network/` |
