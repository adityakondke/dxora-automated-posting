from abc import ABC, abstractmethod
from datetime import datetime, timezone
import httpx
from app.config import settings
from app.schemas import PlatformResult


class BasePlatform(ABC):
    name: str

    def __init__(self) -> None:
        self.timeout = settings.request_timeout_seconds

    @abstractmethod
    async def publish(self, message: str) -> PlatformResult:
        """Publish one message and return a normalized result."""

    def success(self, url: str | None, public: bool) -> PlatformResult:
        now = datetime.now(timezone.utc).astimezone()
        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=url,
            public_access=public,
            date=now.date().isoformat(),
            time=now.strftime("%H:%M:%S"),
        )

    def failure(self, reason: str) -> PlatformResult:
        return PlatformResult(platform=self.name, status="failed", error=reason[:500])

    async def send(self, method: str, url: str, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
