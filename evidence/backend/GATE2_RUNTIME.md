# C Backend 当前运行入口（Gate 2）

分支：`feat/backend`

## 启动

```bat
cd C:\Users\33621\edgecampus
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

组内若使用虚拟环境激活：

```text
.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

本机若 `python` 指向 MSYS2，必须改用 `.venv\Scripts\python.exe`。联调建议不加 `--reload`。

## 检查

```text
http://127.0.0.1:8000/healthz
http://127.0.0.1:8000/api/state
http://127.0.0.1:8000/
```

## 连接

```text
本机 PT：     ws://127.0.0.1:8000/ws/edge
Radmin VPN：  ws://26.181.160.200:8000/ws/edge
```

Gate 2 联调期间不要同时运行 `python -m edge.fake_edge`。
