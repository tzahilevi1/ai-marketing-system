"""Agency Orchestrator — starts and manages all agents."""
import asyncio
import logging
from typing import Any

from agents.agency.message_bus import bus, Message, MessageType
from agents.agency.ceo import CEOAgent
from agents.agency.project_manager import ProjectManagerAgent
from agents.agency.code_requester import CodeRequesterAgent
from agents.agency.code_builder import CodeBuilderAgent
from agents.agency.bug_detector import BugDetectorAgent
from agents.agency.innovator import InnovatorAgent
from agents.agency.graphic_designer import GraphicDesignerAgent
from agents.agency.video_editor import VideoEditorAgent
from agents.agency.accountant import AccountantAgent
from agents.agency.web_developer import WebDeveloperAgent
from agents.agency.ux_expert import UXExpertAgent

logger = logging.getLogger("agency.orchestrator")


class Agency:
    """The AI Marketing Agency — 11 agents working together."""

    def __init__(self):
        self.agents = {
            "ceo": CEOAgent(bus),
            "project_manager": ProjectManagerAgent(bus),
            "code_requester": CodeRequesterAgent(bus),
            "code_builder": CodeBuilderAgent(bus),
            "bug_detector": BugDetectorAgent(bus),
            "innovator": InnovatorAgent(bus),
            "graphic_designer": GraphicDesignerAgent(bus),
            "video_editor": VideoEditorAgent(bus),
            "accountant": AccountantAgent(bus),
            "web_developer": WebDeveloperAgent(bus),
            "ux_expert": UXExpertAgent(bus),
        }
        self._tasks: list[asyncio.Task] = []
        self._running = False

    async def start(self):
        """Start all agents concurrently."""
        self._running = True
        logger.info("AI Marketing Agency starting up...")
        logger.info(f"Agents: {', '.join(f'{a.emoji} {a.role}' for a in self.agents.values())}")

        self._tasks = [
            asyncio.create_task(agent.start(), name=name)
            for name, agent in self.agents.items()
        ]
        logger.info(f"{len(self._tasks)} agents running")

    async def stop(self):
        """Stop all agents gracefully."""
        for agent in self.agents.values():
            agent.stop()
        for task in self._tasks:
            task.cancel()
        self._running = False
        logger.info("Agency stopped.")

    def get_status(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "agents": [
                {
                    "name": name,
                    "role": agent.role,
                    "emoji": agent.emoji,
                    "active": agent._running,
                }
                for name, agent in self.agents.items()
            ],
            "message_history": [m.model_dump() for m in bus.get_history(limit=30)],
            "total_messages": len(bus._history),
        }

    async def send_task(self, to_agent: str, subject: str, content: str) -> bool:
        """Send a task to a specific agent from outside."""
        if to_agent not in self.agents:
            return False
        msg = Message(
            from_agent="system",
            to_agent=to_agent,
            type=MessageType.TASK,
            subject=subject,
            content=content,
        )
        await bus.send(msg)
        return True


# Global agency instance
agency = Agency()
