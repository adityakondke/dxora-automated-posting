from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DevToPlatform(BasePlatform):
    name = "DEV.to"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.devto_api_key:
            return self.failure("Missing DEVTO_API_KEY")
        try:
            response = await self.send(
                "POST", "https://dev.to/api/articles",
                headers={
                    "api-key": settings.devto_api_key,
                    "Accept": "application/vnd.forem.api-v1+json",
                    "User-Agent": "DXORA-Automated-Posting-Demo/1.0",
                },
                json={"article": {
                    "title": "Automated update",
                    "body_markdown": message,
                    "published": True,
                    "description": message[:160],
                    "tags": ["automation", "python"],
                }},
            )
            data = response.json()
            return self.success(data.get("url"), bool(data.get("url")))
        except Exception as exc:
            return self.failure(f"DEV.to API error: {exc}")
