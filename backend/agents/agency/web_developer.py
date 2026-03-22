"""Web Developer Agent — expert in building full-stack web applications."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType, Priority


class WebDeveloperAgent(BaseAgent):
    name = "web_developer"
    role = "Senior Web Developer"
    emoji = "🌐"
    system_prompt = """You are a Senior Full-Stack Web Developer in an AI marketing agency. You specialize in:
- React 18, TypeScript, Next.js, Vite — modern frontend architecture
- FastAPI, Node.js, REST APIs, WebSockets — backend systems
- Performance optimization: Core Web Vitals, Lighthouse scores, bundle size
- SEO technical implementation: meta tags, structured data, sitemaps, robots.txt
- Accessibility (WCAG 2.1 AA): ARIA, keyboard navigation, screen readers
- Animation & interactions: Framer Motion, CSS animations, micro-interactions
- Responsive design: mobile-first, fluid typography, CSS Grid & Flexbox
- Web security: CSP headers, HTTPS, input sanitization, auth flows
- Landing page optimization: conversion rate optimization (CRO), A/B testing setup
- Integration: analytics (GA4, Mixpanel), pixels (Meta, TikTok), tag managers

Your output always includes:
1. Complete, working code (not pseudocode)
2. Performance considerations
3. SEO & accessibility notes
4. Mobile responsiveness specs

You collaborate closely with UX Expert (get designs first), Code Builder (hand off specs), and Bug Detector (code review).
You report to: Project Manager
You work with: ux_expert, code_builder, bug_detector, graphic_designer"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = 0
        self._init_done = False

    async def handle_message(self, msg):
        await super().handle_message(msg)
        if msg.type == MessageType.TASK:
            await self._handle_dev_task(msg)
        elif msg.type == MessageType.REPORT and msg.from_agent == "ux_expert":
            await self._implement_ux_design(msg)

    async def _handle_dev_task(self, msg):
        # First, request UX design before implementing
        await self.send(
            to="ux_expert",
            subject=f"Need UX Design For: {msg.subject}",
            content=f"Please provide UX design specs, wireframes, and user flow before I implement:\n\n{msg.content}",
            msg_type=MessageType.TASK,
            priority=Priority.HIGH,
        )

        implementation = await self.think(
            f"""You are a Senior Web Developer. Implement this task:

Task: {msg.subject}
Details: {msg.content}

Provide:
## Technical Architecture
(Component structure, data flow, API endpoints needed)

## Frontend Implementation (React + TypeScript)
(Complete component code with Tailwind CSS)

## Performance Optimizations
(Lazy loading, memoization, bundle splitting)

## SEO Implementation
(Meta tags, structured data, semantic HTML)

## Accessibility (WCAG 2.1 AA)
(ARIA labels, keyboard nav, color contrast)

## Mobile Responsiveness
(Breakpoints, touch targets, viewport handling)

## Analytics & Tracking
(Events to fire, conversion tracking setup)""",
            max_tokens=4096,
        )

        await self.send(
            to="bug_detector",
            subject=f"Web Code Review: {msg.subject}",
            content=implementation,
            msg_type=MessageType.TASK,
        )
        await self.send(
            to="project_manager",
            subject=f"🌐 Web Implementation Ready: {msg.subject}",
            content=f"Full-stack implementation complete. Sent to bug_detector for review.\n\nSummary:\n{implementation[:400]}...",
            msg_type=MessageType.REPORT,
        )

    async def _implement_ux_design(self, msg):
        code = await self.think(
            f"""Convert this UX design into production React code:

UX Design: {msg.subject}
Design Specs: {msg.content}

Write complete TypeScript React components with:
- Tailwind CSS styling matching the design
- Framer Motion animations for key interactions
- Full responsiveness (mobile-first)
- Loading states and error boundaries
- Accessibility attributes""",
            max_tokens=4096,
        )
        await self.send(
            to="code_builder",
            subject=f"Implement UI Components: {msg.subject}",
            content=code,
            msg_type=MessageType.TASK,
            priority=Priority.HIGH,
        )

    async def do_work(self):
        self._cycle += 1
        if self._cycle == 4 and not self._init_done:
            self._init_done = True
            audit = await self.think(
                """Perform a technical audit of the AI Marketing System frontend.
The stack is: React 18, TypeScript, Vite, Tailwind CSS, Recharts, React Query.

Identify and report:
1. Performance issues (bundle size, render bottlenecks, missing lazy loading)
2. SEO gaps (missing meta tags, poor semantic HTML, no structured data)
3. Accessibility violations (WCAG 2.1 AA compliance)
4. Mobile UX issues (touch targets, viewport, font sizes)
5. Missing conversion optimization elements
6. Security issues (XSS risks, missing CSP, insecure dependencies)

For each issue: severity (critical/high/medium), location, and fix.""",
                max_tokens=2048,
            )
            await self.send(
                to="project_manager",
                subject="🌐 Frontend Technical Audit Report",
                content=audit,
                msg_type=MessageType.REPORT,
                priority=Priority.HIGH,
            )
            await self.send(
                to="ux_expert",
                subject="Share Your UX Audit Findings",
                content="I've completed the technical audit. Please share your UX audit so we can align on improvements.",
                msg_type=MessageType.TASK,
            )
