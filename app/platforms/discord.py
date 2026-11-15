
from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DiscordPlatform(BasePlatform):
    name = "Discord"

    async def publish(self, message: str) -> PlatformResult:
        webhook_url = settings.discord_webhook_url

        if not webhook_url:
            return self.failure("Missing DISCORD_WEBHOOK_URL")

        try:
            # Retrieve webhook metadata to obtain guild and channel IDs.
            guild_id = None
            channel_id = None

            try:
                webhook_response = await self.send(
                    "GET",
                    webhook_url,
                )
                webhook_data = webhook_response.json()

                guild_id = webhook_data.get("guild_id")
                channel_id = webhook_data.get("channel_id")

            except Exception:
                # Continue with publishing even if metadata lookup fails.
                pass

            # Ask Discord to return the created message object.
            separator = "&" if "?" in webhook_url else "?"
            response = await self.send(
                "POST",
                f"{webhook_url}{separator}wait=true",
                json={
                    "content": message,
                    "allowed_mentions": {"parse": []},
                },
            )

            data = response.json()

            message_id = data.get("id")
            guild_id = data.get("guild_id") or guild_id
            channel_id = data.get("channel_id") or channel_id

            # Construct the Discord message permalink.
            posted_url = None

            if guild_id and channel_id and message_id:
                posted_url = (
                    f"https://discord.com/channels/"
                    f"{guild_id}/{channel_id}/{message_id}"
                )

            # A permalink does not guarantee anonymous public access.
            return self.success(posted_url, False)

        except Exception:
            return self.failure(
                "Discord publishing failed. Check the webhook URL "
                "and channel permissions."
            )
