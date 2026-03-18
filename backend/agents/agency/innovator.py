"""Innovation Agent — generates new feature ideas and growth strategies."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class InnovatorAgent(BaseAgent):
    name = "innovator"
    role = "Chief Innovation Officer"
    emoji = "💡"
    system_prompt = """You are the Chief Innovation Officer of an AI marketing agency. You:
- Constantly think about emerging trends in AI, marketing, and technology
- Generate bold, creative ideas for new features and capabilities
- Research competitor offerings and identify gaps
- Propose experiments and A/B tests to improve performance
- Think about future product roadmap (6-12 months out)
- Present ideas clearly with business value and implementation effort
- Submit promising ideas to CEO for approval
Areas of focus: AI/ML innovations, automation opportunities, UX improvements, new ad channels, analytics insights"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = 0
        self._ideas_submitted = 0

    async def handle_message(self, msg):
        await super().handle_message(msg)
        if msg.type == MessageType.TASK:
            await self._generate_ideas(msg.content)

    async def _generate_ideas(self, context: str = ""):
        self._ideas_submitted += 1
        ideas = self.think(
            f"""Generate 5 innovative feature ideas for an AI marketing automation platform.
Context: {context or 'Building a platform that replaces a marketing team with AI agents'}

For each idea include:
- Feature name
- What problem it solves
- Business value (revenue impact)
- Implementation effort (Low/Medium/High)
- Why now is the right time

Focus on: AI-native features, automation, personalization, predictive analytics, creative tools.""",
            max_tokens=2048,
        )
        # Send to CEO for approval
        approved, reason = await self.request_approval(
            from_who="ceo",
            subject=f"Innovation Proposals #{self._ideas_submitted}",
            details=ideas,
            timeout=20.0,
        )
        if approved:
            await self.send(
                to="project_manager",
                subject="CEO-Approved Ideas — Add to Roadmap",
                content=f"CEO approved these innovations:\n\n{ideas}",
                msg_type=MessageType.REPORT,
                priority=Priority.HIGH,
            )
        return ideas

    async def do_work(self):
        self._cycle += 1
        if self._cycle == 7:
            await self._generate_ideas()
