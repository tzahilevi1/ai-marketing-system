"""Shared message bus for inter-agent communication."""
import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Callable
from pydantic import BaseModel


class MessageType(str, Enum):
    TASK = "task"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESPONSE = "approval_response"
    REPORT = "report"
    IDEA = "idea"
    ALERT = "alert"
    DIRECTIVE = "directive"


class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Message(BaseModel):
    id: str = ""
    from_agent: str
    to_agent: str  # agent name or "broadcast"
    type: MessageType
    subject: str
    content: str
    data: dict[str, Any] = {}
    priority: Priority = Priority.NORMAL
    requires_approval: bool = False
    reply_to: str | None = None
    timestamp: str = ""

    def model_post_init(self, __context):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class MessageBus:
    """Central message bus - all agents subscribe and publish here."""

    def __init__(self):
        self._queues: dict[str, asyncio.Queue] = {}
        self._broadcast_queue: asyncio.Queue = asyncio.Queue()
        self._history: list[Message] = []
        self._subscribers: dict[str, list[Callable]] = {}

    def register_agent(self, name: str):
        self._queues[name] = asyncio.Queue()

    async def send(self, message: Message):
        self._history.append(message)
        if message.to_agent == "broadcast":
            for q in self._queues.values():
                await q.put(message)
        elif message.to_agent in self._queues:
            await self._queues[message.to_agent].put(message)

    async def receive(self, agent_name: str, timeout: float = 5.0) -> Message | None:
        if agent_name not in self._queues:
            return None
        try:
            return await asyncio.wait_for(self._queues[agent_name].get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def get_history(self, limit: int = 50) -> list[Message]:
        return self._history[-limit:]

    def get_agent_history(self, agent_name: str, limit: int = 20) -> list[Message]:
        relevant = [m for m in self._history if m.from_agent == agent_name or m.to_agent == agent_name]
        return relevant[-limit:]


# Global bus instance
bus = MessageBus()
