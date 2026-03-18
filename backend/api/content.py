from fastapi import APIRouter
from pydantic import BaseModel

from agents.content_agent import (
    CampaignBrief, generate_ad_copy, generate_ab_variants,
    generate_social_post, check_compliance
)

router = APIRouter(prefix="/content", tags=["content"])


class GenerateRequest(BaseModel):
    brief: CampaignBrief
    platform: str = "facebook"
    variants: int = 3


@router.post("/generate")
async def generate_copy(req: GenerateRequest):
    copies = await generate_ad_copy(req.brief, req.platform, req.variants)
    return {"copies": [c.model_dump() for c in copies]}


@router.post("/ab-variants")
async def ab_variants(original: str, count: int = 5):
    variants = await generate_ab_variants(original, count)
    return {"variants": variants}


@router.post("/social-post")
async def social_post(topic: str, tone: str = "friendly", platform: str = "instagram"):
    post = await generate_social_post(topic, tone, platform)
    return post.model_dump()


@router.post("/compliance-check")
async def compliance_check(content: str):
    report = await check_compliance(content)
    return report.model_dump()
