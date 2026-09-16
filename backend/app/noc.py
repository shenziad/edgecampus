"""NOC REST APIs; no extension to Protocol v1.0 messages."""
from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool
from .pt_controller import controller_from_environment
from .network_agent import NetworkAgent

router = APIRouter(prefix="/api", tags=["NOC"])
agent = NetworkAgent(controller=controller_from_environment())


@router.get("/network/state")
async def network_state():
    return await run_in_threadpool(agent.snapshot)


@router.get("/network/events")
async def network_events():
    return {"source": "SIMULATED", "events": agent.event_history()}


from typing import Literal
from pydantic import BaseModel, ConfigDict

class SecurityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event: Literal["PORT_SECURITY_VIOLATION", "ACL_BLOCK_EVENT"] = "PORT_SECURITY_VIOLATION"

@router.get("/security/state")
async def security_state():
    return agent.security_snapshot()

@router.post("/simulation/security")
async def security_attack(request: SecurityRequest):
    return agent.security_attack(request.event)

@router.post("/simulation/security/restore")
async def security_restore():
    return agent.restore_security()


cloud_failed = False
sync_status = "NOT_RUN"

class BranchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device: Literal["R-BRANCH", "SW-BRANCH"]
    source_ip: str = "192.168.30.20"

@router.post("/branch/check")
async def branch_check(request: BranchRequest):
    return agent.check_device(request.device, request.source_ip)

@router.get("/branch/state")
async def branch_state():
    baseline = agent.provider.get_state()["management"]
    return {"source": "SIMULATED", "allowed_source": baseline["allowed_source"],
            "devices": [agent.check_device(device, baseline["allowed_source"]) for device in baseline["devices"]]}

@router.get("/campus-policy")
async def campus_policy():
    from . import main
    baseline = agent.provider.get_state()["campus_policy"]
    return {**baseline, "campus_version": f"campus-{baseline['version']} / thermal-v{main.state.policy['version']}",
            "thermal": dict(main.state.policy), "source": "Edge policy live; network/security configuration overlay",
            "edge_ack": "See existing Policy ACK; desired policy alone does not prove application"}

@router.post("/simulation/network")
async def network_failure():
    if agent.controller is not None:
        raise HTTPException(409, "真实控制器模式不允许用模拟故障覆盖观测结果")
    return agent.set_network_failure(True)

@router.post("/simulation/network/restore")
async def network_restore():
    if agent.controller is not None:
        raise HTTPException(409, "真实控制器模式没有模拟网络故障需要恢复")
    return agent.set_network_failure(False)

@router.get("/simulation/state")
async def simulation_state():
    from . import main
    return {"cloud": "OFFLINE" if cloud_failed else "ONLINE", "cloud_failed": cloud_failed,
            "edge_connected": main.state.edge_online,
            "edge_mode": "AUTONOMOUS MODE (expected)" if cloud_failed and main.state.policy["mode"] == "AUTO" else main.state.policy["mode"],
            "fan": main.state.fan_state, "fan_observation": "LAST KNOWN · live telemetry unavailable" if cloud_failed or not main.state.edge_online else "LIVE EDGE TELEMETRY",
            "state_sync": sync_status, "network_failed": agent.network_failed,
            "source": "Control-channel outage drill; HTTP backend stays available"}

@router.post("/simulation/cloud")
async def cloud_failure():
    global cloud_failed, sync_status
    from . import main
    if not cloud_failed:
        cloud_failed = True
        sync_status = "WAITING_FOR_RECOVERY"
        socket = main.edge_socket
        main.edge_socket = None
        main.state.mark_edge_offline()
        await main.broadcast_snapshot()
        if socket is not None:
            await socket.close(code=1013, reason="Cloud failure drill")
        agent.record("CLOUD", "CONTROL_CHANNEL_DOWN", "Real Edge WebSocket closed; HTTP recovery remains available")
    return await simulation_state()

@router.post("/simulation/cloud/restore")
async def cloud_restore():
    global cloud_failed, sync_status
    if cloud_failed:
        cloud_failed = False
        sync_status = "WAITING_FOR_STATE_SYNC"
        agent.record("CLOUD", "CONTROL_CHANNEL_RESTORED", "Awaiting actual Edge reconnect and state_sync")
    return await simulation_state()

@router.get("/noc/state")
async def noc_state():
    return {"network": await run_in_threadpool(agent.snapshot), "security": agent.security_snapshot(),
            "branch": await branch_state(), "policy": await campus_policy(),
            "simulation": await simulation_state(), "events": agent.event_history()}


@router.get("/controller/state")
async def controller_state():
    if agent.controller is None:
        return {"configured": False, "status": "NOT_CONFIGURED", "devices": [], "topology": None,
                "source": "PT_CONTROLLER", "error": "设置 PT_CONTROLLER_URL、PT_CONTROLLER_USERNAME、PT_CONTROLLER_PASSWORD 后重启 Backend"}
    return await run_in_threadpool(agent.controller.snapshot)
