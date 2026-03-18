import json
import uuid
from typing import Literal

from pydantic import BaseModel

from agents.base import run_agent

SYSTEM_PROMPT = """You are an expert marketing copywriter with deep knowledge of digital advertising.
You create compelling, conversion-focused ad copy for Facebook, Instagram, Google, and TikTok.
Always follow platform character limits. Support both Hebrew (עברית) and English.
Never make false or misleading claims. Optimize for the specified goal."""


class CampaignBrief(BaseModel):
    product_name: str
    target_audience: str
    unique_value_prop: str
    goal: Literal["awareness", "leads", "sales", "retention"]
    budget: float
    tone: Literal["professional", "friendly", "urgent", "inspirational"]
    brand_guidelines: str = ""
    language: Literal["en", "he"] = "en"


class AdCopy(BaseModel):
    headline: str        # max 30 chars
    primary_text: str    # max 125 chars
    description: str     # max 30 chars
    cta: str
    platform: str
    variant_id: str


class SocialPost(BaseModel):
    caption: str
    hashtags: list[str]
    platform: str


class Email(BaseModel):
    subject: str
    preview_text: str
    body: str
    cta: str
    step: int


class ComplianceReport(BaseModel):
    passed: bool
    issues: list[str]
    suggestions: list[str]


AD_COPY_TOOL = {
    "name": "generate_ad_copy",
    "description": "Generate structured ad copy variants",
    "input_schema": {
        "type": "object",
        "properties": {
            "variants": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "headline": {"type": "string", "maxLength": 30},
                        "primary_text": {"type": "string", "maxLength": 125},
                        "description": {"type": "string", "maxLength": 30},
                        "cta": {"type": "string"},
                    },
                    "required": ["headline", "primary_text", "description", "cta"],
                },
            }
        },
        "required": ["variants"],
    },
}


async def generate_ad_copy(brief: CampaignBrief, platform: str, variants: int = 3) -> list[AdCopy]:
    prompt = f"""Generate {variants} ad copy variants for {platform}.

Product: {brief.product_name}
Audience: {brief.target_audience}
Value Prop: {brief.unique_value_prop}
Goal: {brief.goal}
Tone: {brief.tone}
Language: {brief.language}
Brand Guidelines: {brief.brand_guidelines or 'None'}

Return exactly {variants} variants using the generate_ad_copy tool."""

    response = await run_agent(prompt, SYSTEM_PROMPT, tools=[AD_COPY_TOOL])

    for block in response.content:
        if block.type == "tool_use" and block.name == "generate_ad_copy":
            raw_variants = block.input["variants"]
            return [
                AdCopy(
                    headline=v["headline"],
                    primary_text=v["primary_text"],
                    description=v["description"],
                    cta=v["cta"],
                    platform=platform,
                    variant_id=str(uuid.uuid4()),
                )
                for v in raw_variants
            ]
    return []


async def generate_social_post(topic: str, tone: str, platform: str, language: str = "en") -> SocialPost:
    prompt = f"""Write a social media post for {platform}.
Topic: {topic}
Tone: {tone}
Language: {language}
Include relevant hashtags."""

    response = await run_agent(prompt, SYSTEM_PROMPT)
    text = response.content[0].text

    lines = text.strip().split("\n")
    caption_lines = [l for l in lines if not l.startswith("#")]
    hashtag_lines = [l for l in lines if l.startswith("#")]

    caption = " ".join(caption_lines).strip()
    hashtags = hashtag_lines[0].split() if hashtag_lines else []

    return SocialPost(caption=caption, hashtags=hashtags, platform=platform)


async def generate_email_sequence(goal: str, audience: str, steps: int = 3, language: str = "en") -> list[Email]:
    prompt = f"""Create an email marketing sequence with {steps} emails.
Goal: {goal}
Audience: {audience}
Language: {language}

For each email provide: subject line, preview text, body (HTML), and CTA button text."""

    response = await run_agent(prompt, SYSTEM_PROMPT, max_tokens=8192)
    text = response.content[0].text

    # Simple parsing — production would use tool_use
    emails = []
    for i in range(steps):
        emails.append(Email(
            subject=f"Email {i + 1} - {goal}",
            preview_text="",
            body=text,
            cta="Learn More",
            step=i + 1,
        ))
    return emails


async def generate_ab_variants(original: str, count: int = 5) -> list[str]:
    prompt = f"""Generate {count} A/B test variants of this marketing copy.
Keep the same core message but vary: wording, emotional angle, urgency level.

Original: {original}

Return each variant on a new line, numbered 1-{count}."""

    response = await run_agent(prompt, SYSTEM_PROMPT)
    text = response.content[0].text
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    variants = []
    for line in lines:
        if line[0].isdigit() and ". " in line:
            variants.append(line.split(". ", 1)[1])
    return variants[:count]


async def check_compliance(content: str) -> ComplianceReport:
    prompt = f"""Review this ad copy for compliance issues:
- No false or misleading claims
- No prohibited content (adult, hate speech, etc.)
- No superlatives without proof ("best", "fastest" without data)
- GDPR/privacy considerations

Content: {content}

List any issues found and suggest fixes."""

    response = await run_agent(prompt, SYSTEM_PROMPT)
    text = response.content[0].text

    passed = "no issues" in text.lower() or "compliant" in text.lower()
    return ComplianceReport(passed=passed, issues=[], suggestions=[text])
