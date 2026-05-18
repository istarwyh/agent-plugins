import json
import os
import sqlite3
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

WORK_DIR = Path.home() / "social-autopilot"
SKILL_DIR = Path(__file__).resolve().parent.parent

REQUIRED_VARS = []

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
    ],
    "channels": {
        "meta": {
            "enabled": True,
            "mode": "facebook_only",
            "require_confirmation": True,
        },
        "xiaohongshu": {
            "enabled": False,
            "publish_mode": "draft",
            "visibility": "公开可见",
            "require_confirmation": True,
            "tags": ["极客资讯", "漫威", "DC", "星球大战", "游戏"],
        },
    },
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

CREATE TABLE IF NOT EXISTS content_briefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    news_url TEXT UNIQUE NOT NULL,
    news_title TEXT,
    category TEXT NOT NULL,
    source_id TEXT,
    relevance_score REAL,
    facts TEXT,
    angle TEXT,
    product_tie_in TEXT,
    image_direction TEXT,
    base_tags TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_cb_news_url ON content_briefs(news_url);

CREATE TABLE IF NOT EXISTS post_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brief_id INTEGER,
    news_url TEXT NOT NULL,
    news_title TEXT,
    category TEXT NOT NULL,
    caption TEXT NOT NULL,
    hashtags TEXT NOT NULL,
    image_suggestion TEXT,
    cta TEXT,
    platform TEXT DEFAULT 'meta',
    platform_title TEXT,
    platform_payload TEXT,
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
    openai_key: str = ""
    openai_base_url: str = ""
    openai_model: str = "moonshotai/kimi-k2.5"
    meta_page_id: str = ""
    meta_token: str = ""
    meta_ig_id: str = ""
    max_posts: int = 10
    min_relevance: float = 0.6
    dry_run: bool = False


def load_context(dry_run: bool = False) -> AppContext:
    env_path = WORK_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)

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
        openai_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL", ""),
        openai_model=os.getenv("OPENAI_MODEL", "moonshotai/kimi-k2.5"),
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
        return _merge_defaults(json.loads(config_path.read_text()), DEFAULT_CONFIG)
    return deepcopy(DEFAULT_CONFIG)


def _merge_defaults(config: dict, defaults: dict) -> dict:
    merged = deepcopy(defaults)
    for key, value in config.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_defaults(value, merged[key])
        else:
            merged[key] = value
    return merged


def find_openai_image_skill() -> Path | None:
    for parent in SKILL_DIR.parents:
        direct_path = parent / "openai-plugin" / "skills" / "image-skill" / "SKILL.md"
        if direct_path.exists():
            return direct_path

        versioned_dir = parent / "openai-plugin"
        if versioned_dir.exists():
            matches = sorted(versioned_dir.glob("*/skills/image-skill/SKILL.md"))
            if matches:
                return matches[-1]

    cache_root = Path.home() / ".claude" / "plugins" / "cache"
    if cache_root.exists():
        matches = sorted(cache_root.glob("*/openai-plugin/*/skills/image-skill/SKILL.md"))
        if matches:
            return matches[-1]

    return None


def get_channel_config(config: dict, channel: str) -> dict:
    return config.get("channels", {}).get(channel, {})


def get_enabled_channels(config: dict) -> list[str]:
    return [
        name for name, channel_config in config.get("channels", {}).items()
        if channel_config.get("enabled", False)
    ]


def init_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SQL_SCHEMA)
        migrate_db(conn)


def migrate_db(conn: sqlite3.Connection):
    columns = {row[1] for row in conn.execute("PRAGMA table_info(post_drafts)").fetchall()}
    migrations = {
        "brief_id": "ALTER TABLE post_drafts ADD COLUMN brief_id INTEGER",
        "platform_title": "ALTER TABLE post_drafts ADD COLUMN platform_title TEXT",
        "platform_payload": "ALTER TABLE post_drafts ADD COLUMN platform_payload TEXT",
    }
    for column, statement in migrations.items():
        if column not in columns:
            conn.execute(statement)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_pd_brief_id ON post_drafts(brief_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pd_platform_status ON post_drafts(platform, status)")


def get_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def ensure_dirs():
    for sub in ["data", "output/news", "output/drafts", "output/cards", "output/xiaohongshu", "logs"]:
        (WORK_DIR / sub).mkdir(parents=True, exist_ok=True)
