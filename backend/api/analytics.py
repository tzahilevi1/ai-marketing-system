from datetime import date
from fastapi import APIRouter
from agents.analytics_agent import (
    aggregate_metrics, generate_insights, detect_anomalies,
    answer_question, generate_report, DateRange, UnifiedMetrics
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/metrics")
async def get_metrics(start: date = None, end: date = None):
    from datetime import timedelta
    today = date.today()
    dr = DateRange(
        start=start or today - timedelta(days=30),
        end=end or today,
    )
    metrics = await aggregate_metrics(dr)
    return metrics.model_dump()


@router.get("/insights")
async def get_insights(start: date = None, end: date = None):
    from datetime import timedelta
    today = date.today()
    dr = DateRange(start=start or today - timedelta(days=30), end=end or today)
    metrics = await aggregate_metrics(dr)
    insights = await generate_insights(metrics)
    return {"insights": [i.model_dump() for i in insights]}


@router.get("/anomalies")
async def get_anomalies():
    from datetime import timedelta
    today = date.today()
    dr = DateRange(start=today - timedelta(days=7), end=today)
    metrics = await aggregate_metrics(dr)
    anomalies = await detect_anomalies(metrics)
    return {"anomalies": [a.model_dump() for a in anomalies]}


@router.post("/ask")
async def ask(question: str):
    from datetime import timedelta
    today = date.today()
    dr = DateRange(start=today - timedelta(days=30), end=today)
    metrics = await aggregate_metrics(dr)
    answer = await answer_question(question, metrics)
    return {"question": question, "answer": answer}


@router.get("/report")
async def get_report(period: str = "weekly"):
    report = await generate_report(period)
    return report.model_dump()
