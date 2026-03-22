"""API endpoints for the AI Agency — start, monitor, interact."""
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from agents.agency.orchestrator import agency

router = APIRouter(prefix="/agency", tags=["agency"])

_agency_started = False


@router.post("/start")
async def start_agency(background_tasks: BackgroundTasks):
    global _agency_started
    if _agency_started:
        return {"status": "already_running", "message": "Agency is already running"}
    _agency_started = True
    background_tasks.add_task(agency.start)
    return {
        "status": "started",
        "agents": [f"{a.emoji} {a.role}" for a in agency.agents.values()],
        "message": "All 11 agents are now running autonomously",
    }


@router.post("/stop")
async def stop_agency():
    global _agency_started
    await agency.stop()
    _agency_started = False
    return {"status": "stopped"}


@router.get("/status")
async def get_status():
    return agency.get_status()


@router.get("/messages")
async def get_messages(limit: int = 50):
    from agents.agency.message_bus import bus
    return {
        "messages": [m.model_dump() for m in bus.get_history(limit=limit)],
        "total": len(bus._history),
    }


class TaskRequest(BaseModel):
    to_agent: str
    subject: str
    content: str


@router.post("/task")
async def send_task(task: TaskRequest):
    success = await agency.send_task(task.to_agent, task.subject, task.content)
    if not success:
        raise HTTPException(status_code=404, detail=f"Agent '{task.to_agent}' not found")
    return {"status": "sent", "to": task.to_agent, "subject": task.subject}


@router.get("/agents")
async def list_agents():
    return {
        "agents": [
            {"name": name, "role": a.role, "emoji": a.emoji}
            for name, a in agency.agents.items()
        ]
    }
