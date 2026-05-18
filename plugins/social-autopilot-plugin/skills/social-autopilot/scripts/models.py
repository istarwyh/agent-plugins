from pydantic import BaseModel, Field
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


class ContentBrief(BaseModel):
    id: Optional[int] = None
    news_url: str
    news_title: str
    category: str
    source_id: str = ""
    relevance_score: float = Field(default=0.0, ge=0, le=1)
    facts: list[str] = Field(default_factory=list)
    angle: str = ""
    product_tie_in: str = ""
    image_direction: str = ""
    base_tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PostDraft(BaseModel):
    brief_id: Optional[int] = None
    news_url: str
    news_title: str
    category: str
    caption: str
    hashtags: list[str]
    image_suggestion: str = ""
    cta: str = ""
    platform: str = "meta"
    platform_title: Optional[str] = None
    platform_payload: Optional[dict] = None
    status: str = "pending"
    relevance_score: float = Field(default=0.0, ge=0, le=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    card_path: Optional[str] = None
    meta_post_id: Optional[str] = None


class RunResult(BaseModel):
    run_at: datetime = Field(default_factory=datetime.utcnow)
    news_fetched: int = 0
    news_new: int = 0
    posts_created: int = 0
    cards_generated: int = 0
    posts_scheduled: int = 0
    errors: list[str] = Field(default_factory=list)
    duration_ms: int = 0
