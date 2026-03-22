import json
import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

WORK_DIR = Path.home() / "social-autopilot"
SKILL_DIR = Path(__file__).resolve().parent.parent

REQUIRED_VARS = ["ANTHROPIC_API_KEY"]

DEFAULT_CONFIG = {
    "sources": [
        {
            "id": "marvel",
            "category": "漫威影业",
            "priority": "high",
            "interval_hours": 4,
            "urls": [
                "https://news.google.com/rss/search?q=marvel+MCU+trailer&hl=pt-BR&gl=BR&ceid=BR:pt",
                "https://news.google.com/rss/search?q=marvel+lançamento+filme&hl=pt-BR&gl=BR&ceid=BR:pt",
            ],
            "keywords_whitelist": [
                "marvel", "mcu", "avengers", "spider-man", "thor",
                "iron man", "deadpool", "x-men", "wolverine",
                "lançamento", "trailer", "disney+",
            ],
            "keywords_blacklist": ["rumor não confirmado", "fake", "boato"],
            "brand_color": "#E23636",
            "tags_seed": ["#marvel", "#mcu", "#avengers", "#spiderman", "#marvelstudios"],
        },
        {
            "id": "dc",
            "category": "DC影业",
            "priority": "high",
            "interval_hours": 4,
            "urls": [
                "https://news.google.com/rss/search?q=DC+Comics+filme+trailer&hl=pt-BR&gl=BR&ceid=BR:pt",
                "https://news.google.com/rss/search?q=superman+batman+2025+2026&hl=pt-BR&gl=BR&ceid=BR:pt",
            ],
            "keywords_whitelist": [
                "dc", "batman", "superman", "wonder woman", "flash",
                "aquaman", "james gunn", "dcu", "joker",
            ],
            "keywords_blacklist": [],
            "brand_color": "#0476F2",
            "tags_seed": ["#dc", "#batman", "#superman", "#dcuniverse", "#wonderwoman"],
        },
        {
            "id": "starwars",
            "category": "星球大战",
            "priority": "medium",
            "interval_hours": 4,
            "urls": [
                "https://news.google.com/rss/search?q=star+wars+disney+série+filme&hl=pt-BR&gl=BR&ceid=BR:pt",
                "https://news.google.com/rss/search?q=mandalorian+andor+ahsoka&hl=pt-BR&gl=BR&ceid=BR:pt",
            ],
            "keywords_whitelist": [
                "star wars", "mandalorian", "jedi", "sith",
                "disney+", "lucasfilm", "andor", "ahsoka", "grogu",
            ],
            "keywords_blacklist": [],
            "brand_color": "#FFD700",
            "tags_seed": ["#starwars", "#themandalorian", "#jedi", "#lucasfilm"],
        },
        {
            "id": "f1",
            "category": "F1 2026",
            "priority": "medium",
            "interval_hours": 24,
            "urls": [
                "https://news.google.com/rss/search?q=formula+1+2026+temporada&hl=pt-BR&gl=BR&ceid=BR:pt",
            ],
            "keywords_whitelist": [
                "formula 1", "f1", "verstappen", "hamilton",
                "ferrari", "mclaren", "red bull",
            ],
            "keywords_blacklist": [],
            "brand_color": "#FF1801",
            "tags_seed": ["#f1", "#formula1", "#formulaum", "#ferrari"],
        },
        {
            "id": "games",
            "category": "游戏",
            "priority": "low",
            "interval_hours": 24,
            "urls": [
                "https://news.google.com/rss/search?q=game+release+geek+2025&hl=pt-BR&gl=BR&ceid=BR:pt",
            ],
            "keywords_whitelist": [
                "playstation", "xbox", "nintendo", "game release",
                "rpg", "lançamento jogo",
            ],
            "keywords_blacklist": [],
            "brand_color": "#7B2FBE",
            "tags_seed": ["#gamer", "#gaming", "#playstation", "#xbox"],
        },
    ]
}

SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS processed_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_hash TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    source_id TEXT NOT NULL,
    category TEXT,
    processed_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_pn_source ON processed_news(source_id);

CREATE TABLE IF NOT EXISTS post_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    news_url TEXT NOT NULL,
    news_title TEXT,
    category TEXT NOT NULL,
    caption TEXT NOT NULL,
    hashtags TEXT NOT NULL,
    image_suggestion TEXT,
    cta TEXT,
    platform TEXT DEFAULT 'instagram',
    status TEXT DEFAULT 'pending',
    relevance_score REAL,
    card_path TEXT,
    meta_post_id TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    scheduled_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_pd_status ON post_drafts(status);

CREATE TABLE IF NOT EXISTS run_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at TEXT DEFAULT (datetime('now')),
    news_fetched INTEGER,
    news_new INTEGER,
    posts_created INTEGER,
    cards_generated INTEGER,
    posts_scheduled INTEGER,
    errors TEXT,
    duration_ms INTEGER
);
"""


@dataclass
class AppContext:
    work_dir: Path
    db_path: Path
    config: dict
    anthropic_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"
    meta_page_id: str = ""
    meta_token: str = ""
    meta_ig_id: str = ""
    max_posts: int = 10
    min_relevance: float = 0.6
    dry_run: bool = False


def load_context(dry_run: bool = False) -> AppContext:
    env_path = WORK_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)

    missing = [k for k in REQUIRED_VARS if not os.getenv(k)]
    if missing and not dry_run:
        raise RuntimeError(
            f"缺少环境变量: {', '.join(missing)}。"
            f"请在 {env_path} 中填入对应值。"
        )

    config = load_config()

    return AppContext(
        work_dir=WORK_DIR,
        db_path=WORK_DIR / "data" / "news.db",
        config=config,
        anthropic_key=os.getenv("ANTHROPIC_API_KEY", ""),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
        meta_page_id=os.getenv("META_PAGE_ID", ""),
        meta_token=os.getenv("META_PAGE_ACCESS_TOKEN", ""),
        meta_ig_id=os.getenv("META_IG_USER_ID", ""),
        max_posts=int(os.getenv("MAX_POSTS_PER_RUN", "10")),
        min_relevance=float(os.getenv("MIN_RELEVANCE_SCORE", "0.6")),
        dry_run=dry_run or os.getenv("DRY_RUN", "false").lower() == "true",
    )


def load_config() -> dict:
    config_path = WORK_DIR / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return DEFAULT_CONFIG


def init_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SQL_SCHEMA)


def get_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def ensure_dirs():
    for sub in ["data", "output/news", "output/drafts", "output/cards", "logs"]:
        (WORK_DIR / sub).mkdir(parents=True, exist_ok=True)
