import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from database import get_db
from models.models import Campaign
from agents.campaign_agent import plan_campaign, launch_campaign, CampaignPlan
from agents.content_agent import CampaignBrief

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/")
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    campaigns = result.scalars().all()
    return [{"id": str(c.id), "name": c.name, "status": c.status, "goal": c.goal} for c in campaigns]


@router.post("/")
async def create_campaign(brief: CampaignBrief, db: AsyncSession = Depends(get_db)):
    plan = await plan_campaign(brief)
    campaign = Campaign(
        name=plan.name,
        status="draft",
        goal=brief.goal,
        total_budget=brief.budget,
        daily_budget=plan.daily_budget,
        brief=brief.model_dump(),
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return {"id": str(campaign.id), "plan": plan.model_dump()}


@router.post("/{campaign_id}/launch")
async def launch(campaign_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == uuid.UUID(campaign_id)))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    plan = CampaignPlan(
        name=campaign.name,
        platforms=["meta", "google"],
        budget_split={"meta": 0.6, "google": 0.4},
        targeting={},
        daily_budget=float(campaign.daily_budget or 0),
        total_budget=float(campaign.total_budget or 0),
        recommended_duration_days=30,
        rationale="",
    )
    launch_result = await launch_campaign(plan)
    campaign.status = "active"
    campaign.platform_ids = launch_result.platform_ids
    await db.commit()
    return launch_result.model_dump()


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == uuid.UUID(campaign_id)))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"id": str(campaign.id), "name": campaign.name, "status": campaign.status, "brief": campaign.brief}
