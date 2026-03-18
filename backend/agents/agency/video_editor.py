"""Video Editor Agent — creates video ad scripts, storyboards, and motion concepts."""
from agents.agency.base_agent import BaseAgent
from agents.agency.message_bus import MessageType


class VideoEditorAgent(BaseAgent):
    name = "video_editor"
    role = "Video Editor / Motion Designer"
    emoji = "🎬"
    system_prompt = """You are the Video Editor and Motion Designer of an AI marketing agency. You:
- Write video ad scripts (15s, 30s, 60s formats)
- Create detailed storyboards (scene by scene descriptions)
- Design motion graphic concepts for social media
- Write TikTok/Reels video concepts with hooks and CTAs
- Specify video specs for each platform (aspect ratio, duration, captions)
- Create subtitle/caption copy for video ads
- Collaborate with Graphic Designer on visual style
Platforms: TikTok (9:16, 15-60s), Instagram Reels (9:16, 15-90s), YouTube (16:9, 15-30s), Facebook (1:1 or 16:9)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._videos_scripted = 0

    async def handle_message(self, msg):
        await super().handle_message(msg)
        if msg.type == MessageType.TASK:
            await self._create_video_concept(msg)

    async def _create_video_concept(self, msg):
        self._videos_scripted += 1
        script = self.think(
            f"""Create a complete video ad package for:

Brief: {msg.subject}
Details: {msg.content}

Deliver:
## TikTok/Reels Script (30 seconds)
Scene 1 (0-3s): [HOOK — grab attention]
Scene 2 (3-15s): [PROBLEM/SOLUTION]
Scene 3 (15-25s): [SOCIAL PROOF]
Scene 4 (25-30s): [CTA]

## Captions/Subtitles
(Full caption text, word by word timing)

## Visual Direction
(Color grade, transitions, text overlays, music mood)

## YouTube Pre-roll (15 seconds, skip-resistant)

## Performance Hooks
(5 different opening lines to A/B test)""",
            max_tokens=2048,
        )
        await self.send(
            to="project_manager",
            subject=f"Video Scripts Ready: {msg.subject}",
            content=script,
            msg_type=MessageType.REPORT,
        )

    async def do_work(self):
        pass  # reactive
