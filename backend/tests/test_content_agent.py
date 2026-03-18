import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agents.content_agent import CampaignBrief, generate_ad_copy, generate_ab_variants


@pytest.fixture
def sample_brief():
    return CampaignBrief(
        product_name="Test Product",
        target_audience="25-35 year old professionals",
        unique_value_prop="Saves 2 hours per day",
        goal="leads",
        budget=5000.0,
        tone="professional",
    )


@pytest.mark.asyncio
async def test_generate_ad_copy_returns_variants(sample_brief):
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            type="tool_use",
            name="generate_ad_copy",
            input={
                "variants": [
                    {"headline": "Save Time Today", "primary_text": "Join 10,000 professionals.", "description": "Try free", "cta": "Get Started"},
                    {"headline": "Work Smarter", "primary_text": "2 hours saved daily.", "description": "Sign up now", "cta": "Learn More"},
                    {"headline": "Boost Productivity", "primary_text": "The pro tool you need.", "description": "Free trial", "cta": "Start Free"},
                ]
            },
        )
    ]
    with patch("agents.content_agent.run_agent", new=AsyncMock(return_value=mock_response)):
        copies = await generate_ad_copy(sample_brief, "facebook", variants=3)
    assert len(copies) == 3
    assert all(len(c.headline) <= 30 for c in copies)
    assert all(c.platform == "facebook" for c in copies)


@pytest.mark.asyncio
async def test_generate_ab_variants():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="1. Variant A\n2. Variant B\n3. Variant C")]
    with patch("agents.content_agent.run_agent", new=AsyncMock(return_value=mock_response)):
        variants = await generate_ab_variants("Original copy", count=3)
    assert len(variants) == 3
