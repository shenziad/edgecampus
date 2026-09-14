# 架构决策记录

## ADR-001：采用 FastAPI + WebSocket

状态：Accepted

原因：一个进程同时提供 API、双向消息和静态 Dashboard，满足三天原型，不引入消息队列或微服务。

## ADR-002：Edge 保存最后有效策略

状态：Accepted

原因：控制动作不能依赖 Cloud 永久在线；断云时继续本地 AUTO 循环。

## ADR-003：首版使用内存状态 + JSONL 事件日志

状态：Accepted

原因：现场系统无需复杂查询，数据库会增加部署与恢复风险。正式持久化作为后续增强。

## ADR-004：统一摄氏单位为 `C`

状态：Accepted

原因：传输字段保持 ASCII 与跨平台一致；Dashboard 可展示为 `℃`。

## ADR-005：迟滞控制

状态：Accepted

原因：温度达到阈值时开启，降到“阈值减迟滞”时关闭，避免临界点频繁开关。
