from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import hashlib


class NewsItem(BaseModel):
    url: str
    url_hash: str = Field(description="SHA256(url)")
    title: str
    summary: str = Field(default="", max_length=500)
    published_at: Optional[datetime] = None
    source_id: str
    category: str
    language: str = "pt-BR"

    @staticmethod
    def compute_hash(url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()


class PostDraft(BaseModel):
    news_url: str
    news_title: str
    category: str
    caption: str = Field(description="PT-BR caption, <=150 words")
    hashtags: list[str] = Field(description="Exactly 20 hashtags")
    image_suggestion: str = ""
    cta: str = ""
    platform: str = "instagram"
    status: str = "pending"
    relevance_score: float = Field(default=0.0, ge=0, le=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    card_path: Optional[str] = None
    meta_post_id: Optional[str] = None

    @field_validator("hashtags")
    @classmethod
    def check_hashtags(cls, v):
        if len(v) != 20:
            raise ValueError(f"Need 20 hashtags, got {len(v)}")
        return v


class RunResult(BaseModel):
    run_at: datetime = Field(default_factory=datetime.utcnow)
    news_fetched: int = 0
    news_new: int = 0
    posts_created: int = 0
    cards_generated: int = 0
    posts_scheduled: int = 0
    errors: list[str] = Field(default_factory=list)
    duration_ms: int = 0
