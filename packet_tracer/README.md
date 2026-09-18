# Packet Tracer 交付目录

## 最新本地交付包（2026-09-18）

项目完成（待补证据）。当前用户 `.pkt` 已更新为144326 bytes，SHA-256 `1c390fd766e6cb3c108f4e69853f61f614ca5a1a790cbed92e4cbd3f37e505dd`，本次原样归档未改二进制。来源报告记录新增NC-HQ与管理配置，实际包内内容、保存重开、程序一致性仍待PT核验（EV-26/27），三轮彩排待执行（EV-28）。详见 [最终报告](../docs/final/PROJECT_COMPLETION_REPORT.md)。

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
