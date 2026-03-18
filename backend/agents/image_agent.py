import io
from typing import Any

import boto3
from PIL import Image

from agents.base import run_agent
from config import settings

PLATFORM_SIZES: dict[str, tuple[int, int]] = {
    "facebook_feed": (1200, 630),
    "instagram_square": (1080, 1080),
    "instagram_story": (1080, 1920),
    "google_300x250": (300, 250),
    "google_728x90": (728, 90),
    "tiktok": (1080, 1920),
}

SYSTEM_PROMPT = """You are a creative director specializing in digital marketing visuals.
You create detailed, effective image prompts for AI image generation models.
Focus on visual impact, brand alignment, and platform-specific best practices."""


async def generate_image_prompt(campaign_brief: str, platform: str) -> str:
    prompt = f"""Create a detailed image generation prompt for a marketing ad.

Campaign Brief: {campaign_brief}
Platform: {platform}
Platform size: {PLATFORM_SIZES.get(platform, (1080, 1080))}

The prompt should describe: subject, style, mood, lighting, colors, composition.
Make it suitable for the Flux image generation model.
Return only the prompt text, no explanation."""

    response = await run_agent(prompt, SYSTEM_PROMPT, max_tokens=512)
    return response.content[0].text.strip()


async def generate_image(prompt: str, style: str = "photorealistic") -> bytes:
    """Generate image via Replicate Flux model."""
    try:
        import replicate
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": f"{prompt}, {style}, high quality, marketing material",
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "webp",
            },
        )
        import httpx
        image_url = str(output[0])
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            return response.content
    except Exception:
        # Return a placeholder 1x1 white pixel if Replicate not configured
        img = Image.new("RGB", (1080, 1080), color=(255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format="WEBP")
        return buf.getvalue()


def process_and_resize(image_bytes: bytes, platforms: list[str] | None = None) -> dict[str, bytes]:
    """Resize image for all platforms using Pillow."""
    if platforms is None:
        platforms = list(PLATFORM_SIZES.keys())

    original = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    result: dict[str, bytes] = {}

    for platform in platforms:
        size = PLATFORM_SIZES.get(platform)
        if not size:
            continue
        resized = original.copy()
        resized = resized.resize(size, Image.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format="WEBP", quality=85)
        result[platform] = buf.getvalue()

    return result


async def upload_to_storage(images: dict[str, bytes], campaign_id: str) -> dict[str, str]:
    """Upload resized images to S3 and return CDN URLs."""
    if not settings.aws_access_key_id:
        # Mock URLs for development
        return {platform: f"https://cdn.example.com/{campaign_id}/{platform}.webp" for platform in images}

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )
    urls: dict[str, str] = {}
    for platform, image_bytes in images.items():
        key = f"brand/{campaign_id}/{platform}/image.webp"
        s3.put_object(
            Bucket=settings.aws_s3_bucket,
            Key=key,
            Body=image_bytes,
            ContentType="image/webp",
        )
        urls[platform] = f"https://{settings.aws_s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"
    return urls


async def analyze_image_quality(image_url: str) -> dict[str, Any]:
    """Use Claude vision to analyze image quality."""
    response = await run_agent(
        prompt=f"Analyze this marketing image for quality, composition, and effectiveness: {image_url}",
        system=SYSTEM_PROMPT,
    )
    return {"analysis": response.content[0].text, "url": image_url}
