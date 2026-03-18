from fastapi import APIRouter, UploadFile, File, Form
from agents.image_agent import generate_image_prompt, generate_image, process_and_resize, upload_to_storage

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload")
async def upload_image(
    campaign_id: str = Form(...),
    file: UploadFile = File(...),
):
    image_bytes = await file.read()
    resized = process_and_resize(image_bytes)
    urls = await upload_to_storage(resized, campaign_id)
    return {"urls": urls, "filename": file.filename}


@router.post("/generate")
async def generate(campaign_brief: str, platform: str = "instagram_square", style: str = "photorealistic"):
    prompt = await generate_image_prompt(campaign_brief, platform)
    image_bytes = await generate_image(prompt, style)
    return {"prompt": prompt, "size": len(image_bytes), "message": "Image generated successfully"}


@router.post("/generate-and-upload")
async def generate_and_upload(campaign_id: str, campaign_brief: str, platform: str = "instagram_square"):
    prompt = await generate_image_prompt(campaign_brief, platform)
    image_bytes = await generate_image(prompt)
    resized = process_and_resize(image_bytes)
    urls = await upload_to_storage(resized, campaign_id)
    return {"prompt": prompt, "urls": urls}
