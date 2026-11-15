import asyncio
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.devto import DevToPlatform
from app.schemas import PlatformResult


class PostingService:
    def __init__(self) -> None:
        # The target platforms are intentionally configured internally.
        self.platforms = [
            BlueskyPlatform(),
            MastodonPlatform(),
            TelegramPlatform(),
            DiscordPlatform(),
            DevToPlatform(),
        ]

    async def publish_everywhere(self, message: str) -> list[PlatformResult]:
        # Each adapter catches its own API/configuration errors. gather also prevents
        # one unexpected adapter exception from cancelling the other posting attempts.
        outcomes = await asyncio.gather(
            *(platform.publish(message) for platform in self.platforms),
            return_exceptions=True,
        )
        results: list[PlatformResult] = []
        for platform, outcome in zip(self.platforms, outcomes):
            if isinstance(outcome, Exception):
                results.append(PlatformResult(
                    platform=platform.name, status="failed",
                    error=f"Unexpected integration error: {str(outcome)[:400]}",
                ))
            else:
                results.append(outcome)
        return results


posting_service = PostingService()
