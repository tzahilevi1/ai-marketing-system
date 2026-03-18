"""Meta (Facebook/Instagram) Ads API integration — sandbox mode."""
from typing import Any


class MetaAdsClient:
    def __init__(self, access_token: str = "", ad_account_id: str = "") -> None:
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.sandbox = not bool(access_token)

    async def create_campaign(self, name: str, objective: str, budget: float) -> dict[str, Any]:
        if self.sandbox:
            return {"id": f"mock-meta-campaign-{name[:10]}", "status": "ACTIVE"}
        raise NotImplementedError("Production Meta integration not yet implemented")

    async def get_metrics(self, campaign_id: str, date_range: dict) -> dict[str, Any]:
        if self.sandbox:
            return {
                "impressions": 100000,
                "clicks": 3000,
                "spend": 1500.0,
                "conversions": 75,
            }
        raise NotImplementedError

    async def update_budget(self, campaign_id: str, new_budget: float) -> bool:
        return True

    async def pause_ad(self, ad_id: str) -> bool:
        return True
