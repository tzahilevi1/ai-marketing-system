"""Google Ads API integration — sandbox mode."""
from typing import Any


class GoogleAdsClient:
    def __init__(self, client_id: str = "", developer_token: str = "") -> None:
        self.client_id = client_id
        self.sandbox = not bool(client_id)

    async def create_campaign(self, name: str, goal: str, budget: float) -> dict[str, Any]:
        if self.sandbox:
            return {"id": f"mock-google-campaign-{name[:10]}", "status": "ENABLED"}
        raise NotImplementedError

    async def get_metrics(self, campaign_id: str, date_range: dict) -> dict[str, Any]:
        if self.sandbox:
            return {
                "impressions": 50000,
                "clicks": 1500,
                "cost": 800.0,
                "conversions": 40,
            }
        raise NotImplementedError

    async def update_budget(self, campaign_id: str, new_budget: float) -> bool:
        return True

    async def pause_campaign(self, campaign_id: str) -> bool:
        return True
