import asyncio
import logging
from typing import Any

import anthropic

from config import settings

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
MODEL = "claude-sonnet-4-20250514"


async def run_agent(
    prompt: str,
    system: str,
    tools: list[dict] | None = None,
    max_tokens: int = 4096,
) -> anthropic.types.Message:
    """Run a Claude agent with retry and exponential backoff."""
    kwargs: dict[str, Any] = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    if tools:
        kwargs["tools"] = tools

    for attempt in range(3):
        try:
            response = client.messages.create(**kwargs)
            return response
        except anthropic.RateLimitError as e:
            wait = 2**attempt * 5
            logger.warning(f"Rate limit hit, retrying in {wait}s (attempt {attempt + 1})")
            await asyncio.sleep(wait)
        except anthropic.APIError as e:
            if attempt == 2:
                raise
            wait = 2**attempt * 2
            logger.error(f"API error: {e}, retrying in {wait}s")
            await asyncio.sleep(wait)

    raise RuntimeError("Max retries exceeded")


async def run_agent_stream(
    prompt: str,
    system: str,
    max_tokens: int = 4096,
):
    """Stream response from Claude."""
    with client.messages.stream(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text
