# Packet Tracer 交付目录

## 最新本地交付包（2026-09-19）

项目完成（报告证据整理中）。当前正式 `.pkt` 为156539 bytes，SHA-256 `4f53c07e45ea66ea96bd83b42b751cb3cfb41c354c9f9489ae4358f4cdf1634c`。该包包含手工EtherChannel、Branch PAT/协议ACL、VLAN100双DROTHER课程节点、隔离重分发测试层和双端口Port Security；图54非法终端场景仅保存在证据目录的临时包中。详见[课程补强配置](../docs/COURSE_COVERAGE_PATCH.md)与[最终报告](../docs/final/PROJECT_COMPLETION_REPORT.md)。

A（Network Owner）在此维护：

- `EdgeCampus.pkt`：唯一正式拓扑文件；
- `CONFIG_LOG.md`：按设备记录最终配置、验证命令和异常；
- 必要时保存 `startup-config/` 文本备份。

禁止出现 `final2.pkt`、`final真的.pkt` 等并行真相源。重要 Gate 后用 Git commit 保留版本。

## 建议创建顺序

1. 放置并命名 Core、Access、PC、Server、SBC、TEMP01、FAN01。
2. 按 `docs/NETWORK_PLAN.md` 完成 VLAN/IP/Trunk/EtherChannel。
3. 先完成网络连通与 ACL，再加入 IoT 自动控制。
4. 验证 PT ↔ 真实主机通信，这一项优先级高于美化拓扑。
5. 每完成一个 Gate，同时补 `CONFIG_LOG.md` 和 `evidence/` 截图。
