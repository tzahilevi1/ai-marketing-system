"""UX Expert Agent — world-class user experience design and research."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class UXExpertAgent(BaseAgent):
    name = "ux_expert"
    role = "UX Design Expert"
    emoji = "✨"
    system_prompt = """You are a world-class UX Designer and Product Designer in an AI marketing agency. You specialize in:
- User Research: personas, journey maps, jobs-to-be-done, pain point analysis
- Information Architecture: site maps, navigation flows, content hierarchy
- Interaction Design: micro-interactions, animation principles, gesture design
- Visual Design: design systems, spacing, typography, color psychology
- Conversion Rate Optimization: landing page UX, form design, CTA psychology
- Ad Creative UX: scroll-stopping patterns, hook design, social proof placement
- Dashboard UX: data visualization best practices, cognitive load reduction
- A/B Testing: hypothesis formation, variant design, statistical significance
- Usability Testing: heuristic evaluation, task flows, error prevention
- Design Tokens: consistent spacing, color, typography systems

Design principles you follow:
- Jakob Nielsen's 10 Usability Heuristics
- Gestalt principles (proximity, similarity, continuity, closure)
- Fitts's Law for touch targets and interactive elements
- Miller's Law (7±2 items in working memory)
- Progressive disclosure for complex features
- Emotional design (visceral, behavioral, reflective)

You collaborate with:
- Graphic Designer: visual consistency
- Web Developer: feasibility and implementation
- Video Editor: motion design language
- Code Builder: component specifications

You report to: Project Manager"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = 0
        self._audit_done = False

    async def handle_message(self, msg):
        await super().handle_message(msg)
        if msg.type == MessageType.TASK:
            await self._handle_ux_task(msg)

    async def _handle_ux_task(self, msg):
        ux_design = self.think(
            f"""As a world-class UX Designer, create comprehensive UX specifications for:

Task: {msg.subject}
Context: {msg.content}

Deliver:

## User Research
### Target Persona
(Name, age, goals, pain points, tech comfort, key motivations)

### User Journey Map
(Awareness → Consideration → Decision → Action → Retention)
Stage by stage with emotions, touchpoints, opportunities

### Jobs To Be Done
"When I [situation], I want to [motivation], so I can [outcome]"

## Information Architecture
### Content Hierarchy (priority order)
### Navigation Flow (step by step)
### Page Structure (above/below fold)

## Interaction Design
### Key Micro-interactions
(hover states, loading states, success/error feedback, transitions)
### Animation Specs
(duration: ms, easing curves, what triggers what)
### Empty States
(what users see when no data yet)

## Visual Design Specs
### Spacing System
(use 4px base grid: 4, 8, 12, 16, 24, 32, 48, 64px)
### Typography Hierarchy
(H1-H6 sizes, weights, line-heights, use cases)
### Color Usage
(primary actions, secondary, danger, success, neutral — with specific use cases)
### Component Specs
(exact dimensions for buttons, cards, inputs, modals)

## Conversion Optimization
### Primary CTA Design
(color, size, copy, placement, whitespace)
### Trust Signals
(where to place social proof, testimonials, guarantees)
### Friction Reduction
(what to remove, simplify, or defer)

## Accessibility
### Color Contrast Requirements (WCAG AA: 4.5:1 for text)
### Focus States Design
### Touch Target Minimums (44x44px)
### Screen Reader Considerations

## A/B Test Hypothesis
### What to test first and why
### Success metric
### Expected uplift""",
            max_tokens=4096,
        )

        # Send design to web developer for implementation
        await self.send(
            to="web_developer",
            subject=f"UX Design Specs: {msg.subject}",
            content=ux_design,
            msg_type=MessageType.REPORT,
            priority=Priority.HIGH,
        )
        # Send to graphic designer for visual direction
        await self.send(
            to="graphic_designer",
            subject=f"Visual Direction Needed: {msg.subject}",
            content=f"I've created the UX specs. Please align visual design with these specifications:\n\n{ux_design[:1000]}...",
            msg_type=MessageType.TASK,
        )
        # Report to PM
        await self.send(
            to="project_manager",
            subject=f"✨ UX Design Complete: {msg.subject}",
            content=f"Full UX specifications ready. Sent to web_developer and graphic_designer.\n\nHighlights:\n{ux_design[:400]}...",
            msg_type=MessageType.REPORT,
        )

    async def do_work(self):
        self._cycle += 1
        if self._cycle == 5 and not self._audit_done:
            self._audit_done = True
            audit = self.think(
                """Conduct a UX audit of an AI Marketing Dashboard application.
The app has: Dashboard, Campaigns, Content Studio, Analytics, and Agency pages.
Users are: marketing managers, CMOs, and agency owners.

Deliver a comprehensive UX audit:

## Executive Summary
(3 sentence UX health assessment)

## Critical UX Issues (must fix)
For each: issue, user impact, heuristic violated, fix recommendation

## Information Architecture Review
(Is the navigation clear? Are pages in right order? Missing pages?)

## Key User Flows Analysis
1. New Campaign Creation Flow
2. Content Generation Flow
3. Analytics Review Flow

For each flow: steps, friction points, drop-off risks, improvements

## Emotional Design Assessment
(Does the UI feel trustworthy? Professional? Easy? What emotions does it evoke?)

## Competitive UX Benchmark
(Compare to: HubSpot, Hootsuite, Canva — what we should adopt)

## Quick Wins (implement in <1 day)
(5 specific, high-impact UX improvements)

## Design System Gaps
(Inconsistencies, missing states, unclear patterns)

## Recommended A/B Tests
(3 tests ranked by potential ROI)""",
                max_tokens=3000,
            )
            await self.send(
                to="project_manager",
                subject="✨ UX Audit: AI Marketing Dashboard",
                content=audit,
                msg_type=MessageType.REPORT,
                priority=Priority.HIGH,
            )
            await self.send(
                to="web_developer",
                subject="UX Audit Complete — Align on Technical Fixes",
                content=f"UX audit done. Please review and let's align on what can be fixed technically:\n\n{audit[:800]}...",
                msg_type=MessageType.TASK,
            )
            await self.send(
                to="innovator",
                subject="UX Research Insights — Use for Feature Ideas",
                content=f"Key UX findings that should inform your innovation proposals:\n\n{audit[:600]}...",
                msg_type=MessageType.REPORT,
            )
