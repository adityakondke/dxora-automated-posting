
import httpx

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
                "POST",
                "https://dev.to/api/articles",
                headers={
                    "api-key": settings.devto_api_key,
                    "Accept": "application/vnd.forem.api-v1+json",
                    "User-Agent": "DXORA-Automated-Posting-Demo/1.0",
                },
                json={
                    "article": {
                        "title": "Automated update",
                        "body_markdown": message,
                        "published": True,
                        "description": message[:160],
                        "tags": ["automation", "python"],
                    }
                },
            )

            data = response.json()
            article_url = data.get("url")

            if not article_url:
                return self.failure(
                    "DEV.to accepted the request but returned no article URL."
                )

            return self.success(article_url, True)

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            try:
                error_detail = exc.response.text.strip()
            except Exception:
                error_detail = ""

            if not error_detail:
                error_detail = "No error details returned by DEV.to."

            return self.failure(
                f"DEV.to HTTP {status_code}: {error_detail[:350]}"
            )

        except httpx.RequestError as exc:
            detail = str(exc).strip() or repr(exc)

            return self.failure(
                f"DEV.to network error ({type(exc).__name__}): {detail[:350]}"
            )

        except Exception as exc:
            detail = str(exc).strip() or repr(exc)

            return self.failure(
                f"DEV.to unexpected error ({type(exc).__name__}): {detail[:350]}"
            )
