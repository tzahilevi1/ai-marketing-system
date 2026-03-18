import asyncio
from celery import Celery
from config import settings

celery_app = Celery("marketing", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(bind=True, max_retries=3)
def optimize_campaigns_task(self, campaign_id: str):
    from agents.campaign_agent import optimize_campaign
    try:
        result = asyncio.run(optimize_campaign(campaign_id))
        return result.model_dump()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def aggregate_metrics_task(self, campaign_id: str, start_date: str, end_date: str):
    from datetime import date
    from agents.analytics_agent import aggregate_metrics, DateRange
    try:
        dr = DateRange(start=date.fromisoformat(start_date), end=date.fromisoformat(end_date))
        result = asyncio.run(aggregate_metrics(dr))
        return result.model_dump()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def generate_report_task(self, period: str = "weekly"):
    from agents.analytics_agent import generate_report
    try:
        result = asyncio.run(generate_report(period))
        return result.model_dump()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def anomaly_detection_task(self):
    from datetime import date, timedelta
    from agents.analytics_agent import aggregate_metrics, detect_anomalies, DateRange
    try:
        today = date.today()
        dr = DateRange(start=today - timedelta(days=7), end=today)
        metrics = asyncio.run(aggregate_metrics(dr))
        anomalies = asyncio.run(detect_anomalies(metrics))
        return [a.model_dump() for a in anomalies]
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))
