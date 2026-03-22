"""Code Requester Agent — analyzes requirements and creates technical specs."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class CodeRequesterAgent(BaseAgent):
    name = "code_requester"
    role = "Technical Lead / Code Requester"
    emoji = "📝"
    system_prompt = """You are the Technical Lead who translates business requirements into precise technical specifications. You:
- Analyze feature requests and business needs
- Write detailed technical specs (function signatures, data models, API contracts)
- Identify dependencies and technical risks
- Create acceptance criteria for each feature
- Prioritize technical debt vs new features
- Must get approval from Project Manager before sending specs to Code Builder
You report to: Project Manager
You work with: Code Builder, Bug Detector"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = 0
        self._spec_created = False

    async def do_work(self):
        self._cycle += 1

        if self._cycle == 5 and not self._spec_created:
            self._spec_created = True
            spec = await self.think(
                """Create a detailed technical specification for implementing a Campaign Analytics Dashboard feature.
Include:
1. API endpoints needed (with request/response schemas)
2. Database queries required
3. Frontend components to build
4. Integration points with existing agents
5. Acceptance criteria
Keep it technical and precise."""
            )
            # Request approval from PM before proceeding
            approved, reason = await self.request_approval(
                from_who="project_manager",
                subject="Technical Spec: Campaign Analytics Dashboard",
                details=spec,
                timeout=15.0,
            )
            if approved:
                await self.send(
                    to="code_builder",
                    subject="Approved Spec: Campaign Analytics Dashboard",
                    content=spec,
                    msg_type=MessageType.TASK,
                    priority=Priority.HIGH,
                )
            else:
                await self.send(
                    to="project_manager",
                    subject="Spec Revision Needed",
                    content=f"Spec was rejected: {reason}. Will revise and resubmit.",
                    msg_type=MessageType.REPORT,
                )
