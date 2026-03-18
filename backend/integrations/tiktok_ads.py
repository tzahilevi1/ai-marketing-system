"""TikTok Ads API integration — sandbox mode."""
from typing import Any


class TikTokAdsClient:
    def __init__(self, access_token: str = "", advertiser_id: str = "") -> None:
        self.access_token = access_token
        self.sandbox = not bool(access_token)

    async def create_campaign(self, name: str, objective: str, budget: float) -> dict[str, Any]:
        if self.sandbox:
            return {"campaign_id": f"mock-tiktok-{name[:10]}", "create_time": 1234567890}
        raise NotImplementedError

    async def get_metrics(self, campaign_id: str, date_range: dict) -> dict[str, Any]:
        if self.sandbox:
            return {
                "impression": 200000,
                "click": 8000,
                "spend": 600.0,
                "conversion": 120,
            }
        raise NotImplementedError

    async def update_budget(self, campaign_id: str, new_budget: float) -> bool:
        return True

    async def pause_ad_group(self, ad_group_id: str) -> bool:
        return True
