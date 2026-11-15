from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.mastodon_base_url or not settings.mastodon_access_token:
            return self.failure("Missing MASTODON_BASE_URL or MASTODON_ACCESS_TOKEN")
        try:
            base = settings.mastodon_base_url.rstrip("/")
            response = await self.send(
                "POST", f"{base}/api/v1/statuses",
                headers={"Authorization": f"Bearer {settings.mastodon_access_token}"},
                data={"status": message, "visibility": "public"},
            )
            data = response.json()
            # The response URL is the canonical status URL. Visibility was explicitly set to public.
            return self.success(data.get("url"), bool(data.get("url")))
        except Exception as exc:
            return self.failure(f"Mastodon API error: {exc}")
