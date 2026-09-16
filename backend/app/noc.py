"""NOC REST APIs; no extension to Protocol v1.0 messages."""
from fastapi import APIRouter
from .network_agent import NetworkAgent

router = APIRouter(prefix="/api", tags=["NOC"])
agent = NetworkAgent()


@router.get("/network/state")
async def network_state():
    return agent.snapshot()


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
