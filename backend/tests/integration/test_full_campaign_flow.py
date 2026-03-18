"""Integration test: full campaign creation flow."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_full_campaign_flow():
    """Test brief -> plan -> launch flow end-to-end."""
    from agents.content_agent import CampaignBrief
    from agents.campaign_agent import plan_campaign, launch_campaign

    brief = CampaignBrief(
        product_name="AI Tool",
        target_audience="Startup founders",
        unique_value_prop="10x productivity",
        goal="leads",
        budget=10000.0,
        tone="professional",
    )

    mock_plan_response = MagicMock()
    mock_plan_response.content = [MagicMock(text='{"platforms": ["meta", "google"], "budget_split": {"meta": 0.6, "google": 0.4}, "duration_days": 30, "rationale": "Meta for awareness, Google for intent."}')]

    with patch("agents.campaign_agent.run_agent", new=AsyncMock(return_value=mock_plan_response)):
        plan = await plan_campaign(brief)

    assert "meta" in plan.platforms
    assert plan.total_budget == 10000.0

    result = await launch_campaign(plan)
    assert result.status == "active"
    assert "meta" in result.platform_ids
