"""Graphic Designer Agent — creates visual concepts, design systems, and image prompts."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType


class GraphicDesignerAgent(BaseAgent):
    name = "graphic_designer"
    role = "Creative Director / Graphic Designer"
    emoji = "🎨"
    system_prompt = """You are the Creative Director and Graphic Designer of an AI marketing agency. You:
- Create visual brand identities and design systems
- Design UI/UX concepts and wireframes (described in text)
- Write detailed image generation prompts for Flux/SDXL
- Create style guides (colors, typography, spacing, components)
- Review marketing creatives for visual quality
- Ensure brand consistency across all platforms
- Collaborate with Video Editor on motion graphics concepts
Design philosophy: Clean, modern, conversion-focused. Data-driven design decisions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._designs_created = 0

    async def handle_message(self, msg):
        await super().handle_message(msg)
        if msg.type == MessageType.TASK:
            await self._create_design(msg)

    async def _create_design(self, msg):
        self._designs_created += 1
        design = self.think(
            f"""Create a comprehensive design specification for:

Task: {msg.subject}
Brief: {msg.content}

Provide:
## Brand Colors
(Primary, Secondary, Accent, Background, Text — with hex codes)

## Typography
(Font families, sizes, weights for H1-H6, body, captions)

## Component Specs
(Describe KPI cards, buttons, charts, navigation — dimensions, shadows, border-radius)

## Image Generation Prompts
(Write 3 Flux prompts for hero images, ad creatives, social posts)

## Dashboard Layout
(Describe the grid layout, spacing, responsive breakpoints)""",
            max_tokens=2048,
        )
        await self.send(
            to="project_manager",
            subject=f"Design Specs Ready: {msg.subject}",
            content=design,
            msg_type=MessageType.REPORT,
        )
        await self.send(
            to="code_builder",
            subject=f"Design System to Implement: {msg.subject}",
            content=design,
            msg_type=MessageType.TASK,
        )

    async def do_work(self):
        pass  # reactive
