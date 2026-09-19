# Gate 4 真实证据索引

归档日期：2026-09-17。以当前 feat/edge 工作树为事实源（用户明确要求保留此分支）。9 张新增截图均已逐张查看；只改名/移动，不修改像素、不删除原有 G1-G3 证据。SHA-256 为原图与归档图共同内容校验值。

| 原始路径 | 归档路径 | SHA-256 |
|---|---|---|
| `evidence/edge/gate4/屏幕截图 2026-09-16 222027.png` | `evidence/edge/gate4/G4-B-01-last-policy-before-outage-pass.png` | `cee6df9e9a43faa2a4b111e3a8ac9e5150445414c2524ec476a51a0942daa29e` |
| `evidence/edge/gate4/屏幕截图 2026-09-16 222256.png` | `evidence/edge/gate4/G4-B-02-backend-down-local-auto-on-pass.png` | `0f62468f31dde969e6150c36f12ca04f2e383dfa58df23f25e079540e35b977a` |
| `evidence/edge/gate4/屏幕截图 2026-09-16 222417.png` | `evidence/edge/gate4/G4-B-03-auto-reconnect-state-sync-pass.png` | `15d9777f8fcf6d755c6e36feb799436f38f2a3f651ffe4f7c6a5187fd52aaeff` |
| `evidence/backend/gate4/屏幕截图 2026-09-16 224404.png` | `evidence/backend/gate4/G4-C-01-edge-disconnect-offline-pass.png` | `2fe73d8a6da9e20cca581aef72aa23a0f5fd46b3fba2df9111d65c95ebaba57a` |
| `evidence/backend/gate4/屏幕截图 2026-09-16 225951.png` | `evidence/backend/gate4/G4-C-02-state-sync-event-pass.png` | `58fa74feda42406dee02e96216008a1494ff0f47e6128aa27bdfaedf3e3f76f0` |
| `evidence/backend/gate4/屏幕截图 2026-09-16 231410.png` | `evidence/backend/gate4/G4-C-03-invalid-message-reject-pass.png` | `94c866347e50d236de4d3d5e5e827f46c54711478c2f4786fd28588a9bb3e426` |
| `evidence/backend/gate4/屏幕截图 2026-09-16 231437.png` | `evidence/backend/gate4/G4-C-04-invalid-summary-restored-state-pass.png` | `fc85b6ff8b0a089579ad6257d46775c9fc27a3d05c05db08d13b3e332913cd0e` |
| `evidence/backend/gate4/屏幕截图 2026-09-16 232050.png` | `evidence/dashboard/gate4/G4-D-01-control-plane-disconnected-pass.png` | `15cc1475f1ab92448267344d17d69cb4e9a5c7fdcbba52077f6dc24230454d72` |
| `evidence/backend/gate4/屏幕截图 2026-09-16 232238.png` | `evidence/backend/gate4/G4-C-05-reconnect-state-sync-restored-pass.png` | `58f3d558fde4d0d1b6299d5572f3d860f3f7dd96ead95e8c2a5d90b130842e6c` |

## 待补证据（占位清单，不是图片文件）

用户于 2026-09-17 确认 A 已实测，截图本次跳过后补。下列名称仅为建议，实际图片未入库，不用 Markdown 图片链接制造失效引用。

| DoD | 建议文件名 | 状态 |
|---|---|---|
| N12 HQ SLAAC | G4-A-01-n12-office-slaac-pass.png | USER-REPORTED PASS / EVIDENCE PENDING |
| N12 Branch DHCPv6 + Static | G4-A-02-n12-branch-dhcpv6-static-pass.png | USER-REPORTED PASS / EVIDENCE PENDING |
| N13 IPv6 Tunnel | G4-A-03-n13-ipv6-tunnel-pass.png | USER-REPORTED PASS / EVIDENCE PENDING |
| N14 ADMIN Telnet 两设备 | G4-A-04-n14-admin-telnet-pass.png | USER-REPORTED PASS / EVIDENCE PENDING |
| N14 OFFICE 管理拒绝 | G4-A-05-n14-office-admin-deny.png | USER-REPORTED PASS / EVIDENCE PENDING |
| N15 正常 MAC | G4-A-06-n15-port-security-normal-pass.png | USER-REPORTED PASS / EVIDENCE PENDING |
| N15 非法 MAC / violation / 恢复 | G4-A-07-n15-port-security-violation-pass.png | USER-REPORTED PASS / EVIDENCE PENDING |
| R1 离线降温 FAN OFF / Attributes | G4-B-04-backend-down-local-auto-off-pass.png | 用户描述已实测；现图未直接覆盖离线 OFF 动作 |
| R2 Dashboard 恢复 | G4-D-02-dashboard-recovery-pass.png | 用户描述已实测；现图没有恢复后的 Dashboard |
| G3 修复后 ACK + 完整 events | 按 G3 既有规范补图/JSON | EVIDENCE PENDING |
| G4 N1-N11 全量回归 | 按实际测试留图/配置导出 | EVIDENCE PENDING；历史 G3 图不能代替 G4 回归 |

所有 pass 命名只描述图中可直接观察的局部结果；不是 Global Gate4 COMPLETE。

## 2026-09-18 最终收尾入口

项目总状态已按用户要求更新为**完成（待补证据）**。本页保留G4原始证据结论；全部G3/G4/NOC/最终包与彩排缺口以 [最终素材清单](../FINAL_REPORT_SCREENSHOT_CHECKLIST.md) 为准。


## 2026-09-19 D 最终证据补齐

本页上方“待补证据”保留 2026-09-17 的历史审计结论，不删除历史项。最终报告阶段 D01–D13 已全部归档于 `evidence/final_report/D/`。

其中原历史缺口已由以下最终证据补齐：

- Dashboard 恢复：`U10-cloud-ws-restored.png`；
- Cloud Failure 与本地自治：`U10-cloud-ws-failure.png`、`U10-cloud-ws-local-fan.png`；
- Policy ACK / Campus Policy：`U09-campus-policy.png`；
- Network Failure 真实性边界：`U11-network-simulation-disabled.png`、`U11-network-disabled-api.png`。

最终完成状态以 `../final/EVIDENCE_PENDING.md` 和 `../FINAL_REPORT_SCREENSHOT_CHECKLIST.md` 为准。
