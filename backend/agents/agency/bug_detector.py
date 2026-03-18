"""Bug Detector Agent — reviews code, finds bugs, security issues, and quality problems."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class BugDetectorAgent(BaseAgent):
    name = "bug_detector"
    role = "QA Engineer / Security Reviewer"
    emoji = "🐛"
    system_prompt = """You are a senior QA Engineer and Security Reviewer. You:
- Review code for bugs, logic errors, and edge cases
- Check for security vulnerabilities (SQL injection, XSS, auth issues, exposed secrets)
- Verify error handling is complete
- Check for performance issues (N+1 queries, missing indexes, unoptimized loops)
- Ensure code follows project conventions
- Write test cases for untested code
- If critical bugs found: alert Project Manager immediately
- If code passes: approve and notify Code Builder
Severity levels: CRITICAL (security/data loss), HIGH (crashes), MEDIUM (wrong behavior), LOW (style/perf)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reviews_done = 0

    async def handle_message(self, msg):
        await super().handle_message(msg)
        if msg.type == MessageType.TASK and "review" in msg.subject.lower():
            await self._review_code(msg)

    async def _review_code(self, msg):
        self._reviews_done += 1
        review = self.think(
            f"""Perform a thorough code review:

Code/Feature: {msg.subject}
Content:
{msg.content}

Review for:
1. Bugs and logic errors
2. Security vulnerabilities
3. Missing error handling
4. Performance issues
5. Code quality

Format your response:
## Overall: PASS / FAIL / PASS WITH NOTES
## Critical Issues: (list any)
## Warnings: (list any)
## Suggestions: (list improvements)
## Test Cases: (write 3 test scenarios)""",
            max_tokens=2048,
        )
        passed = "FAIL" not in review.upper() or "PASS" in review
        severity = "critical" if "CRITICAL" in review.upper() else "normal"

        # Notify code builder of results
        await self.send(
            to="code_builder",
            subject=f"{'Review PASSED' if passed else 'Review FAILED'}: {msg.subject}",
            content=review,
            msg_type=MessageType.REPORT,
            priority=Priority.HIGH if not passed else Priority.NORMAL,
        )
        # If critical issues, alert PM
        if severity == "critical":
            await self.send(
                to="project_manager",
                subject=f"CRITICAL ISSUE FOUND: {msg.subject}",
                content=review,
                msg_type=MessageType.ALERT,
                priority=Priority.CRITICAL,
            )
        else:
            await self.send(
                to="project_manager",
                subject=f"Code Review Complete ({self._reviews_done} total): {msg.subject}",
                content=f"Result: {'PASSED' if passed else 'FAILED'}\n\n{review[:300]}...",
                msg_type=MessageType.REPORT,
            )

    async def do_work(self):
        pass  # reactive only
