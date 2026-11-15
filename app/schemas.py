import re
from datetime import datetime
from typing import Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    TypeAdapter,
    field_validator,
)

# Match one URL token. Trailing sentence punctuation is intentionally excluded.
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
URL_ADAPTER = TypeAdapter(HttpUrl)


class PostingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        min_length=1,
        max_length=200,
        description="Text containing exactly one HTTP(S) link"
    )

    @field_validator("message")
    @classmethod
    def validate_single_cta_url(cls, value: str) -> str:
        value = value.strip()
        matches = URL_PATTERN.findall(value)
        if len(matches) != 1:
            raise ValueError("Message must contain exactly one CTA link")

        # Strip common trailing punctuation before URL parsing.
        candidate = matches[0].rstrip(".,!?;:")
        try:
            URL_ADAPTER.validate_python(candidate)
        except Exception as exc:
            raise ValueError("The CTA link must be a valid HTTP or HTTPS URL") from exc
        return value


class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed"]
    posted_url: str | None = None
    public_access: bool = False
    date: str | None = None
    time: str | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool
    overall_status: Literal["success", "partial_success", "failed"]
    results: list[PlatformResult]
