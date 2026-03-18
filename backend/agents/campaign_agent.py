import json
from datetime import date
from typing import Any

from pydantic import BaseModel

from agents.base import run_agent
from agents.content_agent import CampaignBrief

SYSTEM_PROMPT = """You are an expert digital marketing strategist.
You analyze campaign briefs and recommend optimal platform mixes, budgets, and targeting strategies.
You interpret performance data and make data-driven optimization decisions."""


class CampaignPlan(BaseModel):
    name: str
    platforms: list[str]
    budget_split: dict[str, float]  # platform -> percentage
    targeting: dict[str, Any]
    daily_budget: float
    total_budget: float
    recommended_duration_days: int
    rationale: str


class LaunchResult(BaseModel):
    campaign_id: str
    platform_ids: dict[str, str]
    status: str
    message: str


class OptimizationActions(BaseModel):
    paused: list[str]
    scaled: list[str]
    recommendations: list[str]


class Thresholds(BaseModel):
    min_ctr: float = 0.01
    max_cpc: float = 5.0
    target_roas: float = 3.0


class WeeklyReport(BaseModel):
    period: str
    summary: str
    top_performing: list[str]
    recommendations: list[str]
    metrics_snapshot: dict[str, Any]


async def plan_campaign(brief: CampaignBrief) -> CampaignPlan:
    prompt = f"""Create a campaign plan for this brief:

Product: {brief.product_name}
Audience: {brief.target_audience}
Goal: {brief.goal}
Budget: ${brief.budget}
Tone: {brief.tone}

Recommend:
1. Which platforms to use and why
2. Budget split % across platforms
3. Target audience settings
4. Campaign duration
5. Your strategic rationale

Respond in JSON format."""

    response = await run_agent(prompt, SYSTEM_PROMPT, max_tokens=2048)
    text = response.content[0].text

    # Extract JSON from response
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        data = json.loads(text[start:end])
    except Exception:
        data = {}

    return CampaignPlan(
        name=f"{brief.product_name} - {brief.goal} Campaign",
        platforms=data.get("platforms", ["meta", "google"]),
        budget_split=data.get("budget_split", {"meta": 0.6, "google": 0.4}),
        targeting=data.get("targeting", {}),
        daily_budget=brief.budget / 30,
        total_budget=brief.budget,
        recommended_duration_days=data.get("duration_days", 30),
        rationale=data.get("rationale", text),
    )


async def launch_campaign(plan: CampaignPlan) -> LaunchResult:
    """Launch campaign on all platforms (mocked in development)."""
    return LaunchResult(
        campaign_id="mock-campaign-id",
        platform_ids={p: f"mock-{p}-id-001" for p in plan.platforms},
        status="active",
        message="Campaign launched successfully (sandbox mode)",
    )


async def optimize_campaign(campaign_id: str) -> OptimizationActions:
    prompt = f"""Analyze campaign {campaign_id} performance and recommend optimizations.
Check for underperforming ads (CTR < 1%, CPC > $5) and winning ads (ROAS > 3x).
Provide specific action recommendations."""

    response = await run_agent(prompt, SYSTEM_PROMPT)
    return OptimizationActions(
        paused=[],
        scaled=[],
        recommendations=[response.content[0].text],
    )


async def pause_underperformers(campaign_id: str, thresholds: Thresholds) -> list[str]:
    # In production: query metrics DB, compare to thresholds, call platform APIs
    return []


async def scale_winners(campaign_id: str, scale_factor: float = 1.2) -> list[str]:
    # In production: query metrics DB, identify ROAS > target, increase budgets
    return []


async def generate_weekly_report(campaign_id: str) -> WeeklyReport:
    prompt = f"""Generate a weekly performance report for campaign {campaign_id}.
Include: performance summary, top performing creatives, key insights, next week recommendations."""

    response = await run_agent(prompt, SYSTEM_PROMPT, max_tokens=2048)
    return WeeklyReport(
        period="last_7_days",
        summary=response.content[0].text,
        top_performing=[],
        recommendations=[],
        metrics_snapshot={},
    )
