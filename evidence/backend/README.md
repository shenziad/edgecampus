# Backend evidence

WebSocket 连接、Telemetry、Policy/Command ACK、事件日志与错误处理。

## Gate 1

```text
G1-01-unittest-pass.png
G1-02-uvicorn-ws-accepted.png
G1-03-fake-edge-connected.png
G1-04-healthz-pass.png
G1-05-api-state-telemetry-pass.png
G1-06-api-state-temperature-changed-pass.png
G1-07-fan-auto-on-off-pass.png
```

说明：`docs/gate1/C_BACKEND_REPORT.md`

## Gate 2

```text
G2-C-01-healthz-edge-online-pass.png
G2-C-02-api-state-real-pt-temp-pass.png
G2-C-03-pt-environment-32-pass.png
G2-C-04-sbc-tx-telemetry-pass.png
```

说明：`evidence/backend/GATE2_C_REPORT.md`

## Gate 3

```text
G3-C-01-healthz-edge-online-pass.png
G3-C-02-dashboard-policy-v3-33-pass.png
G3-C-03-api-state-policy-v3-33-pass.png
G3-C-04-command-fan-on-remote-manual-pass.png
G3-C-04b-events-remote-manual-on-pass.png
```

说明：`evidence/backend/GATE3_C_REPORT.md`

## 运行入口

`evidence/backend/GATE2_RUNTIME.md`
