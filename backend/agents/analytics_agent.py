from datetime import date
from typing import Any

from pydantic import BaseModel

from agents.base import run_agent

SYSTEM_PROMPT = """You are a senior marketing data analyst.
You interpret marketing metrics, identify trends and anomalies, and provide actionable insights.
Communicate findings clearly in both Hebrew and English as requested."""


class DateRange(BaseModel):
    start: date
    end: date


class UnifiedMetrics(BaseModel):
    total_spend: float
    total_revenue: float
    total_impressions: int
    total_clicks: int
    total_conversions: int
    roas: float
    ctr: float
    cpc: float
    cpa: float
    by_platform: dict[str, dict[str, Any]]
    by_date: list[dict[str, Any]]


class Anomaly(BaseModel):
    metric: str
    expected: float
    actual: float
    severity: str
    description: str


class Insight(BaseModel):
    title: str
    description: str
    impact: str
    action: str


class MarketingReport(BaseModel):
    period: str
    executive_summary: str
    key_metrics: dict[str, Any]
    insights: list[Insight]
    recommendations: list[str]


async def aggregate_metrics(date_range: DateRange) -> UnifiedMetrics:
    """Aggregate metrics from all platforms into unified schema."""
    # In production: query each platform API and DB
    return UnifiedMetrics(
        total_spend=10000.0,
        total_revenue=35000.0,
        total_impressions=500000,
        total_clicks=15000,
        total_conversions=350,
        roas=3.5,
        ctr=0.03,
        cpc=0.67,
        cpa=28.57,
        by_platform={
            "meta": {"spend": 6000, "revenue": 21000, "roas": 3.5},
            "google": {"spend": 3000, "revenue": 10500, "roas": 3.5},
            "tiktok": {"spend": 1000, "revenue": 3500, "roas": 3.5},
        },
        by_date=[],
    )


async def detect_anomalies(metrics: UnifiedMetrics) -> list[Anomaly]:
    prompt = f"""Analyze these marketing metrics for anomalies:
ROAS: {metrics.roas} (target: 3.0)
CTR: {metrics.ctr:.2%}
CPC: ${metrics.cpc:.2f}
CPA: ${metrics.cpa:.2f}

Identify any metrics that are significantly above or below expected ranges."""

    response = await run_agent(prompt, SYSTEM_PROMPT)
    return []


async def generate_insights(metrics: UnifiedMetrics) -> list[Insight]:
    prompt = f"""Generate 3-5 actionable marketing insights from these metrics:

Total Spend: ${metrics.total_spend:,.0f}
Total Revenue: ${metrics.total_revenue:,.0f}
ROAS: {metrics.roas:.2f}x
CTR: {metrics.ctr:.2%}
Platform breakdown: {metrics.by_platform}

For each insight provide: title, description, business impact, and recommended action."""

    response = await run_agent(prompt, SYSTEM_PROMPT, max_tokens=2048)
    return [
        Insight(
            title="AI-Generated Insight",
            description=response.content[0].text,
            impact="medium",
            action="Review metrics and adjust strategy",
        )
    ]


async def answer_question(question: str, context: UnifiedMetrics) -> str:
    prompt = f"""Answer this question about our marketing performance:

Question: {question}

Current Metrics:
- Total Spend: ${context.total_spend:,.0f}
- Total Revenue: ${context.total_revenue:,.0f}
- ROAS: {context.roas:.2f}x
- Platform breakdown: {context.by_platform}

Provide a clear, concise answer with data-backed reasoning."""

    response = await run_agent(prompt, SYSTEM_PROMPT, max_tokens=1024)
    return response.content[0].text


async def generate_report(period: str = "weekly") -> MarketingReport:
    prompt = f"""Generate a {period} marketing performance report.
Include executive summary, key metrics analysis, insights, and recommendations.
Write in a professional tone suitable for stakeholders."""

    response = await run_agent(prompt, SYSTEM_PROMPT, max_tokens=4096)
    return MarketingReport(
        period=period,
        executive_summary=response.content[0].text,
        key_metrics={},
        insights=[],
        recommendations=[],
    )
