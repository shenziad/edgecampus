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
