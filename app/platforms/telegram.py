from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class TelegramPlatform(BasePlatform):
    name = "Telegram"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            return self.failure("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        try:
            response = await self.send(
                "POST", f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={"chat_id": settings.telegram_chat_id, "text": message, "link_preview_options": {"is_disabled": False}},
            )
            data = response.json()["result"]
            chat = settings.telegram_chat_id
            if chat.startswith("@"):
                url = f"https://t.me/{chat[1:]}/{data['message_id']}"
                return self.success(url, True)
            # Numeric/private chat IDs do not provide a public permalink.
            return self.success(None, False)
        except Exception as exc:
            return self.failure("Telegram request failed. Check the bot token, chat ID, and channel permissions.")
