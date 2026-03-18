"""Base class for all agency agents."""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

import anthropic

from agents.agency.message_bus import Message, MessageBus, MessageType, Priority, bus
from config import settings

logger = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
MODEL = "claude-sonnet-4-20250514"


class BaseAgent(ABC):
    """Base agent class. All agents inherit from this."""

    name: str = "base"
    role: str = "Base Agent"
    emoji: str = "🤖"
    system_prompt: str = ""

    def __init__(self, message_bus: MessageBus = None):
        self.bus = message_bus or bus
        self.bus.register_agent(self.name)
        self._running = False
        self._pending_approvals: dict[str, asyncio.Future] = {}
        self.log = logging.getLogger(f"agency.{self.name}")

    def think(self, prompt: str, context: str = "", max_tokens: int = 2048) -> str:
        """Ask Claude to think and respond."""
        if context:
            user_content = f"Context:\n{context}\n\n{prompt}"
        else:
            user_content = prompt
        messages = [{"role": "user", "content": user_content}]
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                system=self.system_prompt or f"You are {self.role} in an AI marketing agency. Be concise and professional.",
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            self.log.error(f"Think error: {e}")
            return f"[{self.name}] Error: {e}"

    async def send(self, to: str, subject: str, content: str, msg_type: MessageType = MessageType.REPORT,
                   data: dict = None, priority: Priority = Priority.NORMAL, requires_approval: bool = False) -> Message:
        msg = Message(
            from_agent=self.name,
            to_agent=to,
            type=msg_type,
            subject=subject,
            content=content,
            data=data or {},
            priority=priority,
            requires_approval=requires_approval,
        )
        await self.bus.send(msg)
        self.log.info(f"-> {to}: [{msg_type}] {subject}")
        return msg

    async def broadcast(self, subject: str, content: str, msg_type: MessageType = MessageType.REPORT):
        await self.send("broadcast", subject, content, msg_type)

    async def request_approval(self, from_who: str, subject: str, details: str, timeout: float = 30.0) -> tuple[bool, str]:
        """Send approval request and wait for response."""
        msg = await self.send(
            to=from_who,
            subject=f"APPROVAL NEEDED: {subject}",
            content=details,
            msg_type=MessageType.APPROVAL_REQUEST,
            requires_approval=True,
        )
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending_approvals[msg.id] = future
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            return True, "Auto-approved (timeout)"  # default auto-approve on timeout

    async def handle_approval_request(self, msg: Message) -> tuple[bool, str]:
        """Decide whether to approve a request. Override in subclasses."""
        decision = self.think(
            f"An approval request was received:\n\nFrom: {msg.from_agent}\nSubject: {msg.subject}\n\nDetails:\n{msg.content}\n\nShould you approve this? Reply with APPROVE or REJECT and a brief reason.",
        )
        approved = "APPROVE" in decision.upper()
        return approved, decision

    async def handle_message(self, msg: Message):
        """Process incoming messages. Override for custom behavior."""
        if msg.type == MessageType.APPROVAL_REQUEST:
            approved, reason = await self.handle_approval_request(msg)
            await self.send(
                to=msg.from_agent,
                subject=f"{'APPROVED' if approved else 'REJECTED'}: {msg.subject}",
                content=reason,
                msg_type=MessageType.APPROVAL_RESPONSE,
                data={"approved": approved, "original_id": msg.id},
            )
        elif msg.type == MessageType.APPROVAL_RESPONSE and msg.data.get("original_id") in self._pending_approvals:
            future = self._pending_approvals.pop(msg.data["original_id"])
            if not future.done():
                future.set_result((msg.data.get("approved", True), msg.content))

    async def run_once(self):
        """Run one cycle: check messages + do work."""
        msg = await self.bus.receive(self.name, timeout=1.0)
        if msg:
            await self.handle_message(msg)
        await self.do_work()

    @abstractmethod
    async def do_work(self):
        """Main agent work loop. Implement in each agent."""
        pass

    async def start(self):
        """Start the agent loop."""
        self._running = True
        self.log.info(f"{self.emoji} {self.role} started")
        while self._running:
            try:
                await self.run_once()
                await asyncio.sleep(2)
            except Exception as e:
                self.log.error(f"Error in {self.name}: {e}")
                await asyncio.sleep(5)

    def stop(self):
        self._running = False
