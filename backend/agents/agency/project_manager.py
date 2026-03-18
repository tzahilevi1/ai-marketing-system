"""Project Manager Agent — coordinates all agents, manages tasks and timeline."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class ProjectManagerAgent(BaseAgent):
    name = "project_manager"
    role = "Project Manager"
    emoji = "📋"
    system_prompt = """You are the Project Manager of an AI marketing agency. You:
- Break down campaign briefs into specific tasks
- Assign tasks to the right agents (code_builder, graphic_designer, etc.)
- Track progress and deadlines
- Escalate blockers to CEO
- Send weekly status reports
- Coordinate between all departments
- Manage sprints and deliverables
You report to: CEO
You manage: Code Requester, Code Builder, Bug Detector, Graphic Designer, Video Editor"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = 0
        self._tasks: list[dict] = []
        self._initialized = False

    async def do_work(self):
        self._cycle += 1

        if self._cycle == 3 and not self._initialized:
            self._initialized = True
            # Assign initial tasks to team
            await self.send(
                to="code_builder",
                subject="Sprint 1 Task: Build Content Generation API",
                content="Please build and test the /api/content/generate endpoint. Ensure it accepts a CampaignBrief and returns 3 AdCopy variants. The code is in backend/api/content.py and backend/agents/content_agent.py",
                msg_type=MessageType.TASK,
                priority=Priority.HIGH,
            )
            await self.send(
                to="graphic_designer",
                subject="Sprint 1 Task: Design System & Component Library",
                content="Create a comprehensive design brief for the dashboard UI. Define: color palette, typography, component styles for KPI cards, charts, and buttons. Output as design specs.",
                msg_type=MessageType.TASK,
            )
            await self.send(
                to="bug_detector",
                subject="Sprint 1 Task: Code Review & Testing",
                content="Review the backend agents (content_agent.py, image_agent.py, campaign_agent.py, analytics_agent.py) for bugs, missing error handling, and code quality issues.",
                msg_type=MessageType.TASK,
            )
            await self.send(
                to="innovator",
                subject="Request: New Feature Ideas for Q1",
                content="We have a marketing automation platform. What innovative AI-powered features could differentiate us? Focus on features that would wow enterprise clients.",
                msg_type=MessageType.TASK,
            )

        # Every 15 cycles, compile and send status to CEO
        elif self._cycle % 15 == 0:
            status = self.think(
                f"Compile a project status report for the CEO. Tasks completed: {len(self._tasks)}. Focus on progress, risks, and next steps. Keep it under 200 words."
            )
            await self.send(
                to="ceo",
                subject="Weekly Status Report",
                content=status,
                msg_type=MessageType.REPORT,
                priority=Priority.HIGH,
            )
