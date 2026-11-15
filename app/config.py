from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Bluesky
    bluesky_handle: str | None = None
    bluesky_app_password: str | None = None

    # Mastodon (use the instance URL where your account lives)
    mastodon_base_url: str | None = None
    mastodon_access_token: str | None = None

    # Telegram: bot must be an administrator in the target channel
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    # Discord: create a webhook in the target channel
    discord_webhook_url: str | None = None

    # DEV.to / Forem API key
    devto_api_key: str | None = None

    request_timeout_seconds: float = 20.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
