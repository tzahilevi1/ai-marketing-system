"""Campaign Manager Agent — world-class paid media specialist."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class CampaignManagerAgent(BaseAgent):
    name = "campaign_manager"
    role = "Head of Performance Marketing"
    emoji = "🚀"
    system_prompt = """You are the world's best performance marketing manager at an AI marketing agency. You have:
- 15+ years managing paid media across Meta, Google, TikTok, LinkedIn, YouTube
- Proven track record of 10x ROAS improvements and 60%+ CPA reductions
- Deep expertise in: audience segmentation, bid strategies, creative testing, funnel optimization
- Mastery of: lookalike audiences, retargeting sequences, dynamic ads, conversion APIs
- Data-driven mindset — every decision backed by numbers and A/B tests
- Ability to scale winning campaigns from $1K to $1M/month budgets

Your responsibilities:
- Receive the ad account briefing and build a full campaign strategy
- Allocate budget across channels based on historical ROAS data
- Design audience segmentation and targeting strategy
- Specify creative requirements for graphic_designer and video_editor
- Set up campaign structure (campaigns > ad sets > ads)
- Implement bidding strategies optimized for each funnel stage
- Execute changes immediately when analytics_director gives directives
- Report results to analytics_director and ceo weekly

Campaign frameworks you use:
- TOFU/MOFU/BOFU funnel structure
- Always-on + burst campaign model
- Creative rotation to combat ad fatigue
- Dayparting and geo-targeting optimization
- Incrementality testing to measure true impact"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = 0
        self._account_briefed = False
        self._campaigns_launched = 0

    async def handle_message(self, msg):
        await super().handle_message(msg)

        # Receive analytics directives and execute
        if msg.type == MessageType.DIRECTIVE and msg.from_agent == "analytics_director":
            await self._execute_directive(msg.content, msg.subject)

        # Receive account briefing from system/ceo
        elif msg.type == MessageType.TASK and "account" in msg.subject.lower():
            await self._build_campaign_strategy(msg.content)

        # Respond to any task
        elif msg.type == MessageType.TASK:
            await self._handle_campaign_task(msg.content, msg.subject)

    async def _build_campaign_strategy(self, brief: str):
        """Build comprehensive campaign strategy from account brief."""
        strategy = await self.think(
            f"""You have received a new ad account briefing. Build a complete campaign strategy.

Account Brief:
{brief}

Deliver a full campaign strategy including:

## 1. Account Audit & Baseline
- Current state assessment
- Benchmark KPIs to beat

## 2. Campaign Architecture
- Campaign structure across all relevant channels
- Budget allocation per channel (with % justification)
- Campaign objectives per funnel stage

## 3. Audience Strategy
- Core audiences (demographics, interests, behaviors)
- Lookalike audiences (seed lists and sizes)
- Retargeting sequences (days 1, 3, 7, 14, 30)
- Exclusion lists

## 4. Bidding Strategy
- Bid type per campaign (CPC, CPM, CPA, ROAS target)
- Starting bids and scaling triggers
- Budget pacing rules

## 5. Creative Requirements
- Ad formats needed per channel
- Copy angles to test (5 hypotheses)
- Visual styles to test
- CTA variations

## 6. 30-60-90 Day Action Plan
- Week 1: Setup and launch
- Month 1: Learning phase targets
- Month 2: Optimization phase
- Month 3: Scale phase

## 7. Success Metrics
- Primary KPIs with targets
- Secondary KPIs
- Reporting cadence""",
            max_tokens=3000,
        )
        self._account_briefed = True
        self._campaigns_launched += 1

        # Request budget approval from CEO
        approved, reason = await self.request_approval(
            from_who="ceo",
            subject=f"Campaign Strategy — Budget Approval Required",
            details=f"Campaign #{self._campaigns_launched} strategy ready. Need budget approval.\n\n{strategy[:500]}...",
            timeout=25.0,
        )

        # Send strategy to analytics_director for alignment
        await self.send(
            to="analytics_director",
            subject=f"Campaign Strategy #{self._campaigns_launched} — Ready for Analytics Alignment",
            content=strategy,
            msg_type=MessageType.REPORT,
            priority=Priority.HIGH,
        )

        # Request creative assets
        await self.send(
            to="graphic_designer",
            subject="Creative Brief: Campaign Assets Needed",
            content=f"Need the following creative assets for campaigns:\n\n{strategy}",
            msg_type=MessageType.TASK,
            priority=Priority.HIGH,
        )

        await self.send(
            to="video_editor",
            subject="Video Brief: Ad Videos Needed",
            content=f"Need video ad assets for campaigns:\n\n{strategy}",
            msg_type=MessageType.TASK,
        )

        # Report to PM
        await self.send(
            to="project_manager",
            subject=f"Campaign Strategy #{self._campaigns_launched} Launched",
            content=f"Campaign strategy built and approved. Assets requested.\n\nHighlights:\n{strategy[:300]}...",
            msg_type=MessageType.REPORT,
        )

    async def _execute_directive(self, directive: str, subject: str):
        """Execute optimization directive from analytics_director."""
        execution_plan = await self.think(
            f"""You received an optimization directive from the Analytics Director:

Subject: {subject}
Directive: {directive}

As the world's best performance marketer, create a precise execution plan:

1. **Immediate actions** (do today, within hours)
2. **This week actions** (structural changes)
3. **Expected impact** (quantified predictions)
4. **Risk assessment** (what could go wrong)
5. **Success measurement** (how we know it worked, in days)

Be specific — exact bid adjustments, exact audience changes, exact budget moves.""",
            max_tokens=2000,
        )

        # Report execution back to analytics_director
        await self.send(
            to="analytics_director",
            subject=f"Executing Directive: {subject}",
            content=execution_plan,
            msg_type=MessageType.REPORT,
            priority=Priority.HIGH,
        )

        # Inform project_manager
        await self.send(
            to="project_manager",
            subject=f"Campaign Optimization Underway: {subject}",
            content=f"Executing analytics directive.\n\nPlan:\n{execution_plan[:300]}...",
            msg_type=MessageType.REPORT,
        )

    async def _handle_campaign_task(self, content: str, subject: str):
        """Handle general campaign tasks."""
        response = await self.think(
            f"Campaign task received: {subject}\n\nDetails: {content}\n\nProvide your expert campaign response.",
            max_tokens=1500,
        )
        await self.send(
            to="analytics_director",
            subject=f"Campaign Update: {subject}",
            content=response,
            msg_type=MessageType.REPORT,
        )

    async def do_work(self):
        self._cycle += 1

        # Cycle 3: Launch initial account assessment if not briefed
        if self._cycle == 3 and not self._account_briefed:
            await self._build_campaign_strategy(
                "AI Marketing Platform — SaaS product targeting SMBs and marketing agencies. "
                "Goal: acquire new users at <$50 CPA. Product: monthly subscription $99-$499/mo. "
                "Budget: $10,000/month. Channels available: Meta, Google, LinkedIn."
            )

        # Every 12 cycles: send performance pulse to analytics_director
        elif self._cycle % 12 == 0 and self._account_briefed:
            pulse = await self.think(
                "Generate a campaign performance pulse report. Include: "
                "estimated CTR ranges, audience saturation warning levels, creative fatigue indicators, "
                "budget pacing status, and top optimization opportunities. Keep it concise.",
                max_tokens=800,
            )
            await self.send(
                to="analytics_director",
                subject="Campaign Performance Pulse",
                content=pulse,
                msg_type=MessageType.REPORT,
                priority=Priority.HIGH,
            )
