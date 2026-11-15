from datetime import datetime, timezone
from urllib.parse import quote
from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class BlueskyPlatform(BasePlatform):
    name = "Bluesky"
    api = "https://bsky.social/xrpc"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.bluesky_handle or not settings.bluesky_app_password:
            return self.failure("Missing BLUESKY_HANDLE or BLUESKY_APP_PASSWORD")
        try:
            session_response = await self.send(
                "POST", f"{self.api}/com.atproto.server.createSession",
                json={"identifier": settings.bluesky_handle, "password": settings.bluesky_app_password},
            )
            session = session_response.json()
            created_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            record_response = await self.send(
                "POST", f"{self.api}/com.atproto.repo.createRecord",
                headers={"Authorization": f"Bearer {session['accessJwt']}"},
                json={
                    "repo": session["did"],
                    "collection": "app.bsky.feed.post",
                    "record": {"$type": "app.bsky.feed.post", "text": message, "createdAt": created_at},
                },
            )
            record = record_response.json()
            rkey = record["uri"].rsplit("/", 1)[-1]
            url = f"https://bsky.app/profile/{quote(settings.bluesky_handle, safe='')}/post/{rkey}"
            return self.success(url, True)
        except Exception as exc:
            return self.failure(f"Bluesky API error: {exc}")
