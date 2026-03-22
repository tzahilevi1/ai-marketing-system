"""Code Builder Agent — writes and implements code based on specs."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class CodeBuilderAgent(BaseAgent):
    name = "code_builder"
    role = "Senior Software Engineer"
    emoji = "👨‍💻"
    system_prompt = """You are a Senior Software Engineer in an AI marketing agency. You:
- Write clean, production-quality Python and TypeScript code
- Follow the project's patterns (FastAPI, SQLAlchemy 2.0, React 18, Tailwind)
- Always use type hints in Python and TypeScript types in frontend code
- Write code with error handling and logging
- After writing code, send it to Bug Detector for review
- Request approval from Project Manager before merging major changes
- Use claude-sonnet-4-20250514 for all AI calls in the code you write
Tech stack: Python/FastAPI backend, React/TypeScript frontend, PostgreSQL, Redis, Celery"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tasks_received: list[str] = []
        self._cycle = 0

    async def handle_message(self, msg):
        await super().handle_message(msg)
        if msg.type == MessageType.TASK:
            self._tasks_received.append(msg.subject)
            await self._process_task(msg)

    async def _process_task(self, msg):
        code = await self.think(
            f"""You received a development task:

Task: {msg.subject}
Details: {msg.content}

Write the implementation code. Include:
1. The actual code (Python or TypeScript as appropriate)
2. Brief explanation of key decisions
3. Any dependencies that need to be installed
4. Test cases to verify it works

Be thorough but practical.""",
            max_tokens=4096,
        )
        # Send to bug detector for review
        await self.send(
            to="bug_detector",
            subject=f"Code Review Request: {msg.subject}",
            content=code,
            msg_type=MessageType.TASK,
            priority=Priority.NORMAL,
        )
        # Report progress to PM
        await self.send(
            to="project_manager",
            subject=f"Code Written: {msg.subject}",
            content=f"Implementation complete. Sent to bug_detector for review.\n\nSummary:\n{code[:500]}...",
            msg_type=MessageType.REPORT,
        )

    async def do_work(self):
        self._cycle += 1
