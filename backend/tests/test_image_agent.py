import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agents.image_agent import process_and_resize, PLATFORM_SIZES


def test_process_and_resize_all_platforms():
    from PIL import Image
    import io
    img = Image.new("RGB", (1080, 1080), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    result = process_and_resize(image_bytes)
    for platform, size in PLATFORM_SIZES.items():
        assert platform in result
        from PIL import Image as PILImage
        img_check = PILImage.open(io.BytesIO(result[platform]))
        assert img_check.size == size


@pytest.mark.asyncio
async def test_generate_image_prompt():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="A vibrant product shot with warm lighting")]
    with patch("agents.image_agent.run_agent", new=AsyncMock(return_value=mock_response)):
        from agents.image_agent import generate_image_prompt
        prompt = await generate_image_prompt("Fitness app for busy professionals", "instagram_square")
    assert len(prompt) > 10
