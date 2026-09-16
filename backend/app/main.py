"""EdgeCampus FastAPI control plane."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .protocol import ProtocolError, envelope, validate_message
from .state import SystemState
from .noc import router as noc_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOGGER = logging.getLogger("edgecampus")
ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "dashboard"
RUNTIME = ROOT / "runtime"
EVENT_LOG = RUNTIME / "events.jsonl"

app = FastAPI(title="EdgeCampus Control Plane", version="0.1.0")
app.include_router(noc_router)
app.mount("/static", StaticFiles(directory=DASHBOARD), name="static")

state = SystemState()
edge_socket: WebSocket | None = None
dashboard_sockets: set[WebSocket] = set()


def append_event_log(message: dict[str, Any]) -> None:
    RUNTIME.mkdir(exist_ok=True)
    with EVENT_LOG.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(message, ensure_ascii=False) + "\n")


async def broadcast_snapshot() -> None:
    dead: list[WebSocket] = []
    payload = state.snapshot()
    for socket in dashboard_sockets:
        try:
            await socket.send_json(payload)
        except Exception:
            dead.append(socket)
    for socket in dead:
        dashboard_sockets.discard(socket)


async def send_error(socket: WebSocket, code: str, message: str) -> None:
    await socket.send_json(envelope("error", code=code, message=message))


@app.get("/")
async def dashboard() -> FileResponse:
    return FileResponse(DASHBOARD / "index.html")


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {"status": "ok", "edge_online": state.edge_online}


@app.get("/api/state")
async def api_state() -> dict[str, Any]:
    return state.snapshot()


@app.websocket("/ws/edge")
async def edge_websocket(socket: WebSocket) -> None:
    global edge_socket
    await socket.accept()
    edge_socket = socket
    LOGGER.info("edge connected")
    try:
        while True:
            try:
                raw = await socket.receive_json()
            except json.JSONDecodeError:
                await send_error(socket, "INVALID_MESSAGE", "invalid JSON text")
                continue
            try:
                message = validate_message(raw)
            except ProtocolError as exc:
                await send_error(socket, "INVALID_MESSAGE", str(exc))
                continue
            state.apply_edge_message(message)
            append_event_log(message)
            await broadcast_snapshot()
    except WebSocketDisconnect:
        LOGGER.info("edge disconnected")
    finally:
        if edge_socket is socket:
            edge_socket = None
            state.mark_edge_offline()
            await broadcast_snapshot()


@app.websocket("/ws/dashboard")
async def dashboard_websocket(socket: WebSocket) -> None:
    await socket.accept()
    dashboard_sockets.add(socket)
    await socket.send_json(state.snapshot())
    try:
        while True:
            try:
                raw = await socket.receive_json()
            except json.JSONDecodeError:
                await send_error(socket, "INVALID_MESSAGE", "invalid JSON text")
                continue
            try:
                message = validate_message(raw)
            except ProtocolError as exc:
                await send_error(socket, "INVALID_MESSAGE", str(exc))
                continue

            if message["type"] not in {"command", "policy"}:
                await send_error(
                    socket,
                    "UNSUPPORTED_FROM_DASHBOARD",
                    "dashboard may send only command or policy",
                )
                continue

            if edge_socket is None:
                await send_error(socket, "EDGE_OFFLINE", "edge is not connected")
                continue

            state.apply_dashboard_message(message)
            append_event_log(message)
            await edge_socket.send_json(message)
            await broadcast_snapshot()
    except WebSocketDisconnect:
        dashboard_sockets.discard(socket)
