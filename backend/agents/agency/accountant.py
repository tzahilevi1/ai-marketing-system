"""Accountant Agent — tracks budget, ROI, spend, and financial health."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class AccountantAgent(BaseAgent):
    name = "accountant"
    role = "CFO / Head of Finance"
    emoji = "💰"
    system_prompt = """You are the CFO and Head of Finance for an AI marketing agency. You:
- Track campaign budgets and actual spend
- Calculate ROI and ROAS for all campaigns
- Alert when budget is over/under pacing
- Approve invoices and budget requests (under $10k auto-approve, over $10k needs CEO)
- Generate financial reports (daily P&L, weekly summary, monthly forecast)
- Identify cost optimization opportunities
- Track LTV/CAC ratios per client
- Forecast next quarter's revenue based on current performance
KPIs you own: ROAS, CPA, LTV, CAC, Margin, Budget Utilization"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = 0
        self._report_sent = False

    async def handle_message(self, msg):
        await super().handle_message(msg)
        if msg.type == MessageType.APPROVAL_REQUEST and "budget" in msg.subject.lower():
            await self._evaluate_budget_request(msg)

    async def _evaluate_budget_request(self, msg):
        decision = self.think(
            f"""Evaluate this budget request as CFO:

Request: {msg.subject}
Details: {msg.content}
From: {msg.from_agent}

Consider: business value, current budget utilization, ROI potential.
APPROVE or REJECT with financial reasoning."""
        )
        approved = "REJECT" not in decision.upper()
        amount_mentioned = any(c.isdigit() for c in msg.content)

        # Large amounts need CEO approval
        if approved and amount_mentioned:
            ceo_approved, ceo_reason = await self.request_approval(
                from_who="ceo",
                subject=f"CFO Escalation: {msg.subject}",
                details=f"CFO recommends approval:\n{decision}\n\nOriginal request:\n{msg.content}",
                timeout=20.0,
            )
            approved = ceo_approved

        await self.send(
            to=msg.from_agent,
            subject=f"{'Budget APPROVED' if approved else 'Budget REJECTED'}: {msg.subject}",
            content=decision,
            msg_type=MessageType.APPROVAL_RESPONSE,
            data={"approved": approved},
        )

    async def do_work(self):
        self._cycle += 1
        if self._cycle == 8 and not self._report_sent:
            self._report_sent = True
            report = self.think(
                """Generate a financial health report for the AI marketing agency.
Include:
- Current quarter budget status (assume $50k total budget)
- Mock P&L breakdown by channel (Meta 40%, Google 30%, TikTok 20%, Other 10%)
- ROAS performance (target: 3.5x, current estimate: 3.2x)
- Cost optimization recommendations
- Q2 revenue forecast
Format as a clean financial report.""",
                max_tokens=1500,
            )
            await self.send(
                to="ceo",
                subject="Q1 Financial Health Report",
                content=report,
                msg_type=MessageType.REPORT,
                priority=Priority.HIGH,
            )
