"""CEO Agent — sets vision, approves major decisions, leads the agency."""
import asyncio
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class CEOAgent(BaseAgent):
    name = "ceo"
    role = "Chief Executive Officer"
    emoji = "👔"
    system_prompt = """You are the CEO of an AI marketing agency. You:
- Set the strategic vision and company direction
- Approve major decisions (budget > $5000, new campaigns, pivots)
- Receive reports from all department heads
- Make final calls on disputes between agents
- Think big picture, not implementation details
- Be decisive, confident, and brief in your communications
You manage: Project Manager, Accountant, Innovation Director"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = 0
        self._directives_sent = False

    async def do_work(self):
        self._cycle += 1

        # On first cycle, send initial directive to all
        if self._cycle == 1 and not self._directives_sent:
            directive = self.think(
                "You are starting a new AI marketing campaign project. Send an opening directive to your team. Include: company vision, Q1 goals, priorities, and your expectations. Be inspiring but concise."
            )
            await self.broadcast(
                subject="Q1 Agency Directive — All Hands",
                content=directive,
                msg_type=MessageType.DIRECTIVE,
            )
            self._directives_sent = True

        # Every 10 cycles, request a status report
        elif self._cycle % 10 == 0:
            await self.send(
                to="project_manager",
                subject="Weekly Status Report Request",
                content="Please provide a full status update: what was completed, what's in progress, any blockers, and next week's priorities.",
                msg_type=MessageType.TASK,
            )

    async def handle_approval_request(self, msg):
        decision = self.think(
            f"As CEO, you received an approval request:\n\nFrom: {msg.from_agent}\nSubject: {msg.subject}\n\nDetails:\n{msg.content}\n\nConsider business impact, cost, and strategy. APPROVE or REJECT with your reasoning.",
        )
        approved = "REJECT" not in decision.upper()
        return approved, decision
