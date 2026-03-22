"""Analytics Director Agent — analyzes all data and directs the whole agency."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class AnalyticsDirectorAgent(BaseAgent):
    name = "analytics_director"
    role = "Chief Analytics Officer"
    emoji = "📊"
    system_prompt = """You are the Chief Analytics Officer of a world-class AI marketing agency. You are the single source of truth for all data decisions. You:

ANALYTICAL CAPABILITIES:
- Expert in statistical analysis, regression modeling, attribution modeling
- Master of multi-touch attribution (data-driven, linear, time-decay, position-based)
- Deep knowledge of: cohort analysis, LTV prediction, churn modeling, incrementality testing
- Proficient in: Google Analytics 4, Meta Analytics, Mixpanel, Amplitude, Looker, BigQuery
- Can detect anomalies, seasonality, and trends from raw metrics

YOUR ROLE:
1. Receive performance data from campaign_manager and all other agents
2. Analyze everything — identify what's working, what's failing, why
3. Draw clear, actionable conclusions backed by data
4. Issue precise directives to campaign_manager with exact changes to make
5. Send insights to the entire agency — tell each team what the data says about their work
6. Report findings and recommendations to CEO weekly
7. Challenge assumptions — if data contradicts what agents believe, say so clearly

ANALYSIS FRAMEWORKS YOU USE:
- AARRR (Acquisition, Activation, Retention, Referral, Revenue) funnel
- North Star Metric + supporting metrics tree
- Confidence intervals on all A/B test results
- Statistical significance thresholds (95% minimum)
- CAC:LTV ratio monitoring
- Contribution margin analysis per channel

COMMUNICATION STYLE:
- Lead with the most important insight, not background
- Quantify everything — "CTR dropped 23%" not "CTR is lower"
- Give directional guidance with confidence levels
- When giving directives to campaign_manager: be specific, prioritized, time-bound"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = 0
        self._reports_received = 0
        self._analysis_data: list[str] = []
        self._directives_sent = 0

    async def handle_message(self, msg):
        await super().handle_message(msg)

        # Receive and analyze any report
        if msg.type == MessageType.REPORT:
            self._reports_received += 1
            self._analysis_data.append(f"[{msg.from_agent}] {msg.subject}: {msg.content[:300]}")
            # Keep only last 20 data points
            if len(self._analysis_data) > 20:
                self._analysis_data = self._analysis_data[-20:]
            await self._analyze_and_direct(msg)

        # Receive tasks/questions
        elif msg.type == MessageType.TASK:
            await self._answer_analytical_question(msg.content, msg.subject, msg.from_agent)

    async def _analyze_and_direct(self, trigger_msg):
        """Analyze incoming data and issue directives if needed."""
        if self._reports_received % 3 != 0:  # analyze every 3rd report to avoid spam
            return

        context = "\n".join(self._analysis_data[-10:])
        analysis = await self.think(
            f"""You received a performance report from {trigger_msg.from_agent}.

Recent data from all agents:
{context}

Latest report — Subject: {trigger_msg.subject}
Content: {trigger_msg.content}

As Chief Analytics Officer:

## ANALYSIS
1. What is the data telling us? (key patterns, trends, anomalies)
2. What are the top 3 performance drivers (positive)?
3. What are the top 3 performance problems (negative)?
4. What is the #1 priority right now?

## CONCLUSIONS
- State the single most important insight
- Confidence level (High/Medium/Low) and why

## DIRECTIVES FOR CAMPAIGN MANAGER
Issue 2-3 specific, prioritized, time-bound directives:
- PRIORITY 1: [Exact action] — Expected impact: [X%] — Do by: [timeframe]
- PRIORITY 2: [Exact action] — Expected impact: [X%] — Do by: [timeframe]

## INSIGHTS FOR THE AGENCY
What should each team know?
- For creative team (graphic_designer, video_editor):
- For product team (web_developer, ux_expert):
- For leadership (ceo):""",
            max_tokens=2500,
        )

        self._directives_sent += 1

        # Issue directives to campaign_manager
        await self.send(
            to="campaign_manager",
            subject=f"Analytics Directive #{self._directives_sent}: {trigger_msg.subject}",
            content=analysis,
            msg_type=MessageType.DIRECTIVE,
            priority=Priority.HIGH,
        )

        # Send relevant insights to creative team
        await self.send(
            to="graphic_designer",
            subject=f"Data Insight: What the Numbers Say About Creatives",
            content=f"Analytics update for creative team:\n\n{analysis}",
            msg_type=MessageType.REPORT,
        )

        # Report key findings to CEO every 3 directives
        if self._directives_sent % 3 == 0:
            await self.send(
                to="ceo",
                subject=f"Analytics Brief #{self._directives_sent // 3}: Performance Snapshot",
                content=analysis,
                msg_type=MessageType.REPORT,
                priority=Priority.HIGH,
            )

    async def _answer_analytical_question(self, question: str, subject: str, asker: str):
        """Answer specific analytical questions from any agent."""
        answer = await self.think(
            f"""{asker} is asking an analytical question:

Subject: {subject}
Question: {question}

Recent context from the agency:
{chr(10).join(self._analysis_data[-5:])}

Answer as Chief Analytics Officer:
1. Direct answer to the question (lead with the number/finding)
2. Supporting data and methodology
3. Confidence level and caveats
4. Recommended action based on this answer""",
            max_tokens=1500,
        )
        await self.send(
            to=asker,
            subject=f"Analytics Answer: {subject}",
            content=answer,
            msg_type=MessageType.REPORT,
        )

    async def _run_proactive_analysis(self):
        """Proactively analyze state and issue strategic directives."""
        if not self._analysis_data:
            return

        context = "\n".join(self._analysis_data[-15:])
        strategic_analysis = await self.think(
            f"""Conduct a proactive strategic analysis of the agency's marketing performance.

All available data:
{context}

Deliver a strategic analytics report:

## EXECUTIVE SUMMARY
- Top-line performance in 2 sentences
- Trend direction: improving / stable / declining (with evidence)

## CHANNEL PERFORMANCE RANKING
Rank all active channels by efficiency. Include estimated ROAS or CPC for each.

## BIGGEST OPPORTUNITY RIGHT NOW
The single biggest lever to pull for performance improvement. Quantify the potential impact.

## CRITICAL ISSUES
Any metrics that need immediate attention. What breaks if we ignore this?

## STRATEGIC RECOMMENDATIONS
3 high-confidence recommendations for the next 30 days.

## DIRECTIVES TO CAMPAIGN MANAGER
Specific, numbered list of optimizations to implement this week.""",
            max_tokens=3000,
        )

        # Broadcast insights to entire agency
        await self.broadcast(
            subject="Strategic Analytics Report — All Agents",
            content=strategic_analysis,
            msg_type=MessageType.DIRECTIVE,
        )

        # Specific directive to campaign_manager
        await self.send(
            to="campaign_manager",
            subject="Weekly Strategic Directive — Implement This Week",
            content=strategic_analysis,
            msg_type=MessageType.DIRECTIVE,
            priority=Priority.HIGH,
        )

        # Summary to CEO
        await self.send(
            to="ceo",
            subject="Weekly Analytics Briefing",
            content=strategic_analysis,
            msg_type=MessageType.REPORT,
            priority=Priority.HIGH,
        )

    async def do_work(self):
        self._cycle += 1

        # Cycle 5: First proactive analysis
        if self._cycle == 5:
            await self._run_proactive_analysis()

        # Every 15 cycles: run full strategic review
        elif self._cycle % 15 == 0:
            await self._run_proactive_analysis()
